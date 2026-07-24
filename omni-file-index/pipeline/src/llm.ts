import OpenAI from 'openai';
import { LLM, MAX_CONTENT_CHARS } from './config.ts';
import type { CachedDoc, Entity, ProjectId } from './types.ts';

let _client: OpenAI | null = null;
function client(): OpenAI {
  if (!_client) {
    if (!LLM.apiKey) {
      throw new Error(
        '未配置 ZHIPU_API_KEY。请复制 .env.example 为 .env 并填入智谱 API key。',
      );
    }
    _client = new OpenAI({ apiKey: LLM.apiKey, baseURL: LLM.baseURL });
  }
  return _client;
}

/** 读文件并截断：头部 + 尾部，控制 token */
export function readSnippet(fullPath: string, size: number, max = MAX_CONTENT_CHARS): string {
  if (size > max * 4) {
    // 大文件：头 + 尾
    const fd = fs.openSync(fullPath, 'r');
    try {
      const head = Buffer.alloc(max);
      fs.readSync(fd, head, 0, max, 0);
      const tail = Buffer.alloc(8192);
      fs.readSync(fd, tail, 0, 8192, Math.max(0, size - 8192));
      return head.toString('utf8') + '\n\n/* ... [中间内容已省略] ... */\n\n' + tail.toString('utf8');
    } finally {
      fs.closeSync(fd);
    }
  }
  return fs.readFileSync(fullPath, 'utf8').slice(0, max);
}

import fs from 'node:fs';

const BULK_SYSTEM = `你是代码索引助手。用户给你一个源文件，你提炼它的"作用"和"内部实体"。
要求：
- 通俗易懂，少而精。
- purpose：1-2 句话说明这个文件在整个项目里的作用（中文）。
- entities：列出该文件里的关键实体，分四组：functions(函数/自由函数)、classes(类/结构/接口/枚举)、methods(类方法，可与 classes 合并)、objects(常量/全局对象/宏/重要变量)。每条给 name 与一行 role。每组最多 15 条，按重要性排序，省略琐碎的 getter/setter。
- 只返回 JSON，不要解释。`;

const BULK_SCHEMA = `{
  "purpose": "string",
  "entities": {
    "functions": [{"name":"string","role":"string"}],
    "classes": [{"name":"string","role":"string"}],
    "methods": [{"name":"string","role":"string"}],
    "objects": [{"name":"string","role":"string"}]
  }
}`;

const KEY_SYSTEM = `你是代码索引助手，专注"SQL 执行端到端"业务流程讲解。用户给你一个位于该链路上的重点源文件。
要求：
- 通俗易懂，多图少字。
- purpose：1-2 句话说明该文件在 SQL 执行链路中的作用（中文）。
- entities：同普通文件（四组，每组最多 15 条）。
- mermaid：用 mermaid 语法画 **一张** 最能体现该文件在 SQL 执行中角色的图（流程图 flowchart 或时序图 sequenceDiagram）。聚焦本文件的输入→处理→输出，节点用中文短标签，避免长文本。只输出 mermaid 代码本身，不要 \`\`\`mermaid 围栏。
- prose：2-3 句通俗说明，呼应图，点明"SQL 数据怎么流经这个文件"。
- 只返回 JSON，不要解释。`;

const KEY_SCHEMA = `{
  "purpose": "string",
  "entities": {
    "functions": [{"name":"string","role":"string"}],
    "classes": [{"name":"string","role":"string"}],
    "methods": [{"name":"string","role":"string"}],
    "objects": [{"name":"string","role":"string"}]
  },
  "mermaid": "string (mermaid 语法)",
  "prose": "string"
}`;

interface RawEntities {
  functions?: Entity[];
  classes?: Entity[];
  methods?: Entity[];
  objects?: Entity[];
}

function parseJson(text: string): any {
  try {
    return JSON.parse(text);
  } catch {
    const m = text.match(/\{[\s\S]*\}/);
    if (m) {
      try {
        return JSON.parse(m[0]);
      } catch {
        /* fallthrough */
      }
    }
    throw new Error('LLM 返回非 JSON');
  }
}

function capEntities(e: RawEntities): RawEntities {
  // 兼容 LLM 返回字符串数组或异名键（func/desc 等）
  const cap = (arr?: any[]): Entity[] =>
    (arr ?? []).slice(0, 15).map((x) => {
      if (typeof x === 'string') return { name: x.slice(0, 120), role: '' };
      const name = String(x?.name ?? x?.func ?? x?.method ?? x?.cls ?? x?.obj ?? x?.field ?? '').slice(0, 120);
      const role = String(x?.role ?? x?.desc ?? x?.description ?? x?.comment ?? '').slice(0, 200);
      const sig = x?.signature ? String(x.signature).slice(0, 200) : undefined;
      return sig ? { name, role, signature: sig } : { name, role };
    });
  return {
    functions: cap(e.functions),
    classes: cap(e.classes),
    methods: cap(e.methods),
    objects: cap(e.objects),
  };
}

async function call(model: string, system: string, schema: string, user: string): Promise<any> {
  const c = client();
  let lastErr: unknown;
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const resp = await c.chat.completions.create({
        model,
        messages: [
          { role: 'system', content: system },
          {
            role: 'user',
            content: `${user}\n\n返回符合如下结构的 JSON：\n${schema}`,
          },
        ],
        temperature: 0.2,
        response_format: { type: 'json_object' },
      });
      const text = resp.choices[0]?.message?.content ?? '';
      return parseJson(text);
    } catch (err) {
      lastErr = err;
      const wait = 800 * Math.pow(2, attempt);
      await new Promise((r) => setTimeout(r, wait));
    }
  }
  throw lastErr;
}

export async function extractBulk(args: {
  project: ProjectId;
  path: string;
  lang: string;
  content: string;
}): Promise<Pick<CachedDoc, 'purpose' | 'entities'>> {
  const user = `项目：${args.project}\n相对路径：${args.path}\n语言：${args.lang}\n\n源文件内容：\n${args.content}`;
  const raw = await call(LLM.bulkModel, BULK_SYSTEM, BULK_SCHEMA, user);
  return {
    purpose: String(raw.purpose ?? '').slice(0, 400),
    entities: capEntities(raw.entities ?? {}),
  };
}

export async function extractKey(args: {
  project: ProjectId;
  path: string;
  lang: string;
  content: string;
  stage: string;
}): Promise<Pick<CachedDoc, 'purpose' | 'entities' | 'mermaid' | 'prose'>> {
  const user = `项目：${args.project}\n相对路径：${args.path}\n语言：${args.lang}\nSQL 执行链路环节：${args.stage}\n\n源文件内容：\n${args.content}`;
  const raw = await call(LLM.keyModel, KEY_SYSTEM, KEY_SCHEMA, user);
  return {
    purpose: String(raw.purpose ?? '').slice(0, 400),
    entities: capEntities(raw.entities ?? {}),
    mermaid: String(raw.mermaid ?? '').slice(0, 4000),
    prose: String(raw.prose ?? '').slice(0, 600),
  };
}
