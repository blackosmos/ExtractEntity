# TASK-0003：定义模型接口与测试替身

状态：Completed

## 目标

在不接入任何真实模型的前提下，建立自动分割、交互分割和 Matting 的模型无关接口与最小请求/响应对象，并提供可用于应用服务测试的 fake/spy 替身。

## 相关文档与需求

- `AGENTS.md`
- `docs/architecture/system-overview.md`
- `docs/architecture/model-adapters.md`
- `docs/architecture/processing-pipeline.md`
- `docs/product/requirements.md`（FR-EXT-001、FR-COR-001、FR-COR-002、FR-COR-003、FR-COR-004、NFR-TEST-001、NFR-ARCH-001）
- `tasks/completed/TASK-0002-core-image-contracts.md`

## 包含范围

- 定义自动分割接口：接收 `ImageDocument`，返回统一的分割候选；
- 定义交互分割接口及最小正向点、负向点和框提示；
- 定义 Matting 接口：接收 `ImageDocument` 与 `Trimap`，返回 `AlphaMatte`；
- 定义最小 `SegmentationCandidate`，包含 `ProbabilityMask` 和必要、类型安全的来源信息；
- 采用 `Protocol` 或等价的结构化接口，使第三方适配器无需继承框架基类；
- 提供固定成功、主动失败和记录调用参数的 fake/spy 测试替身；
- 测试接口可替换性、提示验证、空间对齐和调用记录；
- 更新模型适配器与系统架构文档，使接口名称和职责与代码一致。

## 排除范围

- BiRefNet、BEN2、SAM 2、ViTMatte 或任何真实模型实现；
- PyTorch、Transformers、NumPy、Pillow 等新运行时依赖；
- 模型权重下载、缓存、设备选择和批处理；
- 候选评分、融合、trimap 生成、RGBA 合成和文件导出；
- UI 状态、异步任务队列、重试策略和通用插件框架；
- 为未来未知模型设计复杂继承层次或配置系统。

## 验收标准

- 应用层能够仅依赖项目接口调用自动分割、交互分割和 Matting；
- 接口输入输出只包含领域对象和本任务定义的不可变值对象，不暴露第三方张量；
- 点坐标采用 `(x, y)` 且必须位于图片范围内，框坐标语义清晰并拒绝空框、反向框和越界框；
- 分割候选 Mask 与输入图片、Matting 输出与输入图片必须空间对齐；
- fake 可返回固定结果或固定异常，spy 能以不可变形式记录调用；
- 测试不加载真实模型、不访问网络、不写模型缓存；
- 测试覆盖合法调用、错误提示、尺寸不一致、fake 失败和 spy 调用记录；
- 没有新增运行时依赖，Ruff、Pyright 和 pytest 在 Python 3.11/3.12 通过；
- 架构文档与公开接口一致，任务完成后执行清理并记录下一任务建议。

## 预期变更

- `src/extract_entity/` 下的模型端口、提示和候选对象；
- `tests/` 下的接口契约与测试替身测试；
- 测试支持目录中的 fake/spy；
- `docs/architecture/model-adapters.md`；
- 必要时更新 `docs/architecture/system-overview.md`。

## 风险与决策点

- 测试替身属于测试支持代码，不应进入正式包，除非有明确运行时消费者；
- `Protocol` 只表达当前用例所需的最小调用，不应复制第三方模型 API；
- 来源信息应保持小而类型安全，避免引入任意 `dict[str, Any]`；
- 交互提示本任务只需要点和框，涂抹数据结构等真实 UI 需求明确后再增加。

## 完成记录

完成日期：2026-07-30

### 实际接口与值对象

- `SegmentationModel.segment(ImageDocument) -> SegmentationCandidate`；
- `InteractiveSegmentationModel.segment(ImageDocument, SubjectPrompt) -> SegmentationCandidate`；
- `MattingModel.matte(ImageDocument, Trimap) -> AlphaMatte`；
- 提示由 `PointPrompt`、`PointKind`、`BoxPrompt` 和 `SubjectPrompt` 组成，点使用 `(x, y)`，框使用半开区间；
- 分割候选只包含图像尺寸、`ProbabilityMask` 和类型安全的 `ModelIdentity`。

端口使用标准库 `Protocol`，没有要求第三方适配器继承项目基类。测试替身仅位于 `tests/support/`，支持固定结果、固定异常和不可变调用快照。

### 验证结果

- Python 3.12：Ruff format、Ruff lint、Pyright 通过，pytest 47 项通过；
- Python 3.11：Ruff format、Ruff lint、Pyright 通过，pytest 47 项通过；
- 测试覆盖点/框边界、错误类型、空提示、多框、候选空间对齐、Protocol 可替换性、固定失败、调用记录及输入/输出尺寸复验。

### 已知限制

- `Protocol` 只表达静态调用形状，真实适配器和应用调用边界仍必须复验返回尺寸；
- 当前交互提示支持多点和最多一个框，不包含涂抹、UI 会话或撤销栈；
- 来源信息暂只保留模型名称和修订版，权重哈希、设备和诊断待实际消费者与权重管理任务定义。

### 清理与交接

- 未新增运行时依赖、真实模型、权重、网络访问、缓存或临时文件；
- fake/spy 未进入正式包，公开类型未引入任意元数据字典或通用插件框架；
- 下一任务建议：实现图片文件解码与 EXIF 方向规范化，或先建立不依赖真实模型的小型应用调用边界；两者需由独立 Ready 任务确定顺序。
