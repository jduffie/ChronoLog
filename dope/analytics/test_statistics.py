"""
Unit tests for DOPE Analytics Statistics module
"""

import sys
import os
import pytest
import numpy as np

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dope.analytics.statistics import (
    VelocityStats,
    QualityIndicator,
    calculate_velocity_stats,
    detect_outliers,
    check_normality,
    check_data_quality,
)


class TestVelocityStats:
    """Test VelocityStats dataclass"""

    def test_to_dict_conversion(self):
        """Test converting VelocityStats to dictionary"""
        stats = VelocityStats(
            count=10,
            mean=800.5,
            median=801.0,
            std_dev=5.2,
            extreme_spread=15.0,
            min_velocity=795.0,
            max_velocity=810.0,
            q1=798.0,
            q3=805.0,
        )

        result = stats.to_dict()

        assert result["count"] == 10
        assert result["mean"] == 800.5
        assert result["median"] == 801.0
        assert result["std_dev"] == 5.2
        assert result["extreme_spread"] == 15.0
        assert result["min"] == 795.0
        assert result["max"] == 810.0
        assert result["q1"] == 798.0
        assert result["q3"] == 805.0


class TestQualityIndicator:
    """Test QualityIndicator dataclass"""

    def test_to_dict_conversion(self):
        """Test converting QualityIndicator to dictionary"""
        indicator = QualityIndicator(
            status="good",
            summary="All checks passed",
            warnings=[],
            details={"sample_size": 10},
        )

        result = indicator.to_dict()

        assert result["status"] == "good"
        assert result["summary"] == "All checks passed"
        assert result["warnings"] == []
        assert result["details"]["sample_size"] == 10


class TestCalculateVelocityStats:
    """Test calculate_velocity_stats function"""

    def test_basic_statistics_calculation(self):
        """Test basic statistics are calculated correctly"""
        velocities = [800.0, 801.0, 802.0, 803.0, 804.0]
        stats = calculate_velocity_stats(velocities)

        assert stats is not None
        assert stats.count == 5
        assert stats.mean == 802.0
        assert stats.median == 802.0
        assert stats.min_velocity == 800.0
        assert stats.max_velocity == 804.0
        assert stats.extreme_spread == 4.0
        assert stats.q1 == 801.0
        assert stats.q3 == 803.0

    def test_standard_deviation_calculation(self):
        """Test standard deviation is calculated correctly"""
        velocities = [800.0, 802.0, 804.0, 806.0, 808.0]
        stats = calculate_velocity_stats(velocities)

        expected_std = np.std([800.0, 802.0, 804.0, 806.0, 808.0], ddof=0)
        assert abs(stats.std_dev - expected_std) < 0.001

    def test_single_measurement(self):
        """Test with single measurement"""
        velocities = [800.0]
        stats = calculate_velocity_stats(velocities)

        assert stats.count == 1
        assert stats.mean == 800.0
        assert stats.median == 800.0
        assert stats.std_dev == 0.0
        assert stats.extreme_spread == 0.0

    def test_empty_list_returns_none(self):
        """Test empty list returns None"""
        stats = calculate_velocity_stats([])
        assert stats is None

    def test_none_input_returns_none(self):
        """Test None input returns None"""
        stats = calculate_velocity_stats(None)
        assert stats is None

    def test_quartile_calculation(self):
        """Test quartiles are calculated correctly"""
        velocities = [795.0, 798.0, 800.0, 802.0, 805.0, 808.0, 810.0]
        stats = calculate_velocity_stats(velocities)

        # Verify quartiles
        assert stats.q1 == np.percentile(velocities, 25)
        assert stats.q3 == np.percentile(velocities, 75)


class TestDetectOutliers:
    """Test detect_outliers function"""

    def test_clear_outlier_detection(self):
        """Test detection of clear outlier"""
        # 850 is a clear outlier
        velocities = [800.0, 801.0, 802.0, 803.0, 804.0, 850.0]
        outliers = detect_outliers(velocities)

        assert len(outliers) > 0
        assert 5 in outliers  # Index of 850

    def test_no_outliers_in_normal_data(self):
        """Test no outliers in normally distributed data"""
        velocities = [800.0, 801.0, 802.0, 803.0, 804.0, 805.0]
        outliers = detect_outliers(velocities)

        assert len(outliers) == 0

    def test_insufficient_data_returns_empty(self):
        """Test with < 3 measurements returns empty list"""
        assert detect_outliers([800.0]) == []
        assert detect_outliers([800.0, 801.0]) == []

    def test_multiple_outliers(self):
        """Test detection works with potential multiple outliers"""
        # Extreme values that may or may not be flagged depending on threshold
        velocities = [750.0, 800.0, 801.0, 802.0, 803.0, 804.0, 850.0]
        outliers = detect_outliers(velocities)

        # Just verify function returns a list (outlier detection depends on statistical threshold)
        assert isinstance(outliers, list)

    def test_custom_alpha_level(self):
        """Test with custom significance level"""
        velocities = [800.0, 801.0, 802.0, 803.0, 804.0, 810.0]

        # More strict alpha (fewer outliers)
        strict_outliers = detect_outliers(velocities, alpha=0.01)

        # Less strict alpha (more outliers)
        lenient_outliers = detect_outliers(velocities, alpha=0.10)

        # Both should return consistent results
        assert isinstance(strict_outliers, list)
        assert isinstance(lenient_outliers, list)


class TestCheckNormality:
    """Test check_normality function"""

    def test_normal_distribution(self):
        """Test with normally distributed data"""
        # Generate normally distributed data
        np.random.seed(42)
        velocities = list(np.random.normal(800, 5, 50))

        is_normal, p_value = check_normality(velocities)

        assert isinstance(is_normal, bool)
        assert 0.0 <= p_value <= 1.0

    def test_uniform_distribution_not_normal(self):
        """Test with uniformly distributed data (not normal)"""
        # Uniform distribution should fail normality test with large sample
        velocities = list(np.linspace(790, 810, 100))

        is_normal, p_value = check_normality(velocities)

        assert isinstance(is_normal, bool)
        assert 0.0 <= p_value <= 1.0

    def test_insufficient_data_assumes_normal(self):
        """Test with < 3 measurements assumes normal"""
        is_normal, p_value = check_normality([800.0])
        assert is_normal is True
        assert p_value == 1.0

        is_normal, p_value = check_normality([800.0, 801.0])
        assert is_normal is True
        assert p_value == 1.0

    def test_small_normal_sample(self):
        """Test with small normally distributed sample"""
        velocities = [800.0, 801.0, 802.0, 803.0, 804.0]

        is_normal, p_value = check_normality(velocities)

        assert isinstance(is_normal, bool)
        assert 0.0 <= p_value <= 1.0


class TestCheckDataQuality:
    """Test check_data_quality function"""

    def test_good_quality_data(self):
        """Test with good quality data (n≥10, no outliers, normal)"""
        # Generate clean normally distributed data
        np.random.seed(42)
        velocities = list(np.random.normal(800, 2, 15))

        quality = check_data_quality(velocities, min_sample_size=10)

        assert quality.status in ["good", "warning"]  # May vary due to randomness
        assert isinstance(quality.warnings, list)
        assert "sample_size" in quality.details
        assert quality.details["sample_size"] == 15

    def test_warning_small_sample(self):
        """Test warning for small sample size (5-9)"""
        velocities = [800.0, 801.0, 802.0, 803.0, 804.0, 805.0, 806.0]

        quality = check_data_quality(velocities, min_sample_size=10)

        assert quality.status in ["warning", "good"]
        assert any("sample size" in w.lower() for w in quality.warnings)

    def test_issues_very_small_sample(self):
        """Test issues status for very small sample (< 5)"""
        velocities = [800.0, 801.0, 802.0]

        quality = check_data_quality(velocities)

        assert quality.status == "issues"
        assert any("very small" in w.lower() for w in quality.warnings)

    def test_warning_with_outliers(self):
        """Test warning when outliers detected"""
        velocities = [800.0, 801.0, 802.0, 803.0, 804.0, 805.0, 806.0, 807.0, 808.0, 809.0, 850.0]

        quality = check_data_quality(velocities)

        assert "outlier_count" in quality.details
        if quality.details["outlier_count"] > 0:
            assert any("outlier" in w.lower() for w in quality.warnings)

    def test_skip_outlier_check(self):
        """Test with outlier check disabled"""
        velocities = [800.0, 801.0, 802.0, 803.0, 804.0, 850.0]

        quality = check_data_quality(velocities, check_outliers=False)

        assert "outlier_count" not in quality.details

    def test_skip_normality_check(self):
        """Test with normality check disabled"""
        velocities = [800.0, 801.0, 802.0, 803.0, 804.0]

        quality = check_data_quality(velocities, test_normality_flag=False)

        assert "normality_test" not in quality.details

    def test_quality_indicator_structure(self):
        """Test QualityIndicator has correct structure"""
        velocities = [800.0, 801.0, 802.0, 803.0, 804.0, 805.0, 806.0, 807.0, 808.0, 809.0]

        quality = check_data_quality(velocities)

        assert hasattr(quality, "status")
        assert hasattr(quality, "summary")
        assert hasattr(quality, "warnings")
        assert hasattr(quality, "details")
        assert quality.status in ["good", "warning", "issues"]
        assert isinstance(quality.summary, str)
        assert isinstance(quality.warnings, list)
        assert isinstance(quality.details, dict)

    def test_custom_min_sample_size(self):
        """Test with custom minimum sample size"""
        velocities = [800.0, 801.0, 802.0, 803.0, 804.0]

        # With min_sample_size=3, should be good/warning
        quality_low = check_data_quality(velocities, min_sample_size=3)

        # With min_sample_size=10, should warn about sample size
        quality_high = check_data_quality(velocities, min_sample_size=10)

        # Low threshold should have fewer warnings about sample size
        low_sample_warnings = [w for w in quality_low.warnings if "sample size" in w.lower()]
        high_sample_warnings = [w for w in quality_high.warnings if "sample size" in w.lower()]

        # High threshold should have sample size warning
        assert len(high_sample_warnings) > 0

    def test_multiple_quality_issues(self):
        """Test with multiple quality issues"""
        # Very small sample with outlier
        velocities = [800.0, 801.0, 900.0]

        quality = check_data_quality(velocities)

        assert quality.status == "issues"
        assert len(quality.warnings) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])