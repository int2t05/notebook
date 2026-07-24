export type ProjectId = 'OmniAdaptor' | 'OmniStream' | 'OmniOperator';

export interface ProjectMeta {
  id: ProjectId;
  name: string;
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

export interface Entity {
  name: string;
  role: string;
  signature?: string;
}

export interface FileDoc {
  project: ProjectId;
  path: string;
  purpose: string;
  lang: string;
  isKey: boolean;
  size?: number;
  stage?: string;
  entities: {
    functions?: Entity[];
    classes?: Entity[];
    methods?: Entity[];
    objects?: Entity[];
  };
  mermaid: string;
  mermaidKind: 'llm' | 'auto' | 'none';
  prose?: string;
  related?: string[];
  referencedBy?: string[];
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
  name: string;
  path: string;
  purpose: string;
  fileCount: number;
  children: FolderChild[];
}

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
  docs: Record<string, FileDoc>;
  folders: Record<string, FolderDoc>;
  keyTour: KeyTourItem[];
  overview: { mermaid: string; prose: string };
}
