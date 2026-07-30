# TASK-0106：建立单图自动提取入口

状态：Draft
依赖：TASK-0103、TASK-0105。
权威文档：`docs/architecture/processing-pipeline.md`、`docs/product/requirements.md`、`docs/quality/acceptance-criteria.md`。

## 目标与范围

组合解码、默认分割、M1 Alpha 基线、RGBA 合成和 PNG 导出，提供一个可重复的本地单图命令或应用服务入口。
M1 临时 Alpha 契约是将已验证 `ProbabilityMask` 的连续 `[0, 1]` 值原样作为同尺寸 `AlphaMatte`，
不二值化、羽化或声称它是 M2 最终 Matting 策略。该映射必须有 identity/数值、尺寸错位和管线传递测试。
包含输入/输出路径、不覆盖、错误码和 CPU 路径；不开发 Web UI、交互修正或批处理。

## 验收标准

一条命令将支持图片转为同尺寸 RGBA PNG；原图不变；阶段失败可读；使用 fake 完整集成测试和显式 real-model smoke。

## Ready 前细化

固定入口形态、退出码、默认文件名和预期 application/CLI 文件；测试必须分开 fake 端到端与需权重的显式 smoke。
