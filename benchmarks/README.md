# 评测数据资产

`manifest.json` 是 smoke、common、difficult 和 regression 评测样本的唯一可审阅索引。
当前 `samples` 合法为空，表示尚未获得项目所有者提供或来源与许可已核验的样本。
**空 manifest 不是质量证据，不能用于声称 M1/M2 效果达标。**

## 样本 schema

每个样本精确包含：

- 全局唯一的 canonical slug `id`；
- `smoke`、`common`、`difficult` 或 `regression` 集合；
- 类别、非空且排序去重的 canonical slug 标签；
- 输入文件相对路径和小写 SHA-256；
- Ground Truth 路径和 SHA-256，二者必须同时为字符串或同时为 `null`；
- 相互独立的来源和许可证、预期主体与人工备注。

路径相对于 `benchmarks/` 且必须使用安全 POSIX 格式。添加样本时必须先核验来源和许可，
再计算文件哈希并提交 manifest 变更。

## 存储边界

- 小型、授权明确的 fixture 可直接进入 Git；
- 大图及 Ground Truth 应在后续数据任务中选择 Git LFS 或版本化本地数据包，不得先提交再补许可；
- `reports/` 是可再生成输出并由 `.gitignore` 排除；算法输出不得写入受控输入目录；
- Ground Truth 必须经独立人工复核，不得由当前被测算法生成并用来证明自身正确。
