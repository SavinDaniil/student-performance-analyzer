"""
Report Generator Module

Generates HTML reports with student performance analysis.
"""

import os
from datetime import datetime
from typing import Dict, List
from jinja2 import Template


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Performance Report - {{ report_date }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            opacity: 0.8;
            font-size: 1.1em;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
        }
        .stat-label {
            color: #7f8c8d;
            margin-top: 5px;
            font-size: 0.9em;
        }
        .stat-card.risk-high .stat-value { color: #e74c3c; }
        .stat-card.risk-medium .stat-value { color: #f39c12; }
        .stat-card.risk-low .stat-value { color: #27ae60; }
        .section {
            padding: 30px;
        }
        .section h2 {
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }
        .risk-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .risk-table th, .risk-table td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }
        .risk-table th {
            background: #2c3e50;
            color: white;
        }
        .risk-table tr:hover {
            background: #f8f9fa;
        }
        .risk-badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }
        .risk-high { background: #fadbd8; color: #e74c3c; }
        .risk-medium { background: #fdebd0; color: #f39c12; }
        .risk-low { background: #d5f4e6; color: #27ae60; }
        .trend-improving { color: #27ae60; }
        .trend-stable { color: #3498db; }
        .trend-declining { color: #e74c3c; }
        .recommendations {
            background: #fff3cd;
            padding: 20px;
            border-radius: 10px;
            margin-top: 15px;
        }
        .recommendations h4 {
            color: #856404;
            margin-bottom: 10px;
        }
        .recommendations ul {
            margin-left: 20px;
            color: #856404;
        }
        .footer {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
        }
        .figures {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        .figure-card {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .figure-card img {
            width: 100%;
            height: auto;
        }
        .figure-card p {
            padding: 15px;
            text-align: center;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Student Performance Report</h1>
            <p>Generated on {{ report_date }}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{{ stats.total_students }}</div>
                <div class="stat-label">Total Students</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.average_score_mean }}%</div>
                <div class="stat-label">Average Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.average_attendance }}%</div>
                <div class="stat-label">Avg Attendance</div>
            </div>
            <div class="stat-card risk-high">
                <div class="stat-value">{{ stats.risk_distribution.high }}</div>
                <div class="stat-label">High Risk Students</div>
            </div>
            <div class="stat-card risk-medium">
                <div class="stat-value">{{ stats.risk_distribution.medium }}</div>
                <div class="stat-label">Medium Risk</div>
            </div>
            <div class="stat-card risk-low">
                <div class="stat-value">{{ stats.risk_distribution.low }}</div>
                <div class="stat-label">Low Risk</div>
            </div>
        </div>

        <div class="section">
            <h2>🚨 At-Risk Students (Require Attention)</h2>
            {% if at_risk_students %}
            <table class="risk-table">
                <thead>
                    <tr>
                        <th>Student ID</th>
                        <th>Average Score</th>
                        <th>Attendance</th>
                        <th>Completion</th>
                        <th>Trend</th>
                        <th>Risk Level</th>
                    </tr>
                </thead>
                <tbody>
                    {% for student in at_risk_students %}
                    <tr>
                        <td>{{ student.student_id }}</td>
                        <td>{{ student.average_score }}%</td>
                        <td>{{ student.attendance_rate }}%</td>
                        <td>{{ student.assignment_completion }}%</td>
                        <td class="trend-{{ student.trend }}">
                            {% if student.trend == 'improving' %}📈{% elif student.trend == 'declining' %}📉{% else %}➡️{% endif %}
                            {{ student.trend | capitalize }}
                        </td>
                        <td><span class="risk-badge risk-{{ student.risk_level }}">{{ student.risk_level | upper }}</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p>✅ No high-risk students identified. Great job!</p>
            {% endif %}
        </div>

        {% if figures %}
        <div class="section">
            <h2>📈 Visualizations</h2>
            <div class="figures">
                {% for fig in figures %}
                <div class="figure-card">
                    <img src="{{ fig }}" alt="Analysis Figure">
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        <div class="section">
            <h2>💡 General Recommendations</h2>
            <div class="recommendations">
                <h4>Based on the analysis:</h4>
                <ul>
                    {% for rec in recommendations %}
                    <li>{{ rec }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>

        <div class="footer">
            <p>Student Performance Analyzer v1.0.0 | Automated Report</p>
        </div>
    </div>
</body>
</html>
"""


def generate_general_recommendations(stats: Dict) -> List[str]:
    """
    Generate general recommendations based on overall statistics.

    Args:
        stats: Dictionary containing overall statistics

    Returns:
        List of recommendation strings
    """
    recommendations = []

    if stats['at_risk_percentage'] > 30:
        recommendations.append(
            f"{stats['at_risk_percentage']}% of students are at risk. "
            "Consider implementing additional support programs."
        )

    if stats['average_attendance'] < 80:
        recommendations.append(
            "Average attendance is below 80%. "
            "Consider strategies to improve student engagement."
        )

    if stats['trend_distribution']['declining'] > stats['trend_distribution']['improving']:
        recommendations.append(
            "More students are declining than improving. "
            "Review recent curriculum changes or teaching methods."
        )

    if stats['average_score_mean'] < 70:
        recommendations.append(
            "Overall average score is below 70%. "
            "Consider reviewing assessment difficulty or providing more resources."
        )

    if not recommendations:
        recommendations.append(
            "Overall performance is good. Continue current teaching strategies."
        )
        recommendations.append(
            "Consider implementing peer tutoring to help struggling students."
        )

    return recommendations


def generate_html_report(
    stats: Dict,
    at_risk_students: List,
    figures: List[str] = None,
    output_path: str = 'reports/report.html'
) -> str:
    """
    Generate an HTML report with analysis results.

    Args:
        stats: Dictionary containing overall statistics
        at_risk_students: List of StudentMetrics for at-risk students
        figures: List of paths to figure images
        output_path: Path to save the HTML report

    Returns:
        Path to the generated report
    """
    template = Template(HTML_TEMPLATE)

    recommendations = generate_general_recommendations(stats)

    # Convert figure paths to relative paths for HTML
    relative_figures = []
    if figures:
        for fig in figures:
            # Get just the filename
            relative_figures.append(os.path.basename(fig))

    html_content = template.render(
        report_date=datetime.now().strftime('%Y-%m-%d %H:%M'),
        stats=stats,
        at_risk_students=at_risk_students,
        figures=relative_figures,
        recommendations=recommendations
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return output_path

