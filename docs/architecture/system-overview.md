# 系统架构总览

状态：Accepted
最后审阅：2026-07-30

## 组件

```text
本地 Web UI
    ↓
应用服务 / 用例层
    ├── 图片导入与规范化
    ├── 提取流程编排
    ├── 用户提示与会话状态
    ├── 结果预览与导出
    ↓
领域接口
    ├── SegmentationModel
    ├── InteractiveSegmentationModel
    ├── MattingModel
    └── QualityEvaluator
    ↓
基础设施适配器
    ├── BiRefNet / BEN2
    ├── SAM 2
    ├── ViTMatte
    ├── 模型权重管理
    └── 本地文件系统
```

## 依赖规则

- UI 只调用应用服务，不直接导入模型库、加载权重或合成 Alpha。
- 用例层依赖领域接口，不依赖具体模型名称。
- 模型适配器将第三方输入输出转换为项目统一类型。
- 图片保存、缓存和权重下载是基础设施职责，不属于模型推理接口。
- 评测代码可以调用正式 pipeline，但正式运行时代码不得依赖 benchmark 资产。

## 模型调用信任边界

`extract_entity.application` 中的三个窄调用函数是应用层与不可信模型适配器的统一边界：

- `run_segmentation`；
- `run_interactive_segmentation`；
- `run_matting`。

它们在调用前验证正式输入类型和提示/Trimap 的空间对齐，调用后验证返回类型和候选/Alpha 与当前图片的空间对齐。合法结果保持原对象返回，模型异常原样传播。该边界不负责重试、错误分类、调度或完整 pipeline 编排。

## 内部数据对象

核心图像契约实现在 `extract_entity.domain`，仅使用不可变标准库类型：

- `ImageDocument`：EXIF 方向已修正的 RGB 图像；存储为行主序交错 `bytes`，通道为无符号 8-bit `RGB`；
- `ProbabilityMask`：行主序 `tuple[float, ...]`，值有限且在 `[0, 1]`；
- `BinaryMask`：行主序 `bytes`，只允许 `0` 和 `1`；
- `SubjectPrompt`：多个正负点和最多一个半开区间框；
- `SegmentationCandidate`：与图片对齐的概率 Mask 和最小模型来源信息；
- `Trimap`：行主序 `bytes`，只允许确定背景 `0`、未知区域 `128` 和确定前景 `255`；
- `AlphaMatte`：行主序 `tuple[float, ...]`，值有限且在 `[0, 1]`；
- `RgbaImage`：行主序 packed 8-bit straight-alpha `bytes`，通道顺序为 `RGBARGBA...`；
- `ExtractionResult`：尺寸对齐的原图、Alpha 和不可变告警列表；RGBA 是独立合成阶段的输出，不存入该领域结果。

坐标统一写作 `(x, y)`，物理存储为行主序 `[y, x]`。所有宽高在构造边界验证，Mask 和 Alpha 与图片组合时必须空间对齐。第三方数组和张量必须由基础设施适配器在边界转换，不得进入领域对象。

## 非目标

架构不承诺第一版同时集成所有候选模型。先建立稳定接口和一条端到端 pipeline，再以评测结果决定是否增加模型。

本文只定义组件边界和依赖方向；具体功能义务由[产品需求](../product/requirements.md)定义，处理阶段的数据不变量由[图像处理流水线](processing-pipeline.md)定义。
