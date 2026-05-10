# Chapter 18: RAG — Retrieval-Augmented Generation Engineering

> *"A language model's knowledge is a photograph. RAG gives it a library card."*
> — Kla Tantithamthavorn

---

In November 2023, Air Canada's customer service chatbot told a passenger named Jake Moffatt that he could book a bereavement fare after his grandmother's death and apply for a retroactive discount later. The policy did not work that way. When Moffatt pursued the refund, Air Canada argued the chatbot was a "separate legal entity" responsible for its own representations. The British Columbia Civil Resolution Tribunal disagreed and ordered Air Canada to honour the fare. The chatbot had not been asked to invent a policy — it had simply generated a plausible-sounding answer about a topic for which it had no reliable, current, organisationally authoritative source. The model's parametric knowledge — the facts absorbed during training — had no representation of Air Canada's actual bereavement fare rules. Confident fluency filled the gap where accurate retrieval should have been.

That case was not primarily a prompting failure or a safety guardrail failure. It was a knowledge architecture failure. The system had no mechanism for grounding its answers in Air Canada's actual policy documents. Retrieval-Augmented Generation (RAG) is the engineering discipline that closes that gap — not by making the model smarter, but by ensuring it always answers from authoritative sources rather than from inference.

---
