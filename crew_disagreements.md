# Built-In Disagreement Map

Real software engineers disagree about everything. The crew is chosen so that disagreement is structural — the personas are designed around real, documented operating differences and published positions.

This map is the seam-finder. Use it before any formal run to predict where friction will be — and which agents to explicitly pair to surface it.

## The Rigor ↔ Shipping Axis

| Rigor-leaning | Shipping-leaning |
|---|---|
| Knuth | Torvalds |
| Dijkstra | Pike |
| Lamport | Beck (ship a small thing every day) |
| Hoare | Armstrong (let it crash, then fix it) |
| Liskov | |

**Knuth vs. Torvalds** is the cleanest core disagreement. Knuth wants code that's *correct* by analysis (and beautiful by literate exposition). Torvalds wants code that *compiles, runs, and is maintainable by a stranger six years later*. Both are right; they will not produce the same verdict on a working-but-ugly patch.

When the team is stuck between "but it works" and "but it's not clean," send it through both. The gap between their verdicts is where the answer usually lives.

## The Abstraction ↔ Data Axis

| Abstraction-first | Data-first |
|---|---|
| Liskov | Hickey |
| Hoare | Pike |
| (OO traditions in general) | Torvalds (kernel) |

**Hickey vs. Liskov** is the foundational paradigm disagreement. Liskov's lineage holds that good design starts with abstract data types, contracts, and substitutability — types and abstractions encode discipline. Hickey holds that abstractions are often a way to avoid thinking about data, that "objects are bad," and that the right move is to keep data as values, time-stamped, and let pure functions transform them.

They will disagree on whether to introduce an interface or just pass a hashmap. They will disagree on whether classes or namespaces are the right module boundary. They will disagree on whether `instanceof` is a code smell or a category error. Both are deep, both are right in different regimes. Pair them on any architectural question where the team's defaults are about to win by inertia.

## The TDD ↔ Design-First Axis

| Test-first | Design-first |
|---|---|
| Beck | Hickey (explicitly critical of TDD) |
| | Dijkstra (think first, write later) |
| | Knuth (prove first, type later) |

**Beck vs. Hickey** is a real disagreement, not a stylistic one. Beck holds that tests drive design — you cannot know what the code should look like until you've tried to use it under test. Hickey holds that TDD makes you *change-tolerant* but not *simple*; it gets you to working code without thinking about whether the code is the right code. Beck would write the test first; Hickey would think for an hour first.

Pair them when the question is "should we have started with a test." Beck will say yes; Hickey will say "did you think first about what value, what time, what identity?"

## The Simplicity-As-Minimalism ↔ Simplicity-As-Decomposition Axis

| Minimalism (less of everything) | Decomposition (clean separation, more of less) |
|---|---|
| Pike | Hickey |
| Torvalds | Kay (not in roster, represented partially through Liskov) |
| Wirth (not in roster) | Liskov |

Pike's "make it as small as possible, no smaller" produces Go: a deliberately small language with few abstractions, where you write more code but each piece is obvious. Hickey's "decompose into independent concerns" produces Clojure: a language with many small composable abstractions over immutable values. Both call themselves "simple." They are not the same kind of simple.

Pair them on questions of "should this be one function with a long body, or should it be five small composed functions." Pike will often pick the first; Hickey often the second.

## The Formal ↔ Empirical Axis

| Formal verification / proof | Empirical testing |
|---|---|
| Dijkstra | Beck |
| Lamport | Torvalds |
| Hoare | Armstrong (let it crash and observe) |
| Knuth | |

**Dijkstra vs. Beck** is the cleanest version. Dijkstra famously held that "program testing can be used to show the presence of bugs, but never to show their absence." Beck holds that the discipline of writing tests *before* code is what makes a system actually evolve safely. They are not addressing the same question. Both are right in their domain.

When a project's testing strategy is up for review, run both. Dijkstra will ask whether the design has been formally reasoned about. Beck will ask whether the team can actually change the system without breaking it.

## The "Programming Is Theory" Axis (Naur, alone)

Naur's 1985 paper "Programming as Theory Building" holds that the program is a *secondary* artifact; the primary artifact is the team's shared mental model — the *theory* of the system. When the team that built the system disperses, the theory is lost, and the code becomes legacy regardless of how well-written it is.

This is a position no other crew member explicitly holds, though several would partly agree:
- Brooks ("conceptual integrity") is closest
- Hickey ("what is this code's value, identity, time?") would partly agree
- Knuth (literate programming) tries to write the theory into the program

Use Naur when the question is "we have the code, why isn't it working" and the actual answer is "the team that knew why is gone." Naur is the only voice in the crew who centers this question.

## The Fault-Tolerance ↔ Fault-Prevention Axis

| Prevent the fault | Tolerate the fault |
|---|---|
| Hoare (types, contracts, no null) | Armstrong (let it crash, supervise) |
| Liskov (substitution preserves invariants) | |
| Dijkstra (prove correctness) | |

**Hoare vs. Armstrong** is real. Hoare wants the type system, the contract, and the static analysis to make the bad state unrepresentable. Armstrong observed that real distributed systems will fail anyway, so the right discipline is to design for crash and recovery — supervision trees, isolated processes, "let it crash" as policy.

Pair them on any reliability question. The right answer often combines them (prevent what you can, tolerate what you can't), but the *default* a team chooses tells you a lot about their architecture.

## Pairings That Produce The Sharpest Friction

| Pair | Friction |
|---|---|
| Knuth + Torvalds | Rigor vs. shipping — the cleanest core disagreement |
| Hickey + Beck | TDD as design vs. data-first thinking |
| Hickey + Liskov | Data-oriented composition vs. abstract-data-type discipline |
| Pike + Liskov | Small data + small functions vs. abstract-data-type encapsulation |
| Dijkstra + Torvalds | Formal-rigor floor vs. pragmatic ship-it |
| Lamport + Torvalds | Prove distributed correctness vs. test the kernel |
| Beck + Knuth | Test-first vs. analyze-first |
| Hoare + Armstrong | Prevent bad states vs. tolerate inevitable crashes |
| Naur + everyone | Programming is theory; everything else is artifact |
| Brooks + Beck | Conceptual integrity (one architect) vs. team practice (XP) |

## Pairings That Risk Echo Chamber

| Pair | Why they will agree too easily |
|---|---|
| Knuth + Dijkstra | Both formal-leaning; both prefer mathematical rigor; will agree the patch is sloppy |
| Hickey + Pike | Both minimalist about object hierarchies; will agree to remove abstraction without checking what gets lost |
| Torvalds + Pike | Both Unix philosophy; will agree on the kernel-style answer too quickly |
| Beck + Fowler-style (not in roster) | Both XP; will agree on small steps and refactoring |
| Lamport + Hoare | Both formal-methods-leaning; will produce a beautiful proof and miss the engineering reality |

When the question needs friction, avoid the echo pairings. When the question needs decisive synthesis, *use* them — but verify with one of the friction pairings afterward.

## The AI-Acceleration ↔ Engineering-Trust Axis

| AI-acceleration | Engineering-trust |
|---|---|
| Forge | Sentry |
| Forge | Torvalds (would you accept this patch from anyone) |
| Forge | Knuth (have you read it like a paper) |
| Foreman | Naur (does the team share the theory of this AI-driven change) |

The 2026 temptation is to let AI coding agents move faster than the team's review and theory can support. Forge is the lens that makes AI agents productive; Sentry, Torvalds, Knuth, and Naur are the lenses that hold AI output to the same bar as human output. Use these pairings deliberately:

- **Forge + Sentry**: AI-suggested code passes security/provenance/license review before merge.
- **Forge + Torvalds**: AI-generated patches get the same brutal-but-technical review a human's would.
- **Forge + Knuth**: AI-generated code is read for correctness and clarity, not accepted because the diff looks plausible.
- **Forge + Naur**: AI-driven changes are captured in the team's theory before they accumulate as opaque commits.

If Forge wins these pairings without resistance, the team is on a path toward AI-output-as-truth, which is how silent regressions accumulate. Resistance from Sentry, Torvalds, Knuth, and Naur is a feature, not friction.

## The Local-Agent ↔ Production-Reality Axis

| Local-agent (pre-merge) | Production-reality (post-merge) |
|---|---|
| Knuth, Dijkstra, Hickey, Liskov, Pike, Torvalds | Telemeter |
| Beck (TDD-as-design) | Telemeter (production-as-test) |
| Forge | Telemeter |

Pre-merge review catches what review can catch. Production catches the rest. Telemeter is the only voice that brings post-merge reality back into the review loop. When the team has been iterating on a change for weeks without consulting Telemeter, the question "did the previous change actually do what we said it would" usually surfaces a surprise.

## Anti-Pattern: Forcing Consensus

If a formal run produces "all six core personas plus all seven ops agents agree," something has gone wrong:

- Either the question was too narrow (only one axis was active)
- Or the personas were not actually adopted (the model defaulted to consensus voice)
- Or Foreman didn't load the right friction pairings
- Or the question was a soft preference question, not an engineering question

The crew is healthier when at least one persona dissents. If consensus is real, it should be earned through the disagreement passes — not assumed. Foreman's job is to make sure that disagreement is visible in the change memo, not smoothed over.
