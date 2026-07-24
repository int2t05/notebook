import { fileURLToPath } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';
import dotenv from 'dotenv';
import yaml from 'js-yaml';
import ignore from 'ignore';
import type { KeyFile, ProjectId } from './types.ts';

export { PROJECT_IDS } from './types.ts';

dotenv.config();

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/** 三个项目所在父目录（默认 D:/Project/Work） */
export const OMNI_ROOT = process.env.OMNI_ROOT
  ? path.resolve(process.env.OMNI_ROOT)
  : path.resolve(__dirname, '../../..');

export const PROJECT_ROOTS: Record<ProjectId, string> = {
  OmniAdaptor: path.join(OMNI_ROOT, 'OmniAdaptor'),
  OmniStream: path.join(OMNI_ROOT, 'OmniStream'),
  OmniOperator: path.join(OMNI_ROOT, 'OmniOperator'),
};

export const PROJECT_META: Record<ProjectId, { name: string; desc: string; color: string }> = {
  OmniAdaptor: {
    name: 'OmniAdaptor',
    desc: 'Flink/Spark 与 native 库的桥接层：计划翻译、决策下沉、JNI',
    color: '#3b82f6',
  },
  OmniStream: {
    name: 'OmniStream',
    desc: 'Flink Native 运行时（libtnel.so）：translate、runtime 调度、算子',
    color: '#10b981',
  },
  OmniOperator: {
    name: 'OmniOperator',
    desc: 'Native 算子/表达式加速库：算子执行 + 向量化表达式（OmniVec）',
    color: '#f59e0b',
  },
};

/** 缓存与产物目录 */
export const INDEX_DIR = path.resolve(__dirname, '../../.index');
export const CACHE_DIR = path.join(INDEX_DIR, 'cache');
export const MANIFEST_PATH = path.join(INDEX_DIR, 'manifest.json');
export const TREE_PATH = path.join(INDEX_DIR, 'tree.json');
export const DATA_OUT = path.resolve(__dirname, '../../web/src/data.json');
export const KEY_FILES_PATH = path.resolve(__dirname, '../../key-files.yaml');
export const INDEXIGNORE_PATH = path.resolve(__dirname, '../../.indexignore');

/** 读取 .indexignore（gitignore 语义），返回 ignore 实例 */
export function loadIgnore() {
  const ig = ignore();
  if (fs.existsSync(INDEXIGNORE_PATH)) {
    ig.add(fs.readFileSync(INDEXIGNORE_PATH, 'utf8'));
  }
  return ig;
}

/** 忽略的目录名（任意层） */
export const IGNORE_DIRS = new Set([
  '.git', '.idea', '.vscode', '.cache', '.gradle', '.mvn',
  'node_modules', 'target', 'build', 'dist', 'out',
  'third_party', 'thirdparty', '__pycache__',
  'figures', 'public_sys-resources', 'resources',
  'secDTFuzz',
]);

/** 二进制/资源后缀（不送 LLM，按扩展名给默认作用） */
export const BINARY_EXTS = new Set([
  '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg',
  '.pdf', '.zip', '.tar', '.gz', '.tgz', '.7z', '.jar', '.war',
  '.class', '.so', '.o', '.a', '.dll', '.exe', '.dylib',
  '.dat', '.bin', '.wasm', '.mp4', '.mp3', '.woff', '.woff2', '.ttf',
]);

/** 送 LLM 提炼的文本源码后缀 */
export const SOURCE_EXTS = new Set([
  '.java', '.scala', '.kt', '.cpp', '.cc', '.c', '.h', '.hpp', '.hh', '.hxx', '.cxx',
  '.py', '.ts', '.tsx', '.js', '.jsx', '.mjs',
  '.md', '.yaml', '.yml', '.xml', '.json', '.sh', '.bash', '.cmake',
  '.sql', '.txt', '.proto', '.config', '.properties', '.in', '.cfg', '.ini', '.toml',
  '.gradle', '.groovy', '.md.tmpl',
]);

/** 内容哈希上限；超过则用 size+mtime 伪哈希（避免读巨型文件） */
export const MAX_HASH_SIZE = 1_000_000;
/** 送 LLM 的内容截断上限（字符）——重点文件用全量 */
export const MAX_CONTENT_CHARS = 30_000;
/** 普通文件用更小截断（提炼作用/实体不需要全文，且 GLM 单 key 串行，小内容更快） */
export const MAX_BULK_CONTENT_CHARS = 8_000;

/** LLM 配置 */
export const LLM = {
  apiKey: process.env.ZHIPU_API_KEY || '',
  baseURL: process.env.ZHIPU_BASE_URL || 'https://open.bigmodel.cn/api/paas/v4',
  bulkModel: process.env.BULK_MODEL || 'glm-4-flash',
  keyModel: process.env.KEY_MODEL || 'glm-4-plus',
  concurrency: Number(process.env.CONCURRENCY || 5),
};

/** 语言推断 */
export function langOf(filePath: string): string {
  const ext = path.extname(filePath).toLowerCase();
  const map: Record<string, string> = {
    '.java': 'java', '.scala': 'scala', '.kt': 'kotlin',
    '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp', '.c': 'c',
    '.h': 'cpp', '.hpp': 'cpp', '.hh': 'cpp', '.hxx': 'cpp',
    '.py': 'python', '.ts': 'typescript', '.tsx': 'tsx',
    '.js': 'javascript', '.jsx': 'jsx', '.mjs': 'javascript',
    '.md': 'markdown', '.yaml': 'yaml', '.yml': 'yaml',
    '.xml': 'xml', '.json': 'json', '.sh': 'shell', '.bash': 'shell',
    '.cmake': 'cmake', '.sql': 'sql', '.txt': 'text',
    '.proto': 'proto', '.config': 'config', '.properties': 'properties',
    '.in': 'template', '.cfg': 'config', '.ini': 'config', '.toml': 'toml',
    '.gradle': 'groovy', '.groovy': 'groovy',
  };
  const v = map[ext];
  return v ?? (ext.replace('.', '') || 'unknown');
}

export function isBinary(filePath: string): boolean {
  return BINARY_EXTS.has(path.extname(filePath).toLowerCase());
}

export function isSource(filePath: string): boolean {
  return SOURCE_EXTS.has(path.extname(filePath).toLowerCase());
}

/** 读取 key-files.yaml */
export function loadKeyFiles(): Map<string, KeyFile> {
  const m = new Map<string, KeyFile>();
  if (!fs.existsSync(KEY_FILES_PATH)) return m;
  const doc = yaml.load(fs.readFileSync(KEY_FILES_PATH, 'utf8')) as
    | { files?: KeyFile[] }
    | undefined;
  for (const f of doc?.files ?? []) {
    m.set(`${f.project}:${f.path}`, f);
  }
  return m;
}

export function docKey(project: ProjectId, p: string): string {
  return `${project}:${p}`;
}
