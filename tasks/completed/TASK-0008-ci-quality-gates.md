# TASK-0008：建立 CI 与质量门禁

状态：Completed

## 目标

建立最小 GitHub Actions CI，在 Python 3.11 和 3.12 的干净环境中安装项目并执行统一检查，同时自动验证文档链接、manifest、仓库生成物和运行时依赖边界，为 M0 退出审计提供可重复证据。

## 相关文档与需求

- `AGENTS.md`
- `docs/development/commands.md`
- `docs/development/setup.md`
- `docs/development/repository-hygiene.md`
- `docs/plans/current-milestone.md`
- `docs/product/requirements.md`（NFR-TEST-001、NFR-LICENSE-001、NFR-ARCH-001）
- `tasks/completed/TASK-0001-project-skeleton.md`

## 包含范围

- 创建一个最小 GitHub Actions workflow，使用 Python 3.11/3.12 matrix；
- 在干净环境执行 `python -m pip install -e '.[dev]'` 和 `python -m pip check`；
- 执行 Ruff format、Ruff lint、Pyright 和 pytest；
- 将 Markdown 相对链接、`pyproject.toml` 运行时依赖为空、模型/评测 manifest 可解析、关键 `.gitignore` 行为整合为版本化仓库检查脚本；
- 检查已跟踪文件中不存在 Python 缓存、模型权重、处理输出、评测报告、虚拟环境和常见秘密文件；
- 本地测试检查脚本的成功路径及至少关键失败路径；
- 更新统一开发命令，使本地和 CI 使用相同脚本而非复制不同逻辑；
- 文档记录 CI 不负责真实模型/GPU/质量 benchmark。

## 排除范围

- 发布包、上传制品、部署、Docker 和安装器；
- GPU、CUDA、真实模型和模型权重下载；
- 外部图片数据、benchmark 运行和视觉评分；
- pre-commit、tox、nox、覆盖率服务和第三方 CI action 集合；
- 自动修复、自动提交、PR 评论机器人或依赖更新机器人。

## 验收标准

- workflow 只使用固定主版本的官方 checkout/setup-python actions，并使用最小权限；
- Python 3.11 与 3.12 均执行安装、`pip check` 和完整质量门禁；
- 本地有一个文档化命令运行与 CI 相同的仓库检查脚本；
- 检查脚本对工作目录无隐式依赖或清晰要求从仓库根运行；
- 相对文档链接、两个 manifest、runtime dependencies 和关键忽略/禁止跟踪规则均有自动测试；
- 不把缓存、报告或检查输出写入 Git 跟踪目录；
- 没有新增运行时依赖，Ruff、Pyright、pytest 和仓库检查在 Python 3.11/3.12 通过；
- CI 文档、任务完成记录与仓库清理同步完成。

## 预期变更

- `.github/workflows/quality.yml`；
- `scripts/check_repository.py` 或正式开发工具模块；
- `tests/` 下的仓库检查测试；
- `docs/development/commands.md`；
- 必要时更新 `README.md` 和 setup 文档。

## 风险与决策点

- workflow 网络安装在当前容器无法复现，但配置必须由本地解析/检查并在真实 CI 首次运行后确认；
- 仓库检查规则应针对明确路径和文件类型，避免用宽泛扩展名误伤受控 fixture；
- 不要为了一个检查脚本引入新的 CLI 框架或 YAML parser；
- CI 只能证明工程门禁，不能替代真实物品评测和 MVP 视觉验收。

## 完成记录

完成日期：2026-07-30

### Workflow 与检查项

- 新增单一 GitHub Actions Quality workflow，最小权限为 `contents: read`；
- 使用官方 `actions/checkout@v4` 和 `actions/setup-python@v5`，Python 3.11/3.12 matrix 关闭 fail-fast 并设置 15 分钟超时；
- 每个 matrix job 依次安装 `.[dev]`、执行 `pip check`、仓库不变量检查、Ruff format/lint、Pyright 和 pytest；
- 新增版本化 `scripts/check_repository.py`，基于脚本位置定位仓库根，只读且完全离线；
- 检查脚本验证已跟踪 Markdown 相对链接、M0 空运行时依赖、两个 manifest、关键 `.gitignore` 行为和 Git 已跟踪噪声；
- 已跟踪噪声规则按明确目录、文件名和模型权重扩展名匹配，不宽泛禁止受控 PNG 或二进制 fixture。

### 验证结果

- Python 3.11.15：仓库检查、Ruff format、Ruff lint、Pyright 严格模式和 205 项 pytest 全部通过；
- Python 3.12.13：仓库检查、Ruff format、Ruff lint、Pyright 严格模式和 205 项 pytest 全部通过；
- 测试覆盖 NUL-safe 已跟踪文件列表、非根工作目录调用、链接失败、运行时依赖越界、明确禁止资产与受控图片/二进制文件不被误伤。

### 环境限制

- 当前容器无法代替 GitHub-hosted runner 证明真实 workflow 网络安装成功，需在 PR 的首次 Actions 运行中确认；
- CI 不下载真实模型，不使用 GPU/CUDA，也不运行图片 benchmark 或视觉质量评分。

### 清理与 M0 建议

- 未添加运行时依赖、CI 缓存、上传制品、生成报告或第三方 action 集合；
- 后续 M0 审计应在干净环境复核 editable install 与 `pip check`，并确认首次 GitHub Actions matrix 结果；
- 工程门禁只证明代码和仓库不变量，不得用于替代 M1/M2 真实物品评测。
