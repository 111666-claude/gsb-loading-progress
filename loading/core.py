"""加载进度聚合：按资源权重汇总已完成进度，重复上报不重复计入、进度单调不减。

口径（以 README 为准）：
- 加权进度：已完成资源的权重和除以总权重和；总权重和不为正时按 1 处理。
- 上报幂等：同一资源重复上报不重复计入。
- 忽略未知：权重表里没有的资源上报一律忽略。
- 单调不减：进度只增不减，永远落在 0 到 1 之间。
- 查询代价：增量维护已完成权重和，上报与查询单次摊还 O(1)，不做全表扫描。
"""


class Loading:
    """加载进度台账。"""

    def __init__(self, weights):
        self.weights = dict(weights)
        self.reported = set()
        self.scanned = 0
        self._total = sum(self.weights.values())
        self._done = 0
        self._max_progress = 0.0

    def report(self, asset_id):
        """上报一个资源加载完成。未知资源忽略，重复上报幂等。"""
        if asset_id not in self.weights or asset_id in self.reported:
            return
        self.reported.add(asset_id)
        self._done += self.weights[asset_id]

    def progress(self):
        """当前进度：已完成权重和 / 总权重和；总权重和不为正时进度按 1 处理。"""
        if self._total <= 0:
            value = 1.0
        else:
            value = self._done / self._total
        if value < 0.0:
            value = 0.0
        elif value > 1.0:
            value = 1.0
        if value > self._max_progress:
            self._max_progress = value
        return self._max_progress

    def scanned_count(self):
        return self.scanned
