# TASK-0001：建立 Python 项目骨架

状态：Completed

## 目标

建立可安装、可测试、可静态检查的最小 Python 工程，为后续领域接口和模型适配器提供稳定基础。

## 相关文档

- `AGENTS.md`
- `docs/architecture/system-overview.md`
- `docs/product/requirements.md`（NFR-TEST-001、NFR-ARCH-001）
- `docs/plans/current-milestone.md`
- `docs/development/repository-hygiene.md`

## 包含范围

- 选择并记录受支持的 Python 版本；
- 创建 `pyproject.toml` 和 `src/` 布局；
- 建立最小包、测试目录和一个 smoke test；
- 配置格式化、lint、类型检查和测试命令；
- 创建覆盖虚拟环境、缓存、模型权重、处理输出和本机配置的 `.gitignore`；
- 编写开发环境和常用命令说明；
- 记录直接依赖的用途和许可证检查方法。

## 排除范围

- 下载或接入任何真实模型；
- 定义完整图像 pipeline；
- 开发 Web UI；
- 引入测试图片评测集；
- 添加 Docker、安装包或发布流程。

## 验收标准

- 在受支持的干净 Python 环境中可以安装项目；
- 包可以被正常导入；
- 最小测试通过；
- 格式化、lint 和类型检查具有单一、文档化命令；
- Git 不跟踪缓存、虚拟环境、模型权重和处理输出；
- 没有引入与本任务无关的运行时框架；
- README 和开发文档反映真实命令；
- 任务结束时完成仓库清理清单。

## 预期变更

- `pyproject.toml`
- `.gitignore`
- `src/extract_entity/`
- `tests/`
- `docs/development/setup.md`
- `docs/development/commands.md`

## 验证命令

具体命令由本任务选定工具后写入 `docs/development/commands.md`，至少覆盖安装、测试、lint、格式化检查和类型检查。

## 风险

- 过早引入完整 AI/图像依赖会增加环境噪声；
- 工具配置重复会造成命令来源不唯一；
- 必须避免把本机环境生成物提交进仓库。

## 完成记录

完成日期：2026-07-30

### 实际变更

- 选择 Python 3.11–3.12、Hatchling、pytest、Ruff 和 Pyright；
- 创建 `pyproject.toml`、`src/extract_entity/`、包导入 smoke test 和 `.gitignore`；
- 建立开发环境、统一命令和直接依赖来源/许可证说明；
- 更新 README 与文档地图入口；
- 保持运行时依赖为空，未接入模型、图像库、Web 框架或发布工具。

### 验证结果

- `PYTHONPATH=src python -m ruff format --check .`：通过；
- `PYTHONPATH=src python -m ruff check .`：通过；
- `PYTHONPATH=src python -m pyright`：通过；
- `PYTHONPATH=src python -m pytest`：通过，1 个测试；
- 上述测试与静态检查分别在 Python 3.11.15 和 3.12.13 上通过；
- Markdown 相对链接、Git 忽略规则和 `git diff --check`：通过。

### 环境限制

全新虚拟环境执行 `python -m pip install -e '.[dev]'` 时，外部包代理返回 HTTP 403，无法下载 Hatchling，因此未能在本环境完成联网安装验证；失败发生在依赖下载阶段，不是项目元数据解析或测试失败。完整安装应在具备包源访问的环境或后续 CI 中补充验证。

### 清理结果

未提交虚拟环境、缓存、模型权重、处理输出、调试文件或本机路径；没有新增运行时依赖或第二套开发命令。

### 下一任务

执行 `tasks/TASK-0002-core-image-contracts.md`，在接入真实模型之前定义并测试核心图像数据契约。
