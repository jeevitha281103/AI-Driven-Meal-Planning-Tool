<div align="center">

# 🍛 NutriFit

### AI-Powered Indian Food Classification & Personalized Meal Planning

[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.14-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com)

[![Live Demo](https://img.shields.io/badge/LIVE_DEMO-blue?style=for-the-badge&logo=vercel&logoColor=white)](https://ai-driven-meal-planning-tool.onrender.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](#license)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-orange?style=for-the-badge)](https://github.com/jeevitha281103/AI-Driven-Meal-Planning-Tool/pulls)

<br><br>

**Recognize Indian dishes from photos, get detailed nutritional breakdown, and generate personalized 7-day meal plans — all powered by deep learning.**

[**→ Try it Live**](https://ai-driven-meal-planning-tool.onrender.com)

</div>

---

<br>

## 📸 Preview

<div align="center">
<img src="https://user-images.githubusercontent.com/72247049/121991992-5ba5b980-cdbe-11eb-971c-182bb1a0913b.png" width="44%" alt="Food Prediction" />
&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://user-images.githubusercontent.com/72247049/121992054-7aa44b80-cdbe-11eb-8975-f82da1c28f16.png" width="44%" alt="Meal Plan" />
</div>

---

<br>

## 🧩 Features

<table>
<tr>
<td width="50%" valign="top">

### 🍽️ Food Recognition
- Upload an image or capture from webcam
- InceptionV3 model identifies the dish
- Shows **calories, protein, carbs, fat, fiber**
- Displays **vitamins & minerals** breakdown
- Top-3 predictions with confidence scores

</td>
<td width="50%" valign="top">

### 📋 Meal Planner
- Enter weight, height, and diet preference
- Calculates BMI and categorizes health goal
- Generates a **personalized 7-day meal plan**
- Covers breakfast, lunch, dinner & snacks
- Supports **regular** and **diabetes-friendly** diets

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 📖 Recipe Vault
- **120+ Indian recipes** with ingredients & steps
- Search by name or keyword
- Filter by diet type (regular / diabetes)
- Add, edit, and delete custom recipes
- Full CRUD functionality

</td>
<td width="50%" valign="top">

### 🔐 User System
- Secure signup and login
- Session-based authentication
- Personalized experience per user
- Password-protected routes

</td>
</tr>
</table>

---

<br>

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|:------|:-----------|:--------|
| **Backend** | Python 3.10, Flask | Web server, routing, session management |
| **ML Engine** | TensorFlow / Keras | InceptionV3 transfer learning for food classification |
| **Frontend** | HTML5, CSS3, Bootstrap 5, jQuery | Responsive glassmorphism UI |
| **Database** | SQLite | User authentication, recipe storage |
| **Deployment** | Render, Gunicorn | Cloud hosting with auto-scaling |
| **Model Format** | TensorFlow Lite | Optimized 21MB model (down from 170MB H5) |

---

<br>

## 🧠 How the Model Works

```
Input Image (299×299 RGB)
        │
        ▼
┌─────────────────────┐
│   InceptionV3 Base   │  ← Pre-trained on ImageNet
│   (Transfer Learning)│
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  Custom Dense Layers │  ← Fine-tuned for 20 Indian food classes
│  Dropout + Softmax   │
└─────────────────────┘
        │
        ▼
   Top-3 Predictions
   + Nutrition Data
```

**Performance:**
- **Accuracy:** ~92% on validation set
- **Inference Time:** <1 second per image
- **Model Size:** 21MB (TFLite) / 170MB (H5)

**Supported Food Classes (20):**

| | | | | |
|:-:|:-:|:-:|:-:|:-:|
| Biryani | Butter Chicken | Chapati | Chole Bhature | Dal Makhani |
| Dosa | Fried Rice | Idli | Jalebi | Kaathi Roll |
| Kadai Paneer | Naan | Pakode | Paneer Butter Masala | Parotta |
| Pav Bhaji | Pizza | Samosa | Sushi | Tikka |

---

<br>

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/jeevitha281103/AI-Driven-Meal-Planning-Tool.git
cd AI-Driven-Meal-Planning-Tool

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

Open **http://localhost:5000** in your browser.

### Default Login
| Field | Value |
|:------|:------|
| Username | `admin` |
| Password | `admin` |

---

<br>

## ☁️ Deployment on Render

| Step | Action |
|:-----|:-------|
| 1 | Fork this repository to your GitHub account |
| 2 | Go to [render.com](https://render.com) → **New Web Service** |
| 3 | Connect your GitHub repository |
| 4 | Render auto-detects `render.yaml` — verify the settings |
| 5 | Click **Create Web Service** |
| 6 | Your app will be live at `https://your-app.onrender.com` |

**Build Settings:**
```
Build Command:  pip install -r requirements.txt
Start Command:  gunicorn app:app --timeout 120 --workers 1 --threads 2
```

---

<br>

## 📁 Project Structure

```
├── app.py                          # Main Flask application
├── meal_recipes.py                 # 120+ Indian meal recipes
├── convert_model.py                # H5 → TFLite conversion script
│
├── Model/
│   ├── model_v1_inceptionV3.h5     # Original model (170MB, Git LFS)
│   └── model_v1_inceptionV3.tflite # Optimized model (21MB, deployed)
│
├── templates/
│   ├── base.html                   # Base layout with navbar
│   ├── signin.html                 # Login page
│   ├── signup.html                 # Registration page
│   ├── index.html                  # Food prediction interface
│   ├── deit.html                   # Diet planner input form
│   ├── plan.html                   # 7-day meal plan display
│   └── receipe.html                # Recipe vault with CRUD
│
├── static/
│   ├── css/main.css                # Custom styles & animations
│   └── js/main.js                  # AJAX, webcam capture, UI logic
│
├── requirements.txt                # Python dependencies
├── render.yaml                     # Render deployment config
├── Procfile                        # Gunicorn process definition
└── runtime.txt                     # Python version specification
```

---

<br>

## 📊 Environment Variables

| Variable | Default | Description |
|:---------|:--------|:------------|
| `SECRET_KEY` | Auto-generated | Flask session encryption key |
| `PYTHON_VERSION` | `3.10.9` | Python runtime version |
| `PORT` | `5000` | Application server port |

---

<br>

## 🗺️ Roadmap

- [ ] Expand food recognition to 40+ Tamil Nadu dishes
- [ ] Calorie tracking dashboard with history
- [ ] Multi-language support (Hindi, Tamil, Telugu)
- [ ] Automated grocery list from meal plans
- [ ] Dark mode toggle
- [ ] Nutritional goal setting & progress tracking
- [ ] Integration with fitness APIs

---

<br>

## 📄 License

This project is built for educational and learning purposes. The machine learning model weights are derived from the [Indian Food Classification Dataset](https://www.kaggle.com/theeyeschico/indian-food-classification) on Kaggle.

---

<br>

## 👩‍💻 Author

**Jeevitha**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/r-s-jeevitha-raja-7692642b3?utm_source=share_via&utm_content=profile&utm_medium=member_android)
[![Email](https://img.shields.io/badge/Email-Contact-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:jeevitharaja2811@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/jeevitha281103)

---

<div align="center">

**If you found this project helpful, please give it a ⭐ on GitHub!**

</div>
