# loading-progress

加载进度聚合：按资源权重汇总已完成进度，重复上报不重复计入、进度单调不减，只用 Python 标准库。

```
python3 -m loading.cli --sample dup
python3 -m loading.cli --sample empty
python3 -m loading.cli --sample unknown
python3 -m loading.cli --sample scan
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **加权进度**：进度等于已完成资源的权重和除以总权重和；总权重和不为正时进度按 1 处理。
- **上报幂等**：同一个资源重复上报不重复计入，进度只由「该资源是否已完成」决定。
- **忽略未知**：权重表里没有的资源上报一律忽略，不影响进度。
- **单调不减**：进度只增不减，永远落在 0 到 1 之间。
- **查询代价**：`progress` 不许每次全扫权重表，`scanned_count()` 不随资源数乘查询次数增长。
- **规模**：20 万资源、每秒 10 万次上报与查询，单次摊还 O(1)。

## 输出契约（不改格式）

```
progress=0.00
scanned=..
```

## 目录

```
loading/core.py   加权进度与幂等上报
loading/cli.py    命令行入口
tests/            unittest 用例
```
