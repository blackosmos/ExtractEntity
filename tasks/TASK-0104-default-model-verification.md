# TASK-0104：核验默认开源自动分割模型

状态：Draft
依赖：可访问项目一手代码、模型卡、权重和许可来源；TASK-0102。
权威文档：`docs/architecture/model-adapters.md`、`models/README.md`、`docs/quality/evaluation-dataset.md`。

## 目标与范围

使用一手资料对 BiRefNet 与必要候选进行小型技术可行性及代码/权重许可核验，固定修订、哈希、资源需求和 manifest 条目。
不实现生产 adapter，不用宣传图代替项目评测。

## 验收标准

代码/权重来源与许可分开记录；修订可复现；本地权重通过 SHA-256；至少一个授权样本有技术 smoke 结果；未满足时不选定默认模型。

## Ready 前细化

在网络可用后列出一手 URL、实验配置、权重落盘/清理方式和不进入 Git 的报告路径；不得在 Draft 阶段凭记忆预填许可。
