# .claude/commands/commit.md

Read .claude/CLAUDE.md first.

Prepare a git commit for milestone: $ARGUMENTS

Steps:

1. inspect git diff
2. summarize implemented changes
3. generate a concise professional commit message
4. stage relevant files — always include:
   - all implementation files
   - docs/prs/<milestone>.md
   - docs/reviews/<milestone>_review.md (if exists)
   - tasks/done.md, tasks/in_progress.md, tasks/todo.md
5. create git commit

Commit style:

* concise
* professional
* lower-case
* focused on milestone outcome

Also generate:

* short PR summary
* list of completed tasks
* major technical decisions

Save PR summary into:
docs/prs/$ARGUMENTS.md

PR summary should include:

1. what was implemented
2. technical highlights
3. testing performed
4. remaining work if any
