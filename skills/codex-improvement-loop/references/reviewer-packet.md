# Reviewer Packet

```text
Review <node_or_pr> for <initiative> / <node_id>.

Role: reviewer
Scope: review only this node.

Goal:
- <focused goal>

Expected scope:
- <scope>

Acceptance:
- <acceptance criteria>

Context:
- <relevant files, PR URL, screenshots, or predecessor summary>

Review stance:
- Lead with bugs, regressions, missing tests, truth gaps, accessibility issues, performance risks, data-model issues, and scope creep.
- Check that the node did not overwrite unrelated dirty work or broaden scope beyond its packet.
- Check that any missing-skill fallback was called out with risk level.
- Do not implement fixes.

Output:
- approval/blocking status
- findings ordered by severity with file/line references
- missing tests or validation gaps
- open questions before merge
- requested orchestrator action, if any
```

