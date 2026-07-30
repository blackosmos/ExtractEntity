# TASK-0006：建立模型 Manifest 与权重治理

状态：Completed

## 目标

在接入真实模型前，建立可提交、可验证的模型 manifest 契约，分别记录模型代码和权重的来源、版本与许可证，并提供本地文件 SHA-256 校验能力，避免隐式下载、来源不明和权重漂移。

## 相关文档与需求

- `AGENTS.md`
- `docs/architecture/model-adapters.md`
- `docs/development/repository-hygiene.md`
- `docs/product/requirements.md`（NFR-LOCAL-001、NFR-LICENSE-001、NFR-ARCH-001）
- `tasks/completed/TASK-0001-project-skeleton.md`

## 包含范围

- 创建 `models/README.md` 与可提交的 `models/manifest.json`；
- 定义版本化 manifest schema，记录稳定 model ID、角色、代码来源/修订/许可证、权重来源/修订/许可证、SHA-256 和仓库相对本地路径；
- 使用标准库解析和严格验证 manifest 类型、必填字段、唯一 model ID、相对安全路径及 64 位十六进制 SHA-256；
- 拒绝绝对路径、`..` 路径穿越、空来源、空修订和空许可证；
- 提供显式本地权重校验函数：文件缺失或 SHA-256 不匹配时给出清晰错误；
- manifest 初始可为空，不伪造尚未核验的模型许可或权重来源；
- 单元测试覆盖合法空/非空 manifest、格式错误、重复 ID、危险路径、缺失文件和哈希不匹配；
- 文档说明模型不得在 import 时下载，下载流程由后续真实模型任务显式实现。

## 排除范围

- 下载 BiRefNet、SAM 2、ViTMatte 或任何权重；
- 声称尚未联网核验的具体模型许可证；
- Hugging Face、GitHub 或其他网络客户端；
- 模型加载、设备选择、推理和 adapter 实现；
- 通用依赖锁定、制品仓库、签名验证或自动更新服务；
- 将模型二进制、缓存或测试生成权重提交 Git。

## 验收标准

- manifest 的代码与权重来源、版本和许可证字段相互独立；
- parser 只接受 schema 支持的明确类型和字段，不静默忽略未知字段；
- 本地路径始终相对于仓库模型根目录且不能逃逸；
- SHA-256 格式和真实文件内容均可验证；
- 空 manifest 可作为未选定真实模型时的合法 M0 状态；
- 测试完全离线，临时文件位于测试临时目录且不污染仓库；
- `.gitignore` 允许 README/manifest，继续忽略其他 `models/` 内容；
- 没有新增运行时依赖，Ruff、Pyright 和 pytest 在 Python 3.11/3.12 通过；
- 模型架构文档、任务完成记录和仓库清理同步完成。

## 预期变更

- `models/README.md`；
- `models/manifest.json`；
- `src/extract_entity/infrastructure/` 下的 manifest parser/validator；
- `tests/unit/infrastructure/` 下的离线测试；
- `docs/architecture/model-adapters.md`。

## 风险与决策点

- manifest 是项目配置，不是模型注册表服务；保持单文件、版本化、可人工审阅；
- 初始文件不应填写凭记忆推断的许可证，真实条目必须在后续调研中核验来源；
- 本任务只校验已有本地文件，不负责联网获取或自动修复；
- 不要引入 JSON Schema 库或配置框架，当前标准库严格解析足够。

## 完成记录

完成日期：2026-07-30

### 实际 schema 与实现

- 新增 schema version 1，顶层只允许 `schema_version` 和 `models`，空模型列表合法；
- 每个模型使用唯一非空 `id`、`role`、独立 `code` 来源记录和 `weights` 来源记录；
- 代码和权重各自要求非空、无首尾空白的 `source`、`revision` 和 `license`；
- 权重额外要求小写 64 位十六进制 SHA-256 和安全相对 POSIX 路径；
- 标准库解析器拒绝未知/缺失/重复 JSON 字段、错误标量类型、重复 ID、路径穿越和未支持版本；
- 本地校验器通过 resolved root 边界阻止符号链接逃逸，并流式计算普通文件 SHA-256。

### 验证结果

- Python 3.11.15：Ruff format、Ruff lint、Pyright 严格模式和 136 项 pytest 全部通过；
- Python 3.12.13：Ruff format、Ruff lint、Pyright 严格模式和 136 项 pytest 全部通过；
- 测试完全离线，权重样本仅写入 pytest 临时目录；`pyproject.toml` 运行时依赖仍为空。

### 已知限制

- manifest 当前不包含任何真实模型，本任务不对具体项目许可证作出声明；
- 校验器只验证已存在的本地文件，不下载、修复、签名验证或加载模型。

### 清理与后续

- `.gitignore` 仍只允许跟踪 `models/README.md` 和 `models/manifest.json`，其他模型资产保持忽略；
- 未新增运行时依赖、真实权重、网络客户端、缓存或生成输出；
- 后续真实模型任务必须先核验一手来源和许可证，再显式增加 manifest 条目和下载流程。
