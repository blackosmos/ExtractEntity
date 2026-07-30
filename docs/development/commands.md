# 开发命令

状态：Accepted
最后审阅：2026-07-30

以下命令均在已激活的项目虚拟环境和仓库根目录执行。初次安装见 [`setup.md`](setup.md)。

## 安装

```bash
python -m pip install -e '.[dev]'
```

## 测试

```bash
python -m pytest
```

## Lint

```bash
python -m ruff check .
```

## 格式检查

```bash
python -m ruff format --check .
```

需要修复格式时执行 `python -m ruff format .`。

## 类型检查

```bash
python -m pyright --pythonpath "$(command -v python)"
```

## 仓库不变量检查

```bash
python scripts/check_repository.py
```

该离线脚本使用自身位置定位仓库根，不依赖调用时的工作目录。它验证：

- 已跟踪 Markdown 中的相对文件链接；
- M0 运行时依赖边界；
- 模型与评测 manifest 可解析；
- 关键 `.gitignore` 行为；
- Git 已跟踪文件中不包含缓存、虚拟环境、模型权重、生成输出、完整评测报告或常见秘密文件。

## 提交前完整检查

```bash
python scripts/check_repository.py
python -m ruff format --check .
python -m ruff check .
python -m pyright --pythonpath "$(command -v python)"
python -m pytest
```

GitHub Actions 在 Python 3.11 和 3.12 的独立 matrix 任务中先执行 editable 安装和
`python -m pip check`，再执行上述同一仓库检查与完整工具链。CI 不下载真实模型，
不运行 GPU/CUDA、图片 benchmark 或视觉评分，因此工程门禁通过不等于产品质量达标。

`pyproject.toml` 是工具选项和依赖版本的权威来源；本文档只定义人和 AI 应执行的统一命令入口。
