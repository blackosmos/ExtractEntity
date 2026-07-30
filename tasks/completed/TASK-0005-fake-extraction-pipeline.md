# TASK-0005：建立假实现提取 Pipeline

状态：Completed

## 目标

使用正式应用调用边界和测试模型替身，建立一条完全在内存中运行的最小提取流程：自动分割候选转为确定性 Trimap，交给 Matting 端口生成 Alpha，并返回 `ExtractionResult`。该流程用于验证组件协作，不代表最终质量算法。

## 相关文档与需求

- `AGENTS.md`
- `docs/architecture/processing-pipeline.md`
- `docs/architecture/system-overview.md`
- `docs/product/requirements.md`（FR-EXT-001、FR-EXT-002、FR-EXT-003、NFR-TEST-001、NFR-ARCH-001）
- `docs/quality/acceptance-criteria.md`（AC-ALPHA-001）
- `tasks/completed/TASK-0002-core-image-contracts.md`
- `tasks/completed/TASK-0003-model-interfaces.md`
- `tasks/completed/TASK-0004-model-call-boundaries.md`

## 包含范围

- 定义不可变、经验证的 Trimap 阈值配置，明确 `background < foreground` 且都位于 `[0, 1]`；
- 将 `ProbabilityMask` 按确定性规则转换为同尺寸 Trimap：低概率为背景、高概率为前景、中间为未知；
- 建立同步、单图、内存 pipeline，依次调用 `run_segmentation`、trimap 转换和 `run_matting`；
- 返回包含原始 `ImageDocument` 与最终 `AlphaMatte` 的 `ExtractionResult`；
- 使用 fake/spy 验证调用顺序、参数 identity、生成 Trimap、空间对齐和异常传播；
- 测试分割失败、非法候选、Matting 失败和错误输出不会被吞掉；
- 更新处理流水线文档，明确这是 M0 骨架，后续可替换 trimap 策略。

## 排除范围

- 图片文件解码、EXIF、RGBA 合成、PNG 编码和文件 I/O；
- 真实模型、模型权重、NumPy、Pillow、PyTorch 或 Web 框架；
- 腐蚀、膨胀、自适应边缘宽度、多尺度 Matting 和候选融合；
- 交互提示、重试、进度、异步、缓存和批处理；
- 将测试替身或固定测试输出放入正式运行时包。

## 验收标准

- 合法 0、1 和中间概率按文档规则映射为三种 Trimap 值；
- 阈值类型、有限性、范围和顺序错误被清晰拒绝；
- Pipeline 只依赖模型 Protocol 和正式领域/应用边界，不依赖 `tests`；
- 自动分割恰好调用一次，Matting 恰好调用一次且收到生成的同尺寸 Trimap；
- `ExtractionResult.image` 是原输入对象，Alpha 是 Matting 返回的原对象；
- 分割或 Matting 的异常和边界校验错误原样传播，不产生部分成功结果；
- 测试覆盖非方形图、阈值边界、成功调用、空间错配和两阶段失败；
- 没有新增运行时依赖，Ruff、Pyright 和 pytest 在 Python 3.11/3.12 通过；
- 文档、完成记录和仓库清理同步完成。

## 预期变更

- `src/extract_entity/application/` 下的 trimap 转换与最小 pipeline；
- `tests/unit/application/` 下的转换与 pipeline 测试；
- `docs/architecture/processing-pipeline.md`；
- 必要时更新系统架构。

## 风险与决策点

- 阈值转换只是可替换的 M0 baseline，不能在后续质量评测前宣称为最终 Matting 策略；
- 阈值等于边界时的归类必须固定并测试，避免浮点比较歧义；
- Pipeline 不应保存文件、选择模型、管理权重或知道具体模型名称；
- 不要为了一个顺序流程引入 DAG、步骤注册表或通用工作流框架。

## 完成记录

完成日期：2026-07-30

### 实际实现

- 新增不可变 `TrimapThresholds`，严格校验浮点类型、有限性、`[0, 1]` 范围与阈值顺序；
- 新增 `probability_mask_to_trimap`，以 `<= background`、`>= foreground` 和两者之间的明确边界语义生成同尺寸 Trimap；
- 新增同步 `extract_image` 应用流程，依次经过正式分割调用边界、Trimap 转换、正式 Matting 调用边界和 `ExtractionResult`；
- 流程入口先校验阈值配置，非法配置不会调用任一模型；
- 增加成功路径、非方形尺寸、阈值边界、调用顺序、identity 保留、错位输出、非法输出与异常原样传播测试。

### 验证结果

- Python 3.11.15：Ruff format、Ruff lint、Pyright 严格模式和 95 项 pytest 全部通过；
- Python 3.12.13：Ruff format、Ruff lint、Pyright 严格模式和 95 项 pytest 全部通过；
- `pyproject.toml` 运行时依赖仍为空。

### 已知限制

- 当前 Trimap 转换只是 M0 确定性阈值基线，尚无形态学、自适应边缘或质量评测；
- 流程只处理单张内存图片，不负责解码、导出、交互、重试或模型生命周期。

### 清理与后续

- 未引入运行时依赖、模型资产、生成输出、缓存或临时调试文件；
- 后续任务应继续完成 M0 的权重与许可证治理、smoke 评测基础和 CI，不应将本阈值基线宣称为最终 Matting 策略。
