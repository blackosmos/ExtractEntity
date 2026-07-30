# TASK-0007：建立评测数据 Manifest

状态：Completed

## 目标

建立可审阅、可版本化、完全离线的评测数据 manifest 契约，明确 smoke/common/difficult/regression 分层、样本来源与许可证、输入和 Ground Truth 完整性，为后续模型 benchmark 和视觉回归提供稳定基础。

## 相关文档与需求

- `AGENTS.md`
- `docs/quality/evaluation-dataset.md`
- `docs/quality/acceptance-criteria.md`
- `docs/development/repository-hygiene.md`
- `docs/product/requirements.md`（NFR-QUALITY-002、NFR-LICENSE-001、NFR-LOCAL-001）
- `tasks/completed/TASK-0006-model-manifest.md`

## 包含范围

- 创建 `benchmarks/README.md` 与 `benchmarks/manifest.json`；
- 定义 schema version 1 与四个固定集合：`smoke`、`common`、`difficult`、`regression`；
- 样本记录唯一 ID、集合、类别、稳定标签、输入相对路径/SHA-256、可选 Ground Truth 相对路径/SHA-256、来源、许可证、预期主体和备注；
- manifest 初始允许没有样本，避免提交来源或许可未核验的图片；
- 严格解析 exact keys、重复 JSON keys、唯一样本 ID、枚举集合、规范标签、非空文本、安全 POSIX 路径和小写 SHA-256；
- 验证已有本地输入/Ground Truth 为普通文件、位于 benchmark 根目录且哈希匹配；
- Ground Truth 路径和哈希必须同时存在或同时缺失；
- 单元测试覆盖合法空/非空 manifest、错误 schema、重复 ID/keys、未知集合、危险路径、许可缺失、文件缺失和哈希不匹配；
- 文档明确大图存储策略、Git/LFS 边界和不得由被测算法生成 Ground Truth。

## 排除范围

- 从互联网下载或抓取评测图片；
- 在许可未知时提交图片、Alpha 或商业产品输出；
- 生成真实物品 Ground Truth；
- 运行模型 benchmark、计算 SAD/MSE/Gradient/Connectivity 指标；
- 引入 Git LFS、数据版本服务、数据库或 JSON Schema 依赖；
- 将临时报告和算法输出提交到 benchmark 输入目录。

## 验收标准

- 四个集合语义与质量文档一致，样本 ID 在所有集合中全局唯一；
- 每个样本明确来源、许可证、类别、标签和预期主体；
- 输入必须有 SHA-256；Ground Truth 使用成对可选字段；
- parser 不静默修正路径、标签、空白或未知字段；
- verifier 阻止绝对路径、路径穿越、Windows drive 和符号链接逃逸；
- 空 manifest 合法并明确表示评测数据尚待项目所有者提供或许可核验；
- 所有测试离线且临时文件不污染仓库；
- `.gitignore` 继续忽略 `benchmarks/reports/`，但 manifest 和受控 fixture 可跟踪；
- 没有新增运行时依赖，Ruff、Pyright 和 pytest 在 Python 3.11/3.12 通过；
- 数据集文档、任务完成记录和清理同步完成。

## 预期变更

- `benchmarks/README.md`；
- `benchmarks/manifest.json`；
- `src/extract_entity/evaluation/` 下的 parser/verifier；
- `tests/unit/evaluation/` 下的离线测试；
- `docs/quality/evaluation-dataset.md`。

## 风险与决策点

- 空 manifest 只完成治理基础，不代表质量数据已经充足；后续 M1/M2 退出前必须加入经过核验的真实物品样本；
- 样本元数据应稳定且可人工审阅，不做通用数据资产平台；
- 评测输入和 Ground Truth 是受控资产，模型输出和报告属于可再生成产物；
- 不要复制模型 manifest parser 形成两个漂移实现；可以提取小型私有公共校验函数，但不得创建通用配置框架。

## 完成记录

完成日期：2026-07-30

### 实际 schema 与实现

- 新增 schema version 1，顶层只允许 `schema_version` 和单一 `samples` 数组，空数组合法；
- 样本在全部集合间使用全局唯一 canonical slug ID，集合只允许 smoke、common、difficult 和 regression；
- 每个样本记录类别、排序去重的 canonical slug 标签、输入路径/哈希、成对可选 Ground Truth 路径/哈希、独立来源/许可、预期主体和备注；
- parser 严格拒绝重复 JSON key、未知/缺失字段、错误类型、空白、非规范标签、危险路径和非规范 SHA-256；
- 模型和评测 manifest 共用小型私有 JSON、文本、路径、哈希和本地文件校验 primitive，没有复制两套漂移逻辑；
- verifier 先校验 input，再校验可选 Ground Truth，错误明确携带 sample ID 和字段名。

### 验证结果

- Python 3.11.15：Ruff format、Ruff lint、Pyright 严格模式和 197 项 pytest 全部通过；
- Python 3.12.13：Ruff format、Ruff lint、Pyright 严格模式和 197 项 pytest 全部通过；
- 测试完全离线，所有文件都位于 pytest 临时目录；`pyproject.toml` 运行时依赖仍为空。

### 数据缺口与已知限制

- 当前 manifest 没有真实样本，只证明数据治理和完整性基础可用，不是任何提取质量证据；
- M1/M2 退出前仍需项目所有者提供或核验真实物品图片与独立 Ground Truth；
- 本任务不运行 benchmark、不计算质量指标，也不选择 Git LFS 或外部数据包。

### 清理与后续

- `benchmarks/reports/` 仍由 `.gitignore` 排除，未提交图片、Alpha、算法输出、报告、缓存或临时数据；
- 未新增运行时依赖或网络访问；
- 后续数据任务必须在资产入库前核验来源与许可，Ground Truth 变更必须独立人工复核。
