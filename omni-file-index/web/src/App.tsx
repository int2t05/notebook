import { useEffect, useMemo, useRef, useState } from 'react';
import type { FileDoc, FolderDoc, KeyTourItem, ProjectId, ProjectMeta, TreeNode } from './types.ts';
import { Tree } from './components/Tree.tsx';
import { Detail } from './components/Detail.tsx';
import { FolderDetail } from './components/FolderDetail.tsx';
import { Overview } from './components/Overview.tsx';
import { UpdateButton } from './components/UpdateButton.tsx';

interface TreeData {
  generatedAt: string;
  projects: ProjectMeta[];
  tree: TreeNode[];
  keyTour: KeyTourItem[];
  overview: { mermaid: string; prose: string };
}

const EMPTY_TREE: TreeData = {
  generatedAt: '',
  projects: [],
  tree: [],
  keyTour: [],
  overview: { mermaid: '', prose: '' },
};

// 首屏数据：tree + keyTour + overview 加载即解析
const treeData: TreeData = (() => {
  try {
    const raw = document.getElementById('app-tree')?.textContent;
    return raw ? (JSON.parse(raw) as TreeData) : EMPTY_TREE;
  } catch {
    return EMPTY_TREE;
  }
})();

// 重数据：docs（文件详情）按需解析、缓存
let docsCache: Record<string, FileDoc> | null = null;
function getDocs(): Record<string, FileDoc> {
  if (!docsCache) {
    try {
      const raw = document.getElementById('app-docs')?.textContent;
      docsCache = raw ? (JSON.parse(raw) as Record<string, FileDoc>) : {};
    } catch {
      docsCache = {};
    }
  }
  return docsCache;
}

// 目录解析：folders 按需解析、缓存（点目录才用）
let foldersCache: Record<string, FolderDoc> | null = null;
function getFolders(): Record<string, FolderDoc> {
  if (!foldersCache) {
    try {
      const raw = document.getElementById('app-folders')?.textContent;
      foldersCache = raw ? (JSON.parse(raw) as Record<string, FolderDoc>) : {};
    } catch {
      foldersCache = {};
    }
  }
  return foldersCache;
}

// 由 tree 推断每个 key 是 file 还是 folder（避免依赖懒加载的 folders）
const keyKind = new Map<string, 'file' | 'folder'>();
(() => {
  const walk = (ns: TreeNode[]) => {
    for (const n of ns) {
      keyKind.set(`${n.project}:${n.path}`, n.type === 'dir' ? 'folder' : 'file');
      if (n.children) walk(n.children);
    }
  };
  walk(treeData.tree);
})();

function safeGet(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}
function safeSet(key: string, val: string): void {
  try {
    localStorage.setItem(key, val);
  } catch {
    /* file:// 下 localStorage 可能不可用，忽略 */
  }
}

function countFiles(nodes: TreeNode[]): { files: number; keys: number } {
  let files = 0;
  let keys = 0;
  const walk = (ns: TreeNode[]) => {
    for (const n of ns) {
      if (n.type === 'file') {
        files++;
        if (n.isKey) keys++;
      } else if (n.children) walk(n.children);
    }
  };
  walk(nodes);
  return { files, keys };
}

function firstKeyByProject(nodes: TreeNode[]): Record<ProjectId, string | null> {
  const out = { OmniAdaptor: null, OmniStream: null, OmniOperator: null } as Record<
    ProjectId,
    string | null
  >;
  const have = new Set<ProjectId>();
  const walk = (ns: TreeNode[]) => {
    for (const n of ns) {
      if (n.type === 'file' && n.isKey && !have.has(n.project)) {
        have.add(n.project);
        out[n.project] = `${n.project}:${n.path}`;
      } else if (n.children) walk(n.children);
    }
  };
  walk(nodes);
  return out;
}

// ===== 搜索索引（懒加载，从 docs 建） =====
function camelSplit(s: string): string {
  return s.replace(/([a-z0-9])([A-Z])/g, '$1 $2').replace(/[_\-./]+/g, ' ');
}
let searchIndex: Map<string, string> | null = null;
function getSearchIndex(): Map<string, string> {
  if (searchIndex) return searchIndex;
  searchIndex = new Map();
  const docs = getDocs();
  for (const [key, d] of Object.entries(docs)) {
    const ents = Object.values(d.entities)
      .flatMap((a) => (a ?? []).map((e) => `${e.name} ${e.role}`))
      .join(' ');
    const hay = `${camelSplit(d.path)} ${camelSplit(ents)} ${d.purpose ?? ''}`.toLowerCase();
    searchIndex.set(key, hay);
  }
  return searchIndex;
}

// ===== 多标签页 =====
const HOME_KEY = '__home__';
type TabKind = 'home' | 'file' | 'folder';
interface Tab {
  key: string;
  kind: TabKind;
  pinned?: boolean;
}
const HOME_TAB: Tab = { key: HOME_KEY, kind: 'home' };
const MAX_TABS = 20;

function loadTabs(): Tab[] {
  try {
    const raw = safeGet('omni-tabs');
    if (raw) {
      const arr = JSON.parse(raw) as Tab[];
      if (Array.isArray(arr) && arr.length) {
        const rest = arr.filter(
          (t) => t && t.key && t.key !== HOME_KEY && (t.kind === 'file' || t.kind === 'folder'),
        );
        return [HOME_TAB, ...rest].slice(0, MAX_TABS);
      }
    }
  } catch {
    /* ignore */
  }
  return [HOME_TAB];
}
function loadActive(tabs: Tab[]): string {
  const saved = safeGet('omni-active');
  if (saved && tabs.some((t) => t.key === saved)) return saved;
  return HOME_KEY;
}

const MIN_SB = 220;
const MAX_SB = 560;
const DEF_SB = 312;
function loadSidebarW(): number {
  const v = Number(safeGet('omni-sidebar-w'));
  return v && v >= MIN_SB && v <= MAX_SB ? v : DEF_SB;
}

function tabName(t: Tab): string {
  if (t.kind === 'home') return '概览';
  const i = t.key.indexOf(':');
  const proj = t.key.slice(0, i);
  const p = t.key.slice(i + 1);
  const name = p.split('/').pop();
  return name || proj; // 项目根目录 path='' → 用项目名
}
function tabIcon(t: Tab): string {
  if (t.kind === 'home') return '◇';
  if (t.kind === 'folder') return '◆';
  const name = t.key.slice(t.key.indexOf(':') + 1).split('/').pop() ?? '';
  const ext = name.slice(name.lastIndexOf('.') + 1).toUpperCase();
  return ext ? ext.slice(0, 2) : '·';
}
function tabPid(t: Tab): ProjectId | undefined {
  if (t.kind === 'home') return undefined;
  return t.key.slice(0, t.key.indexOf(':')) as ProjectId;
}

export default function App() {
  const meta = useMemo(
    () =>
      Object.fromEntries(treeData.projects.map((p) => [p.id, p])) as Record<ProjectId, ProjectMeta>,
    [],
  );
  const { files: fileCount, keys: keyCount } = useMemo(() => countFiles(treeData.tree), []);
  const firstKey = useMemo(() => firstKeyByProject(treeData.tree), []);

  const initial = useMemo(() => {
    const t = loadTabs();
    return { tabs: t, active: loadActive(t) };
  }, []);
  const [tabs, setTabs] = useState<Tab[]>(initial.tabs);
  const [activeKey, setActiveKey] = useState<string>(initial.active);

  const [queryInput, setQueryInput] = useState('');
  const [query, setQuery] = useState('');
  const [expanded, setExpanded] = useState<Set<string>>(
    () => new Set(treeData.projects.map((p) => `${p.id}:`)),
  );

  const [sidebarW, setSidebarW] = useState<number>(loadSidebarW);
  const [dragging, setDragging] = useState(false);
  const searchRef = useRef<HTMLInputElement>(null);

  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const saved = safeGet('omni-theme');
    if (saved === 'light' || saved === 'dark') return saved;
    return matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    safeSet('omni-theme', theme);
  }, [theme]);

  useEffect(() => {
    safeSet('omni-tabs', JSON.stringify(tabs));
  }, [tabs]);
  useEffect(() => {
    safeSet('omni-active', activeKey);
  }, [activeKey]);
  useEffect(() => {
    safeSet('omni-sidebar-w', String(sidebarW));
  }, [sidebarW]);

  // 空闲预解析 docs + 预建搜索索引，首次输入即就绪
  useEffect(() => {
    const warm = () => {
      getDocs();
      getSearchIndex();
    };
    const ric = (window as unknown as {
      requestIdleCallback?: (cb: () => void, o?: { timeout: number }) => number;
    }).requestIdleCallback;
    if (ric) ric(warm, { timeout: 3000 });
    else setTimeout(warm, 200);
  }, []);

  // 搜索防抖：输入即时回显，过滤用防抖值，避免每键全量重算
  useEffect(() => {
    const t = setTimeout(() => setQuery(queryInput), 120);
    return () => clearTimeout(t);
  }, [queryInput]);

  // 搜索匹配（query 非空时从 docs 索引）
  const matchedKeys = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return null;
    const terms = q.split(/\s+/).filter(Boolean);
    const idx = getSearchIndex();
    const set = new Set<string>();
    for (const [key, hay] of idx) {
      if (terms.every((t) => hay.includes(t))) set.add(key);
    }
    return set;
  }, [query]);

  // 结果计数（名/路径 + 索引命中）
  const resultCount = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return null;
    let n = 0;
    const walk = (ns: TreeNode[]) => {
      for (const nd of ns) {
        if (nd.type === 'file') {
          const k = `${nd.project}:${nd.path}`;
          if (
            nd.name.toLowerCase().includes(q) ||
            nd.path.toLowerCase().includes(q) ||
            matchedKeys?.has(k)
          )
            n++;
        } else if (nd.children) walk(nd.children);
      }
    };
    walk(treeData.tree);
    return n;
  }, [query, matchedKeys]);

  const openKey = (key: string) => {
    const kind = keyKind.get(key) ?? 'file';
    setTabs((prev) => {
      if (prev.some((t) => t.key === key)) return prev;
      const next = [...prev, { key, kind }];
      if (next.length <= MAX_TABS) return next;
      const cut = next.findIndex((t) => t.key !== HOME_KEY && !t.pinned);
      if (cut >= 0) return [...next.slice(0, cut), ...next.slice(cut + 1)];
      return prev;
    });
    setActiveKey(key);
    setExpanded((prev) => {
      const next = new Set(prev);
      const i = key.indexOf(':');
      const proj = key.slice(0, i);
      const p = key.slice(i + 1);
      next.add(`${proj}:`);
      const segs = p.split('/');
      let acc = '';
      for (let k = 0; k < segs.length - 1; k++) {
        acc += (k ? '/' : '') + segs[k];
        next.add(`${proj}:${acc}`);
      }
      return next;
    });
  };

  const goHome = () => {
    setTabs((prev) => (prev.some((t) => t.key === HOME_KEY) ? prev : [HOME_TAB, ...prev]));
    setActiveKey(HOME_KEY);
  };

  const closeTab = (key: string) => {
    const idx = tabs.findIndex((t) => t.key === key);
    if (idx < 0) return;
    const next = tabs.filter((t) => t.key !== key);
    setTabs(next);
    if (activeKey === key) {
      const fallback = next[idx] ?? next[idx - 1] ?? next[0] ?? null;
      setActiveKey(fallback ? fallback.key : '');
    }
  };

  const togglePin = (key: string) => {
    setTabs((prev) => prev.map((t) => (t.key === key ? { ...t, pinned: !t.pinned } : t)));
  };

  const closeOthers = () => {
    const keep = tabs.filter((t) => t.key === activeKey || t.pinned || t.key === HOME_KEY);
    setTabs(keep);
  };

  const closeAll = () => {
    const keep = tabs.filter((t) => t.pinned || t.key === HOME_KEY);
    setTabs(keep);
    if (!keep.some((t) => t.key === activeKey)) {
      setActiveKey(keep.length ? keep[0].key : '');
    }
  };

  const switchTab = (dir: number) => {
    if (!tabs.length) return;
    const idx = tabs.findIndex((t) => t.key === activeKey);
    const next = tabs[(idx + dir + tabs.length) % tabs.length];
    if (next) setActiveKey(next.key);
  };

  // 全局键盘：Alt+数字跳标签、Alt+[ / Alt+] 前后切、Alt+W 关当前
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!e.altKey || e.ctrlKey || e.metaKey) return;
      if (e.key >= '1' && e.key <= '9') {
        const n = Number(e.key) - 1;
        if (tabs[n]) {
          e.preventDefault();
          setActiveKey(tabs[n].key);
        }
      } else if (e.key === '[') {
        e.preventDefault();
        switchTab(-1);
      } else if (e.key === ']') {
        e.preventDefault();
        switchTab(1);
      } else if (e.key.toLowerCase() === 'w') {
        e.preventDefault();
        closeTab(activeKey);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [tabs, activeKey]);

  // / 聚焦搜索，Esc 清除搜索
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null;
      const inField =
        !!t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable);
      if (e.key === '/' && !inField) {
        e.preventDefault();
        searchRef.current?.focus();
      } else if (e.key === 'Escape' && queryInput) {
        setQueryInput('');
        searchRef.current?.blur();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [queryInput]);

  const onSplitDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setDragging(true);
    const startX = e.clientX;
    const startW = sidebarW;
    const move = (ev: MouseEvent) => {
      const w = Math.max(MIN_SB, Math.min(MAX_SB, startW + ev.clientX - startX));
      setSidebarW(w);
    };
    const up = () => {
      setDragging(false);
      window.removeEventListener('mousemove', move);
      window.removeEventListener('mouseup', up);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', up);
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  };

  const activeTab = tabs.find((t) => t.key === activeKey) ?? null;
  const isHome = activeTab?.kind === 'home';
  const folder = !isHome && activeTab?.kind === 'folder' ? getFolders()[activeTab.key] ?? null : null;
  const doc = !isHome && activeTab?.kind === 'file' ? getDocs()[activeTab.key] ?? null : null;
  const stale = !!activeTab && !isHome && !folder && !doc;

  return (
    <div className="app" style={{ ['--sidebar-w' as string]: `${sidebarW}px` }}>
      <header className="topbar">
        <button className="home-btn" onClick={goHome} title="概览（Alt+0）">
          ◇
        </button>
        <div className="brand" onClick={goHome} style={{ cursor: 'pointer' }}>
          Omni<span className="dot">·</span>文件索引
          <span className="sub">SQL 执行链路</span>
        </div>
        <div className="search">
          <span className="icon">⌕</span>
          <input
            ref={searchRef}
            placeholder="搜索文件名 / 路径 / 作用 / 实体…"
            value={queryInput}
            onChange={(e) => setQueryInput(e.target.value)}
          />
          {queryInput && (
            <button className="search-clear" onClick={() => setQueryInput('')} title="清除 (Esc)">
              ×
            </button>
          )}
        </div>
        <div className="spacer" />
        <div className="meta">
          {resultCount !== null
            ? `${resultCount} 个结果`
            : treeData.generatedAt
            ? `${fileCount} 文件 · ${keyCount} 重点 · ${new Date(treeData.generatedAt).toLocaleDateString('zh-CN')}`
            : `${fileCount} 文件`}
        </div>
        <UpdateButton />
        <button className="theme-toggle" onClick={() => setTheme((t) => (t === 'dark' ? 'light' : 'dark'))}>
          {theme === 'dark' ? '☀ 浅色' : '☾ 深色'}
        </button>
      </header>

      <aside className="sidebar">
        <div className="open-editors">
          <div className="oe-head">
            <span className="oe-title">打开的页面 · {tabs.length}</span>
            <div className="oe-actions">
              <button title="关闭其他（保留当前 + 固定）" onClick={closeOthers}>
                收拢
              </button>
              <button title="关闭全部未固定" onClick={closeAll}>
                清空
              </button>
            </div>
          </div>
          <div className="oe-list">
            {tabs.map((t) => (
              <div
                key={t.key}
                className={'oe-item' + (t.key === activeKey ? ' active' : '')}
                onClick={() => setActiveKey(t.key)}
                title={t.kind === 'home' ? '概览' : t.key}
              >
                <span className="oe-icon" data-pid={tabPid(t)}>
                  {tabIcon(t)}
                </span>
                <span className="oe-name">{tabName(t)}</span>
                {t.kind !== 'home' && (
                  <span
                    className={'oe-pin' + (t.pinned ? ' on' : '')}
                    onClick={(e) => {
                      e.stopPropagation();
                      togglePin(t.key);
                    }}
                    title={t.pinned ? '取消固定' : '固定（不受清空/收拢影响）'}
                  >
                    📌
                  </span>
                )}
                {t.kind !== 'home' && (
                  <span
                    className="oe-close"
                    onClick={(e) => {
                      e.stopPropagation();
                      closeTab(t.key);
                    }}
                    title="关闭"
                  >
                    ×
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="tree-legend">
          <span>★ 重点</span>
          <span>◆ 项目</span>
        </div>
        <Tree
          nodes={treeData.tree}
          selected={isHome ? null : activeTab?.key ?? null}
          onSelect={openKey}
          query={query}
          expanded={expanded}
          onToggle={(key) =>
            setExpanded((prev) => {
              const next = new Set(prev);
              if (next.has(key)) next.delete(key);
              else next.add(key);
              return next;
            })
          }
          matchedKeys={matchedKeys}
        />
      </aside>

      <div
        className={'splitter' + (dragging ? ' dragging' : '')}
        onMouseDown={onSplitDown}
        title="拖动调整侧栏宽度"
      />

      <nav className="tabbar">
        {tabs.map((t) => {
          const active = t.key === activeKey;
          const pid = tabPid(t);
          return (
            <div
              key={t.key}
              className={
                'tab' +
                (active ? ' active' : '') +
                (t.kind === 'home' ? ' home' : '') +
                (t.pinned ? ' pinned' : '')
              }
              data-pid={pid}
              onClick={() => (t.kind === 'home' ? goHome() : setActiveKey(t.key))}
              onAuxClick={(e) => {
                if (e.button === 1) closeTab(t.key);
              }}
              title={t.kind === 'home' ? '概览' : t.key}
            >
              <span className="ticon">{tabIcon(t)}</span>
              <span className="tname">{tabName(t)}</span>
              {t.pinned && t.kind !== 'home' && <span className="tpin">📌</span>}
              {t.kind !== 'home' && (
                <span
                  className="tclose"
                  onClick={(e) => {
                    e.stopPropagation();
                    closeTab(t.key);
                  }}
                  title="关闭"
                >
                  ×
                </span>
              )}
            </div>
          );
        })}
      </nav>

      <main className="main">
        {!activeTab ? (
          <div className="stale-tab">
            <h2>没有打开的页面</h2>
            <p>所有标签已关闭。</p>
            <button onClick={goHome}>◇ 打开概览</button>
          </div>
        ) : isHome ? (
          <Overview
            overview={treeData.overview}
            projects={treeData.projects}
            firstKey={firstKey}
            keyTour={treeData.keyTour}
            onSelect={openKey}
            theme={theme}
            fileCount={fileCount}
            keyCount={keyCount}
          />
        ) : folder ? (
          <FolderDetail folder={folder} meta={meta} onSelect={openKey} />
        ) : doc ? (
          <Detail doc={doc} meta={meta} theme={theme} getDocs={getDocs} onSelect={openKey} />
        ) : stale ? (
          <div className="stale-tab">
            <h2>该文件已不在索引中</h2>
            <p>可能在最近一次过滤 / 更新中被移除：{activeTab.key}</p>
            <button onClick={() => closeTab(activeTab.key)}>关闭此标签</button>
          </div>
        ) : (
          <div className="overview">
            <h1 className="overview-title">文档加载中…</h1>
            <p className="overview-lede">正在解析文件详情数据，请稍候。</p>
          </div>
        )}
      </main>
    </div>
  );
}
