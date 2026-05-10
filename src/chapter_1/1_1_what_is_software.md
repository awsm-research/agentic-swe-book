## 1.1 What Is Software?

**Software** is more than just code. It is the combination of:

- **Programs** — the executable instructions that tell a computer what to do
- **Data** — the information that programs process, including configuration files and databases
- **Documentation** — the materials that describe how to install, use, and maintain the system

This matters because the quality of a software product depends on all three. A perfectly coded program with no documentation is hard to maintain. Poorly designed data structures can cripple an otherwise elegant program.

### Examples of Software Systems

Software underpins virtually every sector of modern life:

| Domain | Example System | Purpose |
|---|---|---|
| **Healthcare** | Electronic Health Record (EHR) | Manage patient data, clinical workflows, prescriptions |
| **Finance** | Online banking platform | Account management, transactions, fraud detection |
| **E-commerce** | Amazon, Shopify | Product catalogue, payments, fulfilment tracking |
| **Transportation** | Uber, Google Maps | Route optimisation, driver dispatch, navigation |
| **Education** | LMS (Moodle, Canvas) | Course delivery, assessment, student progress tracking |

These systems share a common characteristic: they must handle real users, real data, and real consequences when things go wrong. A bug in a spreadsheet script affects one person. A bug in a hospital's prescribing system can endanger lives.

### Generic vs. Customised Products

Software products fall into two broad categories:

- **Generic products** are developed for a broad market and sold to whoever wants them. Examples include Microsoft Office, Adobe Photoshop, and operating systems like Windows. The developer controls the specification.

- **Customised products** (also called bespoke software) are built for a specific client to meet their particular requirements. Examples include a hospital's patient management system or a bank's internal risk platform. The client controls the specification.

The distinction matters for software engineering because it affects who decides what gets built, when it is done, and what constitutes success. Customised projects carry a higher risk of requirements misalignment — the client and developer must invest heavily in understanding each other.

### Why Software Is Different

Software has unique properties that distinguish it from physical engineering products and make it uniquely challenging to build well:

- **Intangible**: You cannot see, touch, or physically measure software. Quality problems can be invisible until they manifest as failures.
- **Malleable**: Unlike a bridge or an engine, software can be changed after deployment — and users expect it to be. This is both a strength and a persistent source of cost.
- **Knowledge-intensive**: Software encodes human knowledge and decision-making. Its complexity scales with the depth of the domain it models.
- **Does not wear out — but it decays**: Hardware degrades physically over time. Software does not rust, but it *decays* as the environment around it changes: operating systems upgrade, dependencies are deprecated, user expectations evolve.

### Unique Challenges

These properties create challenges with no clean parallel in other engineering disciplines:

- **No universal theories or methods.** Civil engineers can consult structural mechanics and established load calculations. Software engineering has no equivalent universal laws — the field lacks a unified theoretical foundation that determines how complex systems should be built.
- **Extraordinarily fast evolution.** Languages, frameworks, and platforms that are standard today may be obsolete in five years. This pace of change means software engineers must be continuous learners.
- **Invisible complexity.** A large software system can contain billions of interacting states. Unlike a physical structure, you cannot visually inspect it for flaws.

These properties mean software engineering has no perfect analogy in civil or mechanical engineering. Fred Brooks captured this in 1987 when he observed that software has no "silver bullet" — no single technique that delivers an order-of-magnitude improvement in productivity, reliability, or simplicity ([Brooks, 1987](https://en.wikipedia.org/wiki/No_Silver_Bullet)).

### The Role of Software in Society

Software is not merely a technical artefact — it is an economic and social force. Technology sectors, of which software is the core, account for a growing share of GDP in developed economies. More critically, essential infrastructure — hospitals, banks, transport networks, power grids — runs on software. When that software fails, the consequences extend far beyond a frustrated user.

Software that fails does not fail quietly. It breaks a city's public transport network, triggers regulatory penalties, or grounds flights. This is why software engineering exists as a discipline — not because writing code is hard, but because the consequences of writing it badly are often borne by people who never saw the source.

---
