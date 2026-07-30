# TASK-0105：实现默认分割模型适配器

状态：Draft
依赖：TASK-0102、TASK-0104。
权威文档：`docs/architecture/model-adapters.md`、`docs/architecture/system-overview.md`、`models/README.md`。

## 目标与范围

将已核验模型隔离在 infrastructure adapter，实现预处理、本地权重加载、坐标/尺寸映射与 `SegmentationCandidate` 输出。
覆盖缺权重、哈希错误、CPU smoke 和 fake backend；不实现 Matting、CLI 或 UI。

## 验收标准

满足现有 Protocol；不 import 下载；输出与修正方向后原图对齐；单元测试不加载大模型；显式 real-model smoke 可离线运行。

## Ready 前细化

由 TASK-0104 的已选模型固定 adapter 模块、optional dependency、fake backend 与显式 real-model marker/命令，并记录 CPU/显存环境限制。
