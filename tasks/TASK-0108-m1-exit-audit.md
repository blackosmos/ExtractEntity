# TASK-0108：执行 M1 退出审计

状态：Draft
依赖：TASK-0101 至 TASK-0107 均完成并验证。
权威文档：`docs/plans/roadmap.md`、`docs/product/requirements.md`、`docs/quality/acceptance-criteria.md`。

## 目标与范围

逐项验证 M1 的安装、解码、模型、RGBA/PNG、单图入口、smoke 数据和质量证据，记录环境限制并决定是否进入 M2。
不实现新功能，不把窄测试或空数据集当作产品质量证明。

## 验收标准

所有 M1 退出项均有直接证据和状态；干净环境与 CI 双版本通过；真实 smoke 报告经人工复核；未满足时不切换 M2。

## Ready 前细化

待前置任务完成后根据实际命令、资产版本和 M1 问题表建立逐条证据清单，审计只更新状态与下一里程碑入口，不夹带功能实现。
