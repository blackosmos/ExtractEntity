# TASK-0103：实现原始尺寸 RGBA PNG 导出

状态：Ready
依赖：TASK-0101、TASK-0102。
权威文档：`docs/architecture/processing-pipeline.md`、`docs/product/requirements.md`、`docs/quality/acceptance-criteria.md`。

## 目标与范围

将经验证 packed straight-alpha RGBA 编码为原始尺寸 PNG，提供内存编码与明确的本地保存边界。
测试 PNG 签名、RGBA mode、尺寸、逐像素回读、不覆盖源文件和导出错误。不提供 CLI、模型或 UI。

## 验收标准

导出是真实 RGBA PNG；尺寸与 RGB/Alpha 不变；默认不覆盖现有文件；测试不经 JPEG 中间结果；双版本门禁通过。

## 实施约束

在 `infrastructure/png_export.py` 提供 `encode_png(RgbaImage) -> bytes` 和 `save_png(RgbaImage, path, *, overwrite=False) -> Path`。保存先在目标目录写临时文件并原子替换；默认在目标存在时失败。测试只使用临时目录，并用 Pillow 回读模式、尺寸和像素；覆盖编码失败、目录/权限类文件系统失败及临时文件清理。
