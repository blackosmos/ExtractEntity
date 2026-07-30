# 模型适配器

状态：Accepted
最后审阅：2026-07-30

## 目的

第三方模型的 API、张量布局、权重加载和输出语义各不相同。项目通过适配器把这些差异限制在基础设施层，避免 UI 和工作流绑定某个模型。

## 领域端口

公开端口实现在 `extract_entity.domain`，使用标准库 `Protocol` 进行结构化类型检查。适配器无需继承项目基类，但必须满足以下窄接口：

- `SegmentationModel.segment(ImageDocument) -> SegmentationCandidate`；
- `InteractiveSegmentationModel.segment(ImageDocument, SubjectPrompt) -> SegmentationCandidate`；
- `MattingModel.matte(ImageDocument, Trimap) -> AlphaMatte`。

### 分割模型

自动分割输入规范化图片；交互分割额外输入 `SubjectPrompt`。点提示使用严格整数 `(x, y)` 像素索引和正/负类型，框使用半开区间 `[left, right) × [top, bottom)`；提示必须与输入图片尺寸匹配。

输出 `SegmentationCandidate` 只包含与原图尺寸对齐的 `ProbabilityMask` 和 `ModelIdentity`（名称与修订版）。不提前引入没有业务消费者的置信度或任意元数据字典。

### Matting 模型

输入原始 RGB 和 trimap，输出与目标图像对齐的 `AlphaMatte`，范围为 `[0, 1]`。

`Protocol` 只规定调用形状，不能在运行时自动验证第三方返回值。每个适配器必须在返回前构造经领域契约验证的对象；应用调用边界仍应复验结果与当前输入的尺寸。

## 适配器责任

- 验证权重是否存在且版本匹配；
- 执行模型要求的缩放、归一化和张量转换；
- 将结果映射回项目坐标和数据类型；
- 返回领域契约要求的模型名称和修订版；权重哈希、设备和诊断细节由后续权重管理与观测任务定义，不塞入当前领域结果；
- 将第三方异常转成项目定义的可处理错误；
- 支持测试替身，避免普通单元测试加载真实大模型。

## 禁止事项

- 模型适配器不得直接操作 UI；
- 不得自行选择输出目录或保存最终 PNG；
- 不得在导入模块时隐式下载权重；
- 不得把模型专有张量暴露给应用服务；
- 不得仅根据代码仓库许可证推断模型权重许可证。

## 可审阅 Manifest

`models/manifest.json` 是本地模型资产的单一、版本化配置。每个条目分别记录：

- 稳定 model ID 和在 pipeline 中的角色；
- 模型代码的来源、不可变修订和已核验许可证；
- 模型权重的独立来源、修订和已核验许可证；
- 权重文件的小写 SHA-256 和相对于 `models/` 的安全 POSIX 路径。

解析器严格拒绝未知字段、重复 ID、危险路径和未支持 schema 版本。校验器只对已存在的
本地普通文件流式计算 SHA-256，并通过 resolved root 边界阻止路径或符号链接逃逸。
解析、import 和校验均不得执行网络请求或隐式下载。尚未核验真实模型时，空 `models` 列表是合法状态。

## 初始角色

- BiRefNet 或经评测选出的同类模型：自动主体候选；
- SAM 2：点击、框选和正负提示修正；
- ViTMatte：连续 Alpha 精修；
- BEN2：保留为候选评测对象，不在首条 pipeline 中强制接入。
