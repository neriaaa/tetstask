import time
from datetime import datetime

from companies import get_company_sites
from email_parser import extract_emails
from csv_export import save_to_csv


# ---------------------------------------------------------------------------
# Company metadata
# Extend this dict to add Country / Type per company name.
# ---------------------------------------------------------------------------
COMPANY_META = {
    "1С":                                {"country": "Russia", "type": "Software / ERP"},
    "Яндекс":                            {"country": "Russia", "type": "Technology / Internet"},
    "Kaspersky Lab":                     {"country": "Russia", "type": "Cybersecurity"},
    "EPAM Systems":                      {"country": "Russia", "type": "IT Services"},
    "Softline":                          {"country": "Russia", "type": "IT Distribution"},
    "Ростелеком":                        {"country": "Russia", "type": "Telecom"},
    "МТС":                               {"country": "Russia", "type": "Telecom"},
    "Билайн":                            {"country": "Russia", "type": "Telecom"},
    "МегаФон":                           {"country": "Russia", "type": "Telecom"},
    "Сбер Бизнес":                       {"country": "Russia", "type": "Banking / Fintech"},
    "ВТБ Бизнес":                        {"country": "Russia", "type": "Banking / Fintech"},
    "Тинькофф Бизнес":                   {"country": "Russia", "type": "Banking / Fintech"},
    "Контур":                            {"country": "Russia", "type": "Software / SaaS"},
    "КРОК":                              {"country": "Russia", "type": "IT Services"},
    "Ланит":                             {"country": "Russia", "type": "IT Services"},
    "Техносерв":                         {"country": "Russia", "type": "IT Services"},
    "Инфосистемы Джет":                  {"country": "Russia", "type": "IT Services"},
    "АйТеко":                            {"country": "Russia", "type": "IT Services"},
    "ICL Services":                      {"country": "Russia", "type": "IT Services"},
    "Luxoft":                            {"country": "Russia", "type": "IT Services"},
    "DataArt":                           {"country": "Russia", "type": "IT Services"},
    "Positive Technologies":             {"country": "Russia", "type": "Cybersecurity"},
    "InfoWatch":                         {"country": "Russia", "type": "Cybersecurity"},
    "Доктор Веб":                        {"country": "Russia", "type": "Cybersecurity"},
    "Aqua Security":                     {"country": "Russia", "type": "Cybersecurity"},
    "Галактика":                         {"country": "Russia", "type": "Software / ERP"},
    "Парус":                             {"country": "Russia", "type": "Software / ERP"},
    "Диасофт":                           {"country": "Russia", "type": "Software / Fintech"},
    "ЦФТ (Центр Финансовых Технологий)": {"country": "Russia", "type": "Software / Fintech"},
    "Terrasoft (Creatio)":               {"country": "Russia", "type": "CRM / SaaS"},
    "Битрикс24":                         {"country": "Russia", "type": "CRM / SaaS"},
    "AmoCRM":                            {"country": "Russia", "type": "CRM / SaaS"},
    "МойСклад":                          {"country": "Russia", "type": "ERP / SaaS"},
    "Мегаплан":                          {"country": "Russia", "type": "CRM / SaaS"},
    "Platforma OFD":                     {"country": "Russia", "type": "Fiscal Tech"},
    "СБИС (Тензор)":                     {"country": "Russia", "type": "Software / SaaS"},
    "Эвотор":                            {"country": "Russia", "type": "POS / Retail Tech"},
    "Атол":                              {"country": "Russia", "type": "POS / Retail Tech"},
    "Транспортная компания СДЭК":        {"country": "Russia", "type": "Logistics"},
    "Деловые Линии":                     {"country": "Russia", "type": "Logistics"},
    "ПЭК":                               {"country": "Russia", "type": "Logistics"},
    "Почта России Бизнес":               {"country": "Russia", "type": "Logistics"},
    "HeadHunter (hh.ru)":               {"country": "Russia", "type": "HR / Recruitment"},
    "SuperJob":                          {"country": "Russia", "type": "HR / Recruitment"},
    "Работа.ру":                         {"country": "Russia", "type": "HR / Recruitment"},
    "Авито Работа":                      {"country": "Russia", "type": "HR / Recruitment"},
    "2ГИС":                              {"country": "Russia", "type": "Geo / Mapping SaaS"},
    "Контур.Фокус":                      {"country": "Russia", "type": "Business Intelligence"},
    "Seldon":                            {"country": "Russia", "type": "Procurement / Tender"},
    "Тендерплан":                        {"country": "Russia", "type": "Procurement / Tender"},
}

DEFAULT_META = {"country": "Russia", "type": "B2B"}


# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
def _log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def _separator(char: str = "─", width: int = 64) -> None:
    print(char * width)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def main() -> None:
    _separator("═")
    _log("🚀  Lead generation pipeline started")
    _separator("═")

    companies = get_company_sites()
    total = len(companies)
    _log(f"📋  Loaded {total} companies from companies.py")
    _separator()

    leads = []
    found_count = 0
    no_email_count = 0

    for idx, company in enumerate(companies, start=1):
        name    = company["name"]
        website = company["website"]
        meta    = COMPANY_META.get(name, DEFAULT_META)
        country = meta["country"]
        ctype   = meta["type"]

        _log(f"[{idx:>2}/{total}]  🌐  {name}  ({website})")

        try:
            emails = extract_emails(website)
        except Exception as exc:
            _log(f"         ⚠️  Error scraping {website}: {exc}")
            emails = []

        if emails:
            for email in emails:
                leads.append({
                    "Company": name,
                    "Website": website,
                    "Email":   email,
                    "Country": country,
                    "Type":    ctype,
                })
            found_count += len(emails)
            _log(f"         ✅  Found {len(emails)} email(s): {', '.join(emails)}")
        else:
            # Still record the company even without an email
            leads.append({
                "Company": name,
                "Website": website,
                "Email":   "",
                "Country": country,
                "Type":    ctype,
            })
            no_email_count += 1
            _log(f"         ❌  No emails found")

        # Be polite to servers
        time.sleep(1)

    _separator()
    _log(f"📊  Scraping complete — {found_count} email(s) across {total} companies")
    _log(f"     ✅  With email   : {total - no_email_count}")
    _log(f"     ❌  Without email: {no_email_count}")
    _separator()

    _log("💾  Saving results to leads.csv …")
    path = save_to_csv(leads)
    _separator("═")
    _log(f"🎉  Done!  File saved → {path}")
    _separator("═")


if __name__ == "__main__":
    main()