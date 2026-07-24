# TPC-DS 99 查询 × OmniOperator 算子覆盖映射

> **用途**：当你优化某个 OmniOperator 算子后，快速定位哪些 TPC-DS 查询最能体现加速效果，形成"优化 → 收益"的可观测闭环。
>
> **分析方法**：基于 SQL 结构静态推断物理算子。实际物理计划由 CBO/统计信息决定，可能存在偏差；建议结合 Spark UI 执行计划二次确认。

---

## 一、算子 → 查询速查表

### 1.1 HashAggregate（GROUP BY 聚合）

**所有查询均包含**，但以下查询聚合计算量特别大，优化 HashAggregate 收益最显著：

| 优先级 | 查询 | 原因 |
|--------|------|------|
| ★★★ | Q4, Q5, Q14, Q23, Q77, Q80 | 多渠道 UNION ALL + ROLLUP，聚合量极大 |
| ★★★ | Q18, Q27, Q36, Q67, Q86 | ROLLUP 多维聚合，产生大量中间 group |
| ★★★ | Q64, Q72 | 超多表 JOIN 后的大规模聚合 |
| ★★ | Q2, Q11, Q31, Q59, Q74, Q75 | CTE + 多路自连接后聚合 |
| ★★ | Q13, Q48, Q85, Q91 | 复杂多 OR 谓词下的全局聚合 |

---

### 1.2 HashJoin / BroadcastHashJoin

绝大多数查询含 HashJoin，以下为 **JOIN 表数量 ≥ 5 且数据量大** 的高价值子集：

| 优先级 | 查询 | JOIN 表数 | 特征 |
|--------|------|-----------|------|
| ★★★ | Q64 | 15+ | 最大规模多维事实自连接，JOIN 成本极高 |
| ★★★ | Q72 | 9 | 多日期维 + 不等式日期谓词，数据倾斜风险 |
| ★★★ | Q17, Q25, Q29 | 8 | 三事实表 + 多日期维联结 |
| ★★★ | Q85, Q91 | 8 | 多客户/退货维连接 |
| ★★ | Q6, Q8, Q16, Q19, Q94, Q95 | 5~6 | 含子查询/EXISTS 的复杂 JOIN |
| ★★ | Q66 | 6 | UNION ALL 两事实 + 月矩阵 |

**BroadcastHashJoin 敏感查询**（小维表 + 大事实表，优化广播 JOIN 构建阶段）：

`Q3, Q7, Q15, Q26, Q42, Q43, Q52, Q55, Q96` — 事实表 × 3~4 维表，维表较小，典型 Broadcast 场景。

---

### 1.3 窗口函数（WindowAgg）

优化 Window 算子（排序+分区+聚合）后，以下查询收益最直接：

| 优先级 | 查询 | 窗口特征 |
|--------|------|---------|
| ★★★ | Q47, Q57 | CTE + 三路 lag/lead 窗口自连接，多次窗口计算 |
| ★★★ | Q51 | FULL OUTER JOIN + 多列累计窗口，最复杂窗口 |
| ★★★ | Q36, Q67, Q70, Q86 | ROLLUP + rank() 窗口排名 |
| ★★ | Q44, Q49 | 双 rank 子查询 + 配对连接 |
| ★★ | Q12, Q20, Q98 | 品类收入窗口占比（三渠道版本） |
| ★★ | Q53, Q63, Q89 | 月均偏差窗口（三种维度版本） |

---

### 1.4 Sort / TopN

优化排序算子（含 TopN 剪枝）：

| 优先级 | 查询 | 特征 |
|--------|------|------|
| ★★★ | Q4, Q5, Q77, Q80 | 超复杂 UNION + ROLLUP 后排序，数据量最大 |
| ★★★ | Q64 | 超大规模 JOIN 后排序 |
| ★★ | Q49, Q67, Q70 | UNION ALL 三渠道后 TopN |
| ★ | Q3, Q7, Q15, Q42, Q52, Q55 | 简单三表 TopN，适合做基线对比 |

---

### 1.5 Sort（无 LIMIT，纯排序）

`Q13, Q24, Q31, Q38, Q64, Q71, Q87, Q91, Q97, Q98` — 无 LIMIT，需完整排序，对排序优化最敏感。

---

### 1.6 CartesianProduct（笛卡尔积）

优化 CartesianProduct 算子后：

| 查询 | 特征 |
|------|------|
| Q28 | 6 个独立子查询无连接条件，笛卡尔合并为一行宽表 |
| Q61 | 两标量子查询叉积，计算促销/非促销占比 |
| Q88 | 8 段 COUNT 叉积一行，半小时段分布统计 |
| Q90 | 两 COUNT 叉积，上午/下午比值 |

---

### 1.7 FullOuterJoin

`Q51`（网/店累计销售 FULL OUTER JOIN），`Q97`（店/目录(客,品)全外连接三分类计数）

---

### 1.8 子查询 / EXISTS / IN

优化相关子查询下推、半连接转换后：

| 优先级 | 查询 | 子查询类型 |
|--------|------|-----------|
| ★★★ | Q8 | INTERSECT + 巨型 IN 列表 + 派生表 |
| ★★★ | Q16, Q94, Q95 | EXISTS + NOT EXISTS（多仓无退货） |
| ★★ | Q1, Q30, Q81 | 相关子查询比均值（三渠道版本） |
| ★★ | Q6, Q21, Q32, Q45, Q65, Q92 | 相关标量子查询作过滤条件 |
| ★★ | Q10, Q35, Q69 | 多 EXISTS 人口统计过滤 |

---

### 1.9 Filter（复杂谓词）

对 Filter 代码生成/向量化优化最敏感：

`Q13, Q48, Q85` — 多 OR 复合谓词，无 ORDER BY，Filter 是主瓶颈。
`Q9` — 多 CASE WHEN COUNT 子查询，纯谓词计算密集。

---

### 1.10 Union / UNION ALL

`Q2, Q5, Q14, Q23, Q33, Q49, Q54, Q56, Q60, Q66, Q71, Q75, Q76, Q77, Q80` — 含 UNION ALL 多渠道拼盘，Exchange 量大。

---

## 二、按查询复杂度分级

### 复杂度：complex（大综合测试，最能体现系统级优化）

`Q4, Q5, Q8, Q14, Q16, Q18, Q23, Q24, Q31, Q36, Q39, Q44, Q47, Q49, Q51, Q53, Q54, Q57, Q63, Q64, Q66, Q67, Q70, Q72, Q74, Q75, Q77, Q78, Q80, Q86, Q89, Q94, Q95`

### 复杂度：medium（单算子优化的干净测量场景）

`Q1, Q2, Q6, Q7, Q9, Q10, Q12, Q13, Q15, Q17, Q19, Q20, Q21, Q22, Q25, Q26, Q27, Q28, Q29, Q30, Q32, Q33, Q34, Q35, Q37, Q38, Q40, Q41, Q43, Q45, Q46, Q48, Q50, Q56, Q58, Q59, Q60, Q61, Q62, Q65, Q68, Q69, Q71, Q73, Q76, Q79, Q81, Q82, Q83, Q84, Q85, Q87, Q88, Q90, Q91, Q92, Q93, Q97, Q99`

### 复杂度：simple（基线测量 / 回归验证）

`Q3, Q7, Q15, Q26, Q42, Q52, Q55, Q84, Q96`

---

## 三、按算子优化场景的推荐测试集

### 场景 A：优化 HashAggregate（含 ROLLUP / 部分聚合）
**首选集（必跑）**：Q4, Q5, Q18, Q27, Q36, Q67, Q77, Q86
**验证集**：Q2, Q11, Q14, Q64, Q72, Q80

---

### 场景 B：优化 HashJoin / BroadcastHashJoin
**首选集（大表）**：Q17, Q25, Q29, Q64, Q72, Q85, Q91
**首选集（小表 Broadcast）**：Q3, Q7, Q42, Q52, Q55, Q96
**验证集**：Q19, Q46, Q68, Q79

---

### 场景 C：优化 WindowAgg（窗口聚合/排名）
**首选集**：Q47, Q51, Q57, Q36, Q67
**验证集**：Q12, Q20, Q44, Q49, Q53, Q63, Q70, Q86, Q89, Q98

---

### 场景 D：优化 Sort / TopN
**首选集（大数据量排序）**：Q4, Q5, Q64, Q77, Q80
**首选集（TopN 剪枝）**：Q1, Q3, Q15, Q42
**纯排序无 LIMIT（Sort Only）**：Q13, Q31, Q71, Q91, Q98

---

### 场景 E：优化 CartesianProduct
**必跑**：Q28, Q61, Q88, Q90

---

### 场景 F：优化子查询（相关子查询/EXISTS 转半连接）
**首选集**：Q8, Q16, Q94, Q95
**验证集**：Q1, Q6, Q10, Q30, Q35, Q65

---

### 场景 G：优化 Filter（复杂谓词向量化）
**首选集**：Q13, Q48, Q85, Q9
**验证集**：Q7, Q26, Q27

---

### 场景 H：优化 FullOuterJoin
**必跑**：Q51, Q97

---

## 四、逐条查询速查表（全99条）

| Q# | 主要算子 | Join表数 | 窗口 | TopN | CTE数 | 聚合复杂度 | 业务场景 |
|----|---------|---------|------|------|-------|-----------|---------|
| Q1 | HashJoin,HashAgg,Filter,Subquery,TopN | 3 | N | Y | 1 | medium | 超额退货客户按店均值筛选 |
| Q2 | HashJoin,HashAgg,Union,Sort | 6 | N | N | 2 | medium | 全渠道日销售周同比对比 |
| Q3 | HashJoin,HashAgg,TopN | 3 | N | Y | 0 | simple | 品牌年门店销售 TopN |
| Q4 | HashJoin,HashAgg,Union,TopN | 6 | N | Y | 1 | complex | 三渠道年毛利六表自连接同比 |
| Q5 | HashJoin,HashAgg,Union,TopN | 6 | N | Y | 3 | complex | 门店/目录/网站销退 ROLLUP |
| Q6 | HashJoin,HashAgg,Filter,Subquery,TopN | 5 | N | Y | 0 | medium | 分类均价带月份子查询过滤 |
| Q7 | HashJoin,HashAgg,Filter,TopN | 5 | N | Y | 0 | simple | 人口统计+促销商品均值 |
| Q8 | HashJoin,HashAgg,Filter,Subquery,TopN | 5 | N | Y | 0 | complex | INTERSECT+巨型IN邮编子查询 |
| Q9 | HashAgg,Filter,Subquery | 1 | N | N | 0 | medium | 单表多CASE分桶聚合 |
| Q10 | HashJoin,HashAgg,Filter,Subquery,TopN | 3 | N | Y | 0 | medium | 三EXISTS人口分组计数 |
| Q11 | HashJoin,HashAgg,Union,TopN | 4 | N | Y | 1 | complex | 店/网两年净支出自连接同比 |
| Q12 | HashJoin,HashAgg,WindowAgg,TopN | 3 | Y | Y | 0 | medium | 网店品类窗口收入占比 |
| Q13 | HashJoin,HashAgg,Filter | 6 | N | N | 0 | medium | 多OR谓词全局聚合 |
| Q14 | HashJoin,HashAgg,Union,Subquery,TopN | 4+ | N | Y | 4 | complex | 跨渠道共同品类+周同比（双语句） |
| Q15 | HashJoin,HashAgg,Filter,TopN | 4 | N | Y | 0 | simple | 邮编地理过滤目录销售 |
| Q16 | HashJoin,HashAgg,Filter,Subquery,TopN | 5 | N | Y | 0 | complex | EXISTS+NOT EXISTS多仓无退货 |
| Q17 | HashJoin,HashAgg,TopN | 8 | N | Y | 0 | medium | 三事实多日期维标准差 |
| Q18 | HashJoin,HashAgg,TopN | 7 | N | Y | 0 | complex | 目录ROLLUP地理+商品 |
| Q19 | HashJoin,HashAgg,TopN | 6 | N | Y | 0 | medium | 客户/店地址不同邮编过滤 |
| Q20 | HashJoin,HashAgg,WindowAgg,TopN | 3 | Y | Y | 0 | medium | 目录品类窗口收入占比 |
| Q21 | HashJoin,HashAgg,Subquery,TopN | 4 | N | Y | 0 | medium | 库存前后量比过滤 |
| Q22 | HashJoin,HashAgg,TopN | 3 | N | Y | 0 | medium | 库存ROLLUP均价排序 |
| Q23 | HashJoin,HashAgg,Union,Subquery,TopN | 3+ | N | Y | 6 | complex | 高频商品+大客户目录/网销（双语句） |
| Q24 | HashJoin,HashAgg,Filter,Subquery,Sort | 6 | N | N | 2 | complex | 颜色过滤与全局均值比（双语句） |
| Q25 | HashJoin,HashAgg,TopN | 8 | N | Y | 0 | medium | 三事实跨月联结按店商品 |
| Q26 | HashJoin,HashAgg,TopN | 5 | N | Y | 0 | simple | 目录+促销人口商品均值 |
| Q27 | HashJoin,HashAgg,TopN | 5 | N | Y | 0 | medium | 门店州ROLLUP+grouping |
| Q28 | HashAgg,Filter,CartesianProduct | 0 | N | Y | 0 | medium | 六区间独立聚合笛卡尔宽表 |
| Q29 | HashJoin,HashAgg,TopN | 8 | N | Y | 0 | medium | 三事实标准差版 |
| Q30 | HashJoin,HashAgg,Subquery,TopN | 3 | N | Y | 1 | medium | 网站退货超额客户（州均值） |
| Q31 | HashJoin,HashAgg,Filter,Sort | 6 | N | N | 2 | complex | 县×季度店/网销售同比 |
| Q32 | HashJoin,HashAgg,Subquery,TopN | 3 | N | Y | 0 | medium | 目录折扣高于1.3倍均值 |
| Q33 | HashJoin,HashAgg,Union,Subquery,TopN | 4 | N | Y | 4 | medium | 家居三渠道按制造商汇总 |
| Q34 | HashJoin,HashAgg,TopN | 4 | N | Y | 0 | medium | 票级计数过滤后客户明细 |
| Q35 | HashJoin,HashAgg,Subquery,TopN | 3 | N | Y | 0 | medium | 三EXISTS州+人口多计数列 |
| Q36 | HashJoin,HashAgg,WindowAgg,TopN | 4 | Y | Y | 0 | complex | 品类毛利ROLLUP+rank窗口 |
| Q37 | HashJoin,HashAgg,TopN | 4 | N | Y | 0 | medium | 目录+库存同商品交集 |
| Q38 | HashAgg,Filter,Subquery | 3 | N | N | 0 | medium | 三渠道INTERSECT客户日计数 |
| Q39 | HashJoin,HashAgg,Filter,Sort | 3 | N | N | 4 | complex | 库存变异系数月环比（双语句） |
| Q40 | HashJoin,HashAgg,TopN | 5 | N | Y | 0 | medium | 目录销退左连接按仓州商品 |
| Q41 | HashAgg,Filter,Subquery,TopN | 1 | N | Y | 0 | medium | 制造商内复杂OR条件过滤品名 |
| Q42 | HashJoin,HashAgg,TopN | 3 | N | Y | 0 | simple | 经理品类年销售排序 |
| Q43 | HashJoin,HashAgg,TopN | 3 | N | Y | 0 | medium | 门店按周日分列CASE销售额 |
| Q44 | HashJoin,HashAgg,WindowAgg,Subquery,TopN | 4 | Y | Y | 0 | complex | 商品净利Top/Bottom rank配对 |
| Q45 | HashJoin,HashAgg,Subquery,TopN | 5 | N | Y | 0 | medium | 邮编+素数商品IN过滤网站销售 |
| Q46 | HashJoin,HashAgg,TopN | 5 | N | Y | 0 | medium | 购票城市≠常住城市票级聚合 |
| Q47 | HashJoin,HashAgg,WindowAgg,Subquery,TopN | 4 | Y | Y | 2 | complex | 店月均窗口+三路lag/lead自连接 |
| Q48 | HashJoin,HashAgg,Filter | 5 | N | N | 0 | medium | 多OR全表sum（Q13精简版） |
| Q49 | HashJoin,HashAgg,WindowAgg,Union,TopN | 4 | Y | Y | 0 | complex | 三渠道退货率rank+UNION取Top10 |
| Q50 | HashJoin,HashAgg,TopN | 5 | N | Y | 0 | medium | 店退货滞后天数直方图CASE |
| Q51 | HashJoin,HashAgg,WindowAgg,FullOuterJoin,TopN | 4 | Y | Y | 2 | complex | 网/店累计窗口FULL OUTER JOIN |
| Q52 | HashJoin,HashAgg,TopN | 3 | N | Y | 0 | simple | 经理品牌月销售排序 |
| Q53 | HashJoin,HashAgg,WindowAgg,TopN | 4 | Y | Y | 0 | complex | 制造商季度窗口均值偏差 |
| Q54 | HashJoin,HashAgg,Union,Subquery,TopN | 6 | N | Y | 4 | complex | 图书客户转门店收入分段计数 |
| Q55 | HashJoin,HashAgg,TopN | 3 | N | Y | 0 | simple | 经理品牌月销售总额排序 |
| Q56 | HashJoin,HashAgg,Union,Subquery,TopN | 4 | N | Y | 4 | medium | 颜色商品三渠道汇总 |
| Q57 | HashJoin,HashAgg,WindowAgg,TopN | 4 | Y | Y | 2 | complex | 呼叫中心月窗口+相邻月偏差 |
| Q58 | HashJoin,HashAgg,Subquery,TopN | 3 | N | Y | 3 | medium | 三渠道同周销售偏差百分比 |
| Q59 | HashJoin,HashAgg,TopN | 4 | N | Y | 1 | medium | 门店周日销售年度对比 |
| Q60 | HashJoin,HashAgg,Union,Subquery,TopN | 4 | N | Y | 4 | medium | 儿童类三渠道汇总 |
| Q61 | HashJoin,HashAgg,CartesianProduct,TopN | 7 | N | Y | 0 | medium | 促销/非促销运动品占比（叉积） |
| Q62 | HashJoin,HashAgg,TopN | 5 | N | Y | 0 | medium | 网站发货滞后天数CASE直方图 |
| Q63 | HashJoin,HashAgg,WindowAgg,TopN | 4 | Y | Y | 0 | complex | 经理维度月均偏差窗口 |
| Q64 | HashJoin,HashAgg,Filter,Sort | 15+ | N | N | 2 | complex | 最大规模多维事实两年对比 |
| Q65 | HashJoin,HashAgg,Subquery,TopN | 3 | N | Y | 0 | complex | 店商品收入低于店均10%滞销品 |
| Q66 | HashJoin,HashAgg,Union,TopN | 6 | N | Y | 0 | complex | 仓网/目录月矩阵+坪效 |
| Q67 | HashJoin,HashAgg,WindowAgg,TopN | 4 | Y | Y | 0 | complex | 门店商品ROLLUP+rank过滤Top100 |
| Q68 | HashJoin,HashAgg,TopN | 5 | N | Y | 0 | medium | 购票异城票级聚合（Q46变体） |
| Q69 | HashJoin,HashAgg,Subquery,TopN | 3 | N | Y | 0 | medium | EXISTS+NOT EXISTS仅门店客户 |
| Q70 | HashJoin,HashAgg,WindowAgg,Subquery,TopN | 3 | Y | Y | 0 | complex | 州ROLLUP+rank+TOP5子查询 |
| Q71 | HashJoin,HashAgg,Union,Sort | 4 | N | N | 0 | medium | 三渠道时段品牌按小时汇总 |
| Q72 | HashJoin,HashAgg,TopN | 9 | N | Y | 0 | complex | 多日期维不等式+促销退货过滤 |
| Q73 | HashJoin,HashAgg,TopN | 4 | N | Y | 0 | medium | 票级计数过滤客户明细（Q34变体） |
| Q74 | HashJoin,HashAgg,Union,TopN | 4 | N | Y | 1 | complex | 店/网两年净支付四路自连接 |
| Q75 | HashJoin,HashAgg,Union,TopN | 4 | N | Y | 1 | complex | 运动品三渠道净销量年同比降幅 |
| Q76 | HashJoin,HashAgg,Union,TopN | 3 | N | Y | 0 | medium | 三渠道可空列分渠道计数 |
| Q77 | HashJoin,HashAgg,Union,TopN | 多 | N | Y | 6 | complex | 多CTE+LEFT JOIN销退ROLLUP |
| Q78 | HashJoin,HashAgg,TopN | 3 | N | Y | 3 | complex | 店与网/目录同客同品量比 |
| Q79 | HashJoin,HashAgg,TopN | 4 | N | Y | 0 | medium | 周一促销家庭员工规模过滤 |
| Q80 | HashJoin,HashAgg,Union,TopN | 5 | N | Y | 3 | complex | 高价促销三渠道销退ROLLUP |
| Q81 | HashJoin,HashAgg,Subquery,TopN | 3 | N | Y | 1 | medium | 目录退货超额客户（州均值） |
| Q82 | HashJoin,HashAgg,TopN | 4 | N | Y | 0 | medium | 库存与门店销售交集（Q37变体） |
| Q83 | HashJoin,HashAgg,Subquery,TopN | 3 | N | Y | 3 | medium | 三渠道退货量对齐偏差 |
| Q84 | HashJoin,Filter,TopN | 6 | N | Y | 0 | simple | 收入带+退货人口关联出客户 |
| Q85 | HashJoin,HashAgg,TopN | 8 | N | Y | 0 | medium | 网站退货原因多维均值 |
| Q86 | HashJoin,HashAgg,WindowAgg,TopN | 3 | Y | Y | 0 | complex | 网销品类ROLLUP+rank |
| Q87 | HashAgg,Filter,Subquery | 3 | N | N | 0 | medium | EXCEPT链仅门店客户集合计数 |
| Q88 | HashAgg,Filter,CartesianProduct | 0 | N | N | 0 | medium | 八段COUNT叉积半小时段分布 |
| Q89 | HashJoin,HashAgg,WindowAgg,TopN | 4 | Y | Y | 0 | complex | 门店月销售对店月均偏差 |
| Q90 | HashAgg,Filter,CartesianProduct,TopN | 0 | N | Y | 0 | simple | 上午/下午网页笔数比 |
| Q91 | HashJoin,HashAgg,Sort | 8 | N | N | 0 | medium | 多客户维目录退货损失 |
| Q92 | HashJoin,HashAgg,Subquery,TopN | 3 | N | Y | 0 | medium | 网站超额折扣（Q32网站版） |
| Q93 | HashJoin,HashAgg,TopN | 4 | N | Y | 0 | medium | 特定退货原因有效销售额按客 |
| Q94 | HashJoin,HashAgg,Subquery,TopN | 5 | N | Y | 0 | complex | 网站多仓无退货订单EXISTS |
| Q95 | HashJoin,HashAgg,Subquery,TopN | 5 | N | Y | 1 | complex | 多仓有退货网单IN子查询 |
| Q96 | HashJoin,HashAgg,TopN | 4 | N | Y | 0 | simple | 时段门店家庭过滤COUNT |
| Q97 | HashAgg,FullOuterJoin | 2 | N | N | 2 | medium | 店/目录全外连接三分类计数 |
| Q98 | HashJoin,HashAgg,WindowAgg,Sort | 3 | Y | N | 0 | medium | 门店品类窗口收入占比（Q12门店版） |
| Q99 | HashJoin,HashAgg,TopN | 5 | N | Y | 0 | medium | 目录发货滞后直方图（Q62目录版） |

---

## 五、跨渠道同构查询族（回归测试套件）

优化某一算子后，同构查询族可作为**回归对照组**，验证优化对所有渠道一致有效：

| 查询族 | 成员 | 共同特征 |
|--------|------|---------|
| 窗口占比族 | Q12, Q20, Q98 | 渠道 × 品类收入窗口占比 |
| 超额退货族 | Q1, Q30, Q81 | 相关子查询比均值，三渠道版本 |
| 折扣超额族 | Q32, Q92 | 相关子查询1.3倍均值过滤，目录/网站 |
| 发货直方图族 | Q62, Q99 | CASE分段滞后天数，网站/目录 |
| 三渠道汇总族 | Q33, Q56, Q60 | 三CTE IN子查询三渠道按制造商 |
| 月均偏差族 | Q47, Q53, Q57, Q63, Q89 | 窗口均值偏差，多维度版本 |
| 票级聚合族 | Q46, Q68 | 购票异城过滤票级聚合 |
| 三事实联结族 | Q17, Q25, Q29 | 三大事实表+多日期维，8表JOIN |
| 年同比自连接族 | Q4, Q11, Q74, Q75 | CTE+多路自连接年度对比 |

---

## 六、使用指南

### 快速定位测试集的方法

```
1. 确定优化的算子 → 查第一章对应小节 → 取"首选集"
2. 跑首选集得到加速比
3. 跑对应"验证集"确认无回归
4. 用"同构查询族"做对照组，确认三渠道一致
5. 跑 complex 级别全集做系统级验证
```

### 性能结论可信度判断

| 加速比一致性 | 结论强度 |
|-------------|---------|
| 首选集 + 验证集均提升 | ★★★ 强证据 |
| 首选集提升、验证集持平 | ★★ 中等证据 |
| 仅首选集提升 | ★ 弱证据，需检查物理计划是否命中目标算子 |
| 同构族不一致 | 需检查是否某渠道走了不同物理计划 |

### 常见陷阱

- **物理计划与预期不符**：统计信息过时可能导致 BroadcastHashJoin ↔ SortMergeJoin 切换，跑前先 `ANALYZE TABLE`
- **CTE 物化**：Spark 可能将 CTE 物化为临时表，影响算子分布，关注 Q4/Q5/Q47/Q57 等多 CTE 查询
- **数据倾斜**：Q72 含不等式日期谓词，Q4/Q64 多路自连接，均有倾斜风险，注意 skew join 配置
- **ROLLUP 行数膨胀**：Q18/Q27/Q36 ROLLUP 产生 NULL 行，聚合量远超预期，需预热后测量
