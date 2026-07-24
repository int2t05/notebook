import { defineConfig, type Plugin } from 'vite';
import react from '@vitejs/plugin-react';
import { viteSingleFile } from 'vite-plugin-singlefile';
import fs from 'node:fs';
import path from 'node:path';

// 把 data.json 拆成三段 <script type="application/json"> 原始文本注入 HTML：
//  - #app-tree（projects+tree+overview+keyTour，首屏必需）加载即 JSON.parse
//  - #app-folders（936 目录解析，~1-2MB）按需 JSON.parse，点目录才用
//  - #app-docs（4242 文件详情，重）按需 JSON.parse，点文件才用
// 这样 V8 不把 14MB 数据当 JS 对象字面量同步解析，首屏只解析少量 JS。
function injectData(): Plugin {
  const dataPath = path.resolve(__dirname, 'src/data.json');
  return {
    name: 'inject-omni-data',
    transformIndexHtml(html: string) {
      if (!fs.existsSync(dataPath)) return html;
      const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
      const tree = JSON.stringify({
        generatedAt: data.generatedAt,
        projects: data.projects,
        tree: data.tree,
        keyTour: data.keyTour ?? [],
        overview: data.overview,
      });
      const folders = JSON.stringify(data.folders ?? {});
      const docs = JSON.stringify(data.docs);
      const esc = (s: string) => s.replace(/<\/script/gi, '<\\/script');
      const injection = `<script type="application/json" id="app-tree">${esc(tree)}</script><script type="application/json" id="app-folders">${esc(folders)}</script><script type="application/json" id="app-docs">${esc(docs)}</script>`;
      return html.replace('</body>', `${injection}</body>`);
    },
  };
}

export default defineConfig({
  plugins: [react(), injectData(), viteSingleFile({ removeViteModuleLoader: true })],
  base: './',
  build: {
    target: 'es2020',
    cssCodeSplit: false,
    assetsInlineLimit: 100000000,
  },
});
