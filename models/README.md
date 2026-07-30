# 本地模型资产

`manifest.json` 是可提交、可人工审阅的模型元数据源。当前没有已核验的真实模型，
因此 `models` 列表合法为空；不得根据记忆或项目名称填写来源和许可证。

## Manifest 结构

```json
{
  "schema_version": 1,
  "models": [
    {
      "id": "stable-model-id",
      "role": "automatic-segmentation",
      "code": {
        "source": "verified-source-url",
        "revision": "immutable-revision",
        "license": "verified-license"
      },
      "weights": {
        "source": "verified-weight-url",
        "revision": "immutable-weight-revision",
        "license": "verified-weight-license",
        "sha256": "64-lowercase-hex-characters",
        "path": "stable-model-id/weights.bin"
      }
    }
  ]
}
```

代码和权重的来源、修订及许可证必须分别核验。`path` 是相对于本目录的 POSIX 路径；
权重本身会被 `.gitignore` 排除，只提交本说明和 manifest。

## 运行规则

- import 任何包都不得触发下载；
- manifest 解析和 SHA-256 校验只读取本地文件；
- 真实模型任务必须明确实现下载或安装步骤，并在加载前校验哈希；
- 文件缺失、路径逃逸或哈希不符时必须停止，不得默默下载或替换。
