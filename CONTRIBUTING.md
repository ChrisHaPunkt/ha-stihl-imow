Contributing

Guidelines:
- Use feature branches and open PRs against `main`.
- Do not add real credentials to PRs, issues, or examples.
- Use Home Assistant's UI config flow for credentials; do not store passwords in YAML.

Testing
- We recommend running hassfest in CI and local pytest for unit tests.
- For integration tests, provide local secrets via Home Assistant secrets or environment variables.