<div align="center">
  <img src="src/images/banner.png" alt="Agentic Software Engineering: A Practical Guide for the AI-Native Engineer" />
</div>

<h1 align="center">Agentic Software Engineering<br><sub>A Practical Guide for the AI-Native Engineer</sub></h1>

<p align="center">
  <strong>Kla Tantithamthavorn</strong><br>
  Associate Professor · Monash University
</p>

<p align="center">
  <a href="http://book.agentic-swe.dev/"><strong>Read the Book →</strong></a>
</p>

<p align="center">
  <a href="https://doi.org/10.5281/zenodo.20053968"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.20053968.svg" alt="DOI"></a>
</p>

---

## About

The bottleneck in software development is moving. AI agents can now write syntactically correct, contextually relevant code from a natural language description. What remains irreducibly human is everything around implementation: understanding the problem deeply, specifying intent precisely, verifying that what was produced is actually correct, and refining until it is truly right.

*Agentic Software Engineering* is a 12-week textbook for engineers making that transition. It teaches the new loop — **Specify → Generate → Verify → Refine** — not as a workflow of AI tools, but as a set of skills that compound and do not expire when the next model is released: problem decomposition, system thinking, critical verification, and judgment under uncertainty.

The book is built around a single running project (a Task Management API) that grows chapter by chapter, from a scope statement to a complete AI-native system — giving readers a concrete, end-to-end illustration of every concept.

## Contents

### Part I: SE Fundamentals
| Week | Chapter |
|------|---------|
| 1 | Software Engineering Fundamentals |
| 2 | Requirements Engineering |
| 3 | Software Design, Architecture, and Patterns |
| 4 | Software Testing, Code Quality, Code Review, and CI/CD |
| 5 | Software Security |

### Part II: Agentic Software Engineering
| Week | Chapter |
|------|---------|
| 6 | Agentic Software Engineering: A New Paradigm |
| 7 | Agentic SWE in SDLC: Hands-on Activities |
| 8 | Emerging Security Concerns in Agentic Software Engineering |
| 9 | Configuring the Agent's World — Context, Skills, and Tools |

### Part III: Engineering with Responsibility
| Week | Chapter |
|------|---------|
| 10 | Licenses, Ethics, and Responsible AI |
| 11 | Developer Productivity and Team Practices |
| 12 | The Future of AI-Native Engineering |

### Appendices
- A: Recommended Tools and Environments
- B: Design Pattern Reference
- C: Applying These Practices in Other Languages
- D: Prompt Pattern Reference

## Key Concepts

- **Specify → Generate → Verify → Refine** — the AI-native SDLC
- **Agentic workflows** — agent paradigm, tool use, multi-agent orchestration
- **AI security** — prompt injection, emerging threats in agentic systems
- **Responsible AI** — licensing, ethics, GDPR, EU AI Act, accountability

## About the Author

**Kla Tantithamthavorn** is Associate Professor in Software Engineering at Monash University. His research spans AI-enabled software engineering, Explainable AI for SE, and LLM-based security testing. He has published 80+ papers with 8,600+ citations (h-index 44), is a World Top 2% Scientist (Stanford), and has secured over $2M in competitive research funding.

→ [chakkrit.com](https://chakkrit.com) · [Google Scholar](https://scholar.google.com.au/citations?user=idShgcoAAAAJ)

## Building Locally

Requires [mdBook](https://rust-lang.github.io/mdBook/) v0.5.2+.

```bash
# Install mdBook
cargo install mdbook

# Serve with live reload
mdbook serve

# Build static site
mdbook build
```

## License

Book content © Kla Tantithamthavorn, Monash University. All rights reserved.  
Code examples in the book are released under the [MIT License](LICENSE).
