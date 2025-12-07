"""
DOPE Analytics Statistics

Statistical calculations for velocity data analysis.
Includes velocity statistics, quality indicators, and outlier detection.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np
from scipy import stats
from outliers import smirnov_grubbs as grubbs


@dataclass
class VelocityStats:
    """Comprehensive velocity statistics"""

    count: int
    mean: float
    median: float
    std_dev: float
    extreme_spread: float  # ES = max - min
    min_velocity: float
    max_velocity: float
    q1: float  # First quartile (25th percentile)
    q3: float  # Third quartile (75th percentile)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "count": self.count,
            "mean": self.mean,
            "median": self.median,
            "std_dev": self.std_dev,
            "extreme_spread": self.extreme_spread,
            "min": self.min_velocity,
            "max": self.max_velocity,
            "q1": self.q1,
            "q3": self.q3,
        }


@dataclass
class QualityIndicator:
    """Data quality assessment results"""

    status: str  # "good", "warning", "issues"
    summary: str  # Human-readable summary
    warnings: List[str]  # List of warning messages
    details: dict  # Technical details (p-values, test results)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "status": self.status,
            "summary": self.summary,
            "warnings": self.warnings,
            "details": self.details,
        }


def calculate_velocity_stats(velocities: List[float]) -> Optional[VelocityStats]:
    """
    Calculate comprehensive velocity statistics.

    Args:
        velocities: List of velocity measurements in m/s

    Returns:
        VelocityStats object, or None if insufficient data

    Example:
        >>> velocities = [800.0, 805.0, 798.0, 802.0, 801.0]
        >>> stats = calculate_velocity_stats(velocities)
        >>> print(f"Mean: {stats.mean:.1f} m/s, SD: {stats.std_dev:.1f}")
    """
    if not velocities or len(velocities) < 1:
        return None

    # Convert to numpy array for calculations
    v = np.array(velocities)

    # Calculate statistics
    return VelocityStats(
        count=len(velocities),
        mean=float(np.mean(v)),
        median=float(np.median(v)),
        std_dev=float(np.std(v, ddof=0)),  # Population std dev
        extreme_spread=float(np.max(v) - np.min(v)),
        min_velocity=float(np.min(v)),
        max_velocity=float(np.max(v)),
        q1=float(np.percentile(v, 25)),
        q3=float(np.percentile(v, 75)),
    )


def detect_outliers(velocities: List[float], alpha: float = 0.05) -> List[int]:
    """
    Detect outliers using Grubbs test (via outlier-utils library).

    Args:
        velocities: List of velocity measurements in m/s
        alpha: Significance level (default 0.05)

    Returns:
        List of indices of detected outliers

    Example:
        >>> velocities = [800, 801, 802, 803, 850]  # 850 is an outlier
        >>> outlier_indices = detect_outliers(velocities)
        >>> print(f"Outliers at indices: {outlier_indices}")
    """
    if len(velocities) < 3:
        return []  # Need at least 3 points for Grubbs test

    # Get outlier indices using two-sided Grubbs test
    try:
        outlier_indices = grubbs.two_sided_test_indices(velocities, alpha=alpha)
        return sorted(list(outlier_indices)) if outlier_indices else []
    except Exception as e:
        print(f"Warning: Grubbs test failed: {e}")
        return []


def check_normality(velocities: List[float]) -> Tuple[bool, float]:
    """
    Check if velocity distribution is normal using Shapiro-Wilk test.

    Args:
        velocities: List of velocity measurements in m/s

    Returns:
        Tuple of (is_normal, p_value)
        - is_normal: True if distribution is normal (p > 0.05)
        - p_value: p-value from Shapiro-Wilk test

    Example:
        >>> velocities = [800, 801, 802, 803, 804]
        >>> is_normal, p_value = test_normality(velocities)
        >>> print(f"Normal: {is_normal}, p-value: {p_value:.3f}")
    """
    if len(velocities) < 3:
        return True, 1.0  # Too few points to test, assume normal

    v = np.array(velocities)

    # Shapiro-Wilk test
    statistic, p_value = stats.shapiro(v)

    # Null hypothesis: data is normally distributed
    # Reject if p < 0.05 (not normal)
    is_normal = bool(p_value > 0.05)

    return is_normal, float(p_value)


def check_data_quality(
    velocities: List[float],
    min_sample_size: int = 10,
    check_outliers: bool = True,
    test_normality_flag: bool = True,
) -> QualityIndicator:
    """
    Assess data quality with traffic light indicators.

    Quality levels:
    - 🟢 Good: Sample size ≥ min_sample_size, no outliers, normal distribution
    - 🟡 Warning: Sample size 5-9, or outliers present, or not normal
    - 🔴 Issues: Sample size < 5, or multiple quality problems

    Args:
        velocities: List of velocity measurements in m/s
        min_sample_size: Minimum recommended sample size (default 10)
        check_outliers: Whether to check for outliers (default True)
        test_normality_flag: Whether to test normality (default True)

    Returns:
        QualityIndicator object with status, warnings, and details

    Example:
        >>> velocities = [800, 801, 802, 803, 804, 805, 806, 807, 808, 809]
        >>> quality = check_data_quality(velocities)
        >>> print(f"Status: {quality.status}, Summary: {quality.summary}")
    """
    warnings = []
    details = {}

    # Check sample size
    n = len(velocities)
    details["sample_size"] = n

    if n < 5:
        warnings.append(f"Sample size ({n}) is very small (< 5)")
    elif n < min_sample_size:
        warnings.append(
            f"Sample size ({n}) is below recommended minimum ({min_sample_size})"
        )

    # Check for outliers
    outlier_indices = []
    if check_outliers and n >= 3:
        outlier_indices = detect_outliers(velocities)
        details["outlier_count"] = len(outlier_indices)
        details["outlier_indices"] = outlier_indices

        if outlier_indices:
            warnings.append(
                f"Detected {len(outlier_indices)} outlier(s) using Grubbs test"
            )

    # Check normality
    is_normal = True
    p_value = 1.0
    if test_normality_flag and n >= 3:
        is_normal, p_value = check_normality(velocities)
        details["normality_test"] = {
            "is_normal": is_normal,
            "p_value": p_value,
            "test": "Shapiro-Wilk",
        }

        if not is_normal:
            warnings.append(f"Distribution may not be normal (p={p_value:.3f})")

    # Determine overall status
    if n < 5 or len(warnings) >= 3:
        status = "issues"
        summary = "Data quality issues detected - use results with caution"
    elif warnings:
        status = "warning"
        summary = f"{len(warnings)} warning(s) - review data quality"
    else:
        status = "good"
        summary = "Data quality is good"

    return QualityIndicator(
        status=status, summary=summary, warnings=warnings, details=details
    )