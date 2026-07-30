# ExtractEntity

ExtractEntity 是一个完全在本地运行、以质量为优先的个人图片工具，用于识别和提取图片中的物品，并以原始分辨率保存为透明 RGBA PNG。

## 当前状态

项目处于 **M1：单图自动提取闭环** 阶段。M0 工程门禁已经通过，图片解码与 RGBA 合成边界已经建立；PNG 导出、真实分割模型和 smoke 质量证据仍待完成。

## 已确定的核心流程

```text
导入图片
→ 自动识别主要物品
→ 生成并精修 Alpha
→ 在多种背景上预览
→ 必要时点击、框选或涂抹修正
→ 导出透明 PNG
```

## 核心原则

- 本地运行，不上传图片；
- 只考虑开源和免费方案；
- 以物品提取为主；
- 质量优先于速度；
- 自动处理与交互修正结合；
- 模型、交互界面与处理编排相互解耦；
- 通过固定评测集证明图像效果，而不是只验证文件能够生成。

## 文档入口

- [文档地图](docs/README.md)
- [产品愿景](docs/product/product-vision.md)
- [用户工作流](docs/product/user-workflow.md)
- [功能与非功能需求](docs/product/requirements.md)
- [项目术语](docs/product/terminology.md)
- [范围边界](docs/product/out-of-scope.md)
- [系统架构](docs/architecture/system-overview.md)
- [图像处理流水线](docs/architecture/processing-pipeline.md)
- [质量验收标准](docs/quality/acceptance-criteria.md)
- [当前里程碑](docs/plans/current-milestone.md)
- [M0 退出审计](docs/plans/m0-exit-audit.md)
- [项目路线图](docs/plans/roadmap.md)
- [仓库文件更新与清理原则](docs/development/repository-hygiene.md)
- [开发环境](docs/development/setup.md)
- [开发命令](docs/development/commands.md)
- [AI 开发规范](AGENTS.md)

## 开发快速开始

项目支持 Python 3.11 和 3.12。创建并激活虚拟环境后，执行：

```bash
python -m pip install -e '.[dev]'
python -m pytest
```

完整环境步骤和检查命令分别见[开发环境](docs/development/setup.md)和[开发命令](docs/development/commands.md)。

## 权威信息优先级

发生冲突时，按以下顺序处理：

1. 已接受的验收标准与功能规格；
2. 已接受的 ADR 和架构约束；
3. 产品需求与范围文档；
4. 当前里程碑；
5. 当前任务文档；
6. 临时讨论和聊天记录。

冲突不能通过猜测解决，应先更新权威文档再继续实现。
