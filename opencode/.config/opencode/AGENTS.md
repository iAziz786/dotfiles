- ALWAYS USE PARALLEL TASKS SUBAGENTS FOR CODE EXPLORATION, INVESTIGATION, DEEP DIVES
- Use all tools available to keep current context window as small as possible
- When reading files, DELEGATE to subagents, if possible
- In plan mode, be bias to delegate to subagents
- Use question tool more frequently
- ALWAYS FOLLOW TDD, red phase to green phase
- Use ripgrep instead of grep, use fd instead of find

## Usage of question tool

Before any kind of implementation, interview me in detail using the question tool.

Ask about technical implementation, UI/UX, edge cases, concerns, and tradeoffs.
Don't ask obvious questions, dig into the hard parts I might not have considered.

Keep interviewing until we've covered everything.

## Tests

- Test actual behavior, not the implementation
- Only test implementation when there is a technical limit to simulating the behavior
