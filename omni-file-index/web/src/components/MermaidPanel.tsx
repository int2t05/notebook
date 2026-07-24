import { useEffect, useRef, useState } from 'react';
import { Mermaid } from './Mermaid.tsx';

export function MermaidPanel({
  code,
  kind,
  theme,
}: {
  code: string;
  kind: string;
  theme: 'light' | 'dark';
}) {
  const [fs, setFs] = useState(false);
  return (
    <div className="mermaid-pane">
      <h3>
        流程图 <span className="kind">{kind}</span>
        <button className="fs-btn" onClick={() => setFs(true)} title="全屏缩放查看">
          ⛶ 全屏
        </button>
      </h3>
      <div className="mermaid-card">
        <Mermaid code={code} theme={theme} />
      </div>
      {fs && <Fullscreen code={code} theme={theme} onClose={() => setFs(false)} />}
    </div>
  );
}

function Fullscreen({
  code,
  theme,
  onClose,
}: {
  code: string;
  theme: 'light' | 'dark';
  onClose: () => void;
}) {
  const [scale, setScale] = useState(1);
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const [ready, setReady] = useState(false);
  const drag = useRef<{ x: number; y: number; px: number; py: number } | null>(null);
  const stageRef = useRef<HTMLDivElement>(null);

  // 适配：按 SVG 实际大小缩放到视口内并居中
  const fit = () => {
    const svg = stageRef.current?.querySelector('svg');
    if (!svg) return;
    const w = (svg as SVGSVGElement).width?.baseVal?.value || svg.getBoundingClientRect().width / scale;
    const h = (svg as SVGSVGElement).height?.baseVal?.value || svg.getBoundingClientRect().height / scale;
    if (!w || !h) return;
    const vpW = window.innerWidth - 48;
    const vpH = window.innerHeight - 76;
    const s = Math.min(vpW / w, vpH / h, 4);
    setScale(Math.max(0.3, s));
    setPos({ x: 0, y: 0 });
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    const stage = stageRef.current;
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      setScale((s) => Math.max(0.3, Math.min(6, s * (e.deltaY < 0 ? 1.12 : 0.89))));
    };
    stage?.addEventListener('wheel', onWheel, { passive: false });
    // 等 mermaid 渲染完后适配
    const t = setTimeout(() => {
      fit();
      setReady(true);
    }, 500);
    return () => {
      window.removeEventListener('keydown', onKey);
      stage?.removeEventListener('wheel', onWheel);
      clearTimeout(t);
    };
  }, [onClose]);

  const onDown = (e: React.MouseEvent) => {
    drag.current = { x: e.clientX, y: e.clientY, px: pos.x, py: pos.y };
  };
  const onMove = (e: React.MouseEvent) => {
    if (!drag.current) return;
    setPos({
      x: drag.current.px + (e.clientX - drag.current.x),
      y: drag.current.py + (e.clientY - drag.current.y),
    });
  };
  const onUp = () => {
    drag.current = null;
  };

  return (
    <div className="fs-overlay">
      <div className="fs-toolbar">
        <button onClick={() => setScale((s) => Math.min(6, s * 1.2))} title="放大">＋</button>
        <button onClick={() => setScale((s) => Math.max(0.3, s / 1.2))} title="缩小">－</button>
        <button onClick={fit} title="适配窗口">⤢</button>
        <span className="fs-zoom">{Math.round(scale * 100)}%</span>
        <span className="fs-hint">滚轮缩放 · 拖拽平移 · Esc 关闭</span>
        <button className="fs-close" onClick={onClose}>✕ 关闭</button>
      </div>
      <div
        ref={stageRef}
        className="fs-stage"
        onMouseDown={onDown}
        onMouseMove={onMove}
        onMouseUp={onUp}
        onMouseLeave={onUp}
        style={{ opacity: ready ? 1 : 0.3 }}
      >
        <div
          className="fs-inner"
          style={{ transform: `translate(${pos.x}px, ${pos.y}px) scale(${scale})` }}
        >
          <Mermaid code={code} theme={theme} />
        </div>
      </div>
    </div>
  );
}
