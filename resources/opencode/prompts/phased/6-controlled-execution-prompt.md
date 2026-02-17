We are executing the migration controller in dry-run mode.

If any validation fails:
- Stop immediately.
- Report the failing file.
- Do not modify tests.
- Do not bypass validation.

After dry-run success, execute full migration.

At completion:
- Generate diff summary.
- List any behavior changes detected.
