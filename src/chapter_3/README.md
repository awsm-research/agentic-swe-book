# Chapter 3: Software Design, Architecture, and Patterns

> *"A designer knows he has achieved perfection not when there is nothing left to add, but when there is nothing left to take away."*
> — Antoine de Saint-Exupéry

---

On 1 August 2012, Knight Capital Group — one of the largest equity trading firms in the United States — deployed new software to its production servers. The deployment was manual, and a technician failed to update one of the eight servers. That server continued running a deprecated trading algorithm called "Power Peg," code that had not been active for years but had never been removed from the codebase. When markets opened at 9:30 a.m., Knight's system began placing buy and sell orders at a rate of thousands per second. Within 45 minutes it had executed four million trades, accumulated a $7 billion position, and lost $440 million. The firm needed an emergency capital injection to survive and was acquired six months later ([SEC, 2013](https://www.sec.gov/litigation/admin/2013/34-70694.pdf)).

The failure had nothing to do with clever algorithms or obscure hardware. It was a design failure: dead code left in the codebase, no automated deployment verification, a manual process with no rollback mechanism, and no circuit-breaker that would halt trading on anomalous volume. Every one of those weaknesses is addressable by practices covered in this chapter and the chapters that follow. Good software design does not prevent all failures — but it closes the gaps that turn a deployment error into a company-ending event.

---
