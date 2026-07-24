import fs from 'node:fs';
import path from 'node:path';
import pLimit from 'p-limit';
import {
  MANIFEST_PATH,
  CACHE_DIR,
  PROJECT_ROOTS,
  LLM,
  MAX_CONTENT_CHARS,
  MAX_BULK_CONTENT_CHARS,
  isSource,
  isBinary,
  loadKeyFiles,
  docKey,
} from './config.ts';
import { extractBulk, extractKey, readSnippet } from './llm.ts';
import type { Manifest, ManifestEntry, CachedDoc } from './types.ts';

function cachePath(hash: string): string {
  return path.join(CACHE_DIR, `${hash}.json`);
}

function cached(hash: string): boolean {
  return fs.existsSync(cachePath(hash));
}

async function processOne(entry: ManifestEntry, keyStage?: string): Promise<void> {
  const full = path.join(PROJECT_ROOTS[entry.project], entry.path);
  const out: CachedDoc = {
    hash: entry.hash,
    project: entry.project,
    path: entry.path,
    lang: entry.lang,
    isKey: !!keyStage,
    purpose: '',
    entities: {},
    stage: keyStage,
  };
  try {
    const content = readSnippet(full, entry.size, keyStage ? MAX_CONTENT_CHARS : MAX_BULK_CONTENT_CHARS);
    if (keyStage) {
      const r = await extractKey({
        project: entry.project,
        path: entry.path,
        lang: entry.lang,
        content,
        stage: keyStage,
      });
      out.purpose = r.purpose;
      out.entities = r.entities;
      out.mermaid = r.mermaid;
      out.prose = r.prose;
      out.model = LLM.keyModel;
    } else {
      const r = await extractBulk({
        project: entry.project,
        path: entry.path,
        lang: entry.lang,
        content,
      });
      out.purpose = r.purpose;
      out.entities = r.entities;
      out.model = LLM.bulkModel;
    }
  } catch (err: any) {
    out.purpose = `（提炼失败：${String(err?.message ?? err).slice(0, 120)}）`;
    out.entities = {};
    console.error(`[err] ${docKey(entry.project, entry.path)} → ${err?.message ?? err}`);
  }
  fs.writeFileSync(cachePath(entry.hash), JSON.stringify(out));
}

async function main() {
  const args = process.argv.slice(2);
  const limitIdx = args.indexOf('--limit');
  const limit = limitIdx >= 0 ? Number(args[limitIdx + 1]) || 0 : 0;
  const keyOnly = args.includes('--key-only');

  if (!LLM.apiKey) {
    console.error('未配置 ZHIPU_API_KEY。请复制 .env.example 为 .env 并填入 key 后重跑。');
    process.exit(1);
  }

  fs.mkdirSync(CACHE_DIR, { recursive: true });
  if (!fs.existsSync(MANIFEST_PATH)) {
    console.error('未找到 manifest，请先运行 npm run scan');
    process.exit(1);
  }
  const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8')) as Manifest;
  const keySet = loadKeyFiles();

  // 待处理：源码文件 + 未缓存
  const pending: { entry: ManifestEntry; stage?: string }[] = [];
  let skippedCached = 0;
  let skippedNonSource = 0;
  for (const entry of Object.values(manifest.files)) {
    if (!isSource(entry.path) || isBinary(entry.path)) {
      skippedNonSource++;
      continue;
    }
    const kf = keySet.get(docKey(entry.project, entry.path));
    if (keyOnly && !kf) continue;
    if (cached(entry.hash)) {
      skippedCached++;
      continue;
    }
    pending.push({ entry, stage: kf?.stage });
  }

  console.log(
    `[extract] 待提炼 ${pending.length} | 已缓存跳过 ${skippedCached} | 非源码跳过 ${skippedNonSource} | 并发 ${LLM.concurrency}`,
  );
  if (pending.length === 0) {
    console.log('[extract] 无需处理，全部已缓存。');
    return;
  }

  const todo = limit > 0 ? pending.slice(0, limit) : pending;
  const limitFn = pLimit(LLM.concurrency);
  let done = 0;
  const start = Date.now();
  let lastReport = 0;

  await Promise.all(
    todo.map(({ entry, stage }) =>
      limitFn(async () => {
        await processOne(entry, stage);
        done++;
        if (done - lastReport >= 5 || done === todo.length) {
          lastReport = done;
          const elapsed = ((Date.now() - start) / 1000).toFixed(0);
          console.log(`[extract] ${done}/${todo.length} (${elapsed}s)`);
        }
      }),
    ),
  );
  console.log(`[extract] 完成 ${done} 个。`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
