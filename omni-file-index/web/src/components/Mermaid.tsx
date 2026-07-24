import { useEffect, useState } from 'react';
import mermaid from 'mermaid';

let seq = 0;
// mermaid.initialize 较重，按主题只初始化一次（多标签/多次渲染复用）
const initedFor = new Set<string>();
function ensureInit(theme: 'light' | 'dark') {
  if (initedFor.has(theme)) return;
  initedFor.add(theme);
  mermaid.initialize({
    startOnLoad: false,
    theme: theme === 'dark' ? 'dark' : 'default',
    securityLevel: 'loose',
    fontFamily: "'IBM Plex Mono', monospace",
    flowchart: { curve: 'basis', htmlLabels: true },
    themeVariables:
      theme === 'dark'
        ? { background: '#1b1e24', primaryColor: '#26282f', primaryTextColor: '#e7e5df', lineColor: '#6f6c64', fontSize: '13px' }
        : { background: '#ffffff', primaryColor: '#f1efe8', primaryTextColor: '#1c1b19', lineColor: '#8a857c', fontSize: '13px' },
  });
}

export function Mermaid({ code, theme }: { code: string; theme: 'light' | 'dark' }) {
  const [svg, setSvg] = useState('');
  const [err, setErr] = useState('');

  useEffect(() => {
    if (!code?.trim()) {
      setSvg('');
      setErr('');
      return;
    }
    let cancelled = false;
    const rid = 'm' + ++seq;
    ensureInit(theme);
    mermaid
      .render(rid, code)
      .then(({ svg }) => {
        if (!cancelled) {
          setSvg(svg);
          setErr('');
        }
      })
      .catch(() => {
        if (!cancelled) {
          setErr(code);
          setSvg('');
        }
      });
    return () => {
      cancelled = true;
    };
  }, [code, theme]);

  if (err)
    return (
      <div className="mermaid-error">
        <p>⚠ 流程图语法渲染失败</p>
        <details>
          <summary>查看原始 mermaid 代码</summary>
          <pre>{err}</pre>
        </details>
      </div>
    );
  if (!svg) return null;
  return <div dangerouslySetInnerHTML={{ __html: svg }} />;
}
