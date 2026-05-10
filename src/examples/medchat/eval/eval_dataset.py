"""
MedChat evaluation dataset builder — Chapter 19.

Provides 15 curated QA pairs (5 from antibiotic guidelines, 5 from drug
interactions, 5 questions not in corpus) and functions to run the RAG
pipeline over all questions to build a RAGAS-ready dataset.

Usage:
    from eval.eval_dataset import get_eval_data, generate_eval_answers

    eval_data = get_eval_data()
    dataset = generate_eval_answers(eval_data)   # runs RAG on each question
"""

from __future__ import annotations

import os
import sys
import logging
from pathlib import Path

# Allow importing retriever from the parent medchat directory
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


# ── Static evaluation dataset ──────────────────────────────────────────────────


def get_eval_data() -> list[dict]:
    """
    Return 15 QA pairs for MedChat evaluation.

    Each dict has:
      - question (str)
      - ground_truth (str)
      - expected_sources (list[str])  — document titles expected in retrieved context
      - in_corpus (bool)              — whether the answer should be found in the corpus

    5 from antibiotic guidelines, 5 from drug interactions, 5 not in corpus.
    """
    return [
        # ── From antibiotic guidelines ─────────────────────────────────────────
        {
            "question": (
                "What is the first-line antibiotic for mild community-acquired "
                "pneumonia in adults?"
            ),
            "ground_truth": (
                "Amoxicillin 500 mg three times daily (TDS) for 5 days is the "
                "first-line treatment for mild community-acquired pneumonia (CAP) "
                "in adults managed in the community."
            ),
            "expected_sources": ["Antibiotic Guidelines"],
            "in_corpus": True,
        },
        {
            "question": (
                "What antibiotic is recommended for CAP in a patient with "
                "penicillin allergy?"
            ),
            "ground_truth": (
                "Doxycycline 200 mg loading dose then 100 mg twice daily for 5 days "
                "is the recommended alternative for mild CAP in penicillin-allergic "
                "patients. Clarithromycin 500 mg BD is also an option."
            ),
            "expected_sources": ["Antibiotic Guidelines"],
            "in_corpus": True,
        },
        {
            "question": "What antibiotic should be used empirically for hospital-acquired pneumonia?",
            "ground_truth": (
                "Piperacillin-tazobactam (Tazocin) 4.5 g IV every 8 hours is "
                "recommended as first-line empirical treatment for non-severe "
                "hospital-acquired pneumonia."
            ),
            "expected_sources": ["Antibiotic Guidelines"],
            "in_corpus": True,
        },
        {
            "question": "Is nitrofurantoin safe to use in a patient with an eGFR of 20 mL/min?",
            "ground_truth": (
                "No. Nitrofurantoin is contraindicated when eGFR is below "
                "30 mL/min/1.73 m² because therapeutic urinary levels cannot be "
                "achieved and the risk of peripheral neuropathy increases."
            ),
            "expected_sources": ["Antibiotic Guidelines"],
            "in_corpus": True,
        },
        {
            "question": "What are the criteria for switching from IV to oral antibiotics?",
            "ground_truth": (
                "Switch to oral antibiotics when the patient is afebrile for ≥ 24 hours, "
                "haemodynamically stable, tolerating oral intake, and a suitable oral "
                "agent with good bioavailability is available. Clinically improving "
                "inflammatory markers also support the switch."
            ),
            "expected_sources": ["Clinical Faq"],
            "in_corpus": True,
        },
        # ── From drug interactions ─────────────────────────────────────────────
        {
            "question": "What is the risk of giving ibuprofen to a patient on warfarin?",
            "ground_truth": (
                "The combination of ibuprofen (an NSAID) and warfarin carries a MAJOR "
                "bleeding risk. NSAIDs inhibit platelet aggregation and increase GI "
                "ulceration risk, significantly compounding warfarin's anticoagulant "
                "effect. The combination should be avoided if possible."
            ),
            "expected_sources": ["Drug Interactions"],
            "in_corpus": True,
        },
        {
            "question": "What must I do about metformin before giving a patient IV contrast?",
            "ground_truth": (
                "Metformin should be withheld 48 hours before and after administration "
                "of iodinated contrast media due to the risk of contrast-induced "
                "nephropathy leading to lactic acidosis. Restart only after confirming "
                "renal function is unchanged."
            ),
            "expected_sources": ["Drug Interactions"],
            "in_corpus": True,
        },
        {
            "question": "Can SSRIs be co-prescribed with MAOIs?",
            "ground_truth": (
                "No. The combination of SSRIs and MAOIs is absolutely contraindicated "
                "due to the risk of serotonin syndrome, which is potentially fatal. "
                "A washout of at least 14 days after stopping the MAOI (5 weeks after "
                "fluoxetine) is required before starting an SSRI."
            ),
            "expected_sources": ["Drug Interactions"],
            "in_corpus": True,
        },
        {
            "question": "What is the interaction between simvastatin and clarithromycin?",
            "ground_truth": (
                "The interaction between simvastatin and clarithromycin is MAJOR. "
                "Clarithromycin inhibits CYP3A4, the enzyme that metabolises "
                "simvastatin, causing elevated statin levels and risk of myopathy and "
                "rhabdomyolysis. The combination should be avoided."
            ),
            "expected_sources": ["Drug Interactions"],
            "in_corpus": True,
        },
        {
            "question": "A patient on warfarin needs fluconazole. What monitoring is required?",
            "ground_truth": (
                "The warfarin–fluconazole interaction is MAJOR. Fluconazole inhibits "
                "CYP2C9, significantly increasing INR within 2–3 days. INR should be "
                "monitored closely during the course, and an empirical warfarin dose "
                "reduction of 25–50% should be considered."
            ),
            "expected_sources": ["Drug Interactions"],
            "in_corpus": True,
        },
        # ── Not in corpus (out-of-scope questions) ─────────────────────────────
        {
            "question": "What is the recommended treatment for Chagas disease?",
            "ground_truth": (
                "This question is outside the scope of MedChat's clinical reference corpus. "
                "MedChat cannot provide a grounded answer and recommends consulting "
                "specialist infectious disease guidelines."
            ),
            "expected_sources": [],
            "in_corpus": False,
        },
        {
            "question": "How do you manage acute angle-closure glaucoma?",
            "ground_truth": (
                "Acute angle-closure glaucoma is an ophthalmological emergency. "
                "This is outside MedChat's current clinical reference corpus. "
                "Immediate ophthalmology referral is required."
            ),
            "expected_sources": [],
            "in_corpus": False,
        },
        {
            "question": "What are the diagnostic criteria for multiple sclerosis?",
            "ground_truth": (
                "Diagnosis of multiple sclerosis uses the McDonald criteria requiring "
                "demonstration of dissemination in space and time. This topic is outside "
                "MedChat's current clinical reference corpus."
            ),
            "expected_sources": [],
            "in_corpus": False,
        },
        {
            "question": "What is the management of diabetic ketoacidosis (DKA)?",
            "ground_truth": (
                "DKA management involves intravenous fluid resuscitation, insulin infusion, "
                "electrolyte replacement (especially potassium), and monitoring for "
                "complications. This is outside MedChat's current corpus."
            ),
            "expected_sources": [],
            "in_corpus": False,
        },
        {
            "question": "What are the indications for thrombolysis in acute ischaemic stroke?",
            "ground_truth": (
                "Thrombolysis with alteplase is indicated within 4.5 hours of stroke onset "
                "in eligible patients. Eligibility involves imaging to exclude haemorrhage "
                "and assessing contraindications. This is outside MedChat's current corpus."
            ),
            "expected_sources": [],
            "in_corpus": False,
        },
    ]


# ── RAG answer generation ─────────────────────────────────────────────────────


def generate_eval_answers(eval_data: list[dict]) -> list[dict]:
    """
    Run the RAG pipeline over each question in eval_data.

    For each question the function calls retrieve() and rerank() from retriever.py,
    builds a context string, queries the OpenAI API, and records the answer and
    retrieved contexts.

    Args:
        eval_data: List of QA dicts as returned by get_eval_data().

    Returns:
        List of dicts, each containing:
          - question (str)
          - answer (str)             — RAG-generated answer
          - contexts (list[str])     — content strings of retrieved chunks
          - ground_truth (str)
          - in_corpus (bool)
    """
    import yaml
    from openai import OpenAI
    from retriever import retrieve, rerank

    prompt_path = Path(__file__).parent.parent / "prompts" / "system_v1.yaml"
    with open(prompt_path, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    base_prompt: str = cfg.get("system_prompt", "").strip()
    model: str = cfg.get("model", "gpt-4o-mini")

    client = OpenAI()
    results: list[dict] = []

    for i, qa in enumerate(eval_data, start=1):
        question = qa["question"]
        logger.info(f"[{i}/{len(eval_data)}] Generating answer for: {question[:60]}…")

        try:
            candidates = retrieve(question, top_k=10)
            top_chunks = rerank(question, candidates, top_n=3)
            context_parts = [ch["content"] for ch in top_chunks]

            if context_parts:
                context_block = (
                    "Answer only from the provided context. "
                    "If the context does not contain the answer, say: "
                    "'I don't have information about that in my clinical references.'\n\n"
                    "## Retrieved Clinical Context\n"
                    + "\n\n".join(
                        f"[Source: {ch.get('title', 'Unknown')}]\n{ch['content']}"
                        for ch in top_chunks
                    )
                )
                system_content = base_prompt + "\n\n" + context_block
            else:
                system_content = base_prompt

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": question},
                ],
                temperature=0.1,
                max_tokens=500,
            )
            answer = response.choices[0].message.content or ""

        except Exception as exc:
            logger.error(f"Failed to generate answer for question {i}: {exc}")
            answer = ""
            context_parts = []

        results.append(
            {
                "question": question,
                "answer": answer,
                "contexts": context_parts,
                "ground_truth": qa["ground_truth"],
                "in_corpus": qa["in_corpus"],
                "expected_sources": qa.get("expected_sources", []),
            }
        )

    return results


# ── Entry point ────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    eval_data = get_eval_data()
    print(f"Evaluation dataset: {len(eval_data)} questions")
    for i, qa in enumerate(eval_data, start=1):
        corpus_tag = "[IN CORPUS]" if qa["in_corpus"] else "[OUT OF CORPUS]"
        print(f"  {i:2d}. {corpus_tag} {qa['question'][:70]}")
