- ALWAYS USE PARALLEL TASKS SUBAGENTS FOR CODE EXPLORATION, INVESTIGATION, DEEP DIVES
- Use all tools available to keep current context window as small as possible
- When reading files, DELEGATE to subagents, if possible
- In plan mode, be bias to delegate to subagents
- Use question tool more frequently
- ALWAYS FOLLOW TDD, red phase to green phase

## Tools

- Use bun, bunx over node, npm, yarn
- Use ripgrep instead of grep, use fd instead of find
- For jira use acli CLI

## Plan Mode

In plan mode:

- output class / struct names, methods, or functions names only.
- DO NOT output entire code of the method / function
- The idea is to don't overwhelm the plan reviewer
- When changing existing function, output sudo code
- It's okay to output json / yaml etc which are response

## Usage of question tool

Before any kind of implementation, interview me in detail using the question tool.

Ask about technical implementation, UI/UX, edge cases, concerns, and tradeoffs.
Don't ask obvious questions, dig into the hard parts I might not have considered.

Keep interviewing until we've covered everything.

## Commit Instructions

- DO NOT include SPEC*.md files in commits

## Tests

- Test actual behavior, not the implementation
- Only test implementation when there is a technical limit to simulating the behavior
