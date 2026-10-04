"""加载进度聚合：按资源权重汇总已完成进度，重复上报不重复计入、进度单调不减。"""


class Loading:
    """加载进度台账。"""

    def __init__(self, weights):
        self.weights = dict(weights)
        self.total_weight = sum(self.weights.values())
        self.completed = set()
        self.done_weight = 0
        self.scanned = 0

    def report(self, asset_id):
        """上报一个资源加载完成；重复上报与未知资源一律忽略。"""
        if asset_id in self.completed:
            return
        weight = self.weights.get(asset_id)
        if weight is None:
            return
        self.completed.add(asset_id)
        self.done_weight += weight

    def progress(self):
        """当前进度：已完成权重和 / 总权重和；总权重和不为正时按 1 处理。"""
        if self.total_weight <= 0:
            return 1.0
        value = self.done_weight / self.total_weight
        if value < 0.0:
            return 0.0
        if value > 1.0:
            return 1.0
        return value

    def scanned_count(self):
        return self.scanned
