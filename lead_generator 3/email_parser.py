import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

CONTACT_PATHS = [
    "",           # homepage
    "/contacts",
    "/contact",
    "/about",
    "/kontakty",  # Russian: контакты
    "/o-kompanii", # Russian: о компании
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

TIMEOUT = 10


def _normalize_base_url(url: str) -> str:
    """Ensure the URL has a scheme and no trailing slash."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


def _fetch_emails_from_url(url: str, session: requests.Session) -> set:
    """Fetch a single page and extract all email addresses from it."""
    emails = set()
    try:
        response = session.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if response.status_code != 200:
            return emails

        # Extract from raw HTML (catches mailto: and plain text)
        raw_emails = EMAIL_REGEX.findall(response.text)
        emails.update(raw_emails)

        # Extract from parsed HTML (catches obfuscated or tag-embedded emails)
        soup = BeautifulSoup(response.text, "html.parser")

        # <a href="mailto:...">
        for tag in soup.select("a[href^='mailto:']"):
            href = tag.get("href", "")
            mailto_email = href.replace("mailto:", "").split("?")[0].strip()
            if EMAIL_REGEX.match(mailto_email):
                emails.add(mailto_email)

        # Visible text nodes
        text = soup.get_text(separator=" ")
        emails.update(EMAIL_REGEX.findall(text))

    except requests.RequestException:
        pass

    return emails


def _filter_emails(emails: set) -> set:
    """Remove common false positives (image filenames, example domains, etc.)."""
    excluded_domains = {
        "example.com", "example.org", "test.com", "domain.com",
        "email.com", "yourdomain.com", "sentry.io",
    }
    excluded_extensions = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".css", ".js"}

    clean = set()
    for email in emails:
        email = email.lower().strip()
        domain = email.split("@")[-1]
        local = email.split("@")[0]

        if domain in excluded_domains:
            continue
        if any(local.endswith(ext) for ext in excluded_extensions):
            continue
        if any(c in local for c in ("*", "{", "}", "<", ">")):
            continue

        clean.add(email)

    return clean


def extract_emails(url: str) -> list:
    """
    Extract unique email addresses from a website.

    Checks the homepage plus /contacts, /contact, /about (and Russian equivalents).

    Args:
        url: The base URL of the website (e.g. 'https://example.com').

    Returns:
        Sorted list of unique, validated email addresses found on the site.
    """
    base_url = _normalize_base_url(url)
    all_emails = set()

    with requests.Session() as session:
        for path in CONTACT_PATHS:
            page_url = base_url + path
            found = _fetch_emails_from_url(page_url, session)
            all_emails.update(found)

    all_emails = _filter_emails(all_emails)
    return sorted(all_emails)



if __name__ == "__main__":
    from companies import get_company_sites

    companies = get_company_sites()

    for company in companies[:5]:  # test first 5 to keep it quick
        name = company["name"]
        site = company["website"]
        print(f"\n{'─' * 60}")
        print(f"  {name}  |  {site}")
        print(f"{'─' * 60}")

        emails = extract_emails(site)
        if emails:
            for email in emails:
                print(f"  ✉  {email}")
        else:
            print("  (no emails found)")