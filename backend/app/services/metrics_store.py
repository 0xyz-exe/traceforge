from collections import defaultdict
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Dict, List, Tuple
import statistics

class MetricsStore:
    """In-memory time-series metrics storage (MVP - lost on restart)"""
    
    def __init__(self, retention_days: int = 7):
        self.retention_days = retention_days
        # Structure: {series_key: [(timestamp, value), ...]}
        self._data: Dict[str, List[Tuple[datetime, float]]] = defaultdict(list)
        self._lock = Lock()
        self._max_series = 1000  # Cardinality limit per instance
    
    def _series_key(self, workspace_id: str, service: str, metric: str, labels: Dict[str, str]) -> str:
        """Generate unique series key"""
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{workspace_id}:{service}:{metric}:{label_str}"
    
    def ingest(self, workspace_id: str, service: str, metric: str, value: float, 
               timestamp: datetime, labels: Dict[str, str]) -> bool:
        """Store metric data point. Returns True if accepted."""
        timestamp = self._as_naive_utc(timestamp)
        if not self._validate_value(value):
            return False
        
        if not self._validate_timestamp(timestamp):
            return False
        
        series_key = self._series_key(workspace_id, service, metric, labels)
        
        with self._lock:
            if series_key not in self._data and len(self._data) >= self._max_series:
                return False  # Cardinality limit reached
            
            self._data[series_key].append((timestamp, value))
            # Keep sorted by timestamp
            self._data[series_key].sort(key=lambda x: x[0])
            # Cleanup old data
            self._cleanup_series(series_key)
        
        return True
    
    def query(self, workspace_id: str, service: str, metric: str, 
              start: datetime, end: datetime, labels: Dict[str, str] = None) -> List[Tuple[datetime, float]]:
        """Query metric data points in time range"""
        start = self._as_naive_utc(start)
        end = self._as_naive_utc(end)
        results = []
        
        with self._lock:
            # Find matching series
            for series_key, data_points in self._data.items():
                if not self._matches_query(series_key, workspace_id, service, metric, labels):
                    continue
                
                # Filter by time range
                for ts, val in data_points:
                    if start <= ts <= end:
                        results.append((ts, val))
        
        results.sort(key=lambda x: x[0])
        return results
    
    def aggregate(self, data_points: List[Tuple[datetime, float]], 
                  aggregation: str, interval_seconds: int = 60) -> List[Tuple[datetime, float]]:
        """Aggregate data points into time buckets"""
        if not data_points:
            return []
        
        # Group by time bucket
        buckets: Dict[datetime, List[float]] = defaultdict(list)
        for ts, val in data_points:
            bucket_ts = self._floor_timestamp(ts, interval_seconds)
            buckets[bucket_ts].append(val)
        
        # Aggregate each bucket
        results = []
        for bucket_ts in sorted(buckets.keys()):
            values = buckets[bucket_ts]
            agg_value = self._aggregate_values(values, aggregation)
            if agg_value is not None:
                results.append((bucket_ts, agg_value))
        
        return results
    
    def _validate_value(self, value: float) -> bool:
        """Check if value is valid (not NaN, not infinite)"""
        import math
        return not (math.isnan(value) or math.isinf(value))
    
    def _validate_timestamp(self, ts: datetime) -> bool:
        """Check if timestamp is within acceptable range"""
        now = datetime.utcnow()
        one_year_ago = now - timedelta(days=365)
        # Not in future, not more than 1 year old
        return one_year_ago <= ts <= now + timedelta(minutes=5)

    def _as_naive_utc(self, timestamp: datetime) -> datetime:
        if timestamp.tzinfo is None:
            return timestamp
        return timestamp.astimezone(timezone.utc).replace(tzinfo=None)
    
    def _cleanup_series(self, series_key: str):
        """Remove old data points beyond retention"""
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        self._data[series_key] = [
            (ts, val) for ts, val in self._data[series_key]
            if ts >= cutoff
        ]
        # Remove empty series
        if not self._data[series_key]:
            del self._data[series_key]
    
    def _matches_query(self, series_key: str, workspace_id: str, service: str, 
                       metric: str, labels: Dict[str, str] = None) -> bool:
        """Check if series key matches query filters"""
        parts = series_key.split(":", 3)
        if len(parts) != 4:
            return False
        
        key_workspace, key_service, key_metric, key_labels = parts
        
        if key_workspace != workspace_id:
            return False
        if key_service != service:
            return False
        if key_metric != metric:
            return False
        
        # Check label filters
        if labels:
            for k, v in labels.items():
                if f"{k}={v}" not in key_labels:
                    return False
        
        return True
    
    def _floor_timestamp(self, ts: datetime, interval_seconds: int) -> datetime:
        """Round timestamp down to interval bucket"""
        seconds_since_epoch = int(ts.timestamp())
        bucket_seconds = (seconds_since_epoch // interval_seconds) * interval_seconds
        return datetime.utcfromtimestamp(bucket_seconds)
    
    def _aggregate_values(self, values: List[float], aggregation: str) -> float | None:
        """Compute aggregation over values"""
        if not values:
            return None
        
        if aggregation == "sum":
            return sum(values)
        elif aggregation == "avg":
            return statistics.mean(values)
        elif aggregation == "min":
            return min(values)
        elif aggregation == "max":
            return max(values)
        elif aggregation == "count":
            return float(len(values))
        elif aggregation == "p50":
            return statistics.median(values)
        elif aggregation == "p95":
            return statistics.quantiles(values, n=20)[18] if len(values) >= 2 else values[0]
        elif aggregation == "p99":
            return statistics.quantiles(values, n=100)[98] if len(values) >= 2 else values[0]
        else:
            return None
    
    def get_series_count(self) -> int:
        """Return current number of unique series"""
        with self._lock:
            return len(self._data)

# Global instance
metrics_store = MetricsStore()
