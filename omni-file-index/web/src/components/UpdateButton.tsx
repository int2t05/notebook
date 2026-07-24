import { useState } from 'react';

export function UpdateButton() {
  const [open, setOpen] = useState(false);
  const [log, setLog] = useState('');
  const [running, setRunning] = useState(false);

  const url =
    typeof location !== 'undefined' && location.protocol === 'file:'
      ? 'http://localhost:7788/api/update'
      : '/api/update';

  async function run() {
    setOpen(true);
    setRunning(true);
    setLog('正在连接本地服务...\n');
    try {
      const resp = await fetch(url, { method: 'POST' });
      if (!resp.ok || !resp.body) {
        setLog((l) => l + `更新失败：HTTP ${resp.status}\n`);
        setRunning(false);
        return;
      }
      const reader = resp.body.getReader();
      const dec = new TextDecoder();
      let done = false;
      while (!done) {
        const { value, done: d } = await reader.read();
        done = d;
        if (value) setLog((l) => l + dec.decode(value, { stream: true }));
      }
      setRunning(false);
      setLog((l) => l + '\n✓ 完成，即将刷新页面...');
      setTimeout(() => location.reload(), 1200);
    } catch {
      setLog(
        (l) =>
          l +
          '\n✗ 无法连接本地服务。\n\n请在本项目目录另开一个终端运行：\n    npm run serve\n保持其开启后，再点「增量更新」即可。\n（双击 dist 打开时，按钮通过 http://localhost:7788 调用本地 API）',
      );
      setRunning(false);
    }
  }

  return (
    <>
      <button
        className="theme-toggle"
        onClick={() => run()}
        disabled={running}
        title="增量扫描新增/变更文件 → LLM 提炼 → 重建前端"
      >
        ⟳ 增量更新
      </button>
      {open && (
        <div className="update-overlay">
          <div className="update-panel">
            <div className="update-head">
              <span>{running ? '增量更新中…' : '增量更新'}</span>
              <button onClick={() => setOpen(false)} disabled={running}>
                ✕
              </button>
            </div>
            <pre className="update-log">{log}</pre>
          </div>
        </div>
      )}
    </>
  );
}
