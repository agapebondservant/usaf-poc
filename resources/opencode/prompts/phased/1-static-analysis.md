You are analyzing a Python 2 codebase for safe migration to Python 3.

Tasks:
1. Identify Python 2-specific constructs:
   - print statements
   - unicode/str mixing
   - old exception syntax
   - iteritems, itervalues
   - implicit relative imports
   - cmp usage
   - old-style classes
2. Detect dynamic patterns:
   - exec
   - eval
   - monkey patching
   - runtime attribute injection
3. List potential high-risk modules.
4. Estimate migration difficulty level (low/medium/high).
5. Recommend mechanical vs manual handling areas.

Constraints:
- Do not rewrite code.
- Do not suggest architectural redesign.
- Output structured markdown only.
