# TA Grading System

This project automates the grading and feedback process for student assignments. It extracts data from student submissions, generates individual reports, and emails them to students. Additionally, it creates a summary page and emails the professor with a tarball containing all reports.

## Features
- **Grading**: The system grades assignments based on a rubric (addresses, decimals, prices, phone numbers, emails).
- **Report Generation**: Creates HTML reports for each student detailing their submission and score.
- **Summary Page**: Generates an index.html with links to each student's report.
- **Tarball Creation**: Creates a tar.gz file containing all submissions, reports, and the summary page.
- **Email Reports**: Sends individual reports to students and a summary tarball to the professor.

## Requirements
- Python 3.6+
- Libraries: `os`, `re`, `csv`, `tarfile`, `jinja2`
- Access to `mutt` command for sending emails

## Files
- **submissions/**: Folder containing student submissions.
- **reports/**: Folder where generated reports will be stored.
- **index.html**: Summary page linking to all reports.
- **submission_reports.tar.gz**: Compressed file containing all reports and submissions.
- **roster.csv**: CSV file with student IDs and email addresses.

## Rubric
- **Address**: 4 points
- **Decimal**: 4 points
- **Price**: 4 points
- **Phone Number**: 4 points
- **Email**: 4 points
- **Max Score**: 20 points

## Usage
1. Place student submissions in the `submissions/` directory.
2. Ensure the `Roster.csv` file contains student IDs and email addresses.
3. Run the Python script to generate reports, create the tarball, and send emails.

## Email Functionality
- Student reports are sent to the email addresses from `Roster.csv`.
- The professor receives a `submission_reports.tar.gz` containing the reports and submissions.

## How to Run
1. Ensure the necessary directories and files are in place.
2. Execute the Python script.
3. Enter the professor's email address when prompted to send the summary tarball.
