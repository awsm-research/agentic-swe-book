## 10.6 Quantifying and Communicating Debt

The SQALE model, developed by Jean-Louis Letouzey in 2010 and adopted by SonarQube, expresses debt in *remediation hours* — the estimated time to repay each detected issue ([Letouzey, 2012](https://www.sqale.org/)). A *debt ratio* is then computed as remediation cost divided by estimated development cost. The numbers are not precise. They are useful for trend, not for absolute claims.

The persistent problem with debt quantification is that engineers and product managers speak different dialects. Telling a product manager that the codebase has 412 hours of technical debt does not motivate action. Telling them that the team's average cycle time has increased from 3.2 to 5.7 days over the last quarter, and that the top three hotspots account for 60% of post-merge defects, will. Translate debt into delivery delay, defect rate, and time-to-recover before bringing it to a stakeholder conversation.

The DORA metrics — deployment frequency, lead time for changes, change failure rate, and time to restore service ([Forsgren et al., 2018](https://itrevolution.com/product/accelerate/)) — are a useful complement to debt metrics. They measure the consequences of debt rather than debt itself, and they are the metrics product and engineering leaders already share.

---
