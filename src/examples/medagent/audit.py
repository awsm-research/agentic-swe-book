"""
audit.py — Append-only audit logger for MedAgent (Chapter 24).

Implements a legally defensible audit trail for all MedAgent sessions,
tool calls, approval requests, approval decisions, and security alerts.

In production, writes to PostgreSQL with INSERT-only permissions for the
medagent service account — DELETE and UPDATE are explicitly revoked.

In development (no DATABASE_URL set), writes to a JSONL file.

The AUDIT_SCHEMA SQL below creates the production table. Run it as a
database administrator (not the medagent service account).

Usage:
    from audit import AuditLogger

    audit = AuditLogger()
    audit.log_session_start("session-001", "PAT-00123", "dr-jones", "question")
    audit.log_tool_call("session-001", "lookup_patient_records", {...}, "...", 42.1, True)
    audit.log_approval_request("session-001", "PAT-00123", "submit_lab_order", {...}, "INR below range")
    audit.log_approval_decision("session-001", "dr-jones", "submit_lab_order", True, None)
    audit.log_session_complete("session-001", "PAT-00123", "Draft note produced.")
    records = audit.get_session_log("session-001")
"""

import json
import logging
import os
import pathlib
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# PostgreSQL DDL — run as DBA before deploying to production
# ---------------------------------------------------------------------------

AUDIT_SCHEMA = """
-- Run as a database administrator, NOT as the medagent application user.

CREATE TABLE IF NOT EXISTS audit_log (
    id          BIGSERIAL PRIMARY KEY,
    event_id    UUID NOT NULL DEFAULT gen_random_uuid(),
    session_id  TEXT NOT NULL,
    event_type  TEXT NOT NULL,
    patient_id  TEXT,
    actor_id    TEXT NOT NULL,
    action      TEXT NOT NULL,
    arguments   JSONB,
    outcome     TEXT,
    approver_id TEXT,
    timestamp   TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    CONSTRAINT event_type_check CHECK (
        event_type IN (
            'session_start', 'session_end',
            'tool_call',
            'approval_request', 'approval_decision',
            'security_alert'
        )
    )
);

-- Grant INSERT-only to the medagent application role
GRANT INSERT ON audit_log TO medagent_app;
GRANT SELECT ON audit_log TO medagent_app;
REVOKE UPDATE, DELETE ON audit_log FROM medagent_app;

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_audit_session
    ON audit_log (session_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_patient
    ON audit_log (patient_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_approver
    ON audit_log (approver_id, timestamp)
    WHERE approver_id IS NOT NULL;
"""

# ---------------------------------------------------------------------------
# AuditLogger class
# ---------------------------------------------------------------------------


class AuditLogger:
    """Append-only audit logger for MedAgent.

    Writes to PostgreSQL in production (set DATABASE_URL env var) or to a
    JSONL file in development. Records are never updated or deleted by the
    application — this is enforced at the database level with REVOKE UPDATE
    / DELETE on the medagent_app role.

    Args:
        database_url: PostgreSQL connection string. If None, falls back to
                      the DATABASE_URL environment variable, then to JSONL.
        audit_file:   Path for the development JSONL fallback. If None,
                      uses the MEDAGENT_AUDIT_FILE env var or
                      'data/medagent_audit.jsonl'.
    """

    def __init__(
        self,
        database_url: Optional[str] = None,
        audit_file: Optional[str] = None,
    ):
        self.database_url = database_url or os.environ.get("DATABASE_URL")
        self.audit_file = audit_file or os.environ.get(
            "MEDAGENT_AUDIT_FILE", "data/medagent_audit.jsonl"
        )

    # ---------------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------------

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _base_record(
        self,
        event_type: str,
        session_id: str,
        actor_id: str,
        action: str,
        **kwargs: Any,
    ) -> dict:
        """Build a base audit record with all required fields."""
        return {
            "event_id": str(uuid.uuid4()),
            "session_id": session_id,
            "event_type": event_type,
            "actor_id": actor_id,
            "action": action,
            "timestamp": self._now(),
            **kwargs,
        }

    def _insert(self, record: dict) -> None:
        """Insert an audit record. Raises on failure — never silently drops records.

        Failure to write an audit record is a critical error: it means an
        action was taken without a corresponding audit trail. The caller should
        treat an exception here as a system-level failure.
        """
        if self.database_url:
            self._insert_postgres(record)
        else:
            self._append_jsonl(record)

    def _insert_postgres(self, record: dict) -> None:
        """Write to PostgreSQL. Requires psycopg2."""
        try:
            import psycopg2  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "psycopg2 is required for PostgreSQL audit logging. "
                "Install it with: pip install psycopg2-binary"
            ) from exc

        conn = psycopg2.connect(self.database_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO audit_log
                        (event_id, session_id, event_type, patient_id,
                         actor_id, action, arguments, outcome, approver_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        record["event_id"],
                        record["session_id"],
                        record["event_type"],
                        record.get("patient_id"),
                        record["actor_id"],
                        record["action"],
                        json.dumps(record.get("arguments")),
                        record.get("outcome"),
                        record.get("approver_id"),
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    def _append_jsonl(self, record: dict) -> None:
        """Append to JSONL file (development fallback)."""
        pathlib.Path(self.audit_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")

    # ---------------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------------

    def log_tool_call(
        self,
        session_id: str,
        patient_id: Optional[str],
        tool_name: str,
        arguments: dict,
        outcome: str,
    ) -> None:
        """Record a tool call with its inputs and outcome.

        Args:
            session_id: The MedAgent session identifier.
            patient_id: The patient this tool call relates to (may be None).
            tool_name:  The name of the tool that was called.
            arguments:  The input arguments passed to the tool (dict).
            outcome:    The tool's return value (truncated to 500 chars for storage).
        """
        record = self._base_record(
            event_type="tool_call",
            session_id=session_id,
            actor_id="medagent_system",
            action=tool_name,
            patient_id=patient_id,
            arguments=arguments,
            outcome=str(outcome)[:500],
        )
        self._insert(record)
        logger.debug(
            "audit=tool_call session=%s tool=%s", session_id, tool_name
        )

    def log_approval_request(
        self,
        session_id: str,
        patient_id: str,
        action: str,
        arguments: dict,
        reasoning: str,
    ) -> None:
        """Record that the agent has proposed an irreversible action requiring approval.

        Args:
            session_id: The session identifier.
            patient_id: The patient the action concerns.
            action:     The action type (e.g. 'submit_lab_order').
            arguments:  The action parameters.
            reasoning:  The agent's stated clinical reasoning for the action.
        """
        record = self._base_record(
            event_type="approval_request",
            session_id=session_id,
            actor_id="medagent_agent",
            action=action,
            patient_id=patient_id,
            arguments={**arguments, "agent_reasoning": reasoning},
            outcome="pending",
        )
        self._insert(record)
        logger.info(
            "audit=approval_request session=%s action=%s patient=%s",
            session_id,
            action,
            patient_id,
        )

    def log_approval_decision(
        self,
        session_id: str,
        approver_id: str,
        action: str,
        decision: bool,
        reason: Optional[str],
    ) -> None:
        """Record a clinician's approval or rejection of a proposed action.

        Args:
            session_id:  The session identifier.
            approver_id: The authenticated clinician ID (e.g. 'dr-smith-001').
            action:      The action that was approved or rejected.
            decision:    True if approved, False if rejected.
            reason:      Rejection reason (required when decision=False).
        """
        outcome = "approved" if decision else f"rejected: {reason}"
        record = self._base_record(
            event_type="approval_decision",
            session_id=session_id,
            actor_id=approver_id,
            action=action,
            approver_id=approver_id,
            arguments={"decision": decision, "reason": reason},
            outcome=outcome,
        )
        self._insert(record)
        logger.info(
            "audit=approval_decision session=%s action=%s approved=%s approver=%s",
            session_id,
            action,
            decision,
            approver_id,
        )

    def log_session_complete(
        self,
        session_id: str,
        patient_id: Optional[str],
        final_output: str,
    ) -> None:
        """Record successful session completion with a preview of the final output.

        Args:
            session_id:   The session identifier.
            patient_id:   The patient this session concerned (may be None).
            final_output: The agent's final answer or draft note (first 300 chars stored).
        """
        record = self._base_record(
            event_type="session_end",
            session_id=session_id,
            actor_id="medagent_system",
            action="session_complete",
            patient_id=patient_id,
            arguments={"final_output_preview": str(final_output)[:300]},
            outcome="completed",
        )
        self._insert(record)
        logger.info(
            "audit=session_complete session=%s patient=%s", session_id, patient_id
        )

    def log_session_start(
        self,
        session_id: str,
        patient_id: Optional[str],
        actor_id: str,
        question: str,
    ) -> None:
        """Record session initiation.

        Args:
            session_id: The session identifier.
            patient_id: The patient this session concerns (may be None).
            actor_id:   The authenticated user who initiated the session.
            question:   The clinical question posed (first 500 chars stored).
        """
        record = self._base_record(
            event_type="session_start",
            session_id=session_id,
            actor_id=actor_id,
            action="session_start",
            patient_id=patient_id,
            arguments={"question_preview": str(question)[:500]},
            outcome="started",
        )
        self._insert(record)
        logger.info(
            "audit=session_start session=%s patient=%s actor=%s",
            session_id,
            patient_id,
            actor_id,
        )

    def log_security_alert(
        self,
        session_id: str,
        alert_type: str,
        details: dict,
    ) -> None:
        """Record a security event (e.g. prompt injection detected).

        Args:
            session_id:  The session identifier.
            alert_type:  Short identifier (e.g. 'prompt_injection').
            details:     Additional details about the event.
        """
        record = self._base_record(
            event_type="security_alert",
            session_id=session_id,
            actor_id="medagent_security",
            action=alert_type,
            arguments=details,
            outcome="alert_raised",
        )
        self._insert(record)
        logger.critical(
            "audit=security_alert session=%s type=%s", session_id, alert_type
        )

    def get_session_log(self, session_id: str) -> list[dict]:
        """Retrieve all audit records for a session.

        In PostgreSQL mode: queries the audit_log table.
        In JSONL mode: scans the JSONL file and filters by session_id.

        Returns:
            List of audit record dicts in chronological order.
        """
        if self.database_url:
            return self._get_session_log_postgres(session_id)
        return self._get_session_log_jsonl(session_id)

    def _get_session_log_postgres(self, session_id: str) -> list[dict]:
        """Query PostgreSQL for a session's audit records."""
        try:
            import psycopg2
            import psycopg2.extras

            conn = psycopg2.connect(self.database_url)
            try:
                with conn.cursor(
                    cursor_factory=psycopg2.extras.RealDictCursor
                ) as cur:
                    cur.execute(
                        """
                        SELECT event_id, session_id, event_type, patient_id,
                               actor_id, action, arguments, outcome,
                               approver_id, timestamp
                        FROM audit_log
                        WHERE session_id = %s
                        ORDER BY timestamp ASC
                        """,
                        (session_id,),
                    )
                    return [dict(row) for row in cur.fetchall()]
            finally:
                conn.close()
        except Exception as exc:
            logger.error("audit get_session_log error: %s", exc)
            return []

    def _get_session_log_jsonl(self, session_id: str) -> list[dict]:
        """Scan the JSONL file for records matching this session_id."""
        records = []
        try:
            with open(self.audit_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        if record.get("session_id") == session_id:
                            records.append(record)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
        return records
