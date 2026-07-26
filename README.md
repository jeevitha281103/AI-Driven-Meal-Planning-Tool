# NutriFit

### AI-Driven Indian Food Classification & Meal Planning Tool

![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.14-FF6F00?logo=tensorflow&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)
![Render](https://img.shields.io/badge/Deployed-Render-46E3B7?logo=render&logoColor=white)
[![Live Demo](https://img.shields.io/badge/Try_It_Live-blue)](https://ai-driven-meal-planning-tool.onrender.com)

**Recognize Indian dishes from photos, get detailed nutritional breakdown, and generate personalized 7-day meal plans — powered by deep learning.**

---

## Features

- **Food Image Recognition** — Upload or capture a photo and identify Indian dishes instantly
- **Nutritional Breakdown** — Calories, protein, carbs, fat, fiber, vitamins & minerals for each dish
- **Top-3 Predictions** — Model returns the dish name + 2 alternatives with confidence scores
- **Personalized Meal Planner** — Enter BMI and diet preference to get a 7-day meal plan
- **120+ Indian Recipes** — Browse, search, and filter recipes by diet type (regular / diabetes-friendly)
- **Recipe CRUD** — Add, edit, and delete custom recipes
- **Webcam Capture** — Take a photo directly from your camera for prediction
- **Responsive UI** — Glassmorphism design, works on mobile and desktop
- **User Authentication** — Secure signup/login with session management

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10, Flask |
| Machine Learning | TensorFlow / Keras, InceptionV3 (Transfer Learning) |
| Frontend | HTML5, CSS3, Bootstrap 5, jQuery |
| Database | SQLite |
| Deployment | Render, Gunicorn |
| Model Format | TensorFlow Lite (21MB) |

---

## How the Model Works

1. **Base Model** — InceptionV3 pre-trained on ImageNet
2. **Fine-Tuning** — Top layers replaced with custom dense layers for 20 Indian food classes
3. **Input** — 299x299 RGB image, normalized to [0, 1]
4. **Output** — Softmax probabilities across 20 classes, top-3 selected
5. **Accuracy** — ~92% on validation set

**Supported Food Classes (20):**

Biryani, Butter Chicken, Chapati, Chole Bhature, Dal Makhani, Dosa, Fried Rice, Idli, Jalebi, Kaathi Roll, Kadai Paneer, Naan, Pakode, Paneer Butter Masala, Parotta, Pav Bhaji, Pizza, Samosa, Sushi, Tikka

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

```bash
git clone https://github.com/jeevitha281103/AI-Driven-Meal-Planning-Tool.git
cd AI-Driven-Meal-Planning-Tool

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000** in your browser.

### Default Login

| Username | Password |
|----------|----------|
| admin | admin |

---

## Deployment on Render

1. Fork this repository
2. Go to [render.com](https://render.com) and create a **New Web Service**
3. Connect your GitHub repository
4. Set the following:

| Setting | Value |
|---------|-------|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app --timeout 120 --workers 1 --threads 2` |

5. Click **Create Web Service**
6. Your app will be live at `https://your-app.onrender.com`

---

## Project Structure

```
├── app.py                      # Flask application
├── meal_recipes.py             # 120+ Indian meal recipes
├── convert_model.py            # H5 to TFLite conversion script
├── Model/
│   ├── model_v1_inceptionV3.h5         # Original model (170MB, Git LFS)
│   └── model_v1_inceptionV3.tflite     # Optimized model (21MB)
├── templates/
│   ├── base.html               # Base layout with navbar
│   ├── signin.html             # Login page
│   ├── signup.html             # Registration page
│   ├── index.html              # Food prediction interface
│   ├── deit.html               # Diet planner input form
│   ├── plan.html               # 7-day meal plan display
│   └── receipe.html            # Recipe vault with CRUD
├── static/
│   ├── css/main.css            # Custom styles and animations
│   └── js/main.js              # AJAX, webcam, UI logic
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render deployment config
├── Procfile                    # Gunicorn process definition
└── runtime.txt                 # Python version
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| SECRET_KEY | Auto-generated | Flask session encryption key |
| PYTHON_VERSION | 3.10.9 | Python runtime version |
| PORT | 5000 | Application server port |

---

## Future Improvements

### ML & Data
- [ ] Expand model to 40+ Tamil Nadu food classes
- [ ] Train with region-specific cuisine (South Indian, North Indian, Bengali, etc.)
- [ ] Add food portion size estimation from images
- [ ] Implement real-time camera prediction (video stream)
- [ ] Add model confidence threshold — reject low-confidence predictions

### User Experience
- [ ] Multi-language support (Hindi, Tamil, Telugu, Kannada)
- [ ] Dark mode toggle with system preference detection
- [ ] Progressive Web App (PWA) — installable on mobile
- [ ] Push notifications for meal reminders

### Health & Nutrition
- [ ] Calorie tracking dashboard with daily/weekly history
- [ ] BMI trend graph over time
- [ ] Allergy filter — exclude recipes with allergens
- [ ] Integrate with Google Fit / Apple Health for activity data
- [ ] AI-powered meal suggestions based on user health goals

### Backend & Infrastructure
- [ ] Migrate SQLite to PostgreSQL for production scalability
- [ ] Add Redis caching for faster page loads
- [ ] REST API for mobile app integration
- [ ] Docker containerization for local development
- [ ] CI/CD pipeline with GitHub Actions

### Social & Community
- [ ] Share meal plans on social media
- [ ] User-generated recipe submissions with ratings
- [ ] Community leaderboard for healthy eating streaks
- [ ] Grocery list export (PDF / email)

---

## License

This project is for educational purposes. Model weights are derived from the [Indian Food Classification Dataset](https://www.kaggle.com/theeyeschico/indian-food-classification).

---

## Contact

**Jeevitha** — [LinkedIn](https://www.linkedin.com/in/r-s-jeevitha-raja-7692642b3?utm_source=share_via&utm_content=profile&utm_medium=member_android) — jeevitharaja2811@gmail.com

If you find a bug or have a feature request, please [open an issue](https://github.com/jeevitha281103/AI-Driven-Meal-Planning-Tool/issues).
