"""
Unit tests for the Student Performance Analyzer.

Tests cover:
- Score calculation
- Trend analysis
- Risk level determination
- Full analysis pipeline
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.analyzer import StudentPerformanceAnalyzer, StudentMetrics


class TestScoreCalculation:
    """Tests for score calculation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = StudentPerformanceAnalyzer()

    def test_calculate_average_score_normal(self):
        """Test average calculation with normal input."""
        scores = "80,85,90,95,100"
        result = self.analyzer.calculate_average_score(scores)
        assert result == 90.0

    def test_calculate_average_score_single(self):
        """Test average calculation with single score."""
        scores = "75"
        result = self.analyzer.calculate_average_score(scores)
        assert result == 75.0

    def test_calculate_average_score_empty(self):
        """Test average calculation with empty string."""
        result = self.analyzer.calculate_average_score("")
        assert result == 0.0

    def test_calculate_average_score_nan(self):
        """Test average calculation with NaN."""
        result = self.analyzer.calculate_average_score(np.nan)
        assert result == 0.0

    def test_calculate_average_score_with_spaces(self):
        """Test average calculation with spaces in input."""
        scores = "80, 85, 90"
        result = self.analyzer.calculate_average_score(scores)
        assert result == 85.0


class TestTrendAnalysis:
    """Tests for trend analysis functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = StudentPerformanceAnalyzer()

    def test_trend_improving(self):
        """Test detection of improving trend."""
        scores = "60,62,65,70,75,80,85,90"
        result = self.analyzer.calculate_trend(scores)
        assert result == 'improving'

    def test_trend_declining(self):
        """Test detection of declining trend."""
        scores = "90,85,80,75,70,65,60,55"
        result = self.analyzer.calculate_trend(scores)
        assert result == 'declining'

    def test_trend_stable(self):
        """Test detection of stable trend."""
        scores = "75,76,74,75,76,75,74,75"
        result = self.analyzer.calculate_trend(scores)
        assert result == 'stable'

    def test_trend_empty(self):
        """Test trend with empty input."""
        result = self.analyzer.calculate_trend("")
        assert result == 'stable'

    def test_trend_single_score(self):
        """Test trend with single score."""
        result = self.analyzer.calculate_trend("75")
        assert result == 'stable'


class TestRiskLevel:
    """Tests for risk level determination."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = StudentPerformanceAnalyzer()

    def test_risk_low(self):
        """Test low risk determination."""
        result = self.analyzer.determine_risk_level(90, 95, 100)
        assert result == 'low'

    def test_risk_medium(self):
        """Test medium risk determination."""
        result = self.analyzer.determine_risk_level(70, 75, 80)
        assert result == 'medium'

    def test_risk_high(self):
        """Test high risk determination."""
        result = self.analyzer.determine_risk_level(40, 50, 60)
        assert result == 'high'

    def test_risk_boundary_low_medium(self):
        """Test boundary between low and medium risk."""
        # Risk score = (100-80)*0.4 + (100-80)*0.3 + (100-80)*0.3 = 20
        result = self.analyzer.determine_risk_level(80, 80, 80)
        assert result == 'medium'

    def test_risk_perfect_scores(self):
        """Test risk with perfect scores."""
        result = self.analyzer.determine_risk_level(100, 100, 100)
        assert result == 'low'


class TestStudentAnalysis:
    """Tests for individual student analysis."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = StudentPerformanceAnalyzer()

    def test_analyze_student_complete(self):
        """Test analysis of a complete student record."""
        row = pd.Series({
            'student_id': 'TEST001',
            'assignment_scores': '80,85,90',
            'quiz_scores': '75,80,85',
            'attendance': 90,
            'completion_rate': 95
        })

        result = self.analyzer.analyze_student(row)

        assert isinstance(result, StudentMetrics)
        assert result.student_id == 'TEST001'
        assert result.average_score == 82.5  # (85 + 80) / 2
        assert result.attendance_rate == 90
        assert result.assignment_completion == 95

    def test_analyze_student_missing_completion(self):
        """Test analysis with missing completion rate."""
        row = pd.Series({
            'student_id': 'TEST002',
            'assignment_scores': '70,75,80',
            'quiz_scores': '65,70,75',
            'attendance': 85
        })

        result = self.analyzer.analyze_student(row)
        assert result.assignment_completion == 100  # Default value


class TestFullAnalysis:
    """Tests for full analysis pipeline."""

    def setup_method(self):
        """Set up test fixtures with sample data."""
        self.analyzer = StudentPerformanceAnalyzer()
        self.sample_data = pd.DataFrame({
            'student_id': ['S001', 'S002', 'S003'],
            'name': ['Alice', 'Bob', 'Carol'],
            'assignment_scores': ['90,92,94', '50,48,45', '75,78,80'],
            'quiz_scores': ['88,90,92', '52,50,48', '73,76,78'],
            'attendance': [95, 55, 82],
            'completion_rate': [100, 60, 90]
        })

    def test_load_data_from_dataframe(self):
        """Test loading data from DataFrame."""
        result = self.analyzer.load_data_from_dataframe(self.sample_data)
        assert len(result) == 3
        assert self.analyzer.data is not None

    def test_analyze_all_students(self):
        """Test analyzing all students."""
        self.analyzer.load_data_from_dataframe(self.sample_data)
        metrics = self.analyzer.analyze_all_students()

        assert len(metrics) == 3
        assert 'S001' in metrics
        assert 'S002' in metrics
        assert 'S003' in metrics

    def test_analyze_without_data_raises_error(self):
        """Test that analyzing without data raises error."""
        with pytest.raises(ValueError, match="No data loaded"):
            self.analyzer.analyze_all_students()

    def test_get_at_risk_students(self):
        """Test getting at-risk students."""
        self.analyzer.load_data_from_dataframe(self.sample_data)
        self.analyzer.analyze_all_students()

        high_risk = self.analyzer.get_at_risk_students('high')
        # S002 should be high risk (low scores, low attendance)
        assert any(s.student_id == 'S002' for s in high_risk)

    def test_get_statistics(self):
        """Test getting statistics."""
        self.analyzer.load_data_from_dataframe(self.sample_data)
        stats = self.analyzer.get_statistics()

        assert 'total_students' in stats
        assert stats['total_students'] == 3
        assert 'risk_distribution' in stats
        assert 'trend_distribution' in stats
        assert 'average_score_mean' in stats


class TestRecommendations:
    """Tests for recommendation generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = StudentPerformanceAnalyzer()
        self.sample_data = pd.DataFrame({
            'student_id': ['S001', 'S002'],
            'name': ['Good Student', 'Struggling Student'],
            'assignment_scores': ['90,92,94,96', '40,38,35,32'],
            'quiz_scores': ['88,90,92,94', '42,40,38,36'],
            'attendance': [98, 50],
            'completion_rate': [100, 55]
        })
        self.analyzer.load_data_from_dataframe(self.sample_data)
        self.analyzer.analyze_all_students()

    def test_recommendations_good_student(self):
        """Test recommendations for well-performing student."""
        recs = self.analyzer.generate_recommendations('S001')
        assert len(recs) >= 1
        assert any('performing well' in r.lower() for r in recs)

    def test_recommendations_struggling_student(self):
        """Test recommendations for struggling student."""
        recs = self.analyzer.generate_recommendations('S002')
        assert len(recs) >= 1
        # Should have multiple recommendations
        assert any('tutoring' in r.lower() or 'attendance' in r.lower()
                   for r in recs)

    def test_recommendations_unknown_student(self):
        """Test recommendations for unknown student."""
        recs = self.analyzer.generate_recommendations('UNKNOWN')
        assert len(recs) == 1
        assert 'not found' in recs[0].lower()


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = StudentPerformanceAnalyzer()

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        empty_df = pd.DataFrame(columns=[
            'student_id', 'name', 'assignment_scores',
            'quiz_scores', 'attendance', 'completion_rate'
        ])
        self.analyzer.load_data_from_dataframe(empty_df)
        metrics = self.analyzer.analyze_all_students()
        assert len(metrics) == 0

    def test_invalid_scores_format(self):
        """Test handling of invalid score format."""
        result = self.analyzer.calculate_average_score("invalid,data")
        assert result == 0.0

    def test_negative_values(self):
        """Test handling of negative values."""
        result = self.analyzer.determine_risk_level(-10, -10, -10)
        # Should still return a valid risk level
        assert result in ['low', 'medium', 'high']

    def test_values_over_100(self):
        """Test handling of values over 100."""
        result = self.analyzer.determine_risk_level(150, 150, 150)
        assert result == 'low'  # Very negative risk score

