"""
Unit tests for the Report Generator module.

Tests cover:
- HTML report generation
- Recommendation generation
"""

import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.report_generator import (
    generate_html_report,
    generate_general_recommendations
)
from src.analyzer import StudentMetrics


class TestRecommendationGeneration:
    """Tests for general recommendation generation."""

    def test_high_risk_percentage_recommendation(self):
        """Test recommendation when many students are at risk."""
        stats = {
            'at_risk_percentage': 45,
            'average_attendance': 85,
            'trend_distribution': {'improving': 5, 'declining': 3},
            'average_score_mean': 75
        }

        recs = generate_general_recommendations(stats)
        assert any('at risk' in r.lower() for r in recs)

    def test_low_attendance_recommendation(self):
        """Test recommendation for low attendance."""
        stats = {
            'at_risk_percentage': 10,
            'average_attendance': 65,
            'trend_distribution': {'improving': 5, 'declining': 3},
            'average_score_mean': 75
        }

        recs = generate_general_recommendations(stats)
        assert any('attendance' in r.lower() for r in recs)

    def test_declining_trend_recommendation(self):
        """Test recommendation when many students declining."""
        stats = {
            'at_risk_percentage': 10,
            'average_attendance': 85,
            'trend_distribution': {'improving': 2, 'declining': 8},
            'average_score_mean': 75
        }

        recs = generate_general_recommendations(stats)
        assert any('declining' in r.lower() for r in recs)

    def test_low_average_score_recommendation(self):
        """Test recommendation for low average scores."""
        stats = {
            'at_risk_percentage': 10,
            'average_attendance': 85,
            'trend_distribution': {'improving': 5, 'declining': 3},
            'average_score_mean': 55
        }

        recs = generate_general_recommendations(stats)
        assert any('score' in r.lower() or 'average' in r.lower() for r in recs)

    def test_good_performance_recommendation(self):
        """Test recommendation when everything is good."""
        stats = {
            'at_risk_percentage': 5,
            'average_attendance': 92,
            'trend_distribution': {'improving': 10, 'declining': 2},
            'average_score_mean': 82
        }

        recs = generate_general_recommendations(stats)
        assert any('good' in r.lower() or 'continue' in r.lower() for r in recs)


class TestHTMLReportGeneration:
    """Tests for HTML report generation."""

    def test_report_creates_file(self):
        """Test that report creates output file."""
        stats = {
            'total_students': 20,
            'average_score_mean': 75.5,
            'average_score_std': 12.3,
            'average_attendance': 85.0,
            'at_risk_percentage': 15.0,
            'risk_distribution': {'low': 12, 'medium': 5, 'high': 3},
            'trend_distribution': {'improving': 8, 'stable': 9, 'declining': 3}
        }

        at_risk = [
            StudentMetrics('S001', 55.0, 60.0, 65.0, 'declining', 'high'),
            StudentMetrics('S002', 62.0, 70.0, 75.0, 'stable', 'medium'),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'report.html')
            result = generate_html_report(stats, at_risk, output_path=output_path)

            assert os.path.exists(result)
            assert result == output_path

    def test_report_contains_statistics(self):
        """Test that report contains statistics."""
        stats = {
            'total_students': 25,
            'average_score_mean': 78.5,
            'average_score_std': 10.2,
            'average_attendance': 88.0,
            'at_risk_percentage': 12.0,
            'risk_distribution': {'low': 15, 'medium': 7, 'high': 3},
            'trend_distribution': {'improving': 10, 'stable': 12, 'declining': 3}
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'report.html')
            generate_html_report(stats, [], output_path=output_path)

            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()

            assert '25' in content  # total_students
            assert '78.5' in content  # average_score_mean

    def test_report_with_figures(self):
        """Test report generation with figure paths."""
        stats = {
            'total_students': 10,
            'average_score_mean': 70.0,
            'average_score_std': 8.0,
            'average_attendance': 80.0,
            'at_risk_percentage': 20.0,
            'risk_distribution': {'low': 5, 'medium': 3, 'high': 2},
            'trend_distribution': {'improving': 4, 'stable': 4, 'declining': 2}
        }

        figures = ['figures/risk.png', 'figures/scores.png']

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'report.html')
            generate_html_report(stats, [], figures, output_path)

            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()

            assert 'risk.png' in content
            assert 'scores.png' in content

    def test_report_empty_at_risk(self):
        """Test report with no at-risk students."""
        stats = {
            'total_students': 10,
            'average_score_mean': 85.0,
            'average_score_std': 5.0,
            'average_attendance': 95.0,
            'at_risk_percentage': 0.0,
            'risk_distribution': {'low': 10, 'medium': 0, 'high': 0},
            'trend_distribution': {'improving': 6, 'stable': 4, 'declining': 0}
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'report.html')
            generate_html_report(stats, [], output_path=output_path)

            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()

            assert 'No high-risk students' in content or 'Great job' in content

