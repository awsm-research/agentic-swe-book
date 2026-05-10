"""
monitor/anomaly_detector.py — Z-score anomaly detection for MedAgent sessions.

Reads session records from a SQLite checkpoints database (written by
LangGraph's SqliteSaver), computes baseline statistics from the last 50
sessions, and alerts when the current session's cost or turn count is
statistically unusual.

Alert conditions:
  - session cost > mean + 3 * std  (Z-score > 3)  → CRITICAL
  - session cost > mean + 2 * std  (Z-score > 2)  → WARNING
  - turn_count > 15                               → WARNING (stuck-loop risk)
  - termination_reason == 'recursion_limit'        → CRITICAL

Usage:
    python anomaly_detector.py --session-id SESSION_ID [--db-path checkpoints.db]
    python anomaly_detector.py --demo               # run simulation demo
"""

import argparse
import json
import logging
import random
import sqlite3
import statistics
import sys
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class SessionRecord:
    """Metrics extracted from a completed MedAgent session."""

    session_id: str
    turn_count: int
    cost_usd: float
    duration_seconds: float
    termination_reason: str
    tool_errors: int


@dataclass
class AnomalyAlert:
    """An anomaly detected in a session's metrics."""

    session_id: str
    metric_name: str
    observed_value: float
    baseline_mean: float
    baseline_std: float
    z_score: float
    severity: str  # 'warning' or 'critical'
    message: str


# ---------------------------------------------------------------------------
# Core detector
# ---------------------------------------------------------------------------


class AgentAnomalyDetector:
    """Z-score anomaly detector for MedAgent session metrics.

    Maintains a rolling window of historical session metrics and fires
    alerts when a new session's metrics are statistically unusual.

    Args:
        window_size:        Number of recent sessions for baseline computation.
        warning_threshold:  Z-score for WARNING alerts.
        critical_threshold: Z-score for CRITICAL alerts.
        max_turn_count:     Hard threshold for turn count (stuck-loop risk).
    """

    def __init__(
        self,
        window_size: int = 50,
        warning_threshold: float = 2.0,
        critical_threshold: float = 3.0,
        max_turn_count: int = 15,
    ):
        self.window_size = window_size
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.max_turn_count = max_turn_count
        self._history: list[SessionRecord] = []

    def load_history_from_db(self, db_path: str, limit: int = 50) -> int:
        """Load recent session metrics from the SQLite checkpoints database.

        The LangGraph SqliteSaver stores checkpoints in a 'checkpoints' table.
        We extract session-level aggregates (turn count as message count,
        estimated cost from token proxies) from the stored JSON blobs.

        Returns the number of sessions loaded.
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Inspect available tables
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = {row[0] for row in cursor.fetchall()}

            if "checkpoints" not in tables:
                logger.warning(
                    "anomaly_detector: 'checkpoints' table not found in %s. "
                    "Available tables: %s",
                    db_path,
                    tables,
                )
                conn.close()
                return 0

            # Retrieve the most recent checkpoint per thread_id (session)
            cursor.execute(
                """
                SELECT thread_id,
                       checkpoint,
                       metadata
                FROM checkpoints
                GROUP BY thread_id
                HAVING MAX(checkpoint_id)
                ORDER BY MAX(checkpoint_id) DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            conn.close()

            loaded = 0
            for thread_id, checkpoint_blob, metadata_blob in rows:
                try:
                    checkpoint = (
                        json.loads(checkpoint_blob)
                        if isinstance(checkpoint_blob, str)
                        else checkpoint_blob
                    )
                    metadata = (
                        json.loads(metadata_blob)
                        if isinstance(metadata_blob, str)
                        else (metadata_blob or {})
                    )

                    # Extract message count as a proxy for turn count
                    messages = checkpoint.get("channel_values", {}).get(
                        "messages", []
                    )
                    turn_count = sum(
                        1
                        for m in messages
                        if isinstance(m, dict) and m.get("type") == "ai"
                        and m.get("tool_calls")
                    )

                    # Estimate cost: ~$0.001 per 1K tokens (rough proxy)
                    total_chars = sum(
                        len(m.get("content", ""))
                        for m in messages
                        if isinstance(m, dict)
                    )
                    cost_usd = (total_chars / 4 / 1000) * 0.001

                    termination = metadata.get(
                        "termination_reason", "completed"
                    )

                    record = SessionRecord(
                        session_id=thread_id,
                        turn_count=max(turn_count, 1),
                        cost_usd=max(cost_usd, 0.0),
                        duration_seconds=metadata.get("duration_seconds", 10.0),
                        termination_reason=termination,
                        tool_errors=metadata.get("tool_errors", 0),
                    )
                    self._history.append(record)
                    loaded += 1
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue

            logger.info(
                "anomaly_detector: loaded %d session records from %s",
                loaded,
                db_path,
            )
            return loaded

        except sqlite3.Error as exc:
            logger.error(
                "anomaly_detector: database error reading %s: %s", db_path, exc
            )
            return 0

    def record(self, session: SessionRecord) -> list[AnomalyAlert]:
        """Record a new session and return any anomaly alerts.

        Requires at least 10 historical sessions for reliable baselines.
        If fewer than 10 sessions are available, no statistical alerts
        are generated (hard threshold checks still apply).
        """
        self._history.append(session)
        if len(self._history) > self.window_size:
            self._history = self._history[-self.window_size :]

        alerts: list[AnomalyAlert] = []

        # Hard threshold: stuck-loop risk
        if session.turn_count > self.max_turn_count:
            alerts.append(
                AnomalyAlert(
                    session_id=session.session_id,
                    metric_name="turn_count",
                    observed_value=float(session.turn_count),
                    baseline_mean=float(self.max_turn_count),
                    baseline_std=0.0,
                    z_score=float("inf"),
                    severity="warning",
                    message=(
                        f"Session {session.session_id}: turn_count={session.turn_count} "
                        f"exceeds hard limit of {self.max_turn_count}. "
                        "WARNING: possible stuck loop."
                    ),
                )
            )

        # Hard threshold: recursion limit hit
        if session.termination_reason == "recursion_limit":
            alerts.append(
                AnomalyAlert(
                    session_id=session.session_id,
                    metric_name="termination_reason",
                    observed_value=1.0,
                    baseline_mean=0.0,
                    baseline_std=0.0,
                    z_score=float("inf"),
                    severity="critical",
                    message=(
                        f"Session {session.session_id} hit recursion limit — "
                        "agent likely stuck in a loop. "
                        "Check tool availability and session traces."
                    ),
                )
            )

        # Statistical Z-score checks (require ≥ 10 historical sessions)
        history_excluding_current = self._history[:-1]
        if len(history_excluding_current) >= 10:
            for metric_name in ("cost_usd", "duration_seconds"):
                alert = self._check_metric(
                    session.session_id,
                    metric_name,
                    getattr(session, metric_name),
                    history_excluding_current,
                )
                if alert:
                    alerts.append(alert)

        # Log all alerts
        for alert in alerts:
            log_fn = (
                logger.error if alert.severity == "critical" else logger.warning
            )
            log_fn(
                "anomaly_detected session=%s metric=%s z_score=%s severity=%s: %s",
                alert.session_id,
                alert.metric_name,
                f"{alert.z_score:.2f}" if alert.z_score != float("inf") else "inf",
                alert.severity,
                alert.message,
            )

        return alerts

    def _check_metric(
        self,
        session_id: str,
        metric_name: str,
        value: float,
        history: list[SessionRecord],
    ) -> Optional[AnomalyAlert]:
        """Compute Z-score and return an alert if it exceeds a threshold."""
        values = [getattr(s, metric_name) for s in history]
        if len(values) < 5:
            return None

        mean = statistics.mean(values)
        try:
            std = statistics.stdev(values)
        except statistics.StatisticsError:
            return None

        if std < 1e-9:
            return None  # No variance — Z-score undefined

        z = (value - mean) / std

        if z > self.critical_threshold:
            return AnomalyAlert(
                session_id=session_id,
                metric_name=metric_name,
                observed_value=value,
                baseline_mean=mean,
                baseline_std=std,
                z_score=z,
                severity="critical",
                message=(
                    f"Session {session_id}: {metric_name}={value:.4f} is "
                    f"{z:.1f} std devs above mean ({mean:.4f}). "
                    "CRITICAL: possible runaway session."
                ),
            )
        elif z > self.warning_threshold:
            return AnomalyAlert(
                session_id=session_id,
                metric_name=metric_name,
                observed_value=value,
                baseline_mean=mean,
                baseline_std=std,
                z_score=z,
                severity="warning",
                message=(
                    f"Session {session_id}: {metric_name}={value:.4f} is "
                    f"{z:.1f} std devs above mean ({mean:.4f}). "
                    "WARNING: unusually high, worth investigating."
                ),
            )
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def detect_anomalies(
    session_id: str,
    turn_count: int,
    cost_usd: float,
    duration_seconds: float,
    termination_reason: str = "completed",
    tool_errors: int = 0,
    db_path: str = "checkpoints.db",
) -> list[AnomalyAlert]:
    """Detect anomalies for a completed session.

    Loads historical sessions from the SQLite checkpoints database,
    then evaluates the current session against the baseline.

    Args:
        session_id:          The session identifier.
        turn_count:          Number of tool-calling turns in the session.
        cost_usd:            Estimated session cost in USD.
        duration_seconds:    Wall-clock duration of the session.
        termination_reason:  'completed', 'recursion_limit', or 'error'.
        tool_errors:         Number of tool call errors in the session.
        db_path:             Path to the LangGraph SQLite checkpoints database.

    Returns:
        List of AnomalyAlert objects (empty if no anomalies detected).
    """
    detector = AgentAnomalyDetector(
        window_size=50,
        warning_threshold=2.0,
        critical_threshold=3.0,
        max_turn_count=15,
    )

    detector.load_history_from_db(db_path, limit=50)

    current_session = SessionRecord(
        session_id=session_id,
        turn_count=turn_count,
        cost_usd=cost_usd,
        duration_seconds=duration_seconds,
        termination_reason=termination_reason,
        tool_errors=tool_errors,
    )

    return detector.record(current_session)


# ---------------------------------------------------------------------------
# Simulation demo
# ---------------------------------------------------------------------------


def run_simulation_demo() -> None:
    """Demonstrate anomaly detection catching a stuck-loop session."""
    detector = AgentAnomalyDetector(
        window_size=50,
        warning_threshold=2.0,
        critical_threshold=3.0,
        max_turn_count=15,
    )

    random.seed(42)
    print("Simulating 20 normal sessions...")
    for i in range(20):
        detector.record(
            SessionRecord(
                session_id=f"session-{i:04d}",
                turn_count=random.randint(2, 4),
                cost_usd=random.uniform(0.01, 0.03),
                duration_seconds=random.uniform(5.0, 15.0),
                termination_reason="completed",
                tool_errors=0,
            )
        )

    print("\nSimulating stuck-loop session...")
    alerts = detector.record(
        SessionRecord(
            session_id="session-STUCK",
            turn_count=15,
            cost_usd=1.25,
            duration_seconds=120.0,
            termination_reason="recursion_limit",
            tool_errors=10,
        )
    )

    print(f"\nAnomalies detected: {len(alerts)}")
    for alert in alerts:
        print(f"  [{alert.severity.upper()}] {alert.message}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="MedAgent anomaly detector — check a session for unusual metrics."
    )
    parser.add_argument(
        "--session-id",
        type=str,
        help="Session ID to evaluate.",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="checkpoints.db",
        help="Path to the LangGraph SQLite checkpoints database (default: checkpoints.db).",
    )
    parser.add_argument(
        "--turn-count",
        type=int,
        default=3,
        help="Number of tool-calling turns in the session.",
    )
    parser.add_argument(
        "--cost-usd",
        type=float,
        default=0.02,
        help="Estimated session cost in USD.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=10.0,
        help="Session duration in seconds.",
    )
    parser.add_argument(
        "--termination",
        type=str,
        default="completed",
        choices=["completed", "recursion_limit", "error"],
        help="Session termination reason.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run the stuck-loop simulation demo instead.",
    )

    args = parser.parse_args()

    if args.demo:
        run_simulation_demo()
        sys.exit(0)

    if not args.session_id:
        parser.error("--session-id is required unless --demo is specified.")

    alerts = detect_anomalies(
        session_id=args.session_id,
        turn_count=args.turn_count,
        cost_usd=args.cost_usd,
        duration_seconds=args.duration,
        termination_reason=args.termination,
        db_path=args.db_path,
    )

    if alerts:
        print(f"\n{len(alerts)} anomaly alert(s) for session '{args.session_id}':")
        for alert in alerts:
            print(f"  [{alert.severity.upper()}] {alert.message}")
        sys.exit(1)
    else:
        print(f"No anomalies detected for session '{args.session_id}'.")
        sys.exit(0)
