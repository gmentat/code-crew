# Code Review Methods

The concrete review and improvement methods the crew uses. Operating companion to the personas — the personas hold the discipline; this file holds the recipes.

## What a code review is for

The crew distinguishes four things people often conflate:

1. **Defect review** — does this code have bugs? (Knuth, Hoare, Dijkstra)
2. **Design review** — is this the right shape? (Liskov, Hickey, Pike, Brooks)
3. **Maintainability review** — will the next person understand it? (Naur, Knuth's literate-programming, Torvalds' "is this readable")
4. **Improvement review** — should we change working code, and how? (Beck, Fowler-style refactoring, Hickey's "simple-not-easy")

A good review names which it is. A confused review tries to do all four at once and produces nothing.

## The crew's review pipeline

Formal multi-lens review means Foreman dispatches each selected lens as an independent blind-pass subagent, preferably in parallel when the lenses are independent. The ordered list below is a selection guide, not permission for one reviewer to impersonate every lens in one context.

```
Naur:      What is the theory? Do we share it?
Liskov:    What are the abstract data types? What are the contracts?
Hickey:    What's incidental complexity? Where is data hiding?
Pike:      Could this be smaller and more composable?
Knuth:     Are the algorithms and invariants right?
Dijkstra:  Would this survive formal-correctness audit?
Torvalds:  Would a brutal-but-technical maintainer accept the patch?
Beck:      Where's the smallest change that would make this easy to change?
Hoare:     Where can null, race, or undefined behavior bite?
Lamport:   Where can distributed semantics surprise us?
Armstrong: Where will this fail in production, and is failure isolated?
Brooks:    Does this preserve conceptual integrity across the team?
```

You don't run all twelve every time. The pipeline is a menu, not a ritual.

## When to use which lens

| Symptom in the code or system | Lenses to load first |
|---|---|
| "It works but I don't trust it." | Knuth + Dijkstra + Hoare |
| "It works but the next person won't understand it." | Naur + Knuth + Torvalds |
| "We can't change anything without breaking five things." | Liskov + Hickey + Beck |
| "Every time we add a feature, there's three weeks of yak-shaving." | Hickey + Pike + Brooks |
| "Tests are slow / brittle / not actually catching bugs." | Beck + Hickey + Dijkstra |
| "The system is fragile in production." | Armstrong + Hoare + Lamport |
| "Performance is bad and we don't know why." | Knuth + Pike + Torvalds |
| "We're rewriting the same thing in three places." | Liskov + Pike + Brooks |
| "Onboarding new engineers takes six months." | Naur + Brooks |
| "Distributed system has surprising failure modes." | Lamport + Armstrong + Hoare |

## Concrete review recipes

### The "five-line review" (fast pass, single function)

Used for everyday code review where the function fits on a screen. This is a lightweight single-reviewer checklist, not a formal crew run. If the output claims to be a multi-lens crew verdict, dispatch independent subagents instead.

1. **Knuth, in 30 seconds:** what does this function do, in one sentence? If you can't say it, the function is doing too much.
2. **Pike, in 30 seconds:** is the data shape obvious? Are the types or structures hiding control flow?
3. **Hickey, in 30 seconds:** what's the value here? What changes over time? What's identity?
4. **Liskov, in 30 seconds:** what does this function promise its caller? Does it keep the promise?
5. **Torvalds, in 30 seconds:** would you accept this patch?

If any of the five fails, the function needs work before merge.

### The "system design review" (slow pass, architectural)

Used when designing or critiquing a system, not just a function.

1. **Naur first, always:** state the theory in one paragraph. If the team can't agree on the paragraph, the theory is missing and design review is premature.
2. **Liskov:** name the abstract data types. Name their contracts. Name the substitutability boundaries.
3. **Hickey:** for each module, name its values, its identities (mutable references), its time semantics, its inputs and outputs as data.
4. **Pike:** could the system be smaller and composed of more general tools? Are we accidentally building a framework where a library would do?
5. **Brooks:** does the system have conceptual integrity? Could one architect explain it in one diagram?
6. **Lamport (if distributed):** what are the failure modes? What's the consistency model? Has it been modeled in TLA+?
7. **Armstrong (if reliability matters):** what fails, and is failure isolated and observable?
8. **Hoare:** where can null, race, or undefined behavior arise? What invariants hold under what concurrency?

### The "is this code's complexity essential?" recipe

Hickey's central question, applied as a method.

For each abstraction in the code, ask:

- **Is the complication essential to the problem, or accidental from the tools we chose?**
- Could we eliminate this abstraction by changing the data shape?
- Could we eliminate it by separating value from time, or value from identity?
- Could we eliminate it by passing data instead of objects?

If the answer to any is yes, the abstraction is incidental complexity and should be removed.

### The "Torvalds patch acceptance" recipe

For any non-trivial patch:

1. **Does it solve a real problem?** Not a hypothetical one, not a "while we're here" one. A specific bug or specific need.
2. **Is the diff readable?** Could a maintainer who's never seen this file follow the change?
3. **Does it match the existing style?** Not your style. The codebase's style.
4. **Does it not break the build, the tests, or any obvious invariant?**
5. **Could it have been smaller?** A patch that does three things should be three patches.

A patch that fails any of these gets refused. Politely or not, depending on the maintainer.

### The "TDD vs. design-first" recipe

When the team is debating whether to write the test first:

1. **Beck:** if you wrote the test now, what would it force you to decide? Is that the decision you should be making first?
2. **Hickey:** what is the value, the identity, the time semantics of what you're about to test? Have you thought about that before writing the test?
3. **Knuth:** can you state the invariant the function maintains? If yes, the test should encode the invariant. If no, you're testing examples, not behavior.

The decision usually isn't binary. The right discipline is "think first about value/identity/time/invariant, then write the test, then write the code." The danger of pure TDD is testing a wrong design quickly. The danger of design-first is overdesigning before reality corrects you.

## Commit-level discipline

A clean commit is small, named, reversible, and explains *why* (not what). The crew's view:

- **Knuth:** the commit message should be literate enough that someone reading the log understands why this change had to happen.
- **Torvalds:** the commit should do one thing. If you have to use "and" in the title, split the commit.
- **Pike:** if the commit changes more than ~50 lines, ask whether it should have been three commits.
- **Beck:** the commit should leave the test suite green. If it doesn't, you're committing speculation.
- **Naur:** the commit should be understandable to the team's *theory*, not just the team's *code*.

## When the harness gets too heavy

Code review can become an end in itself. The crew's brutal truth: review serves the code, the code does not serve review. If the team is spending more time arguing about formatting than fixing bugs, the discipline has become performance.

Three signs review has gone off the rails:

1. The review queue is longer than the work-in-progress queue.
2. Review comments are mostly about style and almost never about correctness or design.
3. The same patch goes through multiple rounds without changing in substance.

When this happens, the crew's recommendation is to **strip the review pipeline back to defect-and-design**, automate the rest (linters, formatters, type checkers), and ship.

## What review explicitly is not

- Review is not approval theater. A rubber-stamp review is worse than no review.
- Review is not language-war ground. Pick a style, hold it, move on.
- Review is not where you teach junior engineers (do that in pairing or in a doc).
- Review is not a substitute for testing, monitoring, or observability. It catches what those don't.
