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

    def test_below_minimum_threshold_returns_zero(self):
        # Tun-Lin et al. (2000): umbral minimo de desarrollo es 8.3°C
        assert _temperature_factor(8.0) == pytest.approx(0.0)

    def test_above_34c_returns_minimal(self):
        # Rueda et al. (1990): supervivencia cae drasticamente por encima de 34°C
        assert _temperature_factor(35.0) == pytest.approx(0.05)

    def test_15c_returns_very_low_factor(self):
        # Rueda et al. (1990): supervivencia de Ae. aegypti a 15°C es solo 3%
        assert _temperature_factor(15.0) < 0.10

    def test_boundary_low_is_valid(self):
        assert _temperature_factor(16.0) > 0.0

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
        # A 10°C el desarrollo es marginal (cerca del umbral minimo de 8.3°C)
        result = calculate_ire("tire", 10.0, 80.0)
        assert result["risk_level"] == "LOW"

    def test_days_to_emergence_calibrated_at_27c(self):
        # Rueda et al. (1990): ~7 dias a 27°C
        result = calculate_ire("tire", 27.0, 80.0)
        assert result["days_to_emergence_estimate"] == 7

    def test_days_to_emergence_calibrated_at_25c(self):
        # Rueda et al. (1990): ~10.5 dias a 25°C
        result = calculate_ire("tire", 25.0, 80.0)
        assert result["days_to_emergence_estimate"] == 10

    def test_days_to_emergence_calibrated_at_20c(self):
        # Rueda et al. (1990): ~12 dias a 20°C
        result = calculate_ire("bucket", 20.0, 80.0)
        assert result["days_to_emergence_estimate"] == 12

    def test_days_to_emergence_calibrated_at_15c(self):
        # Rueda et al. (1990): ~31 dias a 15°C
        result = calculate_ire("bucket", 15.0, 80.0)
        assert result["days_to_emergence_estimate"] == 31
