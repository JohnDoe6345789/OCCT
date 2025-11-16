import Codex from "@openai/codex";
import { spawnSync } from "node:child_process";
import { appendFile, mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { parseArgs } from "node:util";

type PromptResponse = Record<string, unknown>;

interface PromptEvent {
  prompt: string;
  timestamp: string;
  response: PromptResponse;
}

interface PullRequestRecord {
  title: string;
  branch: string;
  body: string;
  approved: boolean;
}

const CODEX_REFERENCE = "https://github.com/openai/codex?tab=readme-ov-file";
const CODEX_API_ENDPOINT = "https://chatgpt.com/codex/api/prompt";
const DEFAULT_PROMPT = `Continue with python port until feature parity using instructions from ${CODEX_REFERENCE}`;

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const REPO_ROOT = resolve(__dirname, "../../..");
const LOG_PATH = resolve(__dirname, "../codex_prompts.jsonl");
const PR_PATH = resolve(__dirname, "../codex_pull_request.json");

function runGit(...args: string[]): string {
  const result = spawnSync("git", args, {
    cwd: REPO_ROOT,
    encoding: "utf-8",
  });
  if (result.status !== 0) {
    throw new Error(result.stderr || `git ${args.join(" ")} failed`);
  }
  return result.stdout.trim();
}

class PromptLogger {
  constructor(private readonly logPath: string) {}

  async append(prompt: string, response: PromptResponse): Promise<PromptEvent> {
    await mkdir(dirname(this.logPath), { recursive: true });
    const iso = new Date().toISOString();
    const timestamp = `${iso.split(".")[0]}Z`;
    const event: PromptEvent = { prompt, timestamp, response };
    await appendFile(this.logPath, `${JSON.stringify(event)}\n`, "utf-8");
    return event;
  }
}

class CodexAPIError extends Error {
  constructor(message: string, options?: ErrorOptions) {
    super(message, options);
    this.name = "CodexAPIError";
  }
}

interface CodexClient {
  runPrompt(prompt: string): Promise<PromptResponse>;
}

class CodexAPIClient implements CodexClient {
  private readonly codex: Codex;

  constructor(options: { endpoint?: string; apiKey?: string } = {}) {
    const endpoint = options.endpoint ?? CODEX_API_ENDPOINT;
    const apiKey = options.apiKey ?? process.env.CODEX_API_KEY;
    this.codex = new Codex({
      baseURL: endpoint,
      apiKey,
    });
  }

  async runPrompt(prompt: string): Promise<PromptResponse> {
    try {
      const result = await this.codex.prompts.create({ prompt });
      return result as PromptResponse;
    } catch (error) {
      const reason = error instanceof Error ? error.message : String(error);
      throw new CodexAPIError(`Codex API request failed: ${reason}`, {
        cause: error instanceof Error ? error : undefined,
      });
    }
  }
}

class PullRequestManager {
  constructor(private readonly gitRunner: (...args: string[]) => string = runGit) {}

  private currentBranch(): string {
    return this.gitRunner("rev-parse", "--abbrev-ref", "HEAD");
  }

  private gatherDiffstat(): string {
    const diffstat = this.gitRunner("diff", "--stat");
    return diffstat || "No changes detected.";
  }

  private gatherStatus(): string {
    const status = this.gitRunner("status", "--short");
    return status || "Working tree clean.";
  }

  async create(prompt: string, dest: string): Promise<PullRequestRecord> {
    const branch = this.currentBranch();
    const diffstat = this.gatherDiffstat();
    const status = this.gatherStatus();
    const title = `codex: ${prompt}`;
    const body = [
      `Prompt: ${prompt}`,
      "",
      `Branch: ${branch}`,
      "",
      "Status:",
      status,
      "",
      "Diffstat:",
      diffstat,
      "",
      "Codex reference:",
      CODEX_REFERENCE,
    ].join("\n");
    const pr: PullRequestRecord = { title, branch, body, approved: false };
    await this.writePR(dest, pr);
    return pr;
  }

  async approve(dest: string): Promise<PullRequestRecord> {
    const pr = await this.readPR(dest);
    const updated: PullRequestRecord = { ...pr, approved: true };
    await this.writePR(dest, updated);
    return updated;
  }

  private async writePR(dest: string, pr: PullRequestRecord): Promise<void> {
    await mkdir(dirname(dest), { recursive: true });
    await writeFile(dest, `${JSON.stringify(pr, null, 2)}\n`, "utf-8");
  }

  private async readPR(dest: string): Promise<PullRequestRecord> {
    const raw = await readFile(dest, "utf-8");
    return JSON.parse(raw) as PullRequestRecord;
  }
}

interface WorkflowOptions {
  logPath: string;
  prPath: string;
  dryRun: boolean;
  codexClient?: CodexClient;
}

async function runWorkflow(
  prompt: string,
  { logPath, prPath, dryRun, codexClient }: WorkflowOptions,
): Promise<Record<string, unknown>> {
  if (dryRun) {
    return {
      prompt,
      log_path: logPath,
      pr_path: prPath,
      actions: ["run_prompt", "create_pull_request", "approve_pull_request", "run_prompt"],
    };
  }

  const logger = new PromptLogger(logPath);
  const prManager = new PullRequestManager();
  const client = codexClient ?? new CodexAPIClient();

  const firstResponse = await client.runPrompt(prompt);
  const firstEvent = await logger.append(prompt, firstResponse);
  const pr = await prManager.create(prompt, prPath);
  const approved = await prManager.approve(prPath);
  const secondResponse = await client.runPrompt(prompt);
  const secondEvent = await logger.append(prompt, secondResponse);

  return {
    first_prompt: firstEvent,
    pull_request: pr,
    approved_pull_request: approved,
    second_prompt: secondEvent,
  };
}

async function main(argv = process.argv.slice(2)): Promise<void> {
  const parser = parseArgs({
    args: argv,
    options: {
      prompt: { type: "string", default: DEFAULT_PROMPT },
      "log-path": { type: "string", default: LOG_PATH },
      "pr-path": { type: "string", default: PR_PATH },
      "dry-run": { type: "boolean", default: false },
      "codex-endpoint": { type: "string", default: CODEX_API_ENDPOINT },
    },
    allowPositionals: false,
  });

  const values = parser.values as {
    prompt: string;
    "log-path": string;
    "pr-path": string;
    "dry-run": boolean;
    "codex-endpoint": string;
  };

  const client = values["dry-run"]
    ? undefined
    : new CodexAPIClient({ endpoint: values["codex-endpoint"] });
  const result = await runWorkflow(values.prompt, {
    logPath: values["log-path"],
    prPath: values["pr-path"],
    dryRun: values["dry-run"],
    codexClient: client,
  });

  console.log(JSON.stringify(result, null, 2));
}

void main().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(message);
  if (error instanceof Error && error.stack) {
    console.error(error.stack);
  }
  process.exitCode = 1;
});
