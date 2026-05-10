## 12.3 AI-Generated Code and Copyright

The copyright status of AI-generated code is one of the most actively litigated and debated questions in technology law as of 2024–2025.

### 12.3.1 The Current Legal Landscape

**Human authorship requirement**: In most jurisdictions, copyright requires human authorship. The United States Copyright Office has repeatedly held that works produced autonomously by AI without human creative input are not copyrightable ([US Copyright Office, 2024](https://www.copyright.gov/ai/)). This means purely AI-generated code may have no copyright holder — it may be in the public domain.

**Human-AI collaboration**: Where a human makes meaningful creative choices in directing, selecting, and refining AI output, the resulting work may be copyrightable as a human-authored work. The threshold for "meaningful creative contribution" is not yet clearly defined.

**Training data and copyright**: Several lawsuits have been filed alleging that AI models trained on copyrighted code without permission infringe copyright ([GitHub Copilot class action, 2022](https://githubcopilotlitigation.com/)). These cases are unresolved as of this writing.

### 12.3.2 Practical Guidance

In the absence of settled law, the pragmatic guidance is:

1. **For critical proprietary systems**: Treat AI-generated code with the same IP review you would apply to any third-party code. Understand what training data the model was trained on, and whether it may reproduce copyrighted code verbatim.

2. **For licence compliance**: AI coding assistants trained on copyleft code could theoretically reproduce that code in their outputs, creating a hidden licence obligation. Some organisations have adopted policies requiring a human review of AI-generated code before incorporating it.

3. **For attribution**: If an AI assistant produces code that is substantially similar to an existing open source project, treat it as if it were copied from that project and apply the appropriate licence obligations.

4. **Keep documentation**: Record which parts of your codebase are AI-generated, which tools were used, and which specifications were provided. This documentation supports IP claims and audits.

---
