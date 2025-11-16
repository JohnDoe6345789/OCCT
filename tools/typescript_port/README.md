# Codex automation CLI (TypeScript)

This package rewrites the Codex automation helper in TypeScript using Node 18+
primitives.  It mirrors the workflow used in Codex prompts:

1. Run the "Continue with python port until feature parity" prompt.
2. Capture the current git diff and status in a pseudo pull-request payload.
3. Approve the pull request locally to simulate the Codex auto-approval loop.
4. Run the prompt a second time so the workflow matches the Codex UX.

Each step calls the public <https://chatgpt.com/codex> automation endpoint so the
logs reflect the real Codex behaviour.  The CLI relies on the TypeScript SDK
documented at <https://developers.openai.com/codex/sdk#typescript-library> to
communicate with the Codex service.

## Installation

```bash
cd tools/typescript_port
npm install
```

The project keeps runtime dependencies to zero so `npm install` only downloads
TypeScript + Node type definitions required for compilation.

## Configuration

Export your Codex API key before running the CLI:

```bash
export CODEX_API_KEY="sk-..."
```

The CLI defaults to `https://chatgpt.com/codex/api/prompt`, but you can override
the endpoint with `--codex-endpoint` to target a mock server when testing.

## Usage

Build the CLI and invoke it with the default prompt:

```bash
npm run build
node dist/codex_cli.js
```

Preview the workflow without hitting the filesystem or Codex API:

```bash
node dist/codex_cli.js --dry-run
```

Pass a custom prompt, log location, PR payload location, or Codex endpoint when
needed:

```bash
node dist/codex_cli.js \
  --prompt "Translate Quantity_Time into Python" \
  --log-path /tmp/codex_log.jsonl \
  --pr-path /tmp/codex_pr.json \
  --codex-endpoint https://chatgpt.com/codex/api/prompt
```

The CLI prints structured JSON describing the steps it executed.  Prompt logs
accumulate in `codex_prompts.jsonl` and the pull-request payload lives in
`codex_pull_request.json` by default.
