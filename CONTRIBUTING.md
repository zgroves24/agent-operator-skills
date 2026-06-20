# Contributing

Contributions are welcome when they make the public skill set more useful, portable, and safe.

## What Belongs Here

Good additions are reusable agent skills for:

- planning and decomposing complex work
- implementation loops and verification gates
- security, SEO, release, or quality audits
- developer tooling and workflow automation
- public, generic operating patterns

Do not add:

- personal admin workflows
- private company or product workflows
- local machine paths
- personal names, emails, account IDs, or customer data
- copied secrets, tokens, cookies, or production payloads
- vendor-owned skills already published elsewhere

## Skill Checklist

Before opening a pull request, make sure the skill has:

- a clear `name` and `description`
- specific trigger guidance
- concrete workflow steps
- verification or review gates
- failure or blocked-state behavior
- no private context
- Apache-2.0 compatible provenance

## Local Audit Commands

Run a privacy scan before publishing:

```bash
rg -n -i "personal-name|private-product|home-directory-path|email-domain|token|secret|password|cookie" .
```

Run any included scripts with `--help` or a safe sample input so reviewers can see that they work.

## Review Standard

Reviews should lead with risks:

- privacy leaks
- unclear trigger conditions
- instructions that are too generic to change behavior
- missing verification gates
- brittle scripts or untested examples

Small, focused skills are preferred over broad prompt packs.
