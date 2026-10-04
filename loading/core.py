"""加载进度聚合：按资源权重汇总已完成进度，重复上报不重复计入、进度单调不减。

缺陷：重复上报重复累加、空权重表返回 0、未知资源按权重 1 计入、每次查询全扫权重表。
"""


class Loading:
    """加载进度台账。"""

    def __init__(self, weights):
        self.weights = dict(weights)
        self.reported = {}
        self.scanned = 0

    def report(self, asset_id):
        """上报一个资源加载完成。缺陷：同一条重复上报也累加计数。"""
        self.reported[asset_id] = self.reported.get(asset_id, 0) + 1

    def progress(self):
        """当前进度。缺陷：空权重表返回 0、未知资源按 1 计、全扫权重表。"""
        self.scanned += len(self.weights)
        total = 0
        for weight in self.weights.values():
            total += weight
        if total <= 0:
            return 0.0
        got = 0
        for asset_id, count in self.reported.items():
            got += self.weights.get(asset_id, 1) * count
        return got / total

    def scanned_count(self):
        return self.scanned
