# crabswarm/llm/cost.py
"""
成本追踪和优化模块
"""

import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

from .config import get_model_price


@dataclass
class UsageRecord:
    """使用记录"""
    timestamp: float
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    latency_ms: float


@dataclass
class CostAlert:
    """成本告警"""
    level: str  # "warning", "critical"
    message: str
    current_cost: float
    threshold: float
    timestamp: float


class TokenTracker:
    """Token使用追踪器"""
    
    def __init__(self):
        self.records: List[UsageRecord] = []
        self._model_stats: Dict[str, Dict] = defaultdict(lambda: {
            "requests": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        })
    
    def record(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float = 0
    ) -> UsageRecord:
        """
        记录一次使用
        
        Args:
            model: 模型名称
            prompt_tokens: 输入token数
            completion_tokens: 输出token数
            latency_ms: 延迟(毫秒)
            
        Returns:
            UsageRecord
        """
        total_tokens = prompt_tokens + completion_tokens
        
        # 计算成本
        pricing = get_model_price(model)
        cost_usd = (prompt_tokens * pricing["input"] + completion_tokens * pricing["output"]) / 1_000_000
        
        record = UsageRecord(
            timestamp=time.time(),
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
        )
        
        self.records.append(record)
        
        # 更新统计
        stats = self._model_stats[model]
        stats["requests"] += 1
        stats["prompt_tokens"] += prompt_tokens
        stats["completion_tokens"] += completion_tokens
        stats["total_tokens"] += total_tokens
        
        return record
    
    def get_stats(self, model: Optional[str] = None) -> Dict:
        """获取统计信息"""
        if model:
            return dict(self._model_stats[model])
        
        # 汇总所有模型
        total = {
            "requests": sum(s["requests"] for s in self._model_stats.values()),
            "prompt_tokens": sum(s["prompt_tokens"] for s in self._model_stats.values()),
            "completion_tokens": sum(s["completion_tokens"] for s in self._model_stats.values()),
            "total_tokens": sum(s["total_tokens"] for s in self._model_stats.values()),
        }
        
        return {
            "total": total,
            "by_model": dict(self._model_stats),
        }
    
    def get_recent_records(self, minutes: int = 60) -> List[UsageRecord]:
        """获取最近的使用记录"""
        cutoff = time.time() - minutes * 60
        return [r for r in self.records if r.timestamp > cutoff]


class CostTracker:
    """成本追踪器"""
    
    def __init__(
        self,
        daily_budget_usd: float = 10.0,
        alert_threshold: float = 0.8,
        on_alert: Optional[Callable[[CostAlert], None]] = None
    ):
        """
        初始化成本追踪器
        
        Args:
            daily_budget_usd: 每日预算(美元)
            alert_threshold: 告警阈值(0-1)
            on_alert: 告警回调函数
        """
        self.daily_budget_usd = daily_budget_usd
        self.alert_threshold = alert_threshold
        self.on_alert = on_alert
        self.token_tracker = TokenTracker()
        self._alerts_triggered: set = set()
        self._day_start = time.time()
    
    def record_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float = 0
    ) -> UsageRecord:
        """记录使用并检查预算"""
        record = self.token_tracker.record(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms
        )
        
        # 检查是否需要告警
        self._check_budget()
        
        return record
    
    def get_daily_cost(self) -> float:
        """获取今日成本"""
        day_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        day_start_ts = day_start.timestamp()
        
        return sum(
            r.cost_usd for r in self.token_tracker.records
            if r.timestamp >= day_start_ts
        )
    
    def get_budget_status(self) -> Dict:
        """获取预算状态"""
        current_cost = self.get_daily_cost()
        remaining = self.daily_budget_usd - current_cost
        usage_percent = current_cost / self.daily_budget_usd if self.daily_budget_usd > 0 else 0
        
        return {
            "daily_budget": self.daily_budget_usd,
            "current_cost": current_cost,
            "remaining": remaining,
            "usage_percent": usage_percent,
            "alert_threshold": self.alert_threshold,
            "is_over_budget": current_cost >= self.daily_budget_usd,
        }
    
    def _check_budget(self):
        """检查预算并触发告警"""
        status = self.get_budget_status()
        usage_percent = status["usage_percent"]
        
        # 检查严重告警 (100%)
        if usage_percent >= 1.0 and "critical" not in self._alerts_triggered:
            self._alerts_triggered.add("critical")
            if self.on_alert:
                self.on_alert(CostAlert(
                    level="critical",
                    message=f"Daily budget exceeded! Current: ${status['current_cost']:.2f}",
                    current_cost=status["current_cost"],
                    threshold=self.daily_budget_usd,
                    timestamp=time.time(),
                ))
        
        # 检查警告 (80%)
        elif usage_percent >= self.alert_threshold and "warning" not in self._alerts_triggered:
            self._alerts_triggered.add("warning")
            if self.on_alert:
                self.on_alert(CostAlert(
                    level="warning",
                    message=f"Daily budget at {usage_percent*100:.0f}%! Current: ${status['current_cost']:.2f}",
                    current_cost=status["current_cost"],
                    threshold=self.daily_budget_usd * self.alert_threshold,
                    timestamp=time.time(),
                ))
    
    def reset_daily(self):
        """重置每日统计"""
        self._alerts_triggered.clear()
        self._day_start = time.time()
    
    def estimate_cost(self, model: str, prompt_tokens: int, expected_output_tokens: int = 500) -> float:
        """
        预估成本
        
        Args:
            model: 模型名称
            prompt_tokens: 输入token数
            expected_output_tokens: 预期输出token数
            
        Returns:
            预估成本(美元)
        """
        pricing = get_model_price(model)
        return (prompt_tokens * pricing["input"] + expected_output_tokens * pricing["output"]) / 1_000_000
    
    def get_report(self) -> Dict:
        """获取完整报告"""
        budget_status = self.get_budget_status()
        token_stats = self.token_tracker.get_stats()
        
        return {
            "budget": budget_status,
            "tokens": token_stats,
            "records_count": len(self.token_tracker.records),
            "alerts_triggered": list(self._alerts_triggered),
        }
