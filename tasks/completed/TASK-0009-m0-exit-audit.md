# TASK-0009：执行 M0 退出审计并规划 M1

状态：Completed

## 目标

基于当前仓库和可重复命令逐项审计 M0 退出标准，区分已证明、环境受限和未完成事项；补齐必要的项目状态文档，并把 M1 单图自动提取闭环拆分成按依赖顺序推进的 Ready/Draft 任务。

## 相关文档

- `AGENTS.md`
- `docs/plans/current-milestone.md`
- `docs/plans/roadmap.md`
- `docs/product/requirements.md`
- `docs/quality/acceptance-criteria.md`
- `docs/quality/evaluation-dataset.md`
- `docs/development/commands.md`
- `tasks/completed/TASK-0001-project-skeleton.md` 至 `TASK-0008-ci-quality-gates.md`

## 包含范围

- 对 M0 每一条退出标准建立证据表，引用文件、测试和精确命令；
- 运行 Python 3.11/3.12 仓库检查、Ruff、Pyright 和 pytest；
- 在当前允许的环境中重新尝试干净 editable 安装与 `pip check`，明确记录成功或包源限制；
- 检查工作区、已跟踪噪声、任务归档、文档链接、模型/评测 manifest 和运行时依赖；
- 确认假 pipeline 通过正式边界端到端运行；
- 记录 GitHub Actions 首次远程运行是否有当前环境可用证据，不以 workflow 文件存在冒充远程成功；
- 将 M1 拆成图片 I/O、RGBA/PNG、默认开源模型核验、模型适配器、单图入口、真实 smoke 评测和 M1 验收等独立任务；
- 只有第一个依赖已满足的 M1 任务标记 `Ready`，其余保持 `Draft`；
- 若 M0 证据完整则切换当前里程碑；如有外部环境证据缺口，保持 M0 并明确最小解除条件。

## 排除范围

- 实现任何 M1 功能；
- 下载模型、图片或权重；
- 修改验收标准以绕过失败证据；
- 把空评测 manifest 声称为质量证明；
- 根据 workflow 配置推断远程 CI 已通过；
- 创建大量无法执行、范围重叠的规划文档。

## 验收标准

- 审计覆盖 M0 每一退出标准且每项具有明确状态和直接证据；
- 环境限制与产品/代码失败被清晰区分；
- 没有用窄单元测试证明宽泛产品质量；
- M1 任务形成清晰依赖链、范围和验收标准；
- 当前里程碑与审计结论一致，不提前标记完成；
- 仓库检查、Ruff、Pyright 和 pytest 在 Python 3.11/3.12 通过；
- 文档链接、任务状态、清理和 Git 差异检查通过；
- 审计结果、下一 Ready 任务和已知解除条件可由下一 Agent 直接执行。

## 预期变更

- `docs/plans/` 下的 M0 审计结果或当前里程碑更新；
- `tasks/` 下的 M1 任务链；
- 必要时更新 README 当前状态；
- 本任务完成后移入 `tasks/completed/`。

## 风险与决策点

- 当前环境的包代理 403 可能继续阻止干净安装，这属于证据缺口但不阻止完成可离线推进的审计和 M1 规划；
- M1 第一个任务应优先建立真实图片 I/O/RGBA 基础，还是先做模型一手来源核验，由依赖和当前网络能力决定；
- 远程 CI 状态如不可访问必须标记未验证，不得猜测；
- 审计文档应短且可执行，不复制全部历史任务完成记录。

## 完成记录

完成日期：2026-07-30

### 逐项结论

- M0 文档/索引、数据契约/模型端口、假 pipeline、smoke 来源/存储治理策略、仓库噪声门禁和 M1 任务拆分均有直接证据；
- M0 唯一尚未证明的明文退出项是干净环境安装与测试；
- 空评测 manifest 符合 M0 治理契约但不是质量证据；远程 CI 状态不可查，已作为附加未验证证据而非伪造为 M0 阻断项。

### 环境与命令证据

- Python 3.11.15/3.12.13 全新 venv 执行 `python -m pip install -e '.[dev]'` 均在 pip 构建隔离安装 `hatchling>=1.27,<2` 时因代理 tunnel HTTP 403 失败；未执行不安全的降级或宣称安装成功；
- 在当前已配置的 Python 3.11.15/3.12.13 环境分别执行 `PYTHONPATH=src python scripts/check_repository.py`、`python -m ruff format --check .`、`python -m ruff check .`、`python -m pyright` 和 `python -m pytest -q`，仓库检查通过且 205 项测试通过；
- 当前 `git remote -v` 为空，无远程 Actions API 证据可查。

### M1 任务入口

- 已建立 TASK-0101 至 TASK-0108 的 RGBA→解码→PNG→模型核验→adapter→单图入口→真实 smoke→退出审计依赖链；
- 只有无新依赖/网络需求的 TASK-0101 为 Ready，已完整记录权威文档、范围、预期文件、命令和风险；
- TASK-0102 至 TASK-0108 保持 Draft，包含基本依赖、范围、验收方向和 Ready 前细化条件，不授权提前实现。

### 清理结果

- 审计未引入功能代码、运行时依赖、图片、权重、报告或缓存；
- 临时 venv 和安装日志仅在 `/tmp` 中用于审计，任务结束时删除；
- 当前里程碑继续为 M0，并明确授权并行推进不需要外部条件的 TASK-0101。
