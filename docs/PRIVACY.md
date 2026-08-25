# AXIOM Private Alpha Privacy Policy & Data Handling

## 1. What We Store
- **Account Metadata**: Email address and alpha access status.
- **Research Artifacts**: User-created research mission titles, goals, uploaded PDF chunks, and generated formal Lean 4 scripts.
- **Telemetry & Logs**: Request IDs, session durations, tool invocation counts, model routing metadata, and user feedback ratings.

## 2. What We NEVER Store
- **Plaintext Passwords**: Passwords are hashed via bcrypt.
- **Provider Secrets**: API keys are isolated in backend environment variables and redacted from logs.
- **Unsanitized Telemetry**: Sensitive code inputs are sanitized before logging.

## 3. Data Retention & Deletion
- **Retention**: Telemetry and research artifacts are retained for the duration of the Private Alpha program.
- **Deletion Requests**: Users may submit a data deletion request to `privacy@axiom-research.org`. All associated project tables and database rows will be purged within 48 hours.
