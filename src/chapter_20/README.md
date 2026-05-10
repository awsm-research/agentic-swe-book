# Chapter 20: LLM Evaluation and Quality Assurance

> *"You cannot improve what you cannot measure. But in LLM evaluation, the danger is measuring the wrong thing with great precision and concluding that you are done."*
> — Kla Tantithamthavorn

---

When a radiology AI company deployed its first LLM-powered report summarisation tool in 2022, the engineering team ran it on a hundred reports, read the summaries, and agreed they looked "pretty good." Eighteen months and 200,000 reports later, a senior radiologist conducting a routine quality audit found that the system had been consistently omitting incidental findings — nodules, lymphadenopathy, unexpected masses — from its summaries. The findings were in the source reports. The summaries were grammatically correct and clinically coherent. They simply did not include the incidental material, because incidental findings were underrepresented in the examples the team had informally reviewed, and no metric had been tracking whether the summaries were complete. The system passed every informal check. Nobody had built a systematic evaluation that would have caught the omission. By the time the failure was discovered, hundreds of thousands of summarised reports had been read by clinicians who had no reason to suspect the summaries were incomplete.

---
