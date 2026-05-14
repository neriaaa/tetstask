# Lead Generator & Personalized Outreach Tool

Автоматизированный mini SDR/outbound workflow для сбора B2B-лидов, email extraction и генерации персонализированного outreach.

## 🚀 Возможности

- сбор списка компаний,
- scraping публичных email-адресов,
- генерация personalization на основе сайта компании,
- экспорт результатов в CSV,
- cold outreach email sequence.

---

## 📂 Структура проекта

project/
├── companies.py
├── email_parser.py
├── personalization.py
├── csv_export.py
├── main.py
├── leads.csv
├── email_sequences.md
├── requirements.txt
└── README.md

---

## ⚙️ Используемые технологии

- Python
- requests
- BeautifulSoup
- CSV export

---

## ▶️ Запуск проекта

Установить зависимости:

```bash
pip install -r requirements.txt
python main.py