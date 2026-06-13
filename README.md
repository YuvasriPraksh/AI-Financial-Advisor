# 💰 AI Financial Advisor & Expense Manager

> A production-ready, AI-powered expense tracking and financial advisory application built with **Python**, **Streamlit**, **Google Gemini AI**, and **Tesseract OCR**.

---

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Gemini API Setup](#gemini-api-setup)
- [Running the App](#running-the-app)
- [Tech Stack](#tech-stack)
- [Deployment on Streamlit Cloud](#deployment-on-streamlit-cloud)

---

## ✨ Features

| Feature | Description |
|---|---|
| 📸 OCR Processing | Extract merchant & amount from PhonePe, GPay, Paytm screenshots |
| 🏷️ Auto Categorization | Classifies expenses into 8 categories using keyword mapping |
| 🗄️ SQLite Storage | Persistent, auto-created database for all expenses |
| 📊 Dashboard | Live metrics — total spend, avg transaction, top category |
| 📈 Analytics | Pie chart, bar chart, and monthly trend with Matplotlib |
| 🤖 AI Advisor | Google Gemini generates personalised financial advice |
| 💼 Budget Planner | 50/30/20 rule analysis with goal tracking |
| 🗑️ Manage Expenses | Filter, search, delete, and export expenses as CSV |

---

## 🗂️ Project Structure

```
AI_Financial_Advisor/
│
├── app.py                  # Main Streamlit application
│
├── modules/
│   ├── __init__.py
│   ├── ocr.py              # Tesseract OCR processing
│   ├── categorizer.py      # Keyword-based expense categorization
│   ├── advisor.py          # Google Gemini AI financial advice
│   ├── budget.py           # Budget calculations (50/30/20 rule)
│   └── database.py         # SQLite CRUD operations
│
├── database/
│   └── expenses.db         # Auto-created SQLite database
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Tesseract OCR installed on your system

### 1. Install Tesseract OCR

**Windows:**
1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (default path: `C:\Program Files\Tesseract-OCR\`)
3. The app auto-configures this path on Windows.

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

### 2. Clone / Download the Project

```bash
cd "AI Financial Advisor"
```

### 3. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Gemini API Setup

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key (starts with `AIza...`)
5. Paste it in the **sidebar** of the running app under "🔑 Gemini API Key"

> **Note:** The free tier of Gemini API is sufficient for this project.

---

## 🚀 Running the App

```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python 3.9+ |
| AI / NLP | Google Gemini 1.5 Flash |
| OCR | Tesseract + pytesseract |
| Database | SQLite3 (via sqlite3 + pandas) |
| Visualisation | Matplotlib |
| Data Processing | Pandas |
| Image Processing | Pillow (PIL) |

---

## ☁️ Deployment on Streamlit Cloud

### Steps:

1. Push this project to a **GitHub repository** (public or private)

2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in

3. Click **"New app"** → select your repository

4. Set **Main file path** to `app.py`

5. Under **Advanced settings → Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your-api-key-here"
   ```

6. Click **Deploy**

### Tesseract on Streamlit Cloud:

Create a file `packages.txt` in the project root:
```
tesseract-ocr
```

This tells Streamlit Cloud to install Tesseract automatically.

---

## 📱 Supported Payment Platforms

- ✅ PhonePe screenshots
- ✅ Google Pay (GPay) screenshots  
- ✅ Paytm screenshots
- ✅ General receipts and invoices
- ✅ Any text-based payment confirmation

---

## 📊 Expense Categories

| Category | Example Merchants |
|---|---|
| 🍔 Food | Swiggy, Zomato, Dominos, KFC |
| 🚗 Transport | Uber, Ola, Rapido, IRCTC |
| 🛍️ Shopping | Amazon, Flipkart, Myntra |
| 🎬 Entertainment | Netflix, Hotstar, BookMyShow |
| 💡 Bills | Airtel, Jio, Electricity, LPG |
| 💊 Healthcare | Apollo Pharmacy, 1mg, Practo |
| 📚 Education | Udemy, BYJU's, Coursera |
| 📦 Others | Any uncategorized expense |

---

## 🎓 College Project Information

- **Project Type:** Track A — AI/ML Application
- **Technology Focus:** Generative AI + Computer Vision + Data Analytics
- **Key Integration:** Google Gemini API for financial intelligence

---

*Built with ❤️ using Python, Streamlit, and Google Gemini AI*
