# Runner Adapters

A Runner Adapter maps the portable contract to a specific runtime without changing the contract's intent.

## Rules

- Keep the portable sections intact.
- Add runtime-specific launch syntax only after validation.
- Do not hide local assumptions in the adapter.
- Do not broaden scope to satisfy a runner's preferred workflow.
- Keep private runner paths out of public package defaults.

## Examples

- Codex slash-command adapter
- Claude Code task adapter
- GitHub issue adapter
- CI job adapter
- private local Codex runner adapter

The public default is generic. Private/local Codex behavior is optional and belongs in a local adapter file outside this public package.
