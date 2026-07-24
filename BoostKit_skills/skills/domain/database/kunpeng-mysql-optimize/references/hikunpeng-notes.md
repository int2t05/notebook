# hikunpeng Notes

## Source Links

- MySQL compute-path optimization: `https://www.hikunpeng.com/document/detail/zh/kunpengdbs/appAccelFeatures/mysqlcompathopt/kunpeng_mysqlrd_tx_003.html`
- MySQL binlog optimization: `https://www.hikunpeng.com/document/detail/zh/kunpengdbs/appAccelFeatures/mysqlbilog/kunpeng_mysqlbinlog_tx_003.html`
- MySQL network multipath optimization: `https://www.hikunpeng.com/document/detail/zh/kunpengdbs/appAccelFeatures/nmo/kunpeng_mysql_dlj_zn_64_002.html`
- MySQL fine-grained lock optimization: `https://www.hikunpeng.com/document/detail/zh/kunpengdbs/appAccelFeatures/fglocktf/kunpengdbsmysqlfglock_20_0001.html`
- MySQL lock-free optimization: `https://www.hikunpeng.com/document/detail/zh/kunpengdbs/appAccelFeatures/lockftf/kunpengdbsmysqllockfree_20_0001.html`
- MySQL NUMA scheduling optimization: `https://www.hikunpeng.com/document/detail/zh/kunpengdbs/appAccelFeatures/numastf/kunpengdbsmysqlnuma_20_0001.html`
- CRC32 instruction optimization: `https://www.hikunpeng.com/document/detail/zh/kunpengdbs/appAccelFeatures/crc32iof/kunpengdbsmysqlcrc32_20_0001.html`

## Usage Rules

- Use hikunpeng docs to understand optimization goals, applicable scenarios, system configuration, and test methodology.
- Use bundled patches as the source of truth for concrete patch paths. When a same-version patch exists, rely on the patch contents.
- If a hikunpeng description disagrees with a bundled patch, state the difference directly and use the bundled same-version patch as the recommendation source.
- If hikunpeng describes an optimization but no bundled patch exists, classify it as a deployment/configuration direction or a patch-porting task.

## Common Categories

- Compute path: charset, comparison, LIKE, record/tuple compare, NEON/SVE, AArch64 unaligned access.
- Binlog: ordered commit, preallocated binlog, writeset map.
- Network multipath: multiple NICs, multiqueue, RSS/RPS/XPS, IRQ affinity, connection distribution; currently mostly system deployment work.
- Fine-grained locking: InnoDB lock_sys, table/record lock queue, deadlock detection, lock_sys mutex.
- Lock-free: ReadView, MVCC, trx_sys snapshot paths.
- NUMA: thread and memory-node affinity, buffer pool warmup, container cpuset/memset.
- CRC32: ARMv8 CRC32 intrinsic for InnoDB page/redo checksums.
- Text huge pages: iTLB/L1I frontend bottlenecks.
