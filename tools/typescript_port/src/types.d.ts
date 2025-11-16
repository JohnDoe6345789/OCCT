declare module "@openai/codex" {
  export interface CodexOptions {
    apiKey?: string;
    baseURL?: string;
    timeout?: number;
  }

  export interface CodexPromptsResource {
    create(request: { prompt: string }): Promise<Record<string, unknown>>;
  }

  export default class Codex {
    constructor(options?: CodexOptions);
    prompts: CodexPromptsResource;
  }
}
