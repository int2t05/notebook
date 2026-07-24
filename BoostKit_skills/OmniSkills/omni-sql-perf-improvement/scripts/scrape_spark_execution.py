"""
使用说明
========
从 Spark History Server（SHS）抓取指定 SQL 执行计划页，保存全页截图、解析后的 JSON 与原始 HTML。

输出目录（固定）
    <项目根目录>/spark_execution_plan/
    文件名：{execution_id}_query_{query_id}.(png|json|html)

依赖
    Python 3；需安装 Playwright 并拉取 Chromium：
    pip install playwright && playwright install chromium

环境变量（可选，优先级：CLI -b > 环境变量 SPARK_HISTORY_URL > 脚本默认值）
    SPARK_HISTORY_URL   SHS 根地址，未设置时使用脚本默认值

常用命令
    python scrape_spark_execution.py -e <应用ID> -q <QueryID> [-b http://<SHS主机>:18080]

参数
    -e / --execution-id   必填，Spark 应用 ID（与 SHS URL 中 /history/<id>/ 一致）
    -q / --query-id        SQL 查询序号，默认 1
    -b / --base-url        SHS 根地址，默认值见 DEFAULT_SHS_URL（受 SPARK_HISTORY_URL 覆盖）
"""
import asyncio
import argparse
import json
import os
import re
from pathlib import Path

from playwright.async_api import async_playwright


def _project_root() -> Path:
    # .../KP_b016/.claude/skills/omni-sql-perf-improvement/scripts/本文件 -> 向上 4 级为项目根
    # 注意:若项目布局不同，可通过环境变量 SPARK_PLAN_OUTPUT_DIR 指定输出目录以避开硬编码位移
    return Path(__file__).resolve().parents[4]


DEFAULT_SHS_URL = os.environ.get("SPARK_HISTORY_URL")
SPARK_PLAN_OUTPUT_DIR = Path(os.environ.get("SPARK_PLAN_OUTPUT_DIR", str(_project_root() / "spark_execution_plan")))


class SparkExecutionPlanScraper:
    def __init__(self, base_url=DEFAULT_SHS_URL):
        self.base_url = base_url
        self.execution_id = None
        self.query_id = None
        self.output_dir = str(SPARK_PLAN_OUTPUT_DIR)
        os.makedirs(self.output_dir, exist_ok=True)

    def get_sql_execution_url(self):
        return f"{self.base_url}/history/{self.execution_id}/SQL/execution/?id={self.query_id}"

    def parse_operator_metrics(self, text):
        results = {
            'operators': [],
            'submitted_time': None,
            'duration': None,
            'succeeded_jobs': None,
        }

        lines = text.split('\n')
        current_op = None

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            if 'Details for Query' in line:
                match = re.search(r'Query\s+(\d+)', line)
                if match:
                    results['query_id'] = int(match.group(1))
            elif 'Submitted Time:' in line:
                match = re.search(r'(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})', line)
                if match:
                    results['submitted_time'] = match.group(1)
            elif line.startswith('Duration:') or line == 'Duration:':
                duration_val = re.search(r'(\d+\s*(?:s|ms|min|h))', line)
                if duration_val:
                    results['duration'] = duration_val.group(1)
            elif 'Succeeded Jobs:' in line:
                match = re.search(r'(\d+)', line)
                if match:
                    results['succeeded_jobs'] = int(match.group(1))
            elif 'WholeStageCodegenTransformer' in line:
                if current_op:
                    results['operators'].append(current_op)
                match = re.search(r'\((\d+)\)', line)
                op_id = match.group(1) if match else '1'
                current_op = {
                    'name': 'WholeStageCodegenTransformer',
                    'id': op_id,
                    'details': {}
                }
            elif 'OmniColumnarToRow' in line:
                if current_op:
                    results['operators'].append(current_op)
                current_op = {
                    'name': 'OmniColumnarToRow',
                    'id': None,
                    'details': {}
                }
            elif 'ScanTransformer' in line:
                if current_op:
                    results['operators'].append(current_op)
                current_op = {
                    'name': 'ScanTransformer',
                    'id': None,
                    'details': {'source': line.replace('ScanTransformer', '').strip()}
                }
            elif 'number of output rows' in line.lower():
                value = line.split(':')[-1].strip()
                if current_op:
                    current_op['details']['output_rows'] = value
            elif 'number of input batches' in line.lower():
                value = line.split(':')[-1].strip()
                if current_op:
                    current_op['details']['input_batches'] = value
            elif 'time in omniColumnar to row' in line.lower():
                if i + 1 < len(lines):
                    time_str = lines[i + 1].strip()
                    if current_op and 'OmniColumnarToRow' in current_op.get('name', ''):
                        current_op['details']['columnar_to_row_time'] = time_str
            elif 'duration' in line.lower() and 'ms' in line.lower() and current_op:
                if 'WholeStageCodegenTransformer' in current_op.get('name', ''):
                    match = re.search(r'(\d+)\s*ms', line)
                    if match:
                        current_op['details']['total_duration_ms'] = int(match.group(1))

        if current_op:
            results['operators'].append(current_op)

        return results

    def format_plan_diagram(self, parsed_data):
        diagram = []
        diagram.append("=" * 70)
        diagram.append("[Spark SQL] Operator Execution Plan")
        diagram.append("=" * 70)

        diagram.append(f"\n执行信息:")
        diagram.append(f"  Execution ID: {self.execution_id}")
        diagram.append(f"  Query ID: {self.query_id}")
        diagram.append(f"  提交时间: {parsed_data.get('submitted_time', 'N/A')}")
        diagram.append(f"  执行时长: {parsed_data.get('duration', 'N/A')}")
        diagram.append(f"  Job状态: Succeeded Jobs {parsed_data.get('succeeded_jobs', 'N/A')}")

        diagram.append(f"\n算子执行顺序:")
        diagram.append("-" * 70)

        for i, op in enumerate(parsed_data['operators'], 1):
            diagram.append(f"\n【算子 {i}】 {op['name']}")
            if op['id']:
                diagram.append(f"  ID: {op['id']}")
            for key, value in op['details'].items():
                diagram.append(f"  {key}: {value}")

        diagram.append("\n" + "-" * 70)
        diagram.append("执行流程图:")
        diagram.append("-" * 70)
        diagram.append("┌─────────────────────────────────────────────────────────────┐")

        for i, op in enumerate(parsed_data['operators']):
            name = op['name']
            duration = op['details'].get('total_duration_ms', op['details'].get('columnar_to_row_time', ''))
            duration_str = f" {duration} ms" if duration else ""

            diagram.append(f"│  {name}{duration_str:<45} │")
            if i < len(parsed_data['operators']) - 1:
                diagram.append("├─────────────────────────────────────────────────────────────┤")
                diagram.append("│                            ↓                               │")

        diagram.append("└─────────────────────────────────────────────────────────────┘")

        return "\n".join(diagram)

    async def scrape(self, execution_id, query_id):
        self.execution_id = execution_id
        self.query_id = query_id
        url = self.get_sql_execution_url()

        print(f"正在抓取执行计划...")
        print(f"URL: {url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={'width': 1920, 'height': 3000})
            page = await context.new_page()

            try:
                await page.goto(url, timeout=30000)
                await page.wait_for_load_state('networkidle', timeout=30000)
                await asyncio.sleep(3)

                text = await page.inner_text('body')
                content = await page.content()

                screenshot_path = os.path.join(self.output_dir, f"{execution_id}_query_{query_id}.png")
                await page.screenshot(path=screenshot_path, full_page=True)
                print(f"截图已保存: {screenshot_path}")

                parsed_data = self.parse_operator_metrics(text)

                result = {
                    'execution_id': execution_id,
                    'query_id': query_id,
                    'url': url,
                    'page_title': await page.title(),
                    **parsed_data,
                    'raw_text': text,
                    'html_length': len(content)
                }

                json_path = os.path.join(self.output_dir, f"{execution_id}_query_{query_id}.json")
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"JSON已保存: {json_path}")

                html_path = os.path.join(self.output_dir, f"{execution_id}_query_{query_id}.html")
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"HTML已保存: {html_path}")

                print("\n" + self.format_plan_diagram(parsed_data))

                return result

            finally:
                await browser.close()


def main():
    parser = argparse.ArgumentParser(description='抓取Spark SQL执行计划')
    parser.add_argument('--execution-id', '-e', required=True, help='Spark Execution ID')
    parser.add_argument('--query-id', '-q', type=int, default=1, help='Query ID (默认: 1)')
    parser.add_argument('--base-url', '-b', default=DEFAULT_SHS_URL, help='Spark History Server URL（受 SPARK_HISTORY_URL 环境变量覆盖）')

    args = parser.parse_args()

    scraper = SparkExecutionPlanScraper(base_url=args.base_url)
    asyncio.run(scraper.scrape(args.execution_id, args.query_id))


if __name__ == "__main__":
    main()