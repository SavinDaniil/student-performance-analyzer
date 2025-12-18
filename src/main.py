"""
Student Performance Analyzer - Main Entry Point

This script demonstrates the full analysis pipeline:
1. Load student data
2. Analyze performance
3. Generate visualizations
4. Create HTML report
"""

import os
import sys
import argparse

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzer import StudentPerformanceAnalyzer
from src.visualizer import generate_all_visualizations
from src.report_generator import generate_html_report


def main(data_path: str = None, output_dir: str = 'reports'):
    """
    Run the complete analysis pipeline.

    Args:
        data_path: Path to the CSV file with student data
        output_dir: Directory to save reports and figures
    """
    print("=" * 60)
    print("  Student Performance Analyzer v1.0.0")
    print("=" * 60)

    # Default to sample data if no path provided
    if data_path is None:
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data',
            'sample_students.csv'
        )

    print(f"\n📁 Loading data from: {data_path}")

    # Initialize analyzer
    analyzer = StudentPerformanceAnalyzer()

    try:
        analyzer.load_data(data_path)
        print(f"✅ Loaded {len(analyzer.data)} student records")
    except FileNotFoundError:
        print(f"❌ Error: File not found: {data_path}")
        return 1
    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1

    # Analyze all students
    print("\n📊 Analyzing student performance...")
    metrics = analyzer.analyze_all_students()
    print(f"✅ Analyzed {len(metrics)} students")

    # Get statistics
    stats = analyzer.get_statistics()

    print("\n📈 Overall Statistics:")
    print(f"   • Total Students: {stats['total_students']}")
    print(f"   • Average Score: {stats['average_score_mean']}% (±{stats['average_score_std']})")
    print(f"   • Average Attendance: {stats['average_attendance']}%")
    print(f"   • At-Risk Percentage: {stats['at_risk_percentage']}%")

    print("\n🎯 Risk Distribution:")
    for level, count in stats['risk_distribution'].items():
        emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}[level]
        print(f"   {emoji} {level.capitalize()}: {count} students")

    print("\n📉 Performance Trends:")
    for trend, count in stats['trend_distribution'].items():
        emoji = {'improving': '📈', 'stable': '➡️', 'declining': '📉'}[trend]
        print(f"   {emoji} {trend.capitalize()}: {count} students")

    # Get at-risk students
    high_risk = analyzer.get_at_risk_students('high')
    medium_risk = analyzer.get_at_risk_students('medium')
    at_risk = high_risk + medium_risk

    if high_risk:
        print(f"\n⚠️  High-risk students requiring immediate attention:")
        for student in high_risk:
            print(f"   • {student.student_id}: Score={student.average_score}%, "
                  f"Attendance={student.attendance_rate}%, Trend={student.trend}")

    # Generate visualizations
    print(f"\n🎨 Generating visualizations...")
    figures_dir = os.path.join(output_dir, 'figures')
    figures = generate_all_visualizations(
        stats,
        list(metrics.values()),
        figures_dir
    )
    print(f"✅ Generated {len(figures)} figures in {figures_dir}")

    # Generate HTML report
    print(f"\n📝 Generating HTML report...")
    report_path = os.path.join(output_dir, 'report.html')
    generate_html_report(stats, at_risk, figures, report_path)
    print(f"✅ Report saved to: {report_path}")

    # Show recommendations for a sample student
    if metrics:
        sample_id = list(metrics.keys())[0]
        print(f"\n💡 Sample recommendations for student {sample_id}:")
        recommendations = analyzer.generate_recommendations(sample_id)
        for rec in recommendations:
            print(f"   • {rec}")

    print("\n" + "=" * 60)
    print("  Analysis complete!")
    print("=" * 60)

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Analyze student performance data'
    )
    parser.add_argument(
        '--data', '-d',
        type=str,
        help='Path to CSV file with student data'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='reports',
        help='Output directory for reports'
    )

    args = parser.parse_args()
    sys.exit(main(args.data, args.output))

