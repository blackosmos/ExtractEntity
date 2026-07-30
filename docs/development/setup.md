# 开发环境

状态：Accepted
最后审阅：2026-07-30

## 支持范围

项目当前支持 Python 3.11 和 3.12。开发工具由 `pyproject.toml` 的 `dev` 可选依赖组统一安装。运行时使用 Pillow 解码本地图片；CI 持续验证两个受支持版本。

## 创建环境

在仓库根目录执行：

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

Windows PowerShell 使用 `.venv\Scripts\Activate.ps1` 激活环境，其余命令相同。

## 验证

安装后执行 [`commands.md`](commands.md) 中的统一检查命令。不要在全局 Python 环境中安装项目开发依赖。

## 依赖与许可证

| 依赖 | 用途 | 类型 | 来源 | 许可证 |
|---|---|---|---|---|
| Hatchling | PEP 517 构建后端 | 构建 | [PyPI](https://pypi.org/project/hatchling/) | MIT |
| pytest | 自动化测试 | 开发 | [PyPI](https://pypi.org/project/pytest/) | MIT |
| Ruff | 格式化和 lint | 开发 | [PyPI](https://pypi.org/project/ruff/) | MIT |
| Pyright | 静态类型检查 | 开发 | [PyPI](https://pypi.org/project/pyright/) | MIT |
| Pillow | JPEG、PNG、WebP 解码、EXIF 方向修正和 RGB 规范化 | 运行时 | [PyPI](https://pypi.org/project/Pillow/) / [源码](https://github.com/python-pillow/Pillow) | MIT-CMU |

依赖版本范围的权威来源是 `pyproject.toml`。升级或新增依赖时，应从实际解析版本的上游发布包元数据或官方仓库核对许可证，并同步更新本表；传递依赖应在可联网的干净环境完成安装后随依赖审计一并检查。
