## Data Handling and Sensitive Information

When exploring a codebase and generating specification files, follow these data handling rules:

### Secrets and Credentials
- **Never include actual secrets in specs.** If you encounter API keys, passwords, tokens, connection strings, private keys, or credentials during codebase exploration, use placeholder references in all generated spec files (e.g., `$DATABASE_URL`, `process.env.API_KEY`, `<REDACTED>`).
- **No credentials in commit messages.** If `autoCommit` is true, commit messages must never reference secrets, tokens, or credentials.

### Personal Data (PII)
- **Use synthetic data in specs.** If user data examples are needed (e.g., for API design or data model documentation), use clearly fake data (e.g., `jane.doe@example.com`, `123 Example Street`). Never copy real user data from the codebase into spec files.

### Spec Metadata
- **No personal emails in spec.json.** The `author` and `reviewers` fields use `name` only (from `git config user.name`). Do not populate `email` fields with personal email addresses.
- **No absolute paths.** Never commit files containing absolute filesystem paths (e.g., `/Users/...`, `/home/...`). Use relative paths for symlinks and file references.

### Data Classification
- When generating `design.md` security considerations, identify data classification levels for any data the feature handles:
  - **Public**: No access restrictions
  - **Internal**: Organization-internal only
  - **Confidential**: Restricted access, requires authorization
  - **Restricted**: Highest sensitivity (PII, financial, health data)

### Spec Sensitivity
- If a `design.md` contains security-related architecture (authentication flows, encryption strategies, access control designs), include a notice at the top: `<!-- This spec contains security-sensitive architectural details. Review access before sharing. -->`
