# State Lifecycle Race

## 适用场景

- 多线程执行、driver/operator close、异步 shuffle 或复杂类型序列化
- 问题表现为偶发 coredump，或与批次数、线程调度相关

## 典型症状

- `close()` 后仍有线程访问 operator
- 指针被置空后其他线程继续使用
- 单线程或小数据量不复现，大数据量、complex type、shuffle 后复现概率升高

## 关键观察点

- operator 生命周期由哪个线程负责
- close 是否会修改共享 vector/operator 指针
- 是否存在 `RunInternal()`、`close()`、serialize/deserialize 并发访问同一状态

## 已知案例

- Q006：complex type shuffle 场景中，`OmniDriver::close()` 修改 `operators_[i]`，与执行线程存在竞争，可能触发 SIGSEGV。

## 排查建议

1. 给 close、run、serialize、deserialize 入口增加线程 id 和对象地址日志。
2. 对被置空的共享指针，确认是否还有其他执行路径持有裸指针。
3. 如果问题只在 complex type shuffle 下出现，不要只看数据编码，也要检查生命周期和跨线程状态。
