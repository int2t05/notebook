"""
使用说明
========
从 Spark History Server（SHS）抓取指定 Stage 详情页，保存全页截图、解析后的 JSON 与原始 HTML；
可尝试自动展开 “Show Additional Metrics” 等以采集更多指标。

输出目录（固定）
    <项目根目录 KP_b016>/spark_execution_plan/
    文件名：{execution_id}_stage_{stage_id}_attempt_{attempt}.(png|json|html)

依赖
    Python 3；需安装 Playwright 并拉取 Chromium：
    pip install playwright && playwright install chromium

环境变量（可选，优先级：CLI -b > 环境变量 SPARK_HISTORY_URL > 脚本默认值）
    SPARK_HISTORY_URL   SHS 根地址，未设置时使用脚本默认值

常用命令
    python scrape_stage_details.py -e <应用ID> -s <StageID> [-a 0] [-b http://<SHS主机>:18080]

参数
    -e / --execution-id   必填，Spark 应用 ID
    -s / --stage-id        必填，Stage ID
    -a / --attempt         Attempt 编号，默认 0
    -b / --base-url        SHS 根地址，默认值见 DEFAULT_SHS_URL（受 SPARK_HISTORY_URL 覆盖）
    --no-expand            不自动点击展开隐藏指标
"""
import asyncio
import argparse
import json
import os
import re
from pathlib import Path

from playwright.async_api import async_playwright


DEFAULT_SHS_URL = os.environ.get("SPARK_HISTORY_URL")


def _project_root() -> Path:
    # .../KP_b016/.claude/skills/omni-sql-perf-improvement/scripts/本文件 -> 向上 4 级为项目根
    # 注意:若项目布局不同，可通过环境变量 SPARK_PLAN_OUTPUT_DIR 指定输出目录以避开硬编码位移
    return Path(__file__).resolve().parents[4]


SPARK_PLAN_OUTPUT_DIR = Path(os.environ.get("SPARK_PLAN_OUTPUT_DIR", str(_project_root() / "spark_execution_plan")))


class SparkStageDetailsScraper:
    def __init__(self, base_url=DEFAULT_SHS_URL):
        self.base_url = base_url
        self.output_dir = str(SPARK_PLAN_OUTPUT_DIR)
        os.makedirs(self.output_dir, exist_ok=True)

    async def scrape(self, execution_id, stage_id, attempt=0, expand_all=True):
        url = f"{self.base_url}/history/{execution_id}/stages/stage/?id={stage_id}&attempt={attempt}"
        print(f"正在抓取 Stage 详情...")
        print(f"URL: {url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={'width': 1920, 'height': 3000})
            page = await context.new_page()

            try:
                await page.goto(url, timeout=30000)
                await page.wait_for_load_state('networkidle', timeout=30000)
                await asyncio.sleep(3)

                if expand_all:
                    await self.expand_all_metrics(page)

                text = await page.inner_text('body')
                content = await page.content()

                screenshot_path = os.path.join(
                    self.output_dir,
                    f"{execution_id}_stage_{stage_id}_attempt_{attempt}.png"
                )
                await page.screenshot(path=screenshot_path, full_page=True)
                print(f"截图已保存: {screenshot_path}")

                parsed_data = self.parse_stage_details(text)

                result = {
                    'execution_id': execution_id,
                    'stage_id': stage_id,
                    'attempt': attempt,
                    'url': url,
                    'page_title': await page.title(),
                    **parsed_data,
                    'raw_text': text,
                    'html_length': len(content)
                }

                json_path = os.path.join(
                    self.output_dir,
                    f"{execution_id}_stage_{stage_id}_attempt_{attempt}.json"
                )
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"JSON已保存: {json_path}")

                html_path = os.path.join(
                    self.output_dir,
                    f"{execution_id}_stage_{stage_id}_attempt_{attempt}.html"
                )
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"HTML已保存: {html_path}")

                self.print_summary(result)

                return result

            finally:
                await browser.close()

    async def expand_all_metrics(self, page):
        print("尝试展开所有隐藏的指标...")

        show_links = await page.query_selector_all('a')
        for link in show_links:
            text = await link.inner_text()
            if 'Show' in text:
                try:
                    await link.click()
                    await asyncio.sleep(0.5)
                    print(f"  点击: {text}")
                except:
                    pass

        dropdown = await page.query_selector('select')
        if dropdown:
            options = await dropdown.query_selector_all('option')
            for option in options:
                value = await option.get_attribute('value')
                text = await option.inner_text()
                if 'All' in text or '100' in text or '200' in text:
                    try:
                        await dropdown.select_option(value)
                        print(f"  选择: {text}")
                        await asyncio.sleep(0.5)
                    except:
                        pass

    def parse_stage_details(self, text):
        lines = text.split('\n')
        results = {
            'stage_info': {},
            'summary_metrics': {},
            'task_table_headers': [],
            'task_metrics': [],
        }

        full_text = text

        match = re.search(r'Details for Stage\s+(\d+)\s+\(Attempt\s+(\d+)\)', full_text)
        if match:
            results['stage_info']['stage_id'] = int(match.group(1))
            results['stage_info']['attempt'] = int(match.group(2))

        match = re.search(r'Resource Profile Id:\s*(\d+)', full_text)
        if match:
            results['stage_info']['resource_profile_id'] = int(match.group(1))

        match = re.search(r'Total Time Across All Tasks:\s*([\d.]+\s*(?:s|ms|min)?)', full_text)
        if match:
            results['stage_info']['total_time'] = match.group(1).strip()

        match = re.search(r'Locality Level Summary:\s*(.+?)(?:\n|$)', full_text)
        if match:
            results['stage_info']['locality_summary'] = match.group(1).strip()

        match = re.search(r'Associated Job Ids:\s*(\d+)', full_text)
        if match:
            results['stage_info']['associated_job_ids'] = int(match.group(1))

        metrics_section = re.search(
            r'Summary Metrics for\s+(\d+)\s+Completed Tasks.*?'
            r'Duration\s*([\d.]+\s*\w+)\s*([\d.]+\s*\w+)\s*([\d.]+\s*\w+)\s*([\d.]+\s*\w+)\s*([\d.]+\s*\w+).*?'
            r'GC Time\s*([\d.]+\s*\w+)\s*([\d.]+\s*\w+)\s*([\d.]+\s*\w+)\s*([\d.]+\s*\w+)\s*([\d.]+\s*\w+)',
            full_text, re.DOTALL
        )
        if metrics_section:
            results['summary_metrics']['Duration'] = {
                'min': metrics_section.group(2),
                '25th': metrics_section.group(3),
                'median': metrics_section.group(4),
                '75th': metrics_section.group(5),
                'max': metrics_section.group(6)
            }
            results['summary_metrics']['GC Time'] = {
                'min': metrics_section.group(7),
                '25th': metrics_section.group(8),
                'median': metrics_section.group(9),
                '75th': metrics_section.group(10),
                'max': metrics_section.group(11)
            }

        task_rows = re.findall(
            r'(\d+)\t(\d+)\t(\d+)\t(SUCCESS|FAILED|KILLED)\t(\w+)\t(\w+)\t(\S+)\t(\S*)\t([\d-]+\s+[\d:]+)\t([\d.]+\s*(?:s|ms))\t([\d.]+\s*\w+)',
            full_text
        )
        for row in task_rows:
            results['task_metrics'].append({
                'index': row[0],
                'task_id': row[1],
                'attempt': row[2],
                'status': row[3],
                'locality': row[4],
                'executor_id': row[5],
                'host': row[6],
                'logs': row[7],
                'launch_time': row[8],
                'duration': row[9],
                'gc_time': row[10]
            })

        return results

    def extract_next_value(self, lines, idx):
        if idx + 1 < len(lines):
            val = lines[idx + 1].strip()
            if val and not val.startswith('Show') and not val.startswith('entries'):
                return val
        return None

    def extract_metrics_section(self, lines, idx):
        metrics = {}
        metric_names = ['Duration', 'GC Time', 'Scheduler Delay',
                        'Task Deserialization Time', 'Shuffle Read', 'Shuffle Write']

        for name in metric_names:
            for j in range(idx, min(idx + 20, len(lines))):
                if name in lines[j] and j + 1 < len(lines):
                    values_line = lines[j + 1].strip()
                    if re.match(r'^[\d.,]+\s*(ms|s|kB|MB|GB)?', values_line):
                        parts = re.findall(r'[\d.,]+\s*(?:ms|s|kB|MB|GB)?', values_line)
                        if len(parts) >= 5:
                            metrics[name] = {
                                'min': parts[0],
                                '25th': parts[1],
                                'median': parts[2],
                                '75th': parts[3],
                                'max': parts[4]
                            }
                        break
        return metrics

    def extract_table_headers(self, lines, idx):
        headers = []
        j = idx
        while j < len(lines) and len(headers) < 20:
            line = lines[j].strip()
            if line and not re.match(r'^\d', line) and 'Show' not in line:
                headers.append(line)
                j += 1
            else:
                break
        return headers

    def parse_task_line(self, line):
        parts = line.split()
        if len(parts) >= 6:
            return {
                'index': parts[0],
                'task_id': parts[1],
                'attempt': parts[2],
                'status': parts[3],
                'locality': parts[4] if len(parts) > 4 else None,
                'host': parts[5] if len(parts) > 5 else None,
                'raw_line': line
            }
        return None

    def print_summary(self, data):
        print("\n" + "=" * 70)
        print("[Stage] 执行详情摘要")
        print("=" * 70)

        stage_info = data.get('stage_info', {})
        print(f"\n【基本信息】")
        print(f"  Stage ID: {stage_info.get('stage_id', 'N/A')}")
        print(f"  Attempt: {stage_info.get('attempt', 'N/A')}")
        print(f"  Resource Profile: {stage_info.get('resource_profile_id', 'N/A')}")
        print(f"  总任务时间: {stage_info.get('total_time', 'N/A')}")
        print(f"  Locality: {stage_info.get('locality_summary', 'N/A')}")
        print(f"  Associated Job IDs: {stage_info.get('associated_job_ids', 'N/A')}")

        metrics = data.get('summary_metrics', {})
        if metrics:
            print(f"\n【Summary Metrics 统计】")
            for metric, values in metrics.items():
                if values:
                    print(f"  {metric}:")
                    print(f"    Min: {values.get('min', 'N/A')}")
                    print(f"    Median: {values.get('median', 'N/A')}")
                    print(f"    Max: {values.get('max', 'N/A')}")

        tasks = data.get('task_metrics', [])
        if tasks:
            print(f"\n【Task 详情】 (共 {len(tasks)} 个 Task)")
            for task in tasks:
                print(f"  Task {task.get('index')}: "
                      f"TaskID={task.get('task_id')}, "
                      f"Status={task.get('status')}, "
                      f"Locality={task.get('locality')}, "
                      f"Host={task.get('host')}")


def main():
    parser = argparse.ArgumentParser(description='抓取Spark Stage详情')
    parser.add_argument('--execution-id', '-e', required=True, help='Spark Execution ID')
    parser.add_argument('--stage-id', '-s', type=int, required=True, help='Stage ID')
    parser.add_argument('--attempt', '-a', type=int, default=0, help='Attempt ID (默认: 0)')
    parser.add_argument('--base-url', '-b', default=DEFAULT_SHS_URL, help='Spark History Server URL（受 SPARK_HISTORY_URL 环境变量覆盖）')
    parser.add_argument('--no-expand', action='store_true', help='不展开隐藏指标')

    args = parser.parse_args()

    scraper = SparkStageDetailsScraper(base_url=args.base_url)
    asyncio.run(scraper.scrape(args.execution_id, args.stage_id, args.attempt, expand_all=not args.no_expand))


if __name__ == "__main__":
    main()