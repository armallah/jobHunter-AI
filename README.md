# LinkedIn Job Hinter

This repository contains a pipeline for parsing a candidate's CV (from a PDF) and then using it to scrape and match LinkedIn job listings. **Important**: This project is still unfinished, and many features are subject to change in future updates.

## Overview

1. **Parse CV**: We extract text from a PDF file (placed in the `pdf/` directory).
2. **Create CV Profile**: The text is tokenised and shaped into a structured CV profile.
3. **LinkedIn Scraping**: We navigate LinkedIn, log in with your credentials, fetch job postings, and match them against the candidate's CV profile.
4. **CSV Output**: Any successfully matched jobs are added to `matched_jobs.csv`.

## Installation

1. Ensure you have Python 3.8+ installed.
2. Clone or download this repository.
3. Install necessary dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Optional: Set up a virtual environment for isolation:
   ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
## Usage
Place your PDF file in the pdf/ directory (or any path accessible to the script).
Run the main script with:
```bash
python3 main.py /pdf/your_cv.pdf
```
When prompted, enter your LinkedIn username and (censored) password.
The scraper logs in to LinkedIn, processes your CV data, and attempts to find matching jobs, saving results in matched_jobs.csv.

## Future Plans
Expand user input for search terms (discipline, location).
More robust handling of LinkedIn pages, including pagination strategies.
Additional logic to refine CV matching (fuzzy skill matches, partial experience, etc.).
Improved security for handling user credentials.

## Disclaimer
Use at your own risk. This tool automates interactions with LinkedIn and parsing of personal CV data. Be mindful of any potential Terms of Service constraints on automated scraping, and avoid exposing sensitive information.
