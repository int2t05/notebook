import { useState } from 'react';
import type { FileDoc, ProjectId, ProjectMeta } from '../types.ts';
import { MermaidPanel } from './MermaidPanel.tsx';

const GROUPS: [keyof FileDoc['entities'], string][] = [
  ['functions', '函数'],
  ['classes', '类 / 结构'],
  ['methods', '方法'],
  ['objects', '对象 / 常量'],
];

function fmtSize(n?: number): string {
  if (!n) return '';
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 / 1024).toFixed(1)} MB`;
}

function EntityGroup({
  label,
  items,
}: {
  label: string;
  items: { name: string; role?: string }[];
}) {
  const [all, setAll] = useState(false);
  const LIMIT = 6;
  const shown = all ? items : items.slice(0, LIMIT);
  return (
    <div className="entity-group">
      <div className="gtitle">
        {label} <span className="gc">{items.length}</span>
      </div>
      {shown.map((e, i) => (
        <div className="entity" key={i}>
          <div className="ename">{e.name}</div>
          {e.role ? <div className="erole">{e.role}</div> : null}
        </div>
      ))}
      {items.length > LIMIT && (
        <button className="expand-btn" onClick={() => setAll((a) => !a)}>
          {all ? '收起' : `展开全部 ${items.length}`}
        </button>
      )}
    </div>
  );
}

export function Detail({
  doc,
  meta,
  theme,
  getDocs,
  onSelect,
}: {
  doc: FileDoc;
  meta: Record<ProjectId, ProjectMeta>;
  theme: 'light' | 'dark';
  getDocs: () => Record<string, FileDoc>;
  onSelect: (key: string) => void;
}) {
  const m = meta[doc.project];
  const segs = doc.path.split('/').filter(Boolean);
  const kindLabel =
    doc.mermaidKind === 'llm' ? 'LLM 流程图' : doc.mermaidKind === 'auto' ? '结构图（自动）' : '无图';
  const totalEntities = GROUPS.reduce((a, [k]) => a + (doc.entities[k]?.length ?? 0), 0);

  return (
    <div className="detail">
      <div className="crumbs">
        <span className="proj" data-p={doc.project}>
          {doc.project}
        </span>
        {segs.map((s, i) => (
          <span key={i}>
            <span className="sep">/</span>
            {s}
          </span>
        ))}
      </div>

      <h1 className="detail-title">{segs[segs.length - 1] ?? doc.path}</h1>

      <div className="tags">
        <span className="tag" style={{ color: m.color, borderColor: m.color + '66' }}>
          {doc.lang}
        </span>
        {doc.size ? <span className="tag">{fmtSize(doc.size)}</span> : null}
        {doc.isKey ? <span className="tag stage">{doc.stage ?? 'SQL 链路'}</span> : null}
      </div>

      <div className="purpose">{doc.purpose}</div>

      <div className="detail-body">
        <div className="entities">
          <h3>实体 · {totalEntities}</h3>
          {totalEntities === 0 ? (
            <div className="entities-empty">无实体（二进制 / 未提炼）</div>
          ) : (
            GROUPS.map(([k, label]) => {
              const arr = (doc.entities[k] ?? []) as { name: string; role?: string }[];
              if (!arr.length) return null;
              return <EntityGroup key={k} label={label} items={arr} />;
            })
          )}
        </div>

        <div>
          {doc.mermaidKind === 'none' ? (
            <div className="mermaid-pane">
              <h3>
                流程图 <span className="kind">无图</span>
              </h3>
              <div className="entities-empty">该文件无流程图。</div>
            </div>
          ) : (
            <MermaidPanel code={doc.mermaid} kind={kindLabel} theme={theme} />
          )}
          {doc.prose ? (
            <div className="prose">
              <span className="plabel">说明</span>
              {doc.prose}
            </div>
          ) : null}
        </div>
      </div>

      {doc.related && doc.related.length > 0 && (
        <div className="related">
          <div className="section-label">相关文件 · {doc.related.length}</div>
          <div className="related-list">
            {doc.related.map((rk) => {
              const r = getDocs()[rk];
              if (!r) return null;
              const rm = meta[r.project];
              return (
                <div key={rk} className="related-item" onClick={() => onSelect(rk)}>
                  <span className="rname" style={{ color: rm.color }}>
                    {r.isKey ? '★ ' : ''}
                    {r.path.split('/').pop()}
                  </span>
                  <span className="rpath">
                    {r.project} · {r.path}
                  </span>
                  <span className="rrole">{(r.purpose || '').slice(0, 80)}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {doc.referencedBy && doc.referencedBy.length > 0 && (
        <div className="related referenced">
          <div className="section-label">被引用 · {doc.referencedBy.length}</div>
          <div className="related-list">
            {doc.referencedBy.map((rk) => {
              const r = getDocs()[rk];
              if (!r) return null;
              const rm = meta[r.project];
              return (
                <div key={rk} className="related-item" onClick={() => onSelect(rk)}>
                  <span className="rname" style={{ color: rm.color }}>
                    {r.isKey ? '★ ' : ''}
                    {r.path.split('/').pop()}
                  </span>
                  <span className="rpath">
                    {r.project} · {r.path}
                  </span>
                  <span className="rrole">{(r.purpose || '').slice(0, 80)}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
