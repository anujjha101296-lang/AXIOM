# Security Profile

- **Sandbox**: Code execution is sandboxed using AST inspection (`CodeSafetyValidator`) and `resource` limits.
- **Database**: All SQL uses parameterized queries to prevent SQL Injection.
- **API**: Endpoints are protected via token-based auth (`VerifyToken`).
- **Isolation**: Tenant isolation is strictly enforced via `project_id` matching on queries.

**Vulnerabilities**: None critical. Sandbox escape is theoretically possible if the host Python interpreter has known vulnerabilities.
