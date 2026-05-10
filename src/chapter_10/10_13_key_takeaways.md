## 10.13 Key Takeaways

1. **Maintenance is the majority of the work.** Sixty to eighty per cent of total software cost is incurred after deployment. Engineering practices that treat maintenance as an afterthought are budgeting against forty years of evidence.

2. **Lehman's first law is decisive.** A system used in the real world must change, or it loses value. Doing nothing is not a stable state — the world around the code keeps moving.

3. **Cunningham's debt metaphor is precise; the popular usage is not.** Debt is the gap between what the code expresses and what the team understands. Calling every imperfection *technical debt* drains the term of meaning.

4. **The dangerous quadrant is reckless and inadvertent.** This is exactly where AI-generated code lands by default, because the agent does not know the rules it is breaking. Reviewers who wave it through inherit the debt without realising.

5. **Different debts need different detectors.** SATD mining, cyclomatic complexity, churn × complexity hotspots, dependency audits, and mutation scores each surface a different category. Pick the detector that matches the debt you are trying to manage.

6. **Pin behaviour with characterisation tests before you refactor.** This is non-negotiable when an agent is doing the refactor. An agent's "clean-up" is a behaviour change unless tests prove otherwise.

7. **Choose repayment strategy by debt shape.** Boy Scout for diffuse, dedicated effort for concentrated, strangler fig for structural, parallel change for external APIs. Rewrites are almost always the wrong answer.

8. **Debugging is a scientific activity.** Reproduce, bisect, hypothesise, observe, conclude. Postmortems are blameless because punishing engineers teaches them to hide failures, not prevent them.

9. **Documentation debt has no compiler.** Code rots when tests fail; documentation rots silently. ADRs, runbooks, and "why" comments are how a team preserves the reasoning that the code itself cannot record.

---

### Review Questions

1. *Hotspot triage*: A churn × complexity report identifies one file as the top hotspot in a backend repository. The file has cyclomatic complexity 47, has been edited by twelve different engineers in the last six months, and has 14% test coverage. Walk through how you would decide whether to refactor it, ignore it, rewrite it, or strangle it — and what evidence you would gather before committing to a strategy.

2. *AI refactor with no safety net*: A junior engineer used an agent to "clean up" a 600-line revenue-reporting module. The pull request reduces cyclomatic complexity from 38 to 9, removes 200 lines, passes the existing test suite, and is open for review. What do you do before approving — and what change would you make to the team's process so that the next agent-driven refactor cannot land this way?

3. *Strangler fig argument*: A legacy payments service still processes 30% of company revenue. Two engineers have proposed rewriting it from scratch over a quarter "because the code is unmaintainable". Make the case for or against the rewrite, propose a strangler fig alternative, and identify the three pieces of work the team must complete before the strangler fig can begin.

4. *Reframing debt for a product manager*: A product manager rejects a debt-payoff sprint with "we don't have time for that — we have features to ship". Reframe the cost of the existing debt in terms the product manager is responsible for. Use specific metrics from this chapter, and identify the smallest piece of work that would produce the evidence you need.

5. *Knight Capital postmortem*: Re-read the Knight Capital incident in the chapter opening. Identify three categories of debt from Section 10.4 that contributed to the failure, and describe one preventive maintenance practice that could have addressed each. What process change — not technology change — would have most reduced the blast radius?

---
