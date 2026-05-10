# Chapter 10: Software Maintenance and Technical Debts

> *"Shipping first-time code is like going into debt. A little debt speeds development so long as it is paid back promptly with a rewrite. The danger occurs when the debt is not repaid."*
> — Ward Cunningham, OOPSLA 1992

---

On 1 August 2012, the high-frequency trading firm Knight Capital deployed new software to its order-routing system. The deployment was manual. One of eight servers did not receive the new code, and an old feature flag — repurposed for the new release — was reactivated on that server, waking up an eight-year-old block of dead code that had never been removed. Over the next forty-five minutes, the dormant code executed roughly four million erroneous trades across 154 stocks. By the time the firm halted trading, it had lost USD 440 million — more than its market capitalisation at the time ([SEC, 2013](https://www.sec.gov/litigation/admin/2013/34-70694.pdf)). Knight Capital was acquired the following year and ceased to exist as an independent company. The bug was not in the new code. It was in the code that should have been deleted years earlier — and in the deployment process that allowed half a release to ship to production.

---
