# M0 退出审计

状态：Passed
审计日期：2026-07-30

## 结论

代理恢复后，项目已在全新 Python 3.12 虚拟环境完成 editable dev 安装、完整测试、Ruff 和 Pyright；M0 全部退出标准获得证据，可以进入 M1。

## 退出标准证据

| M0 退出标准 | 状态 | 直接证据与解除条件 |
|---|---|---|
| M0 文档 Accepted 且索引完整 | 已证明 | `docs/README.md`、Accepted 文档头与 `python scripts/check_repository.py` 的 Markdown 链接检查。 |
| 干净环境可安装并执行测试 | 已证明 | 全新 Python 3.12 venv 成功执行 `pip install -e '.[dev]'`、完整 pytest、Ruff 和 Pyright；Python 3.11 继续由本地双版本门禁与 CI matrix 覆盖。 |
| 数据契约和模型接口有测试 | 已证明 | `tests/unit/domain/`、`tests/unit/application/test_model_calls.py`；双 Python 版本 pytest 通过。 |
| 假实现 pipeline 可运行 | 已证明 | `tests/unit/application/test_extraction.py` 验证分割→Trimap→Matting→`ExtractionResult` 正式边界、顺序和失败传播。 |
| smoke 数据来源和存储方式确定 | 已证明 | `benchmarks/README.md` 确定样本由项目所有者自建或逐项核验来源/许可；小型 smoke 受控资产进入 Git，大图后续选择 Git LFS 或版本化数据包。`benchmarks/manifest.json` 仍为空，因此它不是质量证据；真实样本是 M1/M2 的后续门禁，不是本条治理策略的失败。 |
| `.gitignore` 和自动检查拦截常见噪声 | 已证明 | `.gitignore`、`scripts/check_repository.py` 及 `tests/unit/scripts/test_check_repository.py`；仓库检查通过。 |
| M1 任务可独立验收 | 已证明 | `tasks/completed/TASK-0101-rgba-composition.md` 与 `tasks/TASK-0102` 至 `TASK-0108` 形成依赖链；TASK-0101 已完成，其余 Draft 均声明依赖和 Ready 前细化条件。 |

## 其他审计证据

- Python 3.11.15/3.12.13 当前已配置环境均通过仓库门禁；安装第三方运行时依赖后，Pyright 使用当前虚拟环境解释器解析包类型。
- `pyproject.toml` 运行时依赖为空，模型和评测 manifest 均可离线解析；
- `git ls-files` 经版本化检查脚本审计，TASK-0001 至 TASK-0008 已归档；
- 当前仓库没有 Git remote，因此无法查询首次 GitHub Actions 运行；workflow 配置通过本地结构门禁不等于远程执行成功。这是附加未验证证据，不是 `current-milestone.md` 明文 M0 退出项；配置远程后仍应获得 Python 3.11/3.12 matrix 成功记录。

## 结果

M0 已通过。M1 从 RGBA 合成和图片 I/O 任务继续推进；真实模型仍须经过独立的代码与权重许可核验。
