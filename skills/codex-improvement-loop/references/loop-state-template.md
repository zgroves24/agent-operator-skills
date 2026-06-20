# Loop State Template

```yaml
initiative: "<name>"
slug: "<slug>"
status: planning | active | blocked | complete
repo: "<absolute path or GitHub repo>"
target_branch: "<branch>"
integration_branch: "<branch or local-only>"
constraints:
  - "<constraint>"
non_goals:
  - "<non-goal>"
merge_policy:
  may_push: false
  may_merge_integration: false
  may_merge_main: false
parallelism:
  max_active_workers: 2

nodes:
  - id: pr1
    title: "<focused chunk>"
    relation: sequential | parallel | stacked
    status: queued | active | in_review | changes_requested | ci_failing | approved | merged | blocked
    branch: "<branch or local task>"
    base: "<base>"
    depends_on: []
    scope:
      - "<in scope>"
    out_of_scope:
      - "<out of scope>"
    acceptance:
      - "<observable result>"
    tests:
      - "<command or validation>"
    touched_areas:
      - "<module/platform/workflow>"
    current_thread: null
    reviewer_thread: null
    latest_summary:
      worker: null
      review: null
      verification: null
      blocker: null

events:
  - at: "<ISO timestamp>"
    actor: orchestrator
    event: "<what changed>"
```

## Status Rules

- `queued`: not started or waiting on a dependency.
- `active`: implementation is underway.
- `in_review`: a reviewer or formal review pass is active.
- `changes_requested`: review found blocking issues.
- `ci_failing`: required tests/checks are failing.
- `approved`: gates pass but it is not merged or closed.
- `merged`: merged into the intended base.
- `blocked`: user input or external state is required.

