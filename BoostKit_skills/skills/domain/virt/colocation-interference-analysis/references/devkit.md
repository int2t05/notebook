# DevKit topdown 采集参考

DevKit 是鲲鹏社区提供的开发套件。下载和文档入口以官方页面为准：

- 鲲鹏 DevKit 开发套件页面：<https://www.hikunpeng.com/developer/devkit>

建议在该页面进入下载或文档区域，选择与目标机器架构、操作系统和 DevKit 版本匹配的软件包。安装方式可能随版本变化，请以官方安装文档为准。

## 基本检查

安装完成后，先确认命令可用：

```bash
devkit --help
devkit tuner --help
```

## 系统级 topdown 采集

采集一次系统级 topdown 报告：

```bash
devkit tuner top-down -d 60
```

其中 `-d 60` 表示采样 60 秒。

## 进程级 topdown 采集

如果已知在线业务进程 PID，可以通过 `-p` 指定采集目标，减少节点级噪声：

```bash
devkit tuner top-down -d 60 -p <pid>
```

其中 `-p <pid>` 表示只采集指定进程。

## 采集建议

- 纯在线阶段采集 2 到 3 次。
- 混部稳定阶段采集 2 到 3 次。
- 每次记录业务 P99、QPS、离线任务状态、采集时间和采集范围。
- 两个阶段使用相同采样时长、相同采集范围和相同业务压测参数。
- 如果是进程级采集，确认纯在线和混部阶段采集的是同一个在线业务进程或同一角色的进程。
