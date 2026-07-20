<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.1-green?logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/TensorFlow-2.14-orange?logo=tensorflow&logoColor=white" alt="TensorFlow">
  <img src="https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap&logoColor=white" alt="Bootstrap">
  <a href="https://indian-food-classification.onrender.com"><img src="https://img.shields.io/badge/Live_Demo-Render-brightgreen" alt="Live Demo"></a>
</p>

<h1 align="center">NutriFit</h1>

<p align="center">
  <b>AI-Driven Indian Food Classification & Meal Planning Tool</b><br>
  <sub>Recognize Indian dishes from images, get nutritional info, and generate personalized meal plans.</sub>
</p>

<p align="center">
  <a href="https://indian-food-classification.onrender.com"><b>🔗 Try the Live App</b></a>
</p>

---

## Preview

<p align="center">
  <img src="https://user-images.githubusercontent.com/72247049/121991992-5ba5b980-cdbe-11eb-971c-182bb1a0913b.png" width="45%" alt="Prediction Page">
  &nbsp;&nbsp;
  <img src="https://user-images.githubusercontent.com/72247049/121992054-7aa44b80-cdbe-11eb-8975-f82da1c28f16.png" width="45%" alt="Meal Plan">
</p>

---

## What It Does

| Module | Description |
|--------|-------------|
| **Food Recognition** | Upload or capture a photo → InceptionV3 model identifies the dish, shows calories, protein, carbs, fat, vitamins & minerals |
| **Meal Planner** | Enter your BMI + diet preference → get a personalized 7-day breakfast/lunch/dinner/snack plan |
| **Recipe Vault** | Browse 120+ Indian recipes with search & diet filters (regular / diabetes-friendly) |
| **User Accounts** | Secure signup/login to save your session |

---

## Key Features

- **Top-3 Predictions** — model returns the dish name + 2 alternatives with confidence scores
- **Diet Type Filtering** — filter recipes by `regular`, `diabetes`, or `all`
- **Full CRUD Recipes** — add, edit, and delete custom recipes from the vault
- **Webcam Capture** — take a photo live from your camera and predict instantly
- **Responsive UI** — glassmorphism design, works on mobile and desktop
- **Calorie & Nutrition Breakdown** — protein, carbs, fat, fiber, vitamins, and minerals per dish

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10, Flask |
| **Machine Learning** | TensorFlow / Keras, InceptionV3 (Transfer Learning) |
| **Frontend** | HTML5, CSS3, Bootstrap 5, jQuery |
| **Database** | SQLite (user auth + recipes) |
| **Deployment** | Render (Gunicorn, Git LFS for 177MB model) |

---

## How the Model Works

1. **Base Model** — InceptionV3 pre-trained on ImageNet
2. **Fine-Tuning** — top layers replaced with custom dense layers for 20 Indian food classes
3. **Input** — 299×299 RGB image, normalized to [0, 1]
4. **Output** — softmax probabilities across 20 classes → top-3 selected
5. **Accuracy** — ~92% on validation set

**Supported Food Classes:** biryani, butter_chicken, chapati, chole_bhature, dal_makhani, dosa, fried_rice, idli, jalebi, kaathi_roll, kadai_paneer, naan, pakode, paneer_butter_masala, parotta, pav_bhaji, pizza, samosa, sushi, tikka

---

## Getting Started (Local)

### Prerequisites
- Python 3.10+
- pip

### Install & Run

```bash
# Clone the repo (ensure Git LFS is installed)
git lfs install
git clone https://github.com/jeevitha281103/AI-Driven-Meal-Planning-Tool.git
cd AI-Driven-Meal-Planning-Tool

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Open **http://localhost:5000** in your browser.

> **Note:** The model file (`Model/model_v1_inceptionV3.h5`) is tracked via Git LFS (177MB). If you cloned without LFS, run `git lfs pull` to download it.

---

## Deploy to Render

1. **Fork** this repo to your GitHub account
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` — verify settings:
   - Build: `git lfs install && git lfs pull && pip install -r requirements.txt`
   - Start: `gunicorn app:app --timeout 120 --workers 1 --threads 2`
5. Click **Create Web Service**
6. Done — your app is live!

---

## Project Structure

```
.
├── app.py                      # Flask app, routes, model loading, DB init
├── meal_recipes.py             # 120+ Indian meal recipes with ingredients & instructions
├── Model/
│   └── model_v1_inceptionV3.h5 # Pre-trained InceptionV3 model (Git LFS, 177MB)
├── templates/
│   ├── base.html               # Navbar + footer + FA icons
│   ├── signin.html             # Login page
│   ├── signup.html             # Registration page
│   ├── index.html              # Food prediction (upload + camera)
│   ├── deit.html               # Diet planner input form
│   ├── plan.html               # 7-day meal plan display
│   └── receipe.html            # Recipe vault with CRUD
├── static/
│   ├── css/main.css            # Glassmorphism styles, upload box, animations
│   └── js/main.js              # AJAX prediction, webcam, UI logic
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render deployment config
├── Procfile                    # Gunicorn entrypoint
├── runtime.txt                 # Python 3.10.9
└── .gitattributes              # Git LFS tracking for model file
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | random hex | Flask session secret key |
| `PYTHON_VERSION` | `3.10.9` | Python runtime version |
| `PORT` | `5000` | Local dev server port |

---

## Roadmap

- [ ] Expand model to 40+ Tamil Nadu food classes
- [ ] Add calorie tracking dashboard
- [ ] Multi-language support (Hindi, Tamil, Telugu)
- [ ] Grocery list generation from meal plans
- [ ] Dark mode toggle

---

## License

This project is for educational purposes. Model weights are derived from the [Indian Food Classification Dataset](https://www.kaggle.com/theeyeschico/indian-food-classification).

---

## Contact

**Jeevitha S** — [LinkedIn](https://www.linkedin.com/in/jeevitha-s-281103/) | jeevitharaja2811@gmail.com

If you find a bug or have a feature request, please [open an issue](https://github.com/jeevitha281103/AI-Driven-Meal-Planning-Tool/issues).
