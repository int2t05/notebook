// 共享类型：管线内部 + data.json 契约

export type ProjectId = 'OmniAdaptor' | 'OmniStream' | 'OmniOperator';

export const PROJECT_IDS: ProjectId[] = ['OmniAdaptor', 'OmniStream', 'OmniOperator'];

/** 扫描清单中的一条文件记录 */
export interface ManifestEntry {
  project: ProjectId;
  /** 相对项目根的路径，正斜杠，如 "cpp/runtime/Runtime.h" */
  path: string;
  /** 内容 sha256（大文件用 size+mtime 伪哈希） */
  hash: string;
  size: number;
  mtime: number;
  lang: string;
  /** 本轮扫描相对上次的状态 */
  status: 'new' | 'changed' | 'unchanged' | 'deleted';
}

export interface Manifest {
  generatedAt: string;
  files: Record<string, ManifestEntry>; // key = `${project}:${path}`
}

/** LLM 提炼结果（按内容哈希缓存） */
export interface CachedDoc {
  hash: string;
  project: ProjectId;
  path: string;
  lang: string;
  isKey: boolean;
  purpose: string;
  entities: {
    functions?: Entity[];
    classes?: Entity[];
    methods?: Entity[];
    objects?: Entity[];
  };
  /** 重点文件由 LLM 产出；普通文件为空（build-data 机械生成） */
  mermaid?: string;
  prose?: string;
  stage?: string;
  model?: string;
}

export interface Entity {
  name: string;
  role: string;
  signature?: string;
}

/** key-files.yaml 的一条 */
export interface KeyFile {
  project: ProjectId;
  path: string;
  stage: string;
}

// ===== data.json 契约（前端消费） =====

export interface ProjectMeta {
  id: ProjectId;
  name: string;
  root: string;
  desc: string;
  color: string;
}

export interface TreeNode {
  type: 'dir' | 'file';
  name: string;
  path: string;
  project: ProjectId;
  lang?: string;
  size?: number;
  isKey?: boolean;
  isNew?: boolean;
  children?: TreeNode[];
}

export interface FileDoc {
  project: ProjectId;
  path: string;
  purpose: string;
  lang: string;
  isKey: boolean;
  size?: number;
  stage?: string;
  entities: CachedDoc['entities'];
  mermaid: string;
  mermaidKind: 'llm' | 'auto' | 'none';
  prose?: string;
  related?: string[]; // 相关文件 doc key
  referencedBy?: string[]; // 被哪些文件引用（related 的反向）
}

export interface FolderChild {
  type: 'file' | 'dir';
  name: string;
  key: string;
  purpose?: string;
  fileCount?: number;
  isKey?: boolean;
}

export interface FolderDoc {
  project: ProjectId;
  /** 目录自身名（项目根为项目 id） */
  name: string;
  path: string;
  purpose: string;
  fileCount: number;
  children: FolderChild[];
}

/** 概览页 SQL 链路导览条目 */
export interface KeyTourItem {
  group: string;
  stage: string;
  key: string;
  name: string;
  purpose: string;
  project: ProjectId;
}

export interface DataPackage {
  generatedAt: string;
  projects: ProjectMeta[];
  tree: TreeNode[];
  docs: Record<string, FileDoc>; // key = `${project}:${path}`
  folders: Record<string, FolderDoc>; // key = `${project}:${path}`（目录）
  keyTour: KeyTourItem[]; // 重点文件按 SQL 链路环节排序
  overview: { mermaid: string; prose: string };
}
