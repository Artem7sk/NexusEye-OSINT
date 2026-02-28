# 👁 NexusEye OSINT Bot

A high-performance, asynchronous Telegram bot designed for comprehensive OSINT (Open Source Intelligence) investigations. This tool integrates nickname scanning, email leak detection, phone number analysis, and reverse image searching into a single, user-friendly interface.



## 🚀 Key Features

* **🔍 Nickname Search:** Scans 25+ major social media platforms and forums (Instagram, TikTok, GitHub, VK, etc.) to find digital footprints.
* **📧 Email Leak Check:** Integrates with leak database APIs to verify if a specific email has been compromised in known data breaches.
* **📱 Phone Lookup:** Instant analysis of international phone numbers, providing region, carrier details, and direct links to WhatsApp/Telegram profiles.
* **🖼 Reverse Image Search:** Generates deep links for facial and object recognition through Google Lens, Yandex Images, and Bing Visual Search.
* **📄 PDF Reports:** Automatically generates and delivers professional PDF dossiers containing all investigation results.
* **💳 Monetization Ready:** Built-in support for digital goods and services using **Telegram Stars (XTR)**.

## 🛠 Tech Stack

* **Language:** Python 3.12+
* **Framework:** `aiogram 3.x` (Fully Asynchronous)
* **Database:** `SQLite3` (User profiles, search history, and premium status)
* **Core Libraries:**
    * `aiohttp` — For high-speed concurrent network requests.
    * `fpdf2` — For dynamic PDF report generation.
    * `phonenumbers` — For international phone metadata parsing.

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/NexusEye-OSINT.git](https://github.com/your-username/NexusEye-OSINT.git)
Set up a virtual environment and install dependencies:

Bash

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Configure your Bot Token in main.py.

Launch the system:

Bash

python main.py
📊 Admin Dashboard
The bot includes a built-in monitoring system for the owner to track:

Total active user base.

Real-time search request volume.

Premium sales statistics and revenue in Telegram Stars.

⚖️ Legal Disclaimer
This tool is developed for educational and professional OSINT research purposes only. The author is not responsible for any misuse of the information retrieved by this bot.
