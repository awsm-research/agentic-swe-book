## 18.12 Tutorial: Building a RAG Pipeline for Clinical Documents

The MedChat prototype from Tutorial 16 answers general questions well, but it hallucinates specific drug dosages because its training data has a knowledge cutoff. The clinical team has provided you with three documents: a WHO antibiotic guidelines reference, a drug interaction reference CSV, and a clinical FAQ markdown file. Your job is to build a RAG (Retrieval-Augmented Generation) pipeline that retrieves relevant passages from these documents before generating a response — grounding every answer in real source material and printing the exact document each claim came from.

**Concepts covered:** Chunking strategies, embeddings, pgvector, HNSW index, cosine similarity retrieval, cross-encoder reranking, context injection, source attribution, RAG failure modes

**Format:** Individual or pairs | **Duration:** ~2.5 hours | **Tool:** Python · openai · psycopg2 · pgvector · sentence-transformers · Docker

---

### Outline

- [Part A: Build the Ingestion Pipeline](#part-a-build-the-ingestion-pipeline--75-min)
- [Part B: Build the RAG Query Function](#part-b-build-the-rag-query-function--75-min)
- [References](#references)

---

### Learning Objectives

1. Chunk documents into overlapping passages and explain why chunk size and overlap affect retrieval quality.
2. Embed text with the OpenAI embeddings API and store vectors in PostgreSQL with pgvector.
3. Build and query an HNSW index for approximate nearest-neighbour search.
4. Implement cross-encoder reranking to improve the precision of the top-K results.
5. Inject retrieved context into a prompt and format source attribution for the user.
6. Identify and demonstrate two RAG failure modes: out-of-corpus questions and retrieved irrelevance.

---

### Prerequisites

You need Docker and the Python environment from Tutorial 16.

```bash
docker --version          # Docker 24+ recommended
pip install psycopg2-binary pgvector sentence-transformers PyYAML python-dotenv openai
```

Verify pgvector Python client:

```bash
python -c "from pgvector.psycopg2 import register_vector; print('pgvector OK')"
```

---

### Part A: Build the Ingestion Pipeline *(~75 min)*

#### Step 1: Start PostgreSQL with pgvector

```bash
docker run -d --name pgvector-db \
  -e POSTGRES_PASSWORD=medchat \
  -e POSTGRES_DB=medchat \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

Wait a few seconds for the container to start, then verify:

```bash
docker exec pgvector-db psql -U postgres -d medchat -c "SELECT version();"
```

#### Step 2: Create the database schema

Create `db/schema.sql`:

```sql
-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents table: one row per source file
CREATE TABLE IF NOT EXISTS documents (
    id          SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    source_type TEXT NOT NULL,   -- 'markdown', 'csv', 'text'
    file_path   TEXT NOT NULL,
    ingested_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chunks table: one row per passage
CREATE TABLE IF NOT EXISTS chunks (
    id          SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    content     TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding   vector(1536),    -- text-embedding-3-small produces 1536-dim vectors
    metadata    JSONB DEFAULT '{}'
);

-- HNSW index for fast approximate nearest-neighbour search
-- ef_construction=128 and m=16 are good defaults for <100k vectors
CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw
    ON chunks
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 128);
```

Apply the schema:

```bash
docker exec -i pgvector-db psql -U postgres -d medchat < db/schema.sql
```

Verify the tables exist:

```bash
docker exec pgvector-db psql -U postgres -d medchat \
  -c "\dt"
```

> **Why HNSW over IVFFlat?** HNSW (Hierarchical Navigable Small World) builds its index incrementally, so you can insert new chunks without reindexing. IVFFlat requires knowing the number of clusters at index creation time. For a growing document corpus, HNSW is operationally simpler.

#### Step 3: Create sample clinical documents

Create the directory and three source files:

```bash
mkdir -p docs
```

**`docs/antibiotic_guidelines.md`**

```markdown
# Antibiotic Prescribing Guidelines — WHO Essential Medicines Reference (Excerpt)

### Section 1: Community-Acquired Pneumonia (CAP)

#### Non-hospitalised adults (low severity, no comorbidities)
First-line treatment: Amoxicillin 500 mg orally three times daily for 5 days.
Alternative (penicillin allergy): Doxycycline 200 mg on day 1, then 100 mg once daily for 4 days.
Alternative (suspected atypical pathogen): Azithromycin 500 mg on day 1, then 250 mg once daily for 4 days.

#### Hospitalised adults (moderate severity)
First-line: Amoxicillin-clavulanate 1.2 g IV every 8 hours PLUS Azithromycin 500 mg IV/orally once daily.
Duration: 5–7 days. Step down to oral therapy when patient is afebrile for 24 hours.

#### ICU admission (severe CAP)
First-line: Piperacillin-tazobactam 4.5 g IV every 6 hours PLUS Azithromycin 500 mg IV once daily.
If Pseudomonas suspected: Add Ciprofloxacin 400 mg IV every 8 hours.
Duration: 7–10 days.

### Section 2: Urinary Tract Infections (UTI)

#### Uncomplicated lower UTI in women
First-line: Nitrofurantoin 100 mg (modified-release) twice daily for 5 days.
Alternative: Trimethoprim 200 mg twice daily for 7 days.
Avoid fluoroquinolones for uncomplicated UTI (reserve for complicated infections).

#### Complicated UTI or pyelonephritis
First-line: Cephalexin 500 mg four times daily for 7–14 days (outpatient).
Inpatient: Ceftriaxone 1–2 g IV once daily; switch to oral when clinically improved.

#### UTI in pregnancy
Safe options: Nitrofurantoin (avoid at term), Cefalexin, Amoxicillin (if sensitivities confirm).
Contraindicated: Trimethoprim (first trimester, folate antagonist), Fluoroquinolones.

### Section 3: Skin and Soft Tissue Infections

#### Non-purulent cellulitis
First-line: Flucloxacillin 500 mg four times daily for 5–7 days.
Penicillin allergy: Cefalexin 500 mg four times daily for 5–7 days.
Severe (hospitalised): Flucloxacillin 1–2 g IV every 6 hours.

#### Purulent skin infections (abscess, furuncle)
Incision and drainage is the primary treatment.
Adjuvant antibiotics if systemic features: Co-trimoxazole (trimethoprim/sulfamethoxazole) 960 mg twice daily for 5 days.
If MRSA suspected: Doxycycline 100 mg twice daily for 5–7 days.

### Section 4: Principles of Antibiotic Stewardship

1. Use the narrowest-spectrum agent effective for the pathogen.
2. Confirm allergy history before prescribing alternatives; penicillin allergy is frequently over-reported.
3. Review and de-escalate at 48–72 hours based on culture results.
4. Document the indication, dose, route, and intended duration in every prescription.
5. Avoid empirical broad-spectrum agents (carbapenems, glycopeptides) without senior approval.
```

**`docs/drug_interactions.csv`**

```csv
drug_a,drug_b,severity,mechanism,clinical_action
Warfarin,Amoxicillin,Moderate,Gut flora alteration increases INR,Monitor INR closely; adjust warfarin dose as needed
Warfarin,Azithromycin,Moderate,CYP3A4 inhibition increases warfarin exposure,Check INR within 3–5 days of starting azithromycin
Methadone,Azithromycin,High,Additive QTc prolongation,Avoid combination; use alternative antibiotic
Methadone,Ciprofloxacin,High,CYP3A4 and CYP1A2 inhibition increases methadone levels,Avoid; if unavoidable monitor ECG and methadone levels
Simvastatin,Clarithromycin,High,CYP3A4 inhibition raises simvastatin to toxic levels,Switch to pravastatin or hold simvastatin during treatment
Lithium,NSAIDs,High,NSAIDs reduce renal lithium clearance causing toxicity,Avoid NSAIDs; use paracetamol. Monitor lithium levels.
Clopidogrel,Omeprazole,Moderate,CYP2C19 inhibition reduces clopidogrel activation,Prefer pantoprazole over omeprazole in clopidogrel patients
Digoxin,Amiodarone,High,P-glycoprotein inhibition raises digoxin levels,Reduce digoxin dose by 50% and monitor levels
Phenytoin,Fluconazole,High,CYP2C9 inhibition raises phenytoin to toxic levels,Monitor phenytoin levels; consider dose reduction
Rifampicin,Warfarin,High,CYP induction dramatically reduces warfarin effect,Increase warfarin monitoring frequency; expect large dose increase
Rifampicin,Oral contraceptives,High,CYP induction reduces OCP plasma levels,Additional contraception required during and for 28 days after rifampicin
SSRIs,Tramadol,High,Serotonin syndrome risk plus seizure risk,Avoid combination; if needed use lowest tramadol dose with close monitoring
ACE inhibitors,Potassium-sparing diuretics,Moderate,Additive hyperkalaemia risk,Monitor potassium levels regularly
Metformin,IV contrast,Moderate,Risk of contrast-induced nephropathy and lactic acidosis,Hold metformin 48 h before and after IV contrast
Ciprofloxacin,Dairy products,Low,Divalent cations chelate ciprofloxacin reducing absorption,Take ciprofloxacin 2 h before or 6 h after dairy
Levodopa,Pyridoxine (B6),Moderate,B6 enhances peripheral DOPA decarboxylase reducing CNS effect,Avoid high-dose B6 unless patient is on carbidopa combination
Theophylline,Ciprofloxacin,High,CYP1A2 inhibition increases theophylline to toxic levels,Reduce theophylline dose by 30–50%; monitor levels
Carbamazepine,Erythromycin,High,CYP3A4 inhibition raises carbamazepine causing toxicity,Avoid; use azithromycin with caution and monitor
Aminoglycosides,Loop diuretics,High,Additive ototoxicity and nephrotoxicity,Avoid concurrent use; if unavoidable monitor renal function and audiometry
Tacrolimus,Fluconazole,High,CYP3A4 inhibition markedly increases tacrolimus levels,Reduce tacrolimus dose; monitor trough levels daily initially
```

**`docs/clinical_faq.md`**

```markdown
# Clinical FAQ — MedChat Knowledge Base

### Q1: What is the maximum daily dose of paracetamol (acetaminophen) in adults?
**A:** The maximum recommended dose is 4 g (4,000 mg) per 24 hours in healthy adults. Reduce to 2 g per 24 hours in patients with liver disease, chronic alcohol use (more than 3 units/day), or low body weight (<50 kg). Paracetamol is the analgesic of choice in pregnancy at all trimesters within recommended doses.

### Q2: How do I manage a suspected anaphylactic reaction?
**A:** Follow the ABCDE approach. Immediately administer Adrenaline (epinephrine) 0.5 mg (500 micrograms) IM into the outer thigh (1:1000 solution = 0.5 mL). Lay the patient flat with legs elevated unless breathing is difficult. Call for senior help. Give high-flow oxygen. Establish IV access. Second-line: chlorphenamine 10 mg IV and hydrocortisone 200 mg IV. Repeat adrenaline every 5 minutes if no improvement. Observe for minimum 6 hours after resolution.

### Q3: What are the signs of digoxin toxicity?
**A:** Early: nausea, vomiting, anorexia, visual disturbances (yellow-green halos, blurred vision). Cardiac: bradycardia, AV block, ventricular ectopics, VT. Risk factors: hypokalaemia, hypomagnesaemia, renal impairment (digoxin is renally cleared), hypothyroidism. Management: withhold digoxin, correct electrolytes, consider digoxin-specific antibody fragments (DigiFab) for severe toxicity.

### Q4: When should I escalate a patient to critical care?
**A:** Use the NEWS2 (National Early Warning Score 2) system. Escalate immediately for NEWS2 ≥7 or any single parameter scored 3 (SpO2 <91%, respiratory rate <8 or ≥25, heart rate <40 or ≥131, systolic BP <90). Also escalate for: new confusion/altered consciousness, suspected sepsis with organ dysfunction (qSOFA ≥2), or clinical intuition that the patient is deteriorating despite normal parameters.

### Q5: What is the empirical antibiotic regimen for sepsis of unknown origin?
**A:** Follow your local antimicrobial stewardship policy first. A typical empirical regimen for community-acquired sepsis: Piperacillin-tazobactam 4.5 g IV every 6 hours PLUS Gentamicin 5 mg/kg IV once daily (calculate actual body weight, adjust for renal function). In penicillin allergy: Meropenem 1 g IV every 8 hours. Send blood cultures × 2, urine culture, and CRP before starting antibiotics if this does not delay treatment beyond 1 hour.

### Q6: How do I dose enoxaparin for DVT treatment?
**A:** Treatment dose: 1 mg/kg SC twice daily or 1.5 mg/kg SC once daily. Adjust for renal impairment: if eGFR <30 mL/min/1.73m², use 1 mg/kg SC once daily and monitor anti-Xa levels. In pregnancy, weight-based dosing should be used; target anti-Xa levels 0.6–1.0 IU/mL (twice-daily dosing). Prophylactic dose (DVT prevention): 40 mg SC once daily.

### Q7: What are the contraindications to thrombolysis in acute ischaemic stroke?
**A:** Absolute contraindications include: haemorrhagic stroke on CT, onset >4.5 hours (or unknown onset), active bleeding or bleeding diathesis, significant head trauma or stroke within 3 months, blood pressure >185/110 mmHg (not controllable), platelet count <100,000/mm³, current anticoagulant use with INR >1.7 or DOAC taken within 48 hours. Always discuss with stroke consultant before administering alteplase.

### Q8: How should I manage hyperkalaemia (K⁺ >6.5 mmol/L)?
**A:** 1) Cardiac protection: Calcium gluconate 10% 10 mL IV over 5–10 min (stabilises membrane). 2) Shift potassium into cells: Insulin (10 units actrapid) + Glucose (50 mL of 50% glucose) IV over 15–30 min. Salbutamol 10–20 mg nebulised. 3) Remove potassium: Sodium zirconium cyclosilicate (Lokelma) 10 g three times daily or calcium resonium 15 g three times daily. Dialysis for refractory cases. 4) Identify and treat the cause (medications, renal failure, haemolysis).

### Q9: What is the recommended monitoring for a patient starting methotrexate?
**A:** Baseline: FBC, LFTs, U&E, creatinine, CXR (if respiratory symptoms), hepatitis B/C serology. During treatment: FBC and LFTs every 2–4 weeks for first 3 months, then every 3 months if stable. Stop methotrexate if WBC <3.5 × 10⁹/L, neutrophils <2 × 10⁹/L, platelets <150 × 10⁹/L, or significant LFT elevation (>2× upper limit of normal). Ensure patient is on folic acid 5 mg once weekly on a non-methotrexate day.

### Q10: How do I calculate a paediatric drug dose using weight?
**A:** Use the child's actual body weight for most drugs. For obese children, use ideal body weight for drugs with narrow therapeutic indices (aminoglycosides, digoxin, heparins). Always cross-check calculated doses against age-appropriate maximum doses. Use the BNF for Children (BNFC) or local formulary as the primary reference. Double-check 10× dose errors (common with decimal points) by having a second person verify the calculation. Document the calculation including weight used.
```

#### Step 4: Write `ingest.py`

```python
import os
import csv
import json
import psycopg2
from pgvector.psycopg2 import register_vector
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── Database connection ────────────────────────────────────────────────────────

DB_PARAMS = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "medchat",
    "user":     "postgres",
    "password": "medchat",
}

def get_connection():
    conn = psycopg2.connect(**DB_PARAMS)
    register_vector(conn)
    return conn

# ── Chunking ───────────────────────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks by character count.
    Tries to break at sentence boundaries ('. ') when possible.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        # Try to end on a sentence boundary
        if end < len(text):
            last_period = chunk.rfind(". ")
            if last_period > chunk_size // 2:
                end = start + last_period + 2
                chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
    return [c for c in chunks if len(c) > 30]  # drop very short fragments

def load_markdown(path: str) -> str:
    with open(path) as f:
        return f.read()

def load_csv_as_text(path: str) -> str:
    """Convert each CSV row into a readable sentence for embedding."""
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                f"Drug interaction: {row['drug_a']} + {row['drug_b']}. "
                f"Severity: {row['severity']}. "
                f"Mechanism: {row['mechanism']}. "
                f"Clinical action: {row['clinical_action']}."
            )
    return "\n\n".join(rows)

# ── Embedding ──────────────────────────────────────────────────────────────────

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM   = 1536

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. OpenAI allows up to 2048 items per request."""
    BATCH = 100
    all_embeddings = []
    for i in range(0, len(texts), BATCH):
        batch = texts[i:i + BATCH]
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        all_embeddings.extend([item.embedding for item in response.data])
    return all_embeddings

# ── Ingestion ──────────────────────────────────────────────────────────────────

DOCUMENTS = [
    {
        "title":       "Antibiotic Prescribing Guidelines",
        "source_type": "markdown",
        "file_path":   "docs/antibiotic_guidelines.md",
        "loader":      load_markdown,
    },
    {
        "title":       "Drug Interaction Reference",
        "source_type": "csv",
        "file_path":   "docs/drug_interactions.csv",
        "loader":      load_csv_as_text,
    },
    {
        "title":       "Clinical FAQ",
        "source_type": "markdown",
        "file_path":   "docs/clinical_faq.md",
        "loader":      load_markdown,
    },
]

def ingest_document(conn, doc: dict):
    cur = conn.cursor()

    # 1. Insert document record
    cur.execute(
        "INSERT INTO documents (title, source_type, file_path) VALUES (%s, %s, %s) RETURNING id",
        (doc["title"], doc["source_type"], doc["file_path"]),
    )
    document_id = cur.fetchone()[0]

    # 2. Load and chunk
    text   = doc["loader"](doc["file_path"])
    chunks = chunk_text(text, chunk_size=512, overlap=50)
    print(f"  {doc['title']}: {len(chunks)} chunks")

    # 3. Embed
    embeddings = embed_texts(chunks)

    # 4. Insert chunks
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        metadata = json.dumps({"source_type": doc["source_type"], "title": doc["title"]})
        cur.execute(
            """
            INSERT INTO chunks (document_id, content, chunk_index, embedding, metadata)
            VALUES (%s, %s, %s, %s::vector, %s::jsonb)
            """,
            (document_id, chunk, i, embedding, metadata),
        )

    conn.commit()
    cur.close()

def main():
    print("Starting ingestion...")
    conn = get_connection()

    # Clear existing data so the script is idempotent
    cur = conn.cursor()
    cur.execute("DELETE FROM chunks")
    cur.execute("DELETE FROM documents")
    conn.commit()
    cur.close()

    for doc in DOCUMENTS:
        print(f"Processing: {doc['file_path']}")
        ingest_document(conn, doc)

    # Verify
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM chunks")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()

    print(f"\nIngestion complete. Total chunks stored: {count}")

if __name__ == "__main__":
    main()
```

#### Step 5: Run the ingestion and verify

```bash
python ingest.py
```

Expected output:
```
Starting ingestion...
Processing: docs/antibiotic_guidelines.md
  Antibiotic Prescribing Guidelines: 18 chunks
Processing: docs/drug_interactions.csv
  Drug Interaction Reference: 12 chunks
Processing: docs/clinical_faq.md
  Clinical FAQ: 14 chunks

Ingestion complete. Total chunks stored: 44
```

Verify with a COUNT query:

```bash
docker exec pgvector-db psql -U postgres -d medchat \
  -c "SELECT d.title, COUNT(c.id) AS chunks FROM documents d JOIN chunks c ON d.id = c.document_id GROUP BY d.title;"
```

---

### Part B: Build the RAG Query Function *(~75 min)*

#### Step 1: Write `retriever.py`

```python
import os
import json
import psycopg2
from pgvector.psycopg2 import register_vector
from openai import OpenAI
from sentence_transformers import CrossEncoder
from dotenv import load_dotenv

load_dotenv()

DB_PARAMS = {
    "host": "localhost", "port": 5432,
    "dbname": "medchat", "user": "postgres", "password": "medchat",
}

client       = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def get_connection():
    conn = psycopg2.connect(**DB_PARAMS)
    register_vector(conn)
    return conn

def embed_query(text: str) -> list[float]:
    """Embed a single query string."""
    response = client.embeddings.create(model="text-embedding-3-small", input=[text])
    return response.data[0].embedding

def retrieve(query: str, top_k: int = 5, source_type: str = None) -> list[dict]:
    """
    Cosine similarity search in pgvector.
    Optionally filter by source_type (e.g., 'csv', 'markdown').
    Returns a list of chunk dicts with content, source info, and similarity score.
    """
    query_embedding = embed_query(query)

    conn = get_connection()
    cur  = conn.cursor()

    if source_type:
        cur.execute(
            """
            SELECT c.content,
                   d.title,
                   d.source_type,
                   c.chunk_index,
                   1 - (c.embedding <=> %s::vector) AS similarity
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE d.source_type = %s
            ORDER BY c.embedding <=> %s::vector
            LIMIT %s
            """,
            (query_embedding, source_type, query_embedding, top_k),
        )
    else:
        cur.execute(
            """
            SELECT c.content,
                   d.title,
                   d.source_type,
                   c.chunk_index,
                   1 - (c.embedding <=> %s::vector) AS similarity
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            ORDER BY c.embedding <=> %s::vector
            LIMIT %s
            """,
            (query_embedding, query_embedding, top_k),
        )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "content":     row[0],
            "title":       row[1],
            "source_type": row[2],
            "chunk_index": row[3],
            "similarity":  float(row[4]),
        }
        for row in rows
    ]

def rerank(query: str, chunks: list[dict], top_n: int = 3) -> list[dict]:
    """
    Cross-encoder reranking: score each chunk against the query,
    return the top_n highest-scoring chunks.
    """
    if not chunks:
        return []

    pairs  = [(query, chunk["content"]) for chunk in chunks]
    scores = cross_encoder.predict(pairs)

    for chunk, score in zip(chunks, scores):
        chunk["rerank_score"] = float(score)

    reranked = sorted(chunks, key=lambda c: c["rerank_score"], reverse=True)
    return reranked[:top_n]
```

> **Why cross-encoder reranking?** Bi-encoder embeddings (the HNSW search) are fast but sacrifice precision — they encode query and document independently. A cross-encoder sees the query and document together, giving much better relevance judgements. The two-stage pipeline (fast bi-encoder retrieval → precise cross-encoder rerank) is the standard production pattern.

#### Step 2: Write `rag_chat.py`

```python
import os
import time
import yaml
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI
from retriever import retrieve, rerank

load_dotenv()

PROMPT_FILE          = "prompts/system_v1.yaml"
CONTEXT_BUDGET_TOKENS = 3_000
TOP_K_RETRIEVE        = 5
TOP_N_RERANK          = 3

def load_prompt_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

def count_tokens(messages: list[dict], model: str) -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    total = 0
    for msg in messages:
        total += 4
        for value in msg.values():
            total += len(enc.encode(str(value)))
    total += 2
    return total

def format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks as labelled context blocks."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(
            f"[Source {i}: {chunk['title']}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)

def build_rag_system_prompt(base_prompt: str, context: str) -> str:
    return (
        base_prompt.strip()
        + "\n\n"
        + "=== RETRIEVED CONTEXT ===\n"
        + context
        + "\n=== END OF CONTEXT ===\n\n"
        + "Answer only based on the provided context. "
        + "If the context does not contain the answer, say: "
        + "'I cannot find this information in my reference documents.'"
    )

def main():
    config      = load_prompt_config(PROMPT_FILE)
    model       = config["model"]
    temperature = config["temperature"]
    max_tokens  = config["max_tokens"]
    base_prompt = config["system_prompt"].strip()

    client  = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    history: list[dict] = []

    print(f"MedChat RAG v{config['version']}")
    print("Type 'quit' to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if user_input.lower() in {"quit", "exit", ""}:
            print("Goodbye.")
            break

        # ── RAG: retrieve → rerank → inject ────────────────────────────────
        print("  [retrieving...]")
        chunks   = retrieve(user_input, top_k=TOP_K_RETRIEVE)
        reranked = rerank(user_input, chunks, top_n=TOP_N_RERANK)
        context  = format_context(reranked)

        rag_system_text = build_rag_system_prompt(base_prompt, context)
        system_msg      = {"role": "system", "content": rag_system_text}

        history.append({"role": "user", "content": user_input})
        messages = [system_msg] + history

        # ── Call the API ────────────────────────────────────────────────────
        t_start  = time.perf_counter()
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        latency_ms = (time.perf_counter() - t_start) * 1_000

        assistant_msg = response.choices[0].message.content
        history.append({"role": "assistant", "content": assistant_msg})

        # ── Print answer with source attribution ────────────────────────────
        print(f"\nMedChat: {assistant_msg}\n")
        print("  Sources used:")
        for i, chunk in enumerate(reranked, 1):
            print(f"    [{i}] {chunk['title']} (similarity={chunk['similarity']:.3f})")
        print(
            f"  [tokens: {response.usage.total_tokens} | "
            f"latency={latency_ms:.0f}ms]\n"
        )

if __name__ == "__main__":
    main()
```

#### Step 3: Test with five questions — RAG vs. baseline

Run the RAG chatbot:

```bash
python rag_chat.py
```

Ask these five questions and note the source attributions:

```
You: What is the first-line antibiotic for community-acquired pneumonia?
You: Does azithromycin interact with methadone?
You: What is the maximum daily dose of paracetamol in adults?
You: How do I dose enoxaparin for DVT treatment?
You: What antibiotics are safe in pregnancy for a UTI?
```

For each answer you should see which document the information was drawn from (e.g., "Antibiotic Prescribing Guidelines" vs. "Drug Interaction Reference").

#### Step 4: Trigger a RAG failure — out-of-corpus question

Test what happens when the corpus cannot answer the question:

```
You: What is the standard protocol for managing a diabetic ketoacidosis (DKA) in a paediatric patient?
```

The model should respond with: *"I cannot find this information in my reference documents."*

This is the correct behaviour. A model that hallucinates a DKA protocol that is not in your curated corpus is more dangerous than one that admits ignorance.

> **RAG failure mode 1 — out-of-corpus:** The retriever returns chunks that are topically similar but not actually relevant. The cross-encoder score will be low. If you print `chunk['rerank_score']` for this query, you'll see scores near 0.0, which can be used as a confidence threshold to refuse answering.

#### Step 5: Metadata filtering — restrict retrieval to one document type

Add this test in a Python script `test_filter.py`:

```python
from retriever import retrieve, rerank

# Only search the drug interactions CSV
chunks   = retrieve("azithromycin interaction", top_k=5, source_type="csv")
reranked = rerank("azithromycin interaction", chunks, top_n=3)

for chunk in reranked:
    print(f"[{chunk['title']}] score={chunk['rerank_score']:.3f}")
    print(chunk["content"][:200])
    print()
```

Run it:

```bash
python test_filter.py
```

All returned chunks should be from the drug interactions CSV only. This is useful when a user asks a question that you know belongs to a specific document type — for example, the pharmacy team's interface might always restrict to `source_type="csv"`.

---

### References

1. pgvector documentation — <https://github.com/pgvector/pgvector>
2. OpenAI Embeddings API reference — <https://platform.openai.com/docs/api-reference/embeddings>
3. Sentence Transformers cross-encoders — <https://www.sbert.net/examples/applications/cross-encoder/README.html>
4. HNSW index algorithm (Malkov & Yashunin, 2018) — <https://arxiv.org/abs/1603.09320>
5. RAG survey (Gao et al., 2023) — <https://arxiv.org/abs/2312.10997>
