"""
Student Performance Analyzer - Core Analysis Module

This module provides functionality for analyzing student performance data,
identifying at-risk students, and generating insights for educators.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class StudentMetrics:
    """Data class for storing student performance metrics."""
    student_id: str
    average_score: float
    attendance_rate: float
    assignment_completion: float
    trend: str  # 'improving', 'declining', 'stable'
    risk_level: str  # 'low', 'medium', 'high'


class StudentPerformanceAnalyzer:
    """
    Analyzes student performance data to identify patterns and at-risk students.

    This class provides methods for:
    - Loading and preprocessing student data
    - Calculating performance metrics
    - Identifying at-risk students
    - Generating performance reports

    Attributes:
        data (pd.DataFrame): The loaded student performance data
        metrics (Dict[str, StudentMetrics]): Calculated metrics for each student
    """

    def __init__(self):
        """Initialize the analyzer with empty data."""
        self.data: Optional[pd.DataFrame] = None
        self.metrics: Dict[str, StudentMetrics] = {}

    def load_data(self, filepath: str) -> pd.DataFrame:
        """
        Load student performance data from a CSV file.

        Args:
            filepath: Path to the CSV file containing student data

        Returns:
            pd.DataFrame: Loaded and validated data

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If required columns are missing
        """
        required_columns = [
            'student_id', 'name', 'assignment_scores',
            'attendance', 'quiz_scores'
        ]

        self.data = pd.read_csv(filepath)

        missing_cols = set(required_columns) - set(self.data.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        return self.data

    def load_data_from_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Load student performance data from an existing DataFrame.

        Args:
            df: DataFrame containing student data

        Returns:
            pd.DataFrame: Validated data
        """
        self.data = df.copy()
        return self.data

    def calculate_average_score(self, scores_str: str) -> float:
        """
        Calculate average score from a comma-separated string of scores.

        Args:
            scores_str: Comma-separated string of numeric scores

        Returns:
            float: Average score rounded to 2 decimal places
        """
        if pd.isna(scores_str) or scores_str == '':
            return 0.0

        try:
            scores = [float(s.strip()) for s in str(scores_str).split(',')]
            return round(np.mean(scores), 2)
        except (ValueError, AttributeError):
            return 0.0

    def calculate_trend(self, scores_str: str) -> str:
        """
        Determine the performance trend based on score progression.

        Args:
            scores_str: Comma-separated string of scores over time

        Returns:
            str: 'improving', 'declining', or 'stable'
        """
        if pd.isna(scores_str) or scores_str == '':
            return 'stable'

        try:
            scores = [float(s.strip()) for s in str(scores_str).split(',')]
            if len(scores) < 2:
                return 'stable'

            # Compare first half average with second half average
            mid = len(scores) // 2
            first_half = np.mean(scores[:mid])
            second_half = np.mean(scores[mid:])

            diff = second_half - first_half
            if diff > 5:
                return 'improving'
            elif diff < -5:
                return 'declining'
            else:
                return 'stable'
        except (ValueError, AttributeError):
            return 'stable'

    def determine_risk_level(
        self,
        avg_score: float,
        attendance: float,
        completion: float
    ) -> str:
        """
        Determine the risk level of a student based on multiple factors.

        Args:
            avg_score: Average score (0-100)
            attendance: Attendance rate (0-100)
            completion: Assignment completion rate (0-100)

        Returns:
            str: 'low', 'medium', or 'high' risk level
        """
        # Calculate weighted risk score
        risk_score = (
            (100 - avg_score) * 0.4 +
            (100 - attendance) * 0.3 +
            (100 - completion) * 0.3
        )

        if risk_score >= 40:
            return 'high'
        elif risk_score >= 20:
            return 'medium'
        else:
            return 'low'

    def analyze_student(self, row: pd.Series) -> StudentMetrics:
        """
        Analyze a single student's performance.

        Args:
            row: A pandas Series containing student data

        Returns:
            StudentMetrics: Calculated metrics for the student
        """
        avg_assignment = self.calculate_average_score(row.get('assignment_scores', ''))
        avg_quiz = self.calculate_average_score(row.get('quiz_scores', ''))
        average_score = round((avg_assignment + avg_quiz) / 2, 2)

        attendance = float(row.get('attendance', 0))
        completion = float(row.get('completion_rate', 100))

        trend = self.calculate_trend(row.get('assignment_scores', ''))
        risk_level = self.determine_risk_level(average_score, attendance, completion)

        return StudentMetrics(
            student_id=str(row['student_id']),
            average_score=average_score,
            attendance_rate=attendance,
            assignment_completion=completion,
            trend=trend,
            risk_level=risk_level
        )

    def analyze_all_students(self) -> Dict[str, StudentMetrics]:
        """
        Analyze all students in the loaded data.

        Returns:
            Dict[str, StudentMetrics]: Dictionary mapping student IDs to metrics

        Raises:
            ValueError: If no data has been loaded
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")

        self.metrics = {}
        for _, row in self.data.iterrows():
            metrics = self.analyze_student(row)
            self.metrics[metrics.student_id] = metrics

        return self.metrics

    def get_at_risk_students(self, risk_level: str = 'high') -> List[StudentMetrics]:
        """
        Get list of students at specified risk level.

        Args:
            risk_level: Risk level to filter by ('low', 'medium', 'high')

        Returns:
            List[StudentMetrics]: Students matching the risk level
        """
        if not self.metrics:
            self.analyze_all_students()

        return [m for m in self.metrics.values() if m.risk_level == risk_level]

    def get_statistics(self) -> Dict[str, any]:
        """
        Calculate overall statistics for the student population.

        Returns:
            Dict containing various statistics about student performance
        """
        if not self.metrics:
            self.analyze_all_students()

        scores = [m.average_score for m in self.metrics.values()]
        attendance = [m.attendance_rate for m in self.metrics.values()]

        risk_counts = {'low': 0, 'medium': 0, 'high': 0}
        trend_counts = {'improving': 0, 'stable': 0, 'declining': 0}

        for m in self.metrics.values():
            risk_counts[m.risk_level] += 1
            trend_counts[m.trend] += 1

        return {
            'total_students': len(self.metrics),
            'average_score_mean': round(np.mean(scores), 2) if scores else 0,
            'average_score_std': round(np.std(scores), 2) if scores else 0,
            'average_attendance': round(np.mean(attendance), 2) if attendance else 0,
            'risk_distribution': risk_counts,
            'trend_distribution': trend_counts,
            'at_risk_percentage': round(
                (risk_counts['high'] + risk_counts['medium']) /
                len(self.metrics) * 100, 2
            ) if self.metrics else 0
        }

    def generate_recommendations(
        self,
        student_id: str
    ) -> List[str]:
        """
        Generate personalized recommendations for a student.

        Args:
            student_id: The ID of the student

        Returns:
            List[str]: List of recommendations
        """
        if student_id not in self.metrics:
            return ["Student not found in analyzed data."]

        metrics = self.metrics[student_id]
        recommendations = []

        if metrics.average_score < 60:
            recommendations.append(
                "Consider additional tutoring sessions to improve understanding."
            )

        if metrics.attendance_rate < 80:
            recommendations.append(
                "Attendance is below optimal. Regular attendance strongly "
                "correlates with better performance."
            )

        if metrics.assignment_completion < 90:
            recommendations.append(
                "Focus on completing all assignments. "
                "Missing assignments significantly impact final grades."
            )

        if metrics.trend == 'declining':
            recommendations.append(
                "Performance trend is declining. "
                "Schedule a meeting to discuss challenges."
            )

        if metrics.risk_level == 'high':
            recommendations.append(
                "HIGH PRIORITY: This student needs immediate intervention."
            )

        if not recommendations:
            recommendations.append(
                "Student is performing well. Continue current study habits."
            )

        return recommendations

