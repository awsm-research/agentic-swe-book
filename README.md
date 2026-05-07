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
  <img src="https://img.shields.io/badge/topic-agentic%20AI-purple" alt="AI Engineering">
  <img src="https://img.shields.io/badge/version-2026-blue" alt="Version">
  <img src="https://img.shields.io/badge/status-active%20development-brightgreen" alt="Status">
  <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/"><img src="https://img.shields.io/badge/book-CC%20BY--NC--ND%204.0-lightgrey" alt="CC BY-NC-ND 4.0"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/code-MIT-yellow" alt="MIT License"></a>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=book.agentic-swe.dev" alt="Visitor Count">
</p>

---

## About

The bottleneck in software development is moving. AI agents can now write syntactically correct, contextually relevant code from a natural language description. What remains irreducibly human is everything around implementation: understanding the problem deeply, specifying intent precisely, verifying that what was produced is actually correct, and refining until it is truly right.

*Agentic Software Engineering* is a 12-week textbook for engineers making that transition. It teaches the new loop — **Specify → Generate → Verify → Refine** — not as a workflow of AI tools, but as a set of skills that compound and do not expire when the next model is released: problem decomposition, system thinking, critical verification, and judgment under uncertainty.

The book is built around a single running project (a Task Management API) that grows chapter by chapter, from a scope statement to a complete AI-native system — giving readers a concrete, end-to-end illustration of every concept.

## Contents

### Part I: SE Fundamentals
| Chapter | Title |
|---------|-------|
| 1 | Software Engineering Fundamentals |
| 2 | Requirements Engineering |
| 3 | Software Design, Architecture, and Patterns |
| 4 | Software Quality & Testing |
| 5 | Automated Code Review, Code Quality, and CI/CD |

### Part II: Agentic Software Engineering
| Chapter | Title |
|---------|-------|
| 6 | Agentic Software Engineering: A New Paradigm |
| 7 | Configuring the Agent's World — Context, Skills, and Tools |
| 8 | Security of AI-Generated Code |
| 9 | Security Concerns of Agentic AI Coding Tools |

### Part III: Shipping Your Software Responsibly & Ethically
| Chapter | Title |
|---------|-------|
| 10 | Software Maintenance and Technical Debts |
| 11 | Software Versioning, Packaging, and Deployment |
| 12 | Licenses, Ethics, and Responsible AI |

### Part IV: Tutorials
| Tutorial | Title |
|----------|-------|
| 1 | Setting Up Your Python and GitLab for Code and Project Management |
| 2 | Eliciting Requirements from AI As Your Client |
| 3 | Designing a Learning Management System |
| 4 | Unit Testing 101 |
| 5 | Code Quality and CI/CD |
| 6 | The AI-Assisted SDLC: From Spec to Code |
| 7 | The AI-Assisted SDLC: From Code to Well-Tested App |
| 8 | SAST, AI, and Human on Vulnerability Detection |
| 9 | Security Review in CI/CD Pipeline |
| 10 | Pay Down Debt on a Real Hotspot |
| 11 | Containerise and Ship a Three-Tier Application |
| 12 | Licences, Privacy, and Responsible AI in Practice |

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
