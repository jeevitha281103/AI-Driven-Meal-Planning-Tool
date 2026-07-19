# NutriFit — AI-Driven Indian Food Classification & Meal Planning

[![Live Demo](https://img.shields.io/badge/Live_Demo-Deployed_on_Render-brightgreen)](https://indian-food-classification.onrender.com)

> **Live App:** [https://indian-food-classification.onrender.com](https://indian-food-classification.onrender.com)

---

## Features

- **Food Image Classification** — Upload or capture a food image and get instant recognition with nutritional info
- **AI Meal Planner** — Personalized 7-day meal plans based on BMI, diet type, and health goals
- **Recipe Vault** — Browse, search, and filter 120+ Indian recipes (regular / diabetes-friendly)
- **User Authentication** — Secure signup/login with session management
- **Live Camera Capture** — Take a photo directly from your webcam for prediction

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| ML Model | TensorFlow, InceptionV3 (Transfer Learning) |
| Frontend | HTML5, CSS3 (Bootstrap 5), JavaScript (jQuery) |
| Database | SQLite |
| Deployment | Render (with Git LFS for model) |

## Dataset

The model is trained on the [Indian Food Classification Dataset](https://www.kaggle.com/theeyeschico/indian-food-classification) (20 Indian food classes) using InceptionV3 transfer learning with ~92% accuracy.

## Installation

```bash
git clone https://github.com/jeevitha281103/AI-Driven-Meal-Planning-Tool.git
cd AI-Driven-Meal-Planning-Tool
pip install -r requirements.txt
python app.py
```

The app runs at `http://localhost:5000`

## Deployment (Render)

This project is deployed on [Render](https://render.com). To deploy your own fork:

1. Fork this repo
2. Connect to Render as a Web Service
3. Render auto-detects `render.yaml` settings
4. Deploy — the model file (Git LFS) is pulled during build

## Project Structure

```
├── app.py                 # Flask application
├── meal_recipes.py        # Meal recipe data (120+ recipes)
├── Model/
│   └── model_v1_inceptionV3.h5   # Pre-trained InceptionV3 model (LFS)
├── templates/
│   ├── base.html          # Base template with navbar
│   ├── signin.html        # Login page
│   ├── signup.html        # Registration page
│   ├── index.html         # Prediction page
│   ├── deit.html          # Diet planner input
│   ├── plan.html          # 7-day meal plan
│   └── receipe.html       # Recipe vault
├── static/
│   ├── css/main.css       # Custom styles
│   └── js/main.js         # Frontend logic
├── requirements.txt
├── render.yaml            # Render deployment config
├── Procfile               # Gunicorn entrypoint
└── runtime.txt            # Python version
```

## Contact

If you find any bugs or have suggestions, create an issue or reach out:

- **LinkedIn** — [jeevitha-s](https://www.linkedin.com/in/jeevitha-s-281103/)
- **Email** — jeevitha281103@gmail.com
 

