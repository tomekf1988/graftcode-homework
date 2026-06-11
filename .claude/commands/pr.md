Read .claude/CLAUDE.md first.

Prepare and create a pull request for milestone: $ARGUMENTS

Steps:

1. Read the milestone spec from docs/milestones/ (match by $ARGUMENTS or closest name)
2. Inspect git log main..HEAD and git diff main..HEAD
3. Push current branch to origin (git push -u origin <branch>)
4. Create the GitHub PR immediately using `gh pr create` — do not stop and ask for confirmation
5. Save PR summary to docs/prs/<milestone_name>.md

## PR title

Format: `feat: <milestone name in lowercase>`

## PR description (gh pr create --body)

Use this structure:

```
## Summary

2-3 sentences: what this milestone delivers and why it matters.

## Changes

### Backend
- bullet list of concrete changes (files, endpoints, decisions)

### Frontend
- bullet list of concrete changes (files, components, decisions)

### Infrastructure
- docker, makefile, env, config changes if any

## Acceptance criteria

Copy the checklist from the milestone spec (docs/milestones/) with status.

## Technical decisions

- key architectural or implementation choices made and why
- tradeoffs if relevant

## Testing

- what was tested and how (manual, automated, what commands)

## Remaining work

- next milestone(s) not yet implemented
```

## Rules

* Push the branch before creating the PR
* Use `gh pr create --title "..." --body "..." --base main` to create the PR automatically
* Do not ask for confirmation before creating — just do it
* Print the PR URL at the end
* Save the same content to docs/prs/<milestone_name>.md