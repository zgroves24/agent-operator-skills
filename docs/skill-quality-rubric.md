# Skill Quality Rubric

Use this rubric before adding a skill to this repository.

## Strong Skills

A strong skill should:

- solve a recurring, high-value agent workflow
- have a clear trigger condition
- define what the agent should do first, next, and last
- include verification gates
- make failure modes explicit
- avoid private names, paths, accounts, companies, and customer data
- be useful outside one person's machine or one private product
- be small enough that an agent will actually follow it

## Weak Skills

A weak skill usually:

- repeats generic prompting advice
- has no concrete workflow
- depends on private context
- tells the agent to "be better" without checks
- mixes unrelated domains
- hides risky assumptions
- cannot be verified

## Public Release Bar

Before a skill is published here, check that it passes:

- **Portability:** can someone else use it without your private setup?
- **Specificity:** does it change agent behavior in a concrete way?
- **Safety:** does it avoid secrets, local paths, names, and private data?
- **Verification:** does it force proof before completion?
- **Maintenance:** can future contributors understand when to use it?

If a skill fails one of these checks, keep it private or rewrite it before publishing.
