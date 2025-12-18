"""
Student Performance Visualizer

This module provides visualization functions for student performance data.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List, Optional
import os

# Use non-interactive backend for CI/CD
plt.switch_backend('Agg')


def plot_risk_distribution(
    risk_counts: Dict[str, int],
    output_path: Optional[str] = None
) -> None:
    """
    Create a pie chart showing distribution of risk levels.

    Args:
        risk_counts: Dictionary with risk levels and their counts
        output_path: Path to save the figure (optional)
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    colors = {'low': '#2ecc71', 'medium': '#f39c12', 'high': '#e74c3c'}
    labels = list(risk_counts.keys())
    sizes = list(risk_counts.values())
    chart_colors = [colors[label] for label in labels]

    ax.pie(
        sizes,
        labels=[f"{l.capitalize()}: {s}" for l, s in zip(labels, sizes)],
        colors=chart_colors,
        autopct='%1.1f%%',
        startangle=90
    )
    ax.set_title('Student Risk Level Distribution')

    plt.tight_layout()

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')

    plt.close(fig)


def plot_score_distribution(
    scores: List[float],
    output_path: Optional[str] = None
) -> None:
    """
    Create a histogram of student scores.

    Args:
        scores: List of student average scores
        output_path: Path to save the figure (optional)
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    sns.histplot(scores, bins=20, kde=True, ax=ax, color='#3498db')

    ax.axvline(np.mean(scores), color='red', linestyle='--', label=f'Mean: {np.mean(scores):.1f}')
    ax.axvline(np.median(scores), color='green', linestyle='--', label=f'Median: {np.median(scores):.1f}')

    ax.set_xlabel('Average Score')
    ax.set_ylabel('Number of Students')
    ax.set_title('Distribution of Student Scores')
    ax.legend()

    plt.tight_layout()

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')

    plt.close(fig)


def plot_trend_analysis(
    trend_counts: Dict[str, int],
    output_path: Optional[str] = None
) -> None:
    """
    Create a bar chart showing performance trends.

    Args:
        trend_counts: Dictionary with trends and their counts
        output_path: Path to save the figure (optional)
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    colors = {'improving': '#27ae60', 'stable': '#3498db', 'declining': '#e74c3c'}
    trends = list(trend_counts.keys())
    counts = list(trend_counts.values())
    bar_colors = [colors.get(t, '#95a5a6') for t in trends]

    bars = ax.bar(trends, counts, color=bar_colors)

    for bar, count in zip(bars, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            str(count),
            ha='center',
            va='bottom',
            fontweight='bold'
        )

    ax.set_xlabel('Performance Trend')
    ax.set_ylabel('Number of Students')
    ax.set_title('Student Performance Trends')

    plt.tight_layout()

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')

    plt.close(fig)


def plot_attendance_vs_score(
    attendance: List[float],
    scores: List[float],
    output_path: Optional[str] = None
) -> None:
    """
    Create a scatter plot showing correlation between attendance and scores.

    Args:
        attendance: List of attendance rates
        scores: List of average scores
        output_path: Path to save the figure (optional)
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(attendance, scores, alpha=0.6, c='#9b59b6', s=50)

    # Add trend line
    z = np.polyfit(attendance, scores, 1)
    p = np.poly1d(z)
    x_line = np.linspace(min(attendance), max(attendance), 100)
    ax.plot(x_line, p(x_line), "r--", alpha=0.8, label='Trend line')

    # Calculate correlation
    correlation = np.corrcoef(attendance, scores)[0, 1]

    ax.set_xlabel('Attendance Rate (%)')
    ax.set_ylabel('Average Score')
    ax.set_title(f'Attendance vs Performance (r = {correlation:.2f})')
    ax.legend()

    plt.tight_layout()

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')

    plt.close(fig)


def generate_all_visualizations(
    statistics: Dict,
    metrics_list: List,
    output_dir: str = 'reports/figures'
) -> List[str]:
    """
    Generate all visualizations and save them to the output directory.

    Args:
        statistics: Dictionary containing overall statistics
        metrics_list: List of StudentMetrics objects
        output_dir: Directory to save figures

    Returns:
        List of paths to generated figures
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = []

    # Risk distribution
    risk_path = os.path.join(output_dir, 'risk_distribution.png')
    plot_risk_distribution(statistics['risk_distribution'], risk_path)
    generated_files.append(risk_path)

    # Score distribution
    scores = [m.average_score for m in metrics_list]
    score_path = os.path.join(output_dir, 'score_distribution.png')
    plot_score_distribution(scores, score_path)
    generated_files.append(score_path)

    # Trend analysis
    trend_path = os.path.join(output_dir, 'trend_analysis.png')
    plot_trend_analysis(statistics['trend_distribution'], trend_path)
    generated_files.append(trend_path)

    # Attendance vs Score
    attendance = [m.attendance_rate for m in metrics_list]
    correlation_path = os.path.join(output_dir, 'attendance_correlation.png')
    plot_attendance_vs_score(attendance, scores, correlation_path)
    generated_files.append(correlation_path)

    return generated_files

