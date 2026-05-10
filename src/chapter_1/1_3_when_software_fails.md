## 1.3 When Software Fails

The two cases below are Australian — not because Australian software is unusually bad, but because both are extensively documented in public audit reports and court filings. Read them as patterns, not anomalies. The failure modes recur in every country's software projects.

### Case Study 1: The MYKI Ticketing System

[In 2005, the Victorian Government contracted a consortium to build MYKI — a smartcard-based ticketing system for Melbourne's public transport network.](https://www.audit.vic.gov.au/report/operational-effectiveness-myki-ticketing-system?section=) The project was plagued by problems from the start.

Originally estimated at around AUD$494 million and targeted for full deployment by 2007, MYKI eventually cost over AUD$1.35 billion and was years behind schedule. The Victorian Auditor-General's Office (VAGO) produced multiple critical reports on the project, finding inadequate requirements management, poor contractor oversight, and testing failures that allowed defects to reach passengers (Victorian Auditor-General's Office, 2011).

The MYKI case illustrates several recurring failure patterns:

- **Unclear and unstable requirements**: Scope changed repeatedly, leading to costly rework and disputes
- **Insufficient testing**: Defects were discovered after deployment, when they were most expensive to fix
- **Weak governance**: Problems were not escalated or addressed early enough

### Case Study 2: Commonwealth Bank and Transaction Monitoring

In 2017, Australia's financial intelligence agency AUSTRAC [commenced legal proceedings against the Commonwealth Bank of Australia (CBA)](https://www.austrac.gov.au/news-and-media/media-release/austrac-and-cba-agree-700m-penalty), alleging more than 53,000 breaches of anti-money laundering and counter-terrorism financing laws. At the centre of the case was a software defect.

CBA's Intelligent Deposit Machines (IDMs) — automated cash deposit ATMs — included software required to send threshold transaction reports (TTRs) to AUSTRAC whenever a cash deposit exceeded AUD$10,000. A coding error introduced during a software update in 2012 caused these reports to stop being generated. The defect went undetected for nearly three years, during which time criminals used the machines to launder money. In 2018, CBA settled with AUSTRAC for AUD$700 million — the largest civil penalty in Australian corporate history at the time ([AUSTRAC, 2017](https://www.austrac.gov.au/news-and-media/media-release/austrac-and-cba-agree-700m-penalty)).

The CBA case illustrates a different but equally important class of failure:

- **A single coding error**, undetected in testing, had catastrophic legal and financial consequences
- **No monitoring**: The system provided no alerting when report volumes dropped to zero
- **Compliance requirements** were not adequately translated into verifiable software behaviour

### Lessons from Failures

| Lesson | What It Means |
|---|---|
| **Requirements must be clear and stable** | Ambiguous or moving requirements lead to software that does not meet needs |
| **Testing is not optional** | Defects found in production cost an order of magnitude more than defects found early |
| **Monitor your systems** | Silent failures are dangerous; systems should report on their own health |
| **Cost of failure exceeds cost of quality** | Investing in good engineering is almost always cheaper than recovering from failure |

---
