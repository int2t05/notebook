import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {
  PROJECT_ROOTS,
  PROJECT_IDS,
  IGNORE_DIRS,
  MAX_HASH_SIZE,
  INDEX_DIR,
  MANIFEST_PATH,
  TREE_PATH,
  langOf,
  loadKeyFiles,
  loadIgnore,
  docKey,
} from './config.ts';
import type { Manifest, ManifestEntry, ProjectId, KeyFile } from './types.ts';

/** 扫描阶段内部树节点（带 hash，供 build-data 查缓存） */
export interface ScanNode {
  type: 'dir' | 'file';
  name: string;
  path: string; // 相对项目根，正斜杠；项目根节点为 ''
  project: ProjectId;
  lang?: string;
  size?: number;
  hash?: string;
  mtime?: number;
  isKey?: boolean;
  isNew?: boolean;
  children?: ScanNode[];
}

function hashFile(full: string, size: number): string {
  if (size > MAX_HASH_SIZE) {
    return `pseudo:${size}`;
  }
  try {
    const buf = fs.readFileSync(full);
    return crypto.createHash('sha256').update(buf).digest('hex').slice(0, 24);
  } catch {
    return `pseudo:${size}`;
  }
}

function walk(project: ProjectId, absDir: string, relDir: string, ig: ReturnType<typeof loadIgnore>): ScanNode[] {
  let entries: fs.Dirent[];
  try {
    entries = fs.readdirSync(absDir, { withFileTypes: true });
  } catch {
    return [];
  }
  const nodes: ScanNode[] = [];
  for (const e of entries) {
    if (e.isDirectory()) {
      if (IGNORE_DIRS.has(e.name)) continue;
      const rel = relDir ? `${relDir}/${e.name}` : e.name;
      if (ig.ignores(rel)) continue;
      const children = walk(project, path.join(absDir, e.name), rel, ig);
      if (children.length) {
        nodes.push({ type: 'dir', name: e.name, path: rel, project, children });
      }
    } else if (e.isFile()) {
      const rel = relDir ? `${relDir}/${e.name}` : e.name;
      if (ig.ignores(rel)) continue;
      const full = path.join(absDir, e.name);
      const st = fs.statSync(full);
      nodes.push({
        type: 'file',
        name: e.name,
        path: rel,
        project,
        lang: langOf(e.name),
        size: st.size,
        hash: hashFile(full, st.size),
        mtime: st.mtimeMs,
      });
    }
  }
  nodes.sort((a, b) =>
    a.type !== b.type ? (a.type === 'dir' ? -1 : 1) : a.name.localeCompare(b.name),
  );
  return nodes;
}

/** 在树上标注 isKey / isNew */
function annotate(tree: ScanNode[], oldHashByKey: Map<string, string>, keySet: Map<string, KeyFile>): void {
  for (const n of tree) {
    if (n.type === 'file') {
      const k = docKey(n.project, n.path);
      n.isKey = keySet.has(k);
      const old = oldHashByKey.get(k);
      n.isNew = old !== n.hash; // 新增或内容变更
    } else if (n.children) {
      annotate(n.children, oldHashByKey, keySet);
    }
  }
}

function flatten(tree: ScanNode[], oldHashByKey: Map<string, string>, out: Record<string, ManifestEntry>): void {
  for (const n of tree) {
    if (n.type === 'file') {
      const k = docKey(n.project, n.path);
      const old = oldHashByKey.get(k);
      const status: ManifestEntry['status'] = !old ? 'new' : old !== n.hash ? 'changed' : 'unchanged';
      out[k] = {
        project: n.project,
        path: n.path,
        hash: n.hash!,
        size: n.size!,
        mtime: n.mtime!,
        lang: n.lang!,
        status,
      };
    } else if (n.children) {
      flatten(n.children, oldHashByKey, out);
    }
  }
}

function loadOldManifest(): Map<string, string> {
  const m = new Map<string, string>();
  if (!fs.existsSync(MANIFEST_PATH)) return m;
  try {
    const old = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8')) as Manifest;
    for (const [k, e] of Object.entries(old.files)) m.set(k, e.hash);
  } catch {
    /* ignore */
  }
  return m;
}

async function main() {
  fs.mkdirSync(INDEX_DIR, { recursive: true });
  const oldHashByKey = loadOldManifest();
  const keySet = loadKeyFiles();
  const ig = loadIgnore();

  const tree: ScanNode[] = [];
  const files: Record<string, ManifestEntry> = {};

  for (const id of PROJECT_IDS) {
    const root = PROJECT_ROOTS[id];
    if (!fs.existsSync(root)) {
      console.warn(`[skip] 项目目录不存在: ${root}`);
      continue;
    }
    const children = walk(id, root, '', ig);
    annotate(children, oldHashByKey, keySet);
    flatten(children, oldHashByKey, files);
    tree.push({
      type: 'dir',
      name: id,
      path: '',
      project: id,
      children,
    });
  }

  const manifest: Manifest = { generatedAt: new Date().toISOString(), files };
  fs.writeFileSync(MANIFEST_PATH, JSON.stringify(manifest, null, 0));
  fs.writeFileSync(TREE_PATH, JSON.stringify(tree, null, 0));

  const stats = { new: 0, changed: 0, unchanged: 0, total: 0, key: 0 };
  for (const e of Object.values(files)) {
    stats.total++;
    stats[e.status === 'new' ? 'new' : e.status === 'changed' ? 'changed' : 'unchanged']++;
    if (keySet.has(docKey(e.project, e.path))) stats.key++;
  }
  console.log(
    `[scan] 总文件 ${stats.total} | 新增 ${stats.new} | 变更 ${stats.changed} | 未变 ${stats.unchanged} | 重点 ${stats.key}`,
  );
  console.log(`[scan] manifest → ${MANIFEST_PATH}`);
  console.log(`[scan] tree     → ${TREE_PATH}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
