import type { KeyTourItem, ProjectId, ProjectMeta } from '../types.ts';
import { Mermaid } from './Mermaid.tsx';

export function Overview({
  overview,
  projects,
  firstKey,
  keyTour,
  onSelect,
  theme,
  fileCount,
  keyCount,
}: {
  overview: { mermaid: string; prose: string };
  projects: ProjectMeta[];
  firstKey: Record<ProjectId, string | null>;
  keyTour: KeyTourItem[];
  onSelect: (key: string) => void;
  theme: 'light' | 'dark';
  fileCount: number;
  keyCount: number;
}) {
  // 按链路环节分组（keyTour 已按环节排序，相邻同组归并）
  const groups: { group: string; items: KeyTourItem[] }[] = [];
  for (const it of keyTour) {
    const last = groups[groups.length - 1];
    if (last && last.group === it.group) last.items.push(it);
    else groups.push({ group: it.group, items: [it] });
  }

  return (
    <div className="overview">
      <h1 className="overview-title">
        SQL 如何在 <span className="accent">Omni</span> 里跑通
      </h1>
      <p className="overview-lede">
        三个项目一条链路：OmniAdaptor 桥接翻译 → OmniStream native 运行时 → OmniOperator 算子与向量化执行。
        点左侧目录树任意文件看作用，重点文件带 ★，附 mermaid 流程图。
      </p>

      <div className="section-label">链路总览</div>
      <div className="mermaid-card">
        <Mermaid code={overview.mermaid} theme={theme} />
      </div>
      <p className="prose" style={{ marginTop: 16 }}>
        {overview.prose}
      </p>

      <div className="section-label">三个项目 · 共 {fileCount} 文件 / {keyCount} 重点</div>
      <div className="project-cards">
        {projects.map((p) => (
          <div
            className="pcard"
            key={p.id}
            style={{ ['--pc' as any]: p.color }}
            onClick={() => firstKey[p.id] && onSelect(firstKey[p.id]!)}
          >
            <div className="pname" style={{ color: p.color }}>
              {p.name}
            </div>
            <div className="pdesc">{p.desc}</div>
            <div className="pmeta">
              {firstKey[p.id] ? '点击进入 SQL 链路 →' : '（无重点文件）'}
            </div>
          </div>
        ))}
      </div>

      {groups.length > 0 && (
        <>
          <div className="section-label">SQL 链路导览 · {keyTour.length} 个重点按环节排列</div>
          <p className="tour-hint">从入口到向量化执行，按链路顺序逐个精讲。点击任意条目打开。</p>
          <div className="tour">
            {groups.map((g, gi) => (
              <div className="tour-group" key={gi}>
                <div className="tour-gtitle">
                  <span className="tour-idx">{gi + 1}</span>
                  {g.group}
                  <span className="tour-gcount">{g.items.length}</span>
                </div>
                <div className="tour-items">
                  {g.items.map((it) => (
                    <div
                      className="tour-item"
                      key={it.key}
                      data-pid={it.project}
                      onClick={() => onSelect(it.key)}
                      title={it.key}
                    >
                      <div className="tour-name">
                        <span className="tour-star">★</span>
                        {it.name}
                      </div>
                      <div className="tour-stage">{it.stage}</div>
                      {it.purpose ? <div className="tour-purpose">{it.purpose.slice(0, 110)}</div> : null}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      <div className="hint">
        提示：左上角搜索框可按文件名/路径/作用/实体过滤（支持 camelCase）；Alt+数字切换标签，Alt+W 关闭，方向键在树内移动。
      </div>
    </div>
  );
}
