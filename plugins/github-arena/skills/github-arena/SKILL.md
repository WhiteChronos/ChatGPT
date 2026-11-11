---
name: github-arena
description: Use GitHub Arena MCP tools as a quality-control layer for ChatGPT and Codex tasks. Trigger automatically for GitHub, coding, architecture, CI/CD, repository, security, review, or high-impact work, and when the user asks for arena, competing approaches, adversarial review, or higher assurance. Use the GitHub connector for repository reads/writes and the github_arena MCP server for review planning, strategy cards, rubric, and checklists.
---

# GitHub Arena Tool Workflow

Use the `github_arena` MCP server together with the existing GitHub connector.

## Default

For ordinary work, call `arena_review_checklist` with:
- `github=true` when a GitHub repository, branch, PR, issue, commit, Actions workflow, or GitHub connector is involved.
- `high_impact=true` for code changes, architecture, CI/CD, security, governance, production, public API, or multi-file changes.

Apply the returned checklist before finalizing.

## Complex review

For high-impact work:

1. Call `arena_plan` with 4 to 16 strategies.
2. Call `arena_cards` with the same count.
3. Develop materially different candidate approaches.
4. Attack and revise them using the returned cards.
5. Use `arena_rubric` to compare the finalists.
6. Verify the selected result against the actual GitHub state before writing.

## GitHub division of responsibility

- GitHub connector: repository facts and repository mutations.
- GitHub Arena MCP: quality review, planning, strategy diversity, rubric and checklists.
- Repository `AGENTS.md`: local engineering/governance constraints.

Never claim independent subagents ran unless the runtime actually executed them.
