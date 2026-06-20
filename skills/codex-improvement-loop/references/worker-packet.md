# Worker Packet

```text
You are the worker for <initiative> / <node_id>.

Role: worker
Relationship: <sequential|parallel|stacked>
Repo: <repo>
Base: <base_branch_or_local_state>
Branch/worktree: <branch_or_worktree>

Goal:
- <focused goal>

In scope:
- <item>

Out of scope:
- <item>

Allowed context:
- <specific files, PRs, research notes, screenshots, or predecessor output>

Ignore:
- unrelated PRs
- future nodes
- old review comments not included here
- the full initiative plan unless explicitly pasted here

Skills to use:
- <task-relevant skills only>

Preflight:
- Run `git status --short`.
- If dirty files overlap this task, inspect them before edits and report any risky ownership conflict.
- Do not use `git stash`, `git checkout --`, or `git reset` without explicit orchestrator/user instruction.
- If publishing, verify the worktree can write the git index and read the remote base before edits.
- Stop and report exact stderr if preflight fails.
- If a required skill is missing, report: `MISSING SKILL: <skill>. Fallback: <fallback>. Risk: <high|medium|low>. Action: <pause|proceed>.`

Acceptance:
- <observable result>

Verification expected:
- <test command, screenshot, app check, or manual validation>

Rules:
- Keep the diff narrow.
- Do not merge.
- Do not start dependent work.
- Report any needed new node instead of expanding scope.

Return:
- summary of changes
- changed files
- tests/checks run and results
- remaining risks
- requested orchestrator action, if any
```
