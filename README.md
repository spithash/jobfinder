# JobFind.gr Scraper
jobfind.gr CLI tool that displays job openings in the linux terminal

A simple Python script to scrape job listings from [JobFind.gr](https://www.jobfind.gr).  
It lets you select job specialties and regions interactively, then fetches and displays job postings with brief descriptions.

---

## Features

- Choose job specialty from a list  
- Choose region to filter jobs  
- Counts total available jobs for the chosen filters  
- Displays job title, posting date, link, and a short snippet of the job description  
- Handles pagination to fetch multiple pages of results  
- Polite scraping with delays and user-agent headers

---

## Requirements

- Python 3.x  
- [Requests](https://pypi.org/project/requests/) library  
- [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/) library

You can install the dependencies using pip:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the script:

```bash
python3 jobfinder.py
```

## Notes

- This script scrapes data from [jobfind.gr](https://www.jobfind.gr) and depends on the website's current structure. Changes to the website may require updates to the scraper.

- Job descriptions are extracted from embedded JSON-LD data when available, providing a cleaner text snippet.

- The script uses simple pagination to count and display job listings, with delays between requests to avoid overwhelming the server.

- Colored output improves readability in terminals that support ANSI escape codes.

- If the script encounters unexpected page structures or network issues, it will try to fail gracefully without crashing.

- Use responsibly and avoid making too many rapid requests to respect the website's resources.
```

