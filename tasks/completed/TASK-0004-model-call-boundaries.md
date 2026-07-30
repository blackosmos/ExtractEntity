# TASK-0004：建立模型调用边界

状态：Completed

## 目标

建立最小应用层调用函数，在模型端口与调用方之间统一验证输入、提示和模型返回值，使错误或不可信的第三方适配器不能把错误类型或错位数据带入后续 pipeline。

## 相关文档与需求

- `AGENTS.md`
- `docs/architecture/system-overview.md`
- `docs/architecture/model-adapters.md`
- `docs/architecture/processing-pipeline.md`
- `docs/product/requirements.md`（FR-EXT-001、FR-COR-001、FR-COR-002、FR-COR-004、NFR-TEST-001、NFR-ARCH-001）
- `tasks/completed/TASK-0002-core-image-contracts.md`
- `tasks/completed/TASK-0003-model-interfaces.md`

## 包含范围

- 创建应用层模块，依赖领域端口而不依赖测试替身或具体模型；
- 提供自动分割调用边界，验证输入类型、返回候选类型及 Mask 与输入图片空间对齐；
- 提供交互分割调用边界，先验证提示与图片匹配，再验证返回候选；
- 提供 Matting 调用边界，验证 Trimap 输入对齐、返回 Alpha 类型及输出对齐；
- 保持模型抛出的异常原样传播，不用 `None` 或空结果吞掉失败；
- 用错误的结构化适配器证明调用边界能拒绝错误类型、宽错、高错和宽高互换；
- 用 TASK-0003 的测试替身验证成功、失败和调用记录；
- 更新架构文档，明确应用层是第三方模型输出的信任边界。

## 排除范围

- 图片解码、EXIF、resize、trimap 生成、RGBA 合成和文件导出；
- 真实模型、权重、设备、异步、重试、超时和进度回调；
- 多候选融合、质量评分和业务错误分类；
- UI、会话历史、撤销/重做实现；
- 通用 middleware、代理类、依赖注入容器或插件注册表。

## 验收标准

- 三类调用函数只依赖正式领域对象和 Protocol；
- 错误输入类型在模型调用前被拒绝；
- 提示或 Trimap 与输入图片不对齐时，模型不被调用；
- 返回值类型错误、Mask/Alpha 尺寸错误均被清晰拒绝；
- 合法返回值不被复制、转换或更改；
- 模型异常原样传播，测试能够证明调用已经发生；
- 测试覆盖自动分割、交互分割和 Matting 的成功与全部边界失败；
- 正式包不导入 `tests`，没有新增运行时依赖；
- Ruff、Pyright 和 pytest 在 Python 3.11/3.12 通过；
- 文档同步、任务完成记录和仓库清理完成。

## 预期变更

- `src/extract_entity/application/` 下的最小调用边界；
- `tests/unit/application/` 下的边界测试；
- 必要的 `tests/support/` 错误适配器；
- `docs/architecture/system-overview.md` 或 `model-adapters.md`。

## 风险与决策点

- 调用函数应保持窄且同步，不要提前演变为完整 orchestrator；
- `Protocol` 的静态结构不能替代运行时返回值检查，本任务正是集中这些检查；
- 错误类型当前使用 `TypeError` 和 `ValueError`，真实模型出现稳定错误分类需求后再建立异常层次；
- 不要重复领域对象已经完成的逐像素值验证，只验证调用上下文中的类型和空间关系。

## 完成记录

完成日期：2026-07-30

### 实际 API

- `run_segmentation(model, image) -> SegmentationCandidate`；
- `run_interactive_segmentation(model, image, prompt) -> SegmentationCandidate`；
- `run_matting(model, image, trimap) -> AlphaMatte`。

三个同步函数位于 `extract_entity.application`，只依赖正式领域类型和 Protocol。它们在调用前验证输入与空间对齐，在调用后复验不可信返回类型与尺寸，并原样返回合法对象。

### 验证结果

- Python 3.12：Ruff format、Ruff lint、Pyright 通过，pytest 70 项通过；
- Python 3.11：Ruff format、Ruff lint、Pyright 通过，pytest 70 项通过；
- 测试覆盖三类调用的成功路径、调用前错误类型/尺寸拒绝、调用后错误类型/宽错/高错/宽高互换拒绝、原对象保留、原异常传播和调用记录。

### 已知限制

- 边界当前是同步函数，不提供重试、超时、进度、错误分类或 pipeline 编排；
- 不在此处重复扫描领域值对象的每像素内容，仅复验当前调用上下文的类型和空间关系。

### 清理与交接

- 正式包未导入 `tests`，未新增依赖、通用中间件、代理、注入容器、缓存或临时产物；
- 系统架构已记录调用信任边界，并清理与已实现提示/候选契约冲突的过时表述；
- 下一任务建议：建立图片文件解码与 EXIF 方向规范化，不在本边界中混入文件 I/O。
