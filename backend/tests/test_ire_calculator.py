"""
Unit tests for the IRE (Entomological Risk Index) calculator.
Run with: pytest backend/tests/test_ire_calculator.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from core.bio_engine.ire_calculator import calculate_ire, _temperature_factor


class TestTemperatureFactor:
    def test_optimal_temperature_returns_max(self):
        assert _temperature_factor(28.0) == pytest.approx(1.0)

    def test_below_threshold_returns_minimum(self):
        assert _temperature_factor(15.0) == pytest.approx(0.1)

    def test_above_threshold_returns_minimum(self):
        assert _temperature_factor(35.0) == pytest.approx(0.1)

    def test_boundary_low_is_valid(self):
        assert _temperature_factor(16.0) > 0.1

    def test_boundary_high_is_valid(self):
        assert _temperature_factor(34.0) > 0.1


class TestCalculateIre:
    def test_returns_required_keys(self):
        result = calculate_ire("tire", 28.0, 80.0)
        assert "ire_score" in result
        assert "risk_level" in result
        assert "risk_type" in result
        assert "days_to_emergence_estimate" in result
        assert "recommended_action" in result

    def test_critical_risk_at_optimal_conditions(self):
        result = calculate_ire("tire", 28.0, 90.0, water_present=True)
        assert result["risk_level"] == "CRITICAL"
        assert result["ire_score"] >= 70.0

    def test_no_water_yields_potential_risk_type(self):
        result = calculate_ire("bucket", 28.0, 80.0, water_present=False)
        assert result["risk_type"] == "POTENTIAL"

    def test_no_water_reduces_score(self):
        with_water = calculate_ire("bucket", 28.0, 80.0, water_present=True)
        without_water = calculate_ire("bucket", 28.0, 80.0, water_present=False)
        assert without_water["ire_score"] < with_water["ire_score"]

    def test_organic_matter_increases_score(self):
        without = calculate_ire("bucket", 28.0, 80.0, organic_matter=False)
        with_om = calculate_ire("bucket", 28.0, 80.0, organic_matter=True)
        assert with_om["ire_score"] > without["ire_score"]

    def test_score_clamped_between_5_and_99(self):
        result = calculate_ire("tire", 28.0, 100.0, organic_matter=True, container_size="large")
        assert 5.0 <= result["ire_score"] <= 99.0

    def test_unknown_container_falls_back_to_default(self):
        result = calculate_ire("unknown_container", 28.0, 80.0)
        assert result["ire_score"] > 0

    def test_large_container_scores_higher_than_small(self):
        small = calculate_ire("bucket", 28.0, 80.0, container_size="small")
        large = calculate_ire("bucket", 28.0, 80.0, container_size="large")
        assert large["ire_score"] > small["ire_score"]

    def test_days_estimate_is_positive_integer(self):
        result = calculate_ire("tire", 28.0, 80.0)
        assert isinstance(result["days_to_emergence_estimate"], int)
        assert result["days_to_emergence_estimate"] > 0

    def test_cold_temperature_yields_low_risk(self):
        result = calculate_ire("tire", 10.0, 80.0)
        assert result["risk_level"] == "LOW"
