# TASK-0107：建立 M1 真实物品 Smoke 评测

状态：Draft
依赖：TASK-0106；项目所有者提供或核验的样本与许可。
权威文档：`docs/quality/evaluation-dataset.md`、`docs/quality/acceptance-criteria.md`、`benchmarks/README.md`。

## 目标与范围

将 5–10 张授权明确的代表物品图加入 smoke manifest，对单图入口运行可重复的尺寸、RGBA、孔洞/附件备注和人工黑白背景检查。
本任务不以模型自身输出创建 Ground Truth，不修改 M2 定量阈值。

## 验收标准

每个资产来源/许可/哈希可核验；manifest 不为空；全部样本完成自动不变量和记录在案的人工检查；失败不被删除或替换黄金结果掩盖。

## Ready 前细化

资产到位后列出样本 ID/许可证据、Git 或 LFS 选择、评测命令、人工复核表和报告清理路径。
