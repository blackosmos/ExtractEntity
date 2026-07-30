# TASK-0102：实现图片解码与 EXIF 规范化

状态：Completed
依赖：TASK-0101；干净安装证据；Pillow 版本、用途和许可记录。
权威文档：`docs/architecture/processing-pipeline.md`、`docs/product/requirements.md`、`docs/development/setup.md`。

## 目标与范围

使用经核验的 Pillow 读取 JPEG/PNG/WebP，应用 EXIF 方向并转成规范 RGB `ImageDocument`。
覆盖 orientation 1/3/6/8、RGB/RGBA/灰度、损坏文件和源文件不变。不实现导出、模型或 UI。

## 验收标准

依赖来源与许可已记录；解码后尺寸/通道/方向契约可重复测试；错误可读且不修改源文件；双版本门禁通过。

## 实施约束

使用 `Pillow>=12.0,<13`（MIT-CMU），实现位于 `infrastructure/image_io.py`。测试在临时目录中生成微型 fixture，不提交生成图片；验证方向为双版本仓库门禁、回读尺寸/像素与源文件哈希。

## 完成记录

- 新增受支持格式白名单、本地文件解码、EXIF transpose 和 RGB 规范化；
- 将文件与解码失败统一为可读的 `ImageDecodeError`，保留异常链；
- 覆盖方向 1/3/6/8、RGB/RGBA/灰度、JPEG/PNG/WebP、损坏和不支持格式；
- 在代理恢复后于全新 Python 3.12 环境完成 editable install、212 项既有测试和静态检查，解除 M0 安装证据阻塞。
