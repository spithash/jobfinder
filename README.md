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

