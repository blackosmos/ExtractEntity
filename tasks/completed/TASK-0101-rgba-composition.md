# TASK-0101：实现 RGBA 合成契约

状态：Completed

## 目标

使用原始 `ImageDocument` RGB 与对齐 `AlphaMatte` 生成不可变 packed straight-alpha RGBA 值对象，为后续 PNG 导出提供经测试的纯内存边界。

## 需求与依赖

- FR-EXT-002、FR-EXPORT-001、FR-EXPORT-002、NFR-QUALITY-001；
- 依赖已完成的 `ImageDocument`、`AlphaMatte` 和 `ExtractionResult`。
- 权威文档：`docs/architecture/processing-pipeline.md`、`docs/product/requirements.md`、`docs/quality/acceptance-criteria.md`。

## 包含范围

- 定义经尺寸、长度和字节语义校验的 RGBA 值对象；
- 将 `[0, 1]` Alpha 以明确、有测试的舍入规则转为 8-bit straight alpha；
- RGB 逐字节原样保留，不预乘、重绘或改变尺寸；
- 测试端点、中间值、非方形图和尺寸错位，同步处理流程文档。

## 排除范围

- Pillow、PNG 编码、文件 I/O、颜色管理和 EXIF；
- 分割、Matting、模型或 UI；
- 新运行时依赖。

## 验收标准

- 结果尺寸与输入相同且每像素严格为 RGBA 顺序；
- RGB 与原图字节完全一致，Alpha 0.0/1.0 精确映射到 0/255；
- 中间 Alpha 舍入规则无 Python bankers-rounding 歧义并有边界测试；
- 非法类型和空间错位在合成前拒绝；
- 无运行时依赖，双 Python 版本完整门禁通过。

## 预期变更与验证

- `src/extract_entity/domain/` 下的 RGBA 值对象和 `application/` 下的纯合成函数；
- `tests/unit/domain/` 与 `tests/unit/application/` 下的契约和映射测试；
- 必要的处理 pipeline 文档同步；
- 执行 `python scripts/check_repository.py`、Ruff format/lint、Pyright 和 pytest，分别用 Python 3.11/3.12 复核。

## 风险与决策点

- 必须先固定半整数舍入语义，不得偶然继承 Python `round` 的 bankers rounding；
- 该任务只定义 8-bit straight alpha 导出边界，不改变内部浮点 Alpha 精度。

## 完成记录

完成日期：2026-07-30

### 实现与舍入契约

- 新增不可变 `RgbaImage`，严格校验正整数尺寸、exact `bytes` 和 `width * height * 4` 长度，以 row-major `RGBARGBA...` 存储；
- 新增 `compose_straight_alpha_rgba`，在分配前验证 exact `ImageDocument`/`AlphaMatte` 类型和空间对齐；
- RGB 字节原样保留，包括 Alpha 0 和中间值像素，不执行预乘、重绘或清零；
- Alpha 只在 8-bit 输出边界使用 `floor(alpha * 255 + 0.5)` round-half-up 量化，内部 `AlphaMatte` 仍保持浮点值。

### 验证结果

- Python 3.11.15：仓库检查、Ruff format/lint、Pyright 严格模式和 212 项 pytest 全部通过；
- Python 3.12.13：仓库检查、Ruff format/lint、Pyright 严格模式和 212 项 pytest 全部通过；
- 测试覆盖 0/1/0.5、`(n + 0.5) / 255` 及其两侧、非方形顺序、straight-alpha RGB 保留、值对象边界、错误类型和尺寸错位。

### 已知限制与后续

- 当前只定义 8-bit packed straight-alpha 内存边界，不编码 PNG、不读写文件，也不处理 ICC/颜色管理；
- PNG 回读、保存与不覆盖契约依赖 Draft TASK-0102/TASK-0103 的经核验图片依赖；
- 未新增运行时依赖、文件输出、缓存或临时资产。
