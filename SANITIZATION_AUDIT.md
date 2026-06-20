# Sanitization Audit

Audit date: 2026-06-20

## Publish Strategy

This repository publishes a curated set of generic operator skills, not the entire local skills folder.

Published:

- `codex-improvement-loop`
- `honest-output-auditor`
- `changelog-generator`
- `cli-creator`
- `define-goal`
- `seo-audit`
- `security-best-practices`
- `security-threat-model`
- `security-ownership-map`

Excluded categories:

- personal or local-machine operator skills
- company/product-specific operator skills
- sales/outreach, analytics, ads, and vault workflows
- browser/screen-history workflows tied to a local environment
- third-party/vendor skills already published elsewhere
- large provenance-unclear UI/design tooling that needs a separate audit before public release

## Sanitization Performed

- Rewrote the improvement-loop skill from a private operating pattern into a generic multi-step agent workflow.
- Rewrote the audit skill into a generic hard-audit workflow.
- Rewrote the SEO audit script defaults so they no longer assume any private product route map.
- Removed generated Python cache files.
- Excluded private scripts and path-specific checks.
- Added three generic security skills after scanning for private names, local paths, and account-specific terms.

## Automated Checks

The repository was scanned for common private terms and risky tokens before publication, including:

- personal names and local usernames
- private product or vault names
- home-directory paths
- email addresses
- common secret/token/key patterns
- private repo and cloud-storage references

The audit is a best-effort guardrail, not a legal review.

## Known Limitations

- Some examples reference common third-party service categories such as GitHub. These are generic examples, not account data.
- Security ownership outputs may contain repository contributor names/emails when users run the tool on their own repos. That is expected output, not bundled data.
- The SEO script is intentionally generic. For a real product, pass custom route paths with `--public-path`, `--private-path`, and `--sample-prefix`.
- The security best-practices reference pack is intentionally broader than the other skills. It is included because it materially improves agent security reviews, but it should still be checked against current official framework guidance when high-stakes accuracy matters.
- Skills are prompts and workflow instructions. They improve process discipline, but they do not guarantee model correctness.
