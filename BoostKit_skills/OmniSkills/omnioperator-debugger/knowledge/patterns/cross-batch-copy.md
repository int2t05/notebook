# Cross Batch Copy

## 适用场景

- 上一批数据、累计缓存或共享缓冲区被当前批次错误复用

## 典型症状

- 当前批次结果混入历史批次内容
- 拷贝长度正确，但起始位置错误
- 边界 batch 更容易暴露问题
- 序列化前后 row count、offset、size 不一致
- complex type 的 offsets 或 child vector 复用了上一批残留数据

## 关键观察点

- copy 起点
- copy 长度
- 当前批次窗口
- 累计缓存是否被整段复制
- 每列是否有独立 batch 状态
- buffer 扩容或缩容时是否清理旧 offsets

## 已知案例

- Q006：complex type shuffle 中，proto vector 的 batch 状态没有按列维护，导致跨列、跨 batch 状态错位。
- Q006：`ArrayVector::Expand` 在 `needCapacity <= size` 时只改 size，不清理旧 offset，反序列化后出现负 size 或异常 offset。
- Q007：ExistenceJoin 的 `existJoinBuildIndex` 是累计缓存，但输出时从 begin 整段复制，没有按当前 output window 切片。

## 排查建议

1. 同时打印输入 batch 行数、输出 batch 行数、offset、copy length、缓存 size。
2. 对 complex type，额外打印 offsets 前后几位和 child vector size。
3. 如果状态是累计的，所有输出构造都必须显式带上当前窗口起点。
