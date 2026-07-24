import type { FolderDoc, ProjectId, ProjectMeta } from '../types.ts';

export function FolderDetail({
  folder,
  meta,
  onSelect,
}: {
  folder: FolderDoc;
  meta: Record<ProjectId, ProjectMeta>;
  onSelect: (key: string) => void;
}) {
  const m = meta[folder.project];
  const segs = folder.path.split('/').filter(Boolean);
  const isRoot = segs.length === 0;
  const dirs = folder.children.filter((c) => c.type === 'dir');
  const files = folder.children.filter((c) => c.type === 'file');
  const title = folder.name || segs[segs.length - 1] || folder.project;

  return (
    <div className="detail">
      <div className="crumbs">
        <span className="proj" data-p={folder.project}>
          {folder.project}
        </span>
        {segs.map((s, i) => (
          <span key={i}>
            <span className="sep">/</span>
            {s}
          </span>
        ))}
      </div>

      <h1 className="detail-title">{title}</h1>

      <div className="tags">
        <span className="tag" style={{ color: m.color, borderColor: m.color + '66' }}>
          {isRoot ? '项目根目录' : '目录'}
        </span>
        <span className="tag">{folder.fileCount} 个文件</span>
      </div>

      <div className="purpose">{folder.purpose}</div>

      <div className="detail-body" style={{ gridTemplateColumns: '1fr' }}>
        <div className="entities">
          {dirs.length > 0 && (
            <>
              <h3>子目录 · {dirs.length}</h3>
              <div className="entity-group">
                {dirs.map((c, i) => (
                  <div className="entity" key={i} style={{ cursor: 'pointer' }} onClick={() => onSelect(c.key)}>
                    <div className="ename">📁 {c.name}</div>
                    <div className="erole">{c.fileCount} 个文件</div>
                  </div>
                ))}
              </div>
            </>
          )}
          <h3 style={{ marginTop: dirs.length ? 20 : 0 }}>文件 · {files.length}</h3>
          <div className="entity-group">
            {files.map((c, i) => (
              <div className="entity" key={i} style={{ cursor: 'pointer' }} onClick={() => onSelect(c.key)}>
                <div className="ename">
                  {c.isKey ? '★ ' : ''}
                  {c.name}
                </div>
                {c.purpose ? <div className="erole">{c.purpose}</div> : null}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
