# ExtractEntity 文档地图

状态：Accepted
维护责任：项目负责人
最后审阅：2026-07-30

本目录是项目知识的持久化入口。聊天记录不是项目事实的权威来源。

## 去哪里查找信息

| 问题 | 权威文档 |
|---|---|
| 为什么开发、怎样才算成功 | [产品愿景](product/product-vision.md) |
| 用户最终如何操作 | [用户工作流](product/user-workflow.md) |
| 产品必须满足哪些可追踪需求 | [功能与非功能需求](product/requirements.md) |
| Mask、Alpha 等术语是什么意思 | [项目术语](product/terminology.md) |
| 当前明确不做什么 | [范围边界](product/out-of-scope.md) |
| 系统如何分层 | [系统总览](architecture/system-overview.md) |
| 图片数据如何流动 | [处理流水线](architecture/processing-pipeline.md) |
| 如何替换和接入模型 | [模型适配器](architecture/model-adapters.md) |
| 为什么作出架构选择 | [ADR 索引](decisions/README.md) |
| 如何证明功能和效果达标 | [验收标准](quality/acceptance-criteria.md) |
| 评测图片如何维护 | [评测数据集](quality/evaluation-dataset.md) |
| 当前开发阶段 | [当前里程碑](plans/current-milestone.md) |
| M0 为什么尚未退出 | [M0 退出审计](plans/m0-exit-audit.md) |
| 后续阶段按什么顺序推进 | [项目路线图](plans/roadmap.md) |
| 文件何时更新、归档或删除 | [仓库治理](development/repository-hygiene.md) |
| 如何创建开发环境 | [开发环境](development/setup.md) |
| 应运行哪些统一命令 | [开发命令](development/commands.md) |
| AI 这一次具体做什么 | [`tasks/`](../tasks/README.md) |

## 文档分类

- `product/`：稳定的产品目标、用户流程与范围。
- `architecture/`：系统边界、组件职责、依赖方向和数据契约。
- `decisions/`：具有长期影响的决策及其原因。
- `quality/`：功能验收、视觉评测、回归与已知限制。
- `development/`：开发环境、命令、代码规则和仓库治理。
- `plans/`：路线图、当前里程碑和阶段性计划。
- `../tasks/`：可独立实现和验收的工作单元；不是长期产品知识库。

## 文档维护规则

1. 同一事实只在一处定义；其他文件链接到它。
2. 文档必须标明 `Draft`、`Accepted` 或 `Superseded` 状态。
3. 用户行为变化与相应文档在同一个变更中更新。
4. 长期架构选择写入 ADR，临时实现过程写入任务完成记录。
5. 完成任务后清理重复、过期、无引用和纯过程性内容。
6. 更完整的保留与删除规则见[仓库治理](development/repository-hygiene.md)。

## 当前有意暂缓的文档

以下文档等对应实现任务进入 `Ready` 后再创建，避免为尚未验证的实现提前制造第二套事实来源：

- 前端、后端和文件系统细节：在相应架构任务确定技术方案后创建；
- 单项功能规格：在功能进入当前或下一里程碑、需求需要展开时创建；
- 模型 benchmark 结果和许可证清单：在模型调研任务记录具体版本、权重与实验数据时创建。
