"""
Unit tests for the Visualizer module.

Tests cover:
- Risk distribution plotting
- Score distribution plotting
- Trend analysis plotting
- Correlation plotting
"""

import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.visualizer import (
    plot_risk_distribution,
    plot_score_distribution,
    plot_trend_analysis,
    plot_attendance_vs_score,
    generate_all_visualizations
)
from src.analyzer import StudentMetrics


class TestRiskDistributionPlot:
    """Tests for risk distribution visualization."""

    def test_plot_creates_file(self):
        """Test that plot creates output file."""
        risk_counts = {'low': 10, 'medium': 5, 'high': 3}

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'risk.png')
            plot_risk_distribution(risk_counts, output_path)
            assert os.path.exists(output_path)

    def test_plot_without_output(self):
        """Test that plot works without output path."""
        risk_counts = {'low': 10, 'medium': 5, 'high': 3}
        # Should not raise an exception
        plot_risk_distribution(risk_counts)


class TestScoreDistributionPlot:
    """Tests for score distribution visualization."""

    def test_plot_creates_file(self):
        """Test that plot creates output file."""
        scores = [75, 80, 85, 90, 65, 70, 88, 92, 78, 82]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'scores.png')
            plot_score_distribution(scores, output_path)
            assert os.path.exists(output_path)

    def test_plot_with_few_scores(self):
        """Test plot with minimal data."""
        scores = [75, 80]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'scores.png')
            plot_score_distribution(scores, output_path)
            assert os.path.exists(output_path)


class TestTrendAnalysisPlot:
    """Tests for trend analysis visualization."""

    def test_plot_creates_file(self):
        """Test that plot creates output file."""
        trend_counts = {'improving': 8, 'stable': 10, 'declining': 4}

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'trends.png')
            plot_trend_analysis(trend_counts, output_path)
            assert os.path.exists(output_path)


class TestCorrelationPlot:
    """Tests for attendance vs score correlation plot."""

    def test_plot_creates_file(self):
        """Test that plot creates output file."""
        attendance = [90, 85, 75, 95, 60, 80, 88, 92]
        scores = [88, 82, 70, 92, 55, 78, 85, 90]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'correlation.png')
            plot_attendance_vs_score(attendance, scores, output_path)
            assert os.path.exists(output_path)


class TestGenerateAllVisualizations:
    """Tests for generating all visualizations."""

    def test_generates_all_files(self):
        """Test that all visualization files are generated."""
        statistics = {
            'risk_distribution': {'low': 10, 'medium': 5, 'high': 3},
            'trend_distribution': {'improving': 8, 'stable': 7, 'declining': 3}
        }

        metrics_list = [
            StudentMetrics('S001', 85.0, 90.0, 95.0, 'stable', 'low'),
            StudentMetrics('S002', 70.0, 75.0, 80.0, 'improving', 'medium'),
            StudentMetrics('S003', 55.0, 60.0, 65.0, 'declining', 'high'),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = os.path.join(tmpdir, 'figures')
            files = generate_all_visualizations(statistics, metrics_list, output_dir)

            assert len(files) == 4
            for f in files:
                assert os.path.exists(f)

