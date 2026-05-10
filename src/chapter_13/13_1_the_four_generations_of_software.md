## 13.1 The Four Generations of Software

Software has not been the same thing in every decade. The technologies have changed, but the more important change has been in the *relationship between the engineer and the program's logic*. Each generation defined a different answer to the question: who decides what the software does?

### 13.1.1 Software 1.0: The Engineer Decides

Software 1.0 is the software described in Chapters 1 through 12. The engineer reads requirements, translates them into logic, and writes code that implements that logic explicitly. The program does exactly what the code says. Every decision point — every `if`, every `while`, every database query — was put there by a human who reasoned about it.

This is not a limitation; it is a design. Explicit logic is auditable, testable, and debuggable. When a Software 1.0 system produces the wrong output, you can find the line of code responsible. The engineering practices described in this book — requirements engineering, design patterns, unit testing, CI/CD, code review — were built for this model. They work because the system is deterministic and its logic is fully visible.

The limitation of Software 1.0 is not its correctness — it is the range of problems it can address. Writing explicit rules for spam detection, face recognition, or language translation is not merely difficult; it is practically impossible. The rules are too numerous, too interdependent, and too contextually sensitive for any team of engineers to enumerate. For decades, this boundary defined what software could and could not do.

### 13.1.2 Software 2.0: The Data Decides

In 2017, Andrej Karpathy — then Director of AI at Tesla — published an essay titled "Software 2.0" that named a shift that was already underway ([Karpathy, 2017](https://karpathy.medium.com/software-2-0-a64152b37c35)). The argument was simple and radical: for a growing class of problems, engineers do not write the program. They write the dataset and the objective function, and the optimisation algorithm writes the program. The resulting program — the neural network — is not human-readable. It is a matrix of floating-point weights that encodes patterns extracted from millions of examples.

Software 2.0 expanded what software could do dramatically. ImageNet-scale image classifiers, speech recognition systems, and recommendation engines that would have been unthinkable as explicit rule sets became tractable as learned models. It introduced failure modes that Software 1.0 practices were not designed to catch.

**The logic is invisible.** You cannot read a neural network's weights and understand why it made a particular decision. Debugging is replaced by probing: you run more examples through the model and look for patterns in its errors. The Obermeyer et al. case is precisely this failure — the network's logic was not inspectable, and the engineering process did not have a systematic way to test it for the right properties.

**The system is sensitive to data.** Change the training data and you change the system's behaviour — without touching a line of code. Traditional version control tracks code. It does not track the dataset that produced the model. Two identical codebases trained on different data produce different systems.

**Performance is a distribution, not a value.** A Software 1.0 function either returns the right answer or it does not. A Software 2.0 model returns a correct answer on 94.3% of test examples — a statistic that says nothing about which examples it gets wrong, whether the errors are uniformly distributed across demographic groups, or whether performance will hold when the input distribution shifts.

These are not bugs to be fixed. They are structural properties of the paradigm. Addressing them requires new practices — practices that Software 2.0 gave us both the need and the motivation to develop.

### 13.1.3 Software 3.0: The Prompt Decides

The release of GPT-3 in 2020 and the subsequent wave of instruction-tuned foundation models introduced a third generation. Software 3.0 describes systems built on top of large pre-trained models that can perform a wide range of tasks without task-specific training — instead, the task is specified through natural language instructions: the prompt.

The defining characteristic of Software 3.0 is that the barrier between specification and execution collapsed. In Software 1.0, requirements are translated into code by an engineer. In Software 3.0, requirements can be expressed directly in the language the model was trained on — English, Python, SQL — and the model executes them. For many tasks, an engineer's job shifted from writing logic to writing prompts.

This created new leverage and new risk simultaneously. A well-crafted prompt can replace weeks of feature engineering. A poorly crafted prompt — or a maliciously injected one — can cause a production system to behave arbitrarily. The Software 3.0 engineer is no longer primarily a programmer; they are a system designer who must understand model capabilities, failure modes, context window limits, and the economics of inference at scale.

Software 3.0 also introduced a new deployment model. The model itself is rarely trained by the team building the application — it is accessed through an API. The application developer controls the prompt layer, the retrieval layer, and the guard layer, but not the model weights. This separation of concerns creates both engineering advantages (you benefit from the model provider's investments in safety and capability) and engineering risks (the model can change under you, and you cannot inspect its internals).

### 13.1.4 Software 4.0: The Agent Decides

Software 4.0 is where the field currently stands and where the trajectory is leading. In Software 4.0, the system is not merely responding to prompts — it is pursuing goals. An agent perceives its environment, selects actions, executes them through tools, observes outcomes, and revises its plan. The engineer defines the goal and the constraints. The agent decides the sequence of steps.

This is a fundamental shift in the locus of control. In every previous generation, the engineer or the user drives execution. In Software 4.0, the agent drives execution, and the engineer's job is to specify the boundaries within which it operates.

The implications for software engineering are profound. A Software 4.0 system can take actions in the world: write files, execute queries, call APIs, send messages. When it makes an error, the error may not be a wrong output — it may be a real-world consequence that cannot be undone. The reliability requirements are qualitatively different from previous generations: you are not asking whether the system produces the right prediction, but whether an autonomous system operating at scale can be trusted not to cause harm.

| Generation | Who decides the logic | Primary artifact | Dominant failure mode |
|---|---|---|---|
| Software 1.0 | The engineer (explicit code) | Source code | Logic bugs, missing edge cases |
| Software 2.0 | The data (learned weights) | Trained model | Distributional bias, data leakage |
| Software 3.0 | The prompt (foundation model) | Prompt + retrieval pipeline | Hallucination, injection, context drift |
| Software 4.0 | The agent (goal-directed action) | Agent system with tools | Unintended real-world actions, compounding errors |

SE4AI is the discipline that addresses this accumulation of failure modes — the ones that each prior generation's engineering practices were not built to handle.

---
