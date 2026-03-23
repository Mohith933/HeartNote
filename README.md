# ❤️ HeartNote AI

> Write from what actually happened.

HeartNote AI is an emotional AI writing assistant that transforms real-life moments into meaningful, structured, and deeply personal writing.

---

## 🌟 Overview

HeartNote AI focuses on helping users express thoughts and emotions clearly.  
Instead of generic AI responses, it generates **context-aware, emotionally aligned writing** based on real user input.

---

## 🚀 Features

- ✍️ Emotion-aware writing generation  
- ⚡ Real-time response using AI API  
- 🧠 Context-based output (not generic text)  
- 💾 User authentication (Signup / Login / Delete Account)  
- 🗂️ Persistent database (PostgreSQL - Cloud)  
- 📱 Progressive Web App (PWA support)  
- 🎯 Clean and minimal UI for better focus  

---

## 🛠️ Tech Stack

**Frontend**
- HTML, CSS, JavaScript

**Backend**
- Python (Django)

**Database**
- PostgreSQL (Cloud - Render)

**Other**
- REST APIs  
- PWA (Service Workers, Manifest)

---

## 🧩 Architecture

User Input → Backend (Django) → AI API → Response Processing → UI Display  

---

## 🌐 Live Demo

👉 https://hearnote-ai.onrender.com/

---

## 📸 Screenshots

<img src = "/static/screenshots/home.png" width="1280" />
<img src = "/static/screenshots/dashboard.png" width="1280" />

---

## ⚙️ Setup (Local Development)

```bash
git clone https://github.com/your-username/HeartNote-Ai.git
cd HeartNote-Ai
pip install -r requirements.txt
python manage.py runserver
