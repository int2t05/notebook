# upstream-tech-radar verification

## Purpose

验证 `upstream-tech-radar` 这份 skill 在真实服务器环境中是否具备“获取最新 GitHub 上游动态”的基础可行性。这里验证的是方法能否落地，不是正式月报案例。

## Verification Time

- 验证日期：`2026-06-02`
- 时间窗口：`2026-05-03` 到 `2026-06-02`
- 验证环境：`bot-ywh-950`

## Environment Check

服务器返回结果表明具备最小可行环境：

- 架构：`aarch64`
- Python：`3.11.6`
- Git：`2.43.0`
- HTTP 工具：`curl` 可用

这满足 skill 当前“实时抓取 GitHub 数据”的最小前提。

## Repositories Checked

- `bytedance/sonic-cpp`
- `simdjson/simdjson`
- `Tencent/rapidjson`

## What Was Verified

对每个仓库验证了以下三类数据能否读取：

1. open PR
2. 最近 30 天 merged PR
3. 最近活跃 issue

## Verification Result Summary

### bytedance/sonic-cpp

- 仓库基础信息可读取
- open PR 可读取
- 最近 30 天 merged PR 可读取
- 活跃 issue 在该窗口内为 0

可见示例：

- Open PR `#108`: `sve2 HISTSEG support for fast ondemand parsing on ARM`
- Open PR `#136`: `Propagate allocation failures through parser and DOM paths`
- Merged PR `#137`: `ci: add agent guide and benchmark comparison`

结论：`sonic-cpp` 能提供与 Arm 高性能视角高度相关的最新信号，特别适合作为该 skill 的主上游验证对象。

### simdjson/simdjson

- 仓库基础信息可读取
- open PR 可读取
- 最近 30 天 merged PR 可读取
- 活跃 issue 可读取

可见示例：

- Open PR `#2742`: `Key selectors: compile-time perfect-hash field selection for On Demand`
- Open PR `#2697`: `Add support for custom allocators`
- Active issue `#2660`: `Add support for C++26 annotations`

结论：`simdjson` 更新活跃，适合作为 peer repo，用来观察 API 演进、工具链兼容性和性能路线信号。

### Tencent/rapidjson

- 仓库基础信息可读取
- open PR 可读取
- 最近 30 天 merged PR 在该窗口内为 0
- 活跃 issue 可读取

可见示例：

- Open PR `#2362`: `Making GenericMemberIterator comply with C++20's std::random_access_iterator concept`
- Active issue `#2385`: `Can we please have a new release to address some CVEs?`
- Active issue `#2384`: `Pointer::Create/Set with a large array index allocates unboundedly`

结论：`rapidjson` 在该窗口内更偏维护和问题压力信号，适合作为“活跃度较低但维护风险值得观察”的对照样本。

## Overall Conclusion

`upstream-tech-radar` 这份 skill 的核心方法，在 `bot-ywh-950` 上已经验证可行：

- 可以访问 GitHub 最新数据
- 可以同时抓到 open PR、merged PR、活跃 issue
- 可以支撑基于最近 30 天窗口的固定格式月报
- 对 `sonic-cpp / simdjson / rapidjson` 这类 C++ 基础库，能够抓到足够多的 Arm 高性能相关信号

## Not Included Yet

本次验证**没有**生成正式月报案例；如需正式样例，应在后续单独生成并落到 `skills/upstream-tech-radar/` 的示例目录中。
