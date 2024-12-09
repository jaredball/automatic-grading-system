
# Imports
import os
import re
import csv
import tarfile
from pathlib import Path
from jinja2 import Template

# Paths
SUBMISSIONS_DIR = 'submissions'
REPORTS_DIR = 'reports'
INDEX_FILE = 'index.html'
PROFESSOR_FILE = 'submission_reports.tar.gz'
ROSTER_FILE = 'Roster.csv'

# Regular expressions for pattern matching
PATTERNS = {
    'address': r'(?<![\S])\b\d+\s+(?:[A-Z][a-zA-Z]*(?:\.\s*)?)+\s+(?:[A-Z][a-zA-Z]*(?:\.\s*)?)+\b',
    'decimal': r'(?<![\S])-?\s?(?!0\d)\d+\.\d+\b(?!\.\d)',
    'price': r'\$(?:(?!0\d)\d{1,3}(?:,\d{3})*|\d+)(?:\.\d{2})?\b(?!\s*,\S)',
    'phone': r'(\(\d{3}\)\s?[-]?\d{3}-\d{4}|\d{3}-\d{3}-\d{4})',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b'
}

# Scoring rubric
RUBRIC = {
    'address': 4,
    'decimal': 4,
    'price': 4,
    'phone': 4,
    'email': 4,
    'max_score': 20
}


# Extract patterns from text with uniqueness check
def extract_patterns(text, patterns):
    matches = {}
    for key, pattern in patterns.items():
        # Find all matches and remove duplicates while preserving order
        matches[key] = list(dict.fromkeys(re.findall(pattern, text)))
    return matches


# Calculate scores based on the rubric
def calculate_score(matches):
    scores = {}
    for key, values in matches.items():
        # Max number of matches is 5
        unique_values = list(dict.fromkeys(values))[:5]
        scores[key] = min(len(unique_values), 5) * RUBRIC[key]

    return scores, unique_values


# Generate HTML report for a student
def generate_report(student_id, submission_file, matches, scores, total_score):
    template = Template("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Report for Student {{ student_id }}</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1, h2 { color: #333; }
            ul { list-style-type: disc; margin-left: 20px; }
        </style>
    </head>
    <body>
        <h1>Report for Student {{ student_id }}</h1>
        <p><strong>Submission:</strong> <a href="../submissions/{{ submission_file }}">{{ submission_file }}</a></p>
        <h2>Details</h2>
        {% for category, values in matches.items() %}
        <h3>{{ category.capitalize() }}</h3>
        <ul>
            {% for value in values %}
            <li>{{ value }}</li>
            {% endfor %}
        </ul>
        {% endfor %}
        <h2>Scores</h2>
        <ul>
            {% for category, score in scores.items() %}
            <li>{{ category.capitalize() }}: {{ score }}</li>
            {% endfor %}
        </ul>
        <h2>Total Score: {{ total_score }}</h2>
    </body>
    </html>
    """)
    # Render the template with specific data
    return template.render(
        student_id=student_id,
        submission_file=submission_file,
        matches=matches,
        scores=scores,
        total_score=total_score
    )


# Send email using mutt
def send_email(to_email, subject, body, attachment=None):
    command = f'echo "{body}" | mutt -s "{subject}"'
    if attachment:
        command += f' -a {attachment}'
    command += f' -- {to_email}'
    os.system(command)


# Main function
def main():

    # Create reports directory
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # Load roster
    with open(ROSTER_FILE, 'r') as file:
        roster = {row['Student ID']: row for row in csv.DictReader(file)}

    # Process each submission
    summary_links = []
    for submission_file in Path(SUBMISSIONS_DIR).glob('submission_student_*.txt'):
        student_id = submission_file.stem.split('_')[-1]
        with open(submission_file, 'r') as file:
            content = file.read()

        # Extract matches and calculate scores
        matches = extract_patterns(content, PATTERNS)
        scores, _ = calculate_score(matches)
        total_score = sum(scores.values())

        # Generate report
        report_html = generate_report(student_id, submission_file.name, matches, scores, total_score)
        report_path = Path(REPORTS_DIR) / f'report_student_{student_id}.html'
        with open(report_path, 'w') as file:
            file.write(report_html)

        # Add to summary
        summary_links.append(f'<li><a href="reports/{report_path.name}">Report for Student {student_id}</a></li>')

        # Email individual reports
        if student_id in roster:
            send_email(
                to_email=roster[student_id]['Email address'],
                subject=f"Report for Student {student_id}",
                body="Attached is your assignment report.",
                attachment=report_path
            )

    # Create index.html
    with open(INDEX_FILE, 'w') as file:
        file.write(f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>All Reports</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #333; }}
                ul {{ list-style-type: none; padding: 0; }}
                li {{ margin-bottom: 10px; }}
            </style>
        </head>
        <body>
            <h1>All Reports</h1>
            <ul>
                {''.join(summary_links)}
            </ul>
        </body>
        </html>
        """)

    # Fill summary file
    with tarfile.open(PROFESSOR_FILE, 'w:gz') as tar:
        tar.add(SUBMISSIONS_DIR)
        tar.add(REPORTS_DIR)
        tar.add(INDEX_FILE)

    # Email professor
    professor_email = input("Enter the professor's email: ")
    send_email(
        to_email=professor_email,
        subject="All Submission Reports",
        body="Attached is the file containing all the submission reports.",
        attachment=PROFESSOR_FILE
    )


if __name__ == '__main__':
    main()
