# TASK-0002：定义核心图像数据契约

状态：Completed

## 目标

为图片、概率 Mask、二值 Mask、Trimap、Alpha 和提取结果建立明确、可验证且不依赖具体模型的内部数据契约，避免第三方张量语义扩散到应用层。

## 相关文档与需求

- `AGENTS.md`
- `docs/architecture/system-overview.md`
- `docs/architecture/processing-pipeline.md`
- `docs/product/terminology.md`
- `docs/product/requirements.md`（FR-EXT-002、FR-EXT-003、FR-EXPORT-002、NFR-TEST-001、NFR-ARCH-001）
- `docs/quality/acceptance-criteria.md`（AC-IO-002、AC-ALPHA-001）

## 包含范围

- 决定并记录核心数据对象的模块位置和依赖方向；
- 定义规范化 RGB 图片及其宽高、通道顺序、dtype 和 EXIF 后尺寸语义；
- 定义概率 Mask、二值 Mask、Trimap 和 Alpha Matte 的形状、dtype、数值范围及空间对齐规则；
- 定义最小 `ExtractionResult`，组合原图引用/数据、Alpha 和必要告警或元数据；
- 在对象构造边界拒绝形状错误、非有限值和越界值；
- 添加不依赖 NumPy、Pillow 或真实模型的单元测试，或先通过独立决策证明必须引入某个运行时依赖；
- 更新相关架构文档，使文档与实际类型一致。

## 排除范围

- 图片文件解码和 EXIF 实际处理；
- Mask resize、trimap 生成、Matting 和 RGBA 合成算法；
- 任何真实模型、模型权重或第三方张量适配器；
- UI、文件导出、benchmark 数据和性能优化；
- 为尚未使用的字段建立复杂继承层次或通用框架。

## 验收标准

- 每个核心对象具有唯一职责和明确的公开不变量；
- 坐标使用 `(x, y)`，数组维度使用文档化顺序，不出现未说明的宽高互换；
- Alpha 与概率数据是有限值且位于 `[0, 1]`；
- Trimap 只接受项目明确规定的三种值；
- Mask/Alpha 与关联图片尺寸不一致时产生清晰错误；
- 测试覆盖合法对象、错误 shape、错误 dtype、非有限值、越界值和尺寸不一致；
- 正式包不依赖测试代码，且未绑定任何具体模型；
- Ruff、Pyright 和 pytest 全部通过；
- 任务结束时完成仓库清理清单并记录下一任务建议。

## 预期变更

- `src/extract_entity/` 下的领域类型模块；
- `tests/` 下对应单元测试；
- `docs/architecture/system-overview.md`；
- 必要时更新 `docs/architecture/processing-pipeline.md` 和术语文档。

## 风险与决策点

- 标准库对象无法自然表达高效像素数组；本任务优先定义语义和验证边界，不应仅为便利提前引入重型图像依赖；
- dtype 与数据所有权策略会影响后续 NumPy/PyTorch 适配，若存在多种合理方案，应先记录轻量 ADR；
- 不要在领域对象中保存模型专有张量或设备状态。

## 完成记录

完成日期：2026-07-30

### 实际类型

- `ImageDocument`：宽高加行主序交错 RGB `bytes`；
- `ProbabilityMask` / `AlphaMatte`：宽高加不可变 `tuple[float, ...]`；
- `BinaryMask` / `Trimap`：宽高加经值域验证的 `bytes`；
- `ExtractionResult`：空间对齐的原图、Alpha 和不可变告警。

全部类型使用 frozen/slots dataclass，不依赖 NumPy、Pillow、模型张量或测试代码。

### 验证结果

- Python 3.12：Ruff format、Ruff lint、Pyright 通过，pytest 27 项通过；
- Python 3.11：Ruff format、Ruff lint、Pyright 通过，pytest 27 项通过；
- 单元测试覆盖尺寸、存储长度、dtype、非有限值、越界值、trimap 值域、坐标和图像/Alpha 空间不对齐。

### 已知限制

- 标准库存储优先表达稳定契约，不适合大图高性能计算；后续数组/张量转换应留在适配器边界。
- 本任务不保存文件来源或任意元数据，待真实用例出现后由独立任务扩展。
- 当前容器缺少 Hatchling，无法重新执行 editable install；测试使用 `PYTHONPATH=src` 验证，未改变 TASK-0001 已记录的环境限制。

### 清理与交接

- 未新增运行时依赖、权重、输出、缓存、临时脚本或本机路径；
- 架构文档已改为实际类型的权威说明，并删除 `ExtractionResult` 已包含 RGBA 预览的过时表述；
- 下一任务建议：定义模型无关接口及 fake/spy 测试替身，不接入真实模型。
