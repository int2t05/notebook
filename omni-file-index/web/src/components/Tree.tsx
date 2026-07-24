import { useEffect, useMemo } from 'react';
import type { TreeNode, ProjectId } from '../types.ts';

function fileIcon(name: string): string {
  const ext = name.slice(name.lastIndexOf('.') + 1).toLowerCase();
  const m: Record<string, string> = {
    cpp: 'C', cc: 'C', cxx: 'C', c: 'C', h: 'H', hpp: 'H', hh: 'H', hxx: 'H',
    java: 'J', scala: 'S', kt: 'K', py: 'P', ts: 'T', tsx: 'T', js: 'J', mjs: 'J',
    md: '☰', sql: 'Q', xml: '{}', json: '{}', yaml: '{}', yml: '{}',
    sh: '$', bash: '$', cmake: '⌬', proto: '◈', properties: '☰', config: '☰',
    toml: '☰', ini: '☰', txt: '☰', gradle: 'G', groovy: 'G', in: '☰',
  };
  return m[ext] ?? '·';
}

function nodeKey(n: TreeNode): string {
  return `${n.project}:${n.path}`;
}

function matches(node: TreeNode, q: string, matched: Set<string> | null): boolean {
  if (!q) return true;
  const k = nodeKey(node);
  if (node.type === 'file') {
    if (node.name.toLowerCase().includes(q) || node.path.toLowerCase().includes(q)) return true;
    if (matched && matched.has(k)) return true;
    return false;
  }
  return (node.children ?? []).some((c) => matches(c, q, matched));
}

function highlight(name: string, q: string): React.ReactNode {
  if (!q) return name;
  const i = name.toLowerCase().indexOf(q);
  if (i < 0) return name;
  return (
    <>
      {name.slice(0, i)}
      <mark>{name.slice(i, i + q.length)}</mark>
      {name.slice(i + q.length)}
    </>
  );
}

interface FlatEntry {
  key: string;
  isDir: boolean;
}

interface Props {
  nodes: TreeNode[];
  selected: string | null;
  onSelect: (key: string) => void;
  query: string;
  expanded: Set<string>;
  onToggle: (key: string) => void;
  matchedKeys: Set<string> | null;
}

export function Tree({ nodes, selected, onSelect, query, expanded, onToggle, matchedKeys }: Props) {
  const q = query.trim().toLowerCase();
  const visible = nodes.filter((n) => matches(n, q, matchedKeys));

  // 选中项滚入视野（方向键导航不丢选）
  useEffect(() => {
    const el = document.querySelector('.node.selected');
    el?.scrollIntoView({ block: 'nearest' });
  }, [selected]);

  // 扁平化当前可见节点（含展开的目录），供方向键导航
  const flat = useMemo<FlatEntry[]>(() => {
    const out: FlatEntry[] = [];
    const walk = (ns: TreeNode[]) => {
      for (const n of ns) {
        if (!matches(n, q, matchedKeys)) continue;
        const k = nodeKey(n);
        if (n.type === 'file') {
          out.push({ key: k, isDir: false });
        } else {
          out.push({ key: k, isDir: true });
          const open = q ? true : expanded.has(k);
          if (open && n.children) walk(n.children);
        }
      }
    };
    walk(nodes);
    return out;
  }, [nodes, q, expanded, matchedKeys]);

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (!flat.length) return;
    const idx = selected ? flat.findIndex((f) => f.key === selected) : -1;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      const n = flat[Math.min(idx + 1, flat.length - 1)];
      if (n) onSelect(n.key);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      const n = flat[Math.max(idx - 1, 0)];
      if (n && n.key !== selected) onSelect(n.key);
    } else if (e.key === 'ArrowRight') {
      const cur = idx >= 0 ? flat[idx] : null;
      if (cur?.isDir && !expanded.has(cur.key)) {
        e.preventDefault();
        onToggle(cur.key);
      }
    } else if (e.key === 'ArrowLeft') {
      const cur = idx >= 0 ? flat[idx] : null;
      if (cur?.isDir && expanded.has(cur.key)) {
        e.preventDefault();
        onToggle(cur.key);
      }
    }
  };

  if (!visible.length) return <div className="tree-empty">无匹配文件</div>;
  return (
    <div className="tree-root" tabIndex={0} onKeyDown={onKeyDown}>
      {visible.map((n) => (
        <NodeView
          key={nodeKey(n) || n.name}
          node={n}
          depth={0}
          selected={selected}
          onSelect={onSelect}
          query={q}
          expanded={expanded}
          onToggle={onToggle}
          matchedKeys={matchedKeys}
          isProject
        />
      ))}
    </div>
  );
}

function NodeView({
  node,
  depth,
  selected,
  onSelect,
  query,
  expanded,
  onToggle,
  matchedKeys,
  isProject,
}: {
  node: TreeNode;
  depth: number;
  selected: string | null;
  onSelect: (key: string) => void;
  query: string;
  expanded: Set<string>;
  onToggle: (key: string) => void;
  matchedKeys: Set<string> | null;
  isProject?: boolean;
}) {
  const key = nodeKey(node);
  if (node.type === 'file') {
    const isSel = selected === key;
    return (
      <div
        className={'node file' + (isSel ? ' selected' : '')}
        style={{ paddingLeft: 8 + depth * 14 }}
        onClick={() => onSelect(key)}
        title={node.path}
      >
        <span className="chev spacer">▸</span>
        <span className="ficon">{fileIcon(node.name)}</span>
        <span className="name">{highlight(node.name, query)}</span>
        <span className="badges">
          {node.isKey && <span className="badge key">★</span>}
        </span>
      </div>
    );
  }
  const open = query ? true : expanded.has(key);
  const visibleChildren = (node.children ?? []).filter((c) => matches(c, query, matchedKeys));
  if (query && !visibleChildren.length && !isProject) return null;
  return (
    <>
      <div
        className={'node dir' + (isProject ? ' project' : '')}
        style={{ paddingLeft: 8 + depth * 14 }}
        data-pid={isProject ? (node.name as ProjectId) : undefined}
        onClick={() => onSelect(key)}
        title="点击查看目录解析（展开/折叠请点左侧箭头）"
      >
        <span
          className={'chev' + (open ? ' open' : '')}
          onClick={(e) => {
            e.stopPropagation();
            onToggle(key);
          }}
          title="展开/折叠"
        >
          ▸
        </span>
        <span className="ficon">{isProject ? '◆' : ''}</span>
        <span className="name">{highlight(node.name, query)}</span>
      </div>
      {open &&
        visibleChildren.map((c) => (
          <NodeView
            key={nodeKey(c) || c.name}
            node={c}
            depth={depth + 1}
            selected={selected}
            onSelect={onSelect}
            query={query}
            expanded={expanded}
            onToggle={onToggle}
            matchedKeys={matchedKeys}
          />
        ))}
    </>
  );
}
