"""
Threshold Calibration Test Suite
Tests calibration analysis across different operational ratios.
"""

from config.thresholds import analyze_calibration, get_current_thresholds


def test_well_calibrated_system():
    # 100 apps, 30 escalated (30%), 70 autonomous, 2 overrides (2.8%)
    cal = analyze_calibration(
        total_apps=100,
        escalated_count=30,
        autonomous_count=70,
        human_overrides_count=2,
    )
    assert cal["status"] == "WELL_CALIBRATED"
    assert cal["escalation_rate"] == 0.30
    assert cal["override_rate"] == 0.0286


def test_too_conservative_thresholds():
    # 100 apps, 70 escalated (70% > 35% target max)
    cal = analyze_calibration(
        total_apps=100,
        escalated_count=70,
        autonomous_count=30,
        human_overrides_count=1,
    )
    assert cal["status"] == "TOO_CONSERVATIVE"
    assert "exceeds target max" in cal["recommendations"][0]


def test_too_loose_high_override_rate():
    # 100 apps, 20 escalated, 80 autonomous, 16 overrides (20% > 10% target max)
    cal = analyze_calibration(
        total_apps=100,
        escalated_count=20,
        autonomous_count=80,
        human_overrides_count=16,
    )
    assert cal["status"] == "TOO_LOOSE_HIGH_OVERRIDES"
    assert "exceeds threshold" in cal["recommendations"][0]
