# Extended Council

The core six in `agents/` cover everyday code work. The council adds specialist lenses for harder runs — software project management, distributed-system formal methods, concurrency and null-safety, TDD/refactoring discipline, the "programming as theory building" perspective, and fault-tolerance.

These are reasoning archetypes inspired by public work. They do not impersonate, invent quotations from, endorse, or claim to represent the real people. Several are still living and active; the system uses them as decision contracts, not identity simulations.

## Roster

- [Brooks](brooks_agent.md) — *Mythical Man-Month*, conceptual integrity, "no silver bullet," software project management
- [Lamport](lamport_agent.md) — distributed-system theory, Paxos, formal verification with TLA+
- [Hoare](hoare_agent.md) — CSP, Hoare logic, the null-reference "billion-dollar mistake," correctness contracts
- [Beck](beck_agent.md) — XP, TDD, JUnit, refactoring discipline, "make the change easy, then make the easy change"
- [Naur](naur_agent.md) — *Programming as Theory Building*, mental models over text
- [Armstrong](armstrong_agent.md) — Erlang, OTP, "let it crash," supervision trees, fault-tolerant systems

## When To Use The Council

Use the council when:

- the core six have produced a verdict but the question deserves an adversarial second pass
- the project has distributed-system semantics (Lamport)
- the project is concurrent or has null-safety / type-safety problems (Hoare)
- the team is debating TDD vs. design-first (Beck against Hickey)
- the team has the code right but doesn't share the *theory* (Naur)
- the system needs fault-tolerance discipline (Armstrong)
- the project crosses team boundaries and needs conceptual-integrity / project-management lens (Brooks)

Do not load the entire council by default. Pick the smallest useful set. Most runs need 1–3 council agents added to the core six.

## Selection Patterns

| Question shape | Council lenses to add |
|---|---|
| "Is the distributed correctness right?" | Lamport |
| "Is null / race / undefined behavior a problem?" | Hoare |
| "Should we have written the test first?" | Beck (in tension with Hickey) |
| "We have the code; why isn't the team productive?" | Naur |
| "The system fails in surprising ways under load." | Armstrong |
| "This crosses three teams; how do we keep conceptual integrity?" | Brooks |
| "Adding people isn't speeding things up." | Brooks (canonical) |

## Built-In Disagreement Patterns

The council is designed for friction. See [crew_disagreements.md](../../crew_disagreements.md) for the full map. Most load-bearing council pairs:

- **Beck + Hickey** — TDD-as-design vs. think-first-data-first. Beck invented TDD; Hickey explicitly criticized it. The cleanest practice-level disagreement on the team.
- **Lamport + Torvalds** — formal verification of distributed correctness vs. test-and-ship pragmatism.
- **Hoare + Armstrong** — prevent-the-fault (types, contracts) vs. tolerate-the-fault (supervisors, "let it crash"). Both about reliability; opposite routes.
- **Brooks + Beck** — single-architect conceptual integrity vs. team-practice (XP) emergent design.
- **Naur alone** — when the team has the code right but doesn't share the theory, no other voice in the crew centers this question.

## Living-Person Disclaimer

Lamport, Hoare, and Beck are alive and active. Their personas here are reasoning archetypes based strictly on published work and well-documented public talks; no claim to represent their current views, no endorsement, no quotation as if from them. Brooks, Naur, and Armstrong are deceased.
