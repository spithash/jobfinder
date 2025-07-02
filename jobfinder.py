import requests
from bs4 import BeautifulSoup
import json
import time

# Base URL of the job site we're scraping
BASE_URL = "https://www.jobfind.gr"

# Headers to mimic a real browser request (helps avoid blocks)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0"
}

def get_job_description(job_url):
    """
    Fetch the full job description text from a job detail page.
    Parses JSON-LD script tag to extract description HTML, then cleans it.
    """
    try:
        res = requests.get(job_url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        script_tag = soup.find("script", type="application/ld+json")
        if script_tag:
            # Load JSON data embedded in the script tag
            data = json.loads(script_tag.string, strict=False)
            html = data.get("description", "").strip()
            # Return plain text description without HTML tags
            return BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True)
    except:
        pass  # Fail silently and return empty string if any error occurs
    return ""

# Terminal color codes for nicer output formatting
COLOR_TITLE = "\033[1;36m"  # Bright cyan
COLOR_DATE  = "\033[0;33m"  # Yellow
COLOR_LINK  = "\033[0;34m"  # Blue
COLOR_DESC  = "\033[0;37m"  # Light gray
COLOR_RESET = "\033[0m"     # Reset to default

def count_all_jobs(start_url):
    """
    Count total number of job listings available for a given search URL.
    Follows pagination links until no more pages left.
    """
    url = start_url
    total = 0
    page_num = 1
    while True:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        job_divs = soup.find_all("div", class_="jobitem")
        total += len(job_divs)
        # Show progress with job count updated on the same line
        print(f"Counting jobs... Page {page_num}, found {total} jobs so far.", end='\r', flush=True)
        nxt = soup.find("a", class_="gtnext")  # Link to next page
        if nxt and nxt.get("href"):
            url = BASE_URL + nxt["href"]
            page_num += 1
            time.sleep(0.5)  # Small delay to be polite to server
        else:
            break
    print(f"Total jobs found after counting {page_num} page(s): {total}          ")
    return total

def crawl_jobs(start_url, max_jobs):
    """
    Crawl and display job listings, up to max_jobs.
    For each job, print title, date, link, and a short description snippet.
    """
    url = start_url
    shown = 0
    page = 1
    try:
        while shown < max_jobs:
            print(f"\n--- Page {page} ---")
            res = requests.get(url, headers=headers)
            print(f"[{res.status_code}] Fetching {url}")
            soup = BeautifulSoup(res.text, "html.parser")
            jobs = soup.find_all("div", class_="jobitem")
            for job in jobs:
                if shown >= max_jobs:
                    break
                # Extract posting date and job title link
                date_span = job.find("span", class_="datemob")
                title_tag = job.find("h3", class_="title").find("a")
                if not (date_span and title_tag):
                    continue  # Skip incomplete entries
                shown += 1
                date = date_span.text.strip()
                title = title_tag.text.strip()
                link  = BASE_URL + title_tag["href"]
                # Fetch full job description text (can be slow, so added delay)
                desc = get_job_description(link)
                words = desc.split()
                # Show first 30 words as snippet
                snippet = " ".join(words[:30]) + ("..." if len(words) > 30 else "")
                # Print nicely formatted job info
                print(f"[{shown}] {COLOR_TITLE}{title}{COLOR_RESET} ({COLOR_DATE}{date}{COLOR_RESET})")
                print(f"{COLOR_LINK}→ {link}{COLOR_RESET}")
                print(f"{COLOR_DESC}{snippet}{COLOR_RESET}\n")
                time.sleep(0.5)  # Be nice to the server and avoid spamming requests
            if shown >= max_jobs:
                print(f"Displayed {shown} job(s). Done as requested.")
                break
            nxt = soup.find("a", class_="gtnext")
            if nxt and nxt.get("href"):
                url = BASE_URL + nxt["href"]
                page += 1
                time.sleep(1)  # Slightly longer wait before loading next page
            else:
                print("No more pages. Crawl complete.")
                break
    except KeyboardInterrupt:
        print("\nDetected Ctrl+C — stopping crawl cleanly.")

def select_region():
    """
    Fetch and display available regions from homepage.
    Let user pick one by number, returning the chosen region's URL part.
    Filters to only include region links (exclude specialties).
    """
    print("Fetching regions...")
    res = requests.get(BASE_URL, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    regions = []
    # Search all lists with 'homelist' class for region links
    for ul in soup.find_all("ul", class_="homelist"):
        for li in ul.find_all("li"):
            a = li.find("a")
            if a and 'href' in a.attrs:
                href = a['href']
                # Only keep links that are region filters (contain '/JobAds/all/')
                if "/JobAds/all/" in href:
                    name = a.text.strip()
                    if "(" in name:
                        name = name[:name.rfind("(")].strip()  # Clean extra text like (35)
                    regions.append((name, href))
    if not regions:
        print("No regions found.")
        return None
    print("\nAvailable Regions:")
    for i, (name, _) in enumerate(regions, start=1):
        print(f"{i}. {name}")
    while True:
        choice = input(f"Select a region (1-{len(regions)}): ").strip()
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(regions):
                return regions[choice-1][1]
        print("Invalid choice. Try again.")

def select_specialty():
    """
    Fetch and display job specialties from a dedicated specialties page.
    Prompt user to choose one, return selected specialty's URL part.
    """
    print("Fetching specialties...")
    url = BASE_URL + "/JobAdsSearchCat/GR/Theseis-Ergasias-ana-Eidikotita"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    specialties = []
    # Each specialty is inside a div with class 'catbox'
    for catbox in soup.find_all("div", class_="catbox"):
        h3 = catbox.find("h3")
        if not h3:
            continue
        a = h3.find("a")
        if a and 'href' in a.attrs:
            name = a.text.strip()
            link = a["href"]
            specialties.append((name, link))
    if not specialties:
        print("No specialties found.")
        return None
    print("\nAvailable Specialties:")
    for i, (name, _) in enumerate(specialties, start=1):
        print(f"{i}. {name}")
    while True:
        choice = input(f"Select a specialty (1-{len(specialties)}): ").strip()
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(specialties):
                return specialties[choice-1][1]
        print("Invalid choice. Try again.")

def extract_slug(url):
    """
    Helper function to split a URL path into its parts.
    Used to parse specialty and region from selected URLs.
    """
    parts = url.strip("/").split("/")
    return parts

if __name__ == "__main__":
    # First, user selects a specialty category
    specialty_url_part = select_specialty()
    if not specialty_url_part:
        print("Could not retrieve specialties. Exiting.")
        exit(1)

    # Then, user selects a region
    region_url_part = select_region()
    if not region_url_part:
        print("Could not retrieve regions. Exiting.")
        exit(1)

    # Extract URL slugs (parts) from the specialty and region URLs
    spec_parts = extract_slug(specialty_url_part)
    region_parts = extract_slug(region_url_part)

    # Specialty slug usually at position 1 in URL like /JobAds/SPECIALTY/GR/Theseis-Ergasias
    try:
        specialty_slug = spec_parts[1]
    except IndexError:
        print("Error parsing specialty URL.")
        exit(1)

    # Region slug usually at position 2 in URL like /JobAds/all/REGION/GR/Theseis_Ergasias
    try:
        region_slug = region_parts[2]
    except IndexError:
        print("Error parsing region URL.")
        exit(1)

    # Build the combined URL to search jobs with both specialty and region filters
    combined_url = f"{BASE_URL}/JobAds/{specialty_slug}/{region_slug}/GR/Theseis_Ergasias"
    print(f"\nCombined search URL:\n{combined_url}")

    # Count how many jobs match the criteria
    total_jobs = count_all_jobs(combined_url)

    # Ask user how many jobs to show, validate input
    while True:
        try:
            choice = int(input(f"How many jobs to show? (1–{total_jobs}): ").strip())
            if 1 <= choice <= total_jobs:
                break
        except ValueError:
            pass
        print(f"Please enter a number between 1 and {total_jobs}.")

    # Finally, crawl and display the chosen number of jobs
    crawl_jobs(combined_url, choice)

