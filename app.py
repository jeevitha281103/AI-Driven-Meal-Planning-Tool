import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

import sys
import secrets
import time
import logging
import numpy as np
import pandas as pd
from flask import Flask, request, session, redirect, render_template, jsonify, url_for
from werkzeug.utils import secure_filename
import sqlite3
import random
from meal_recipes import MEAL_RECIPES

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.after_request
def add_cache_headers(response):
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    return response

@app.route('/health')
def health():
    return jsonify({"status": "ok", "timestamp": time.time()}), 200

# Database auto-initialization
def init_db():
    # Ensure uploads folder exists
    os.makedirs(os.path.join(BASE_DIR, 'uploads'), exist_ok=True)
    
    # Initialize SQLite database
    con = sqlite3.connect(os.path.join(BASE_DIR, 'signup.db'))
    cur = con.cursor()
    # Create info table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS info (
            user TEXT PRIMARY KEY,
            email TEXT,
            password TEXT,
            mobile TEXT,
            name TEXT
        )
    ''')
    # Create recipe table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS recipe (
            recipeid INTEGER PRIMARY KEY AUTOINCREMENT,
            receipename TEXT,
            description TEXT,
            videoid TEXT,
            ingredients TEXT,
            instructions TEXT,
            diet_type TEXT
        )
    ''')
    
    # Migrate old table: add columns if missing
    for col in ['ingredients', 'instructions', 'diet_type']:
        try:
            cur.execute(f"ALTER TABLE recipe ADD COLUMN {col} TEXT")
        except sqlite3.OperationalError:
            pass
    
    # Seed initial recipes if empty
    cur.execute("SELECT COUNT(*) FROM recipe")
    if cur.fetchone()[0] == 0:
        initial_recipes = [
            ("Healthy Masala Dosa", "A light and crispy South Indian classic made with fermented rice batter, filled with a potato mash.", "S75gIapV3Kk",
             "1 cup rice\n1/2 cup urad dal\n1/2 tsp fenugreek seeds\n2 potatoes (boiled, mashed)\n1 onion (chopped)\n1 tsp mustard seeds\nCurry leaves, salt, oil",
             "1. Soak rice, urad dal, and fenugreek seeds for 6 hours.\n2. Grind to a smooth batter and ferment overnight.\n3. For filling: heat oil, add mustard seeds, curry leaves, onion, turmeric, and mashed potatoes. Sauté well.\n4. Pour batter on hot griddle, spread thin, drizzle oil, cook until golden.\n5. Place filling in center, fold, and serve hot with chutney.", "both"),
            ("Sprouted Moong Chaat", "High protein and nutrient-rich salad made with sprouted green gram, tossed with chopped onions, tomatoes, and spices.", "aV_j6Zndlco",
             "1 cup sprouted moong beans\n1 onion (finely chopped)\n1 tomato (finely chopped)\n1 green chili (chopped)\n1 tsp chaat masala\n1/2 tsp black salt\nJuice of 1 lemon\nCoriander leaves",
             "1. Steam sprouted moong for 5-7 minutes until tender but crunchy.\n2. Let it cool completely.\n3. Add chopped onion, tomato, green chili, and coriander.\n4. Sprinkle chaat masala, black salt, and lemon juice.\n5. Toss well and serve fresh as a healthy snack.", "both"),
            ("Indian Oats Khichdi", "A wholesome, comforting one-pot meal made with oats, yellow lentils, and loaded with fresh vegetables.", "A3V-vT9cZlc",
             "1 cup rolled oats\n1/2 cup yellow moong dal\n1 carrot (diced)\n1/2 cup peas\n1 tomato (chopped)\n1 tsp cumin seeds\n1/2 tsp turmeric\n1 tbsp ghee\nSalt, water",
             "1. Dry roast oats for 2 minutes and set aside.\n2. Wash moong dal and cook with turmeric until soft.\n3. In a pressure cooker, heat ghee, add cumin seeds, tomato, veggies, and sauté.\n4. Add cooked dal, oats, salt, and 2 cups water.\n5. Pressure cook for 3 whistles.\n6. Serve hot with a dollop of ghee and pickle.", "diabetes"),
        ]
        cur.executemany("INSERT INTO recipe (receipename, description, videoid, ingredients, instructions, diet_type) VALUES (?, ?, ?, ?, ?, ?)", initial_recipes)

    # Seed admin user if not exists
    cur.execute("SELECT user FROM info WHERE user = 'admin'")
    if cur.fetchone() is None:
        cur.execute("INSERT INTO info (user, email, password, mobile, name) VALUES (?, ?, ?, ?, ?)",
                    ('admin', 'admin@admin.com', 'admin', '', 'Admin'))
    con.commit()
    con.close()

    # Seed famous dietary recipes from database if not present
    seed_famous_recipes()

def seed_famous_recipes():
    con = sqlite3.connect(os.path.join(BASE_DIR, 'signup.db'))
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM recipe")
    if cur.fetchone()[0] > 3:
        con.close()
        return
    famous_recipes = [
        # ---- REGULAR DIET RECIPES ----
        ("Whole Wheat Gehun Khichdi", "A fiber-rich Rajasthani khichdi made with whole wheat and moong dal, perfect for wholesome meals.",
         "", "1 cup whole wheat (soaked overnight)\n1/4 cup yellow moong dal\n1 tsp ghee\n1 tsp oil\n1/4 tsp cumin seeds\n2 green chilies (slit)\n1/4 tsp asafoetida\n1/4 tsp turmeric\nSalt to taste",
         "1. Soak whole wheat overnight, drain and grind to coarse paste.\n2. Soak moong dal for 2 hours, drain.\n3. Heat ghee and oil, add cumin, green chilies, asafoetida.\n4. Add ground wheat and moong dal, sauté for 2 mins.\n5. Add 3.5 cups hot water, turmeric, salt.\n6. Pressure cook for 6 whistles.\n7. Serve hot with low-fat curd.", "regular"),

        ("Besan Chilla (Gram Flour Pancake)", "A protein-packed savory pancake made with gram flour, onions, and spices — a popular North Indian breakfast.",
         "", "1 cup besan (gram flour)\n1/2 cup finely chopped onion\n1/4 cup chopped coriander\n1 green chili (chopped)\n1/2 tsp cumin seeds\n1/4 tsp turmeric\nSalt to taste\nOil for cooking",
         "1. Mix besan with water to make a smooth batter (no lumps).\n2. Add onion, coriander, green chili, cumin, turmeric, salt. Mix well.\n3. Heat non-stick pan, pour a ladle of batter, spread.\n4. Drizzle oil, cook until golden on both sides.\n5. Serve hot with mint chutney or ketchup.", "regular"),

        ("Quinoa Dosa", "A high-protein, no-fermentation twist to classic dosa using quinoa instead of rice.",
         "", "1 cup quinoa (soaked 4 hours)\n1/2 cup urad dal (soaked 4 hours)\n1/4 cup grated carrot\n1 green chili\nSalt to taste\nOil for cooking",
         "1. Grind soaked quinoa and urad dal with green chili to smooth batter.\n2. Add grated carrot and salt. Mix.\n3. Heat tawa, pour ladle of batter, spread thin.\n4. Drizzle oil, cook until crisp.\n5. Serve with coconut chutney.", "regular"),

        ("Egg Bhurji (Indian Scrambled Eggs)", "Classic Indian-style scrambled eggs with onions, tomatoes, and aromatic spices.",
         "", "2 eggs\n1 onion (finely chopped)\n1 tomato (finely chopped)\n1 green chili (chopped)\n1/2 tsp cumin seeds\n1/4 tsp turmeric\n1 tbsp butter\nSalt and pepper to taste\nCoriander leaves",
         "1. Whisk eggs with salt and pepper.\n2. Heat butter, add cumin seeds, then onions and green chili. Sauté until golden.\n3. Add tomatoes and turmeric. Cook until soft.\n4. Pour whisked eggs, stir gently until set.\n5. Garnish with coriander and serve with toast.", "regular"),

        ("Chickpea Salad", "A protein-rich, refreshing salad with chickpeas, fresh veggies, and tangy lemon dressing.",
         "", "1 cup boiled chickpeas\n1/2 cucumber (diced)\n1 tomato (diced)\n1/4 onion (finely chopped)\n2 tbsp olive oil\n1 tbsp lemon juice\n1/2 tsp chaat masala\nSalt and pepper to taste",
         "1. Mix chickpeas, cucumber, tomato, and onion in a bowl.\n2. Whisk olive oil, lemon juice, chaat masala, salt, and pepper.\n3. Pour dressing over salad, toss well.\n4. Serve chilled.", "regular"),

        ("Paneer Jalfrezi", "A colorful stir-fry of paneer and bell peppers in a tangy onion-tomato masala.",
         "", "200g paneer (cubed)\n1 capsicum (diced)\n1 onion (sliced)\n2 tomatoes (diced)\n1 tsp ginger-garlic paste\n1/2 tsp turmeric\n1 tsp coriander powder\n1/2 tsp garam masala\n2 tbsp oil\nSalt to taste",
         "1. Heat oil, fry paneer cubes until golden. Set aside.\n2. In same pan, add onions and capsicum. Sauté for 2 mins.\n3. Add ginger-garlic paste, tomatoes, and spices. Cook 5 mins.\n4. Return paneer, mix well, cook for 2 mins.\n5. Serve hot with roti or naan.", "regular"),

        ("Chicken Curry (Home-style)", "A simple, homestyle chicken curry made with onion-tomato gravy and whole spices.",
         "", "200g chicken (curry cut)\n1 onion (chopped)\n2 tomatoes (pureed)\n1 tsp ginger-garlic paste\n1/2 tsp turmeric\n1 tsp coriander powder\n1/2 tsp chili powder\n2 tbsp oil\nSalt to taste\nCoriander leaves",
         "1. Heat oil, add whole spices and onions. Sauté until golden.\n2. Add ginger-garlic paste, cook 1 min.\n3. Add tomato puree and spice powders. Cook until oil separates.\n4. Add chicken and salt. Cook 5 mins.\n5. Add 1/2 cup water, cover, simmer 15 mins.\n6. Garnish with coriander and serve with rice.", "regular"),

        ("Dal Palak (Spinach Dal)", "A nutritious lentil soup with spinach, packed with iron and protein.",
         "", "1 cup toor dal\n2 cups spinach (chopped)\n1 onion (chopped)\n2 tomatoes (chopped)\n1 tsp ginger-garlic paste\n1/2 tsp turmeric\n1 tsp cumin seeds\n1 tbsp ghee\nSalt to taste",
         "1. Pressure cook dal with turmeric until soft. Mash.\n2. Heat ghee, add cumin seeds, onions. Sauté until golden.\n3. Add ginger-garlic paste and tomatoes. Cook 2 mins.\n4. Add spinach and cook until wilted.\n5. Add cooked dal and salt. Simmer 10 mins.\n6. Serve hot with rice or roti.", "regular"),

        ("Rajma Masala", "A comforting North Indian red kidney bean curry, a favorite with rice.",
         "", "1 cup rajma (kidney beans, soaked overnight)\n1 onion (chopped)\n2 tomatoes (pureed)\n1 tsp ginger-garlic paste\n1/2 tsp turmeric\n1 tsp coriander powder\n1/2 tsp garam masala\n2 tbsp oil\nSalt to taste",
         "1. Pressure cook soaked rajma until soft.\n2. Heat oil, add cumin seeds and onions. Sauté until golden.\n3. Add ginger-garlic paste, tomato puree, spices. Cook 5 mins.\n4. Add cooked rajma and salt. Simmer 15 mins.\n5. Sprinkle garam masala and coriander.\n6. Serve with steamed rice.", "regular"),

        # ---- DIABETES-FRIENDLY RECIPES ----
        ("Diabetic Adai (Lentil Pancake)", "A rice-free adai made with broken wheat and mixed lentils — low GI, high protein.",
         "", "1/2 cup broken wheat (dalia)\n1/4 cup green moong dal\n2 tbsp masoor dal\n2 tbsp urad dal\n1 tsp fenugreek seeds\n1/4 cup chopped onion\n1 tsp ginger-green chili paste\n1/4 tsp turmeric\nSalt to taste\nOil for cooking",
         "1. Soak broken wheat, all dals, and fenugreek seeds for 2 hours. Drain.\n2. Grind to a coarse batter with minimal water.\n3. Mix in onions, ginger-chili paste, turmeric, salt.\n4. Heat non-stick tawa, pour batter, spread thin.\n5. Drizzle oil, cook until golden on both sides.\n6. Serve with sugar-free green chutney.", "diabetes"),

        ("Millet Upma (Jowar/Bajra)", "A diabetes-friendly upma made with millets instead of semolina — high fiber, low GI.",
         "", "1 cup jowar (sorghum) or bajra flour\n1/2 cup mixed vegetables (carrot, beans, peas)\n1 onion (chopped)\n1 tsp mustard seeds\nFew curry leaves\n1 green chili\n1/2 tsp turmeric\n1 tbsp oil\nSalt to taste",
         "1. Dry roast millet flour for 3 mins. Set aside.\n2. Heat oil, add mustard seeds, curry leaves, green chili.\n3. Add onions and vegetables. Sauté 3 mins.\n4. Add 2 cups hot water, turmeric, salt. Bring to boil.\n5. Slowly add roasted flour, stirring continuously.\n6. Cook on low flame 5 mins. Serve hot.", "diabetes"),

        ("Ragi (Finger Millet) Dosa", "A crispy, nutritious dosa made with ragi flour — rich in calcium and diabetes-friendly.",
         "", "1 cup ragi flour\n1/4 cup rice flour\n1/4 cup urad dal (soaked, ground)\n1/2 cup curd\n1 onion (chopped)\n1 green chili\nSalt to taste\nOil for cooking",
         "1. Mix ragi flour, rice flour, and ground urad dal.\n2. Add curd and water to make pouring consistency batter.\n3. Add onion, green chili, and salt. Mix.\n4. Heat tawa, pour batter, spread thin.\n5. Drizzle oil, cook until crisp.\n6. Serve with sugar-free chutney.", "diabetes"),

        ("Moong Dal Chilla (Diabetes-Friendly)", "A high-protein lentil pancake with low glycemic index, ideal for diabetic breakfast.",
         "", "1 cup moong dal (soaked 4 hours)\n1/4 cup chopped spinach\n1/4 cup grated zucchini\n1 green chili\n1/2 inch ginger\n1/4 tsp turmeric\nSalt to taste\nOil for cooking",
         "1. Grind soaked moong dal with green chili and ginger to smooth batter.\n2. Mix in spinach, zucchini, turmeric, and salt.\n3. Heat non-stick pan, pour ladle of batter, spread.\n4. Cook until golden on both sides with minimal oil.\n5. Serve with mint chutney.", "diabetes"),

        ("Karela (Bitter Gourd) Sabzi", "A classic diabetes-friendly bitter gourd stir-fry that helps regulate blood sugar.",
         "", "2 medium karela (bitter gourd)\n1 onion (sliced)\n1/2 tsp cumin seeds\n1/4 tsp turmeric\n1/2 tsp red chili powder\n1 tsp mango powder (amchur)\n1 tbsp oil\nSalt to taste",
         "1. Scrape karela skin, slice thinly, rub with salt. Set aside 15 mins.\n2. Squeeze out bitter water, rinse.\n3. Heat oil, add cumin seeds, then onions. Sauté until golden.\n4. Add karela, turmeric, chili powder. Cook on low flame 10 mins.\n5. Add mango powder, mix, cook 2 more mins.\n6. Serve as a side dish with roti.", "diabetes"),

        ("Methi (Fenugreek) Thepla", "A Gujarathi-style flatbread made with fenugreek leaves and whole wheat — helps control blood sugar.",
         "", "1 cup whole wheat flour\n1/2 cup chopped methi (fenugreek) leaves\n1/4 cup yogurt\n1/2 tsp turmeric\n1/2 tsp red chili powder\n1/2 tsp cumin seeds\nSalt to taste\nOil for cooking",
         "1. Mix flour, methi leaves, yogurt, spices, and salt.\n2. Knead into a soft dough using water as needed.\n3. Divide into balls, roll out into thin theplas.\n4. Cook on tawa with oil until golden spots appear.\n5. Serve with yogurt or pickle.", "diabetes"),

        ("Brown Rice Pulao with Vegetables", "A low-GI pulao made with brown rice and mixed vegetables — perfect diabetic lunch.",
         "", "1 cup brown rice (soaked 2 hours)\n1 cup mixed vegetables\n1 onion (sliced)\n1 tsp cumin seeds\nWhole spices (cardamom, clove, bay leaf)\n1 tbsp ghee\nSalt to taste",
         "1. Heat ghee, add whole spices and cumin.\n2. Add onions, sauté until golden.\n3. Add vegetables, cook 2 mins.\n4. Add soaked brown rice, mix gently.\n5. Add 2.5 cups water and salt.\n6. Pressure cook for 4 whistles.\n7. Fluff and serve with raita.", "diabetes"),

        ("Soya Chaap Curry (Low-Calorie)", "A protein-rich, low-calorie curry made with soya chaap in light tomato gravy.",
         "", "250g soya chaap\n2 onions (chopped)\n3 tomatoes (pureed)\n2 tbsp low-fat curd\n1 tsp ginger-garlic paste\n1 tsp cumin seeds\n1/2 tsp turmeric\n1 tsp coriander powder\n1/2 tsp garam masala\n1 tbsp olive oil\nSalt to taste",
         "1. Heat oil, add cumin seeds, onions. Sauté until golden.\n2. Add ginger-garlic paste, cook 1 min.\n3. Add tomato puree, turmeric, coriander powder. Cook 5 mins.\n4. Add low-fat curd and garam masala. Mix.\n5. Add soya chaap pieces and salt. Cook 10 mins.\n6. Garnish with coriander. Serve hot.", "diabetes"),

         ("Lauki (Bottle Gourd) Curry", "A light, low-calorie bottle gourd curry that's easy to digest and diabetes-friendly.",
          "", "2 cups lauki (bottle gourd, cubed)\n1 onion (chopped)\n2 tomatoes (chopped)\n1 tsp ginger-garlic paste\n1/2 tsp cumin seeds\n1/4 tsp turmeric\n1 tsp coriander powder\n1 tbsp oil\nSalt to taste",
          "1. Heat oil, add cumin seeds and onions. Sauté until golden.\n2. Add ginger-garlic paste and tomatoes. Cook 2 mins.\n3. Add turmeric, coriander powder, and lauki.\n4. Add 1/2 cup water, cover, cook 15 mins until lauki is soft.\n5. Add salt and cook 2 more mins.\n6. Serve with roti or rice.", "diabetes"),

        # ---- NEW REGULAR RECIPES (10) ----
        ("Pesarattu (Green Gram Dosa)", "A protein-rich Andhra-style dosa made from whole green gram — crispy, nutritious, and delicious.",
         "", "1 cup whole green gram (soaked overnight)\n1/2 inch ginger\n2 green chilies\n1/4 tsp cumin seeds\nSalt to taste\nOil for cooking",
         "1. Drain soaked green gram and grind with ginger, green chili, and minimal water to thick batter.\n2. Add cumin seeds and salt. Mix.\n3. Heat tawa, pour ladle of batter and spread thin.\n4. Drizzle oil and cook until golden and crisp.\n5. Serve hot with ginger chutney and upma.", "regular"),

        ("Sabudana Khichdi", "A beloved fasting dish made with sago pearls, peanuts, and mild spices — light yet filling.",
         "", "1 cup sabudana (sago, soaked overnight)\n1/2 cup roasted peanuts (crushed)\n1 potato (diced)\n1 green chili (chopped)\n1 tsp cumin seeds\nFew curry leaves\n1 tbsp lemon juice\nSalt to taste\n1 tbsp oil\nFresh coriander",
         "1. Drain soaked sabudana and add salt and crushed peanuts.\n2. Heat oil, add cumin seeds, curry leaves, green chili.\n3. Add diced potato and cook until golden.\n4. Add sabudana mixture and cook on low flame for 5-7 mins.\n5. Stir gently until sabudana turns translucent.\n6. Add lemon juice and coriander.\n7. Serve hot.", "regular"),

        ("Chole Bhature", "A iconic Punjabi street food — spicy chickpea curry paired with fluffy deep-fried bread.",
         "", "1 cup chickpeas (soaked overnight)\n2 onions (pureed)\n2 tomatoes (pureed)\n1 tbsp ginger-garlic paste\n2 tsp chole masala\n1/2 tsp turmeric\n1 tsp coriander powder\n1/2 tsp red chili powder\n2 tbsp oil\nSalt to taste\nFor bhature: 2 cups maida, 1/2 cup yogurt, 1 tsp baking powder, salt, oil for frying",
         "1. Pressure cook chickpeas until soft.\n2. Heat oil, add onion puree and cook until golden.\n3. Add ginger-garlic paste, then tomato puree and spices. Cook until oil separates.\n4. Add chickpeas and simmer 15 mins.\n5. For bhature: mix flour, yogurt, baking powder, salt. Knead dough, rest 2 hours.\n6. Roll into rounds and deep fry until puffed.\n7. Serve hot bhature with chole.", "regular"),

        ("Aloo Gobi Masala", "A North Indian classic — potatoes and cauliflower cooked in aromatic onion-tomato gravy.",
         "", "2 potatoes (cubed)\n1 cauliflower (cut into florets)\n1 onion (chopped)\n2 tomatoes (chopped)\n1 tsp ginger-garlic paste\n1/2 tsp turmeric\n1 tsp coriander powder\n1/2 tsp garam masala\n1 tsp cumin seeds\n2 tbsp oil\nSalt to taste\nFresh coriander",
         "1. Heat oil, add cumin seeds.\n2. Add onions and sauté until golden.\n3. Add ginger-garlic paste and cook for 1 min.\n4. Add tomatoes, turmeric, coriander powder. Cook until soft.\n5. Add potatoes and cauliflower. Mix well.\n6. Add 1/4 cup water, cover and cook until tender.\n7. Add garam masala and coriander. Serve hot with roti.", "regular"),

        ("Egg Curry (Kerala Style)", "A fragrant coconut-based egg curry from Kerala — rich, creamy, and full of flavor.",
         "", "4 boiled eggs\n1 cup coconut milk\n1 onion (sliced)\n2 tomatoes (chopped)\n1 tsp ginger-garlic paste\n1/2 tsp turmeric\n1 tsp red chili powder\n1 tsp cumin seeds\nFew curry leaves\n2 tbsp coconut oil\nSalt to taste",
         "1. Score boiled eggs lightly.\n2. Heat coconut oil, add cumin seeds and curry leaves.\n3. Add onions and sauté until golden.\n4. Add ginger-garlic paste and tomatoes. Cook until soft.\n5. Add turmeric, chili powder, and coconut milk. Simmer.\n6. Add boiled eggs and cook for 5 mins.\n7. Serve hot with steamed rice.", "regular"),

        ("Paneer Tikka Masala", "Smoky grilled paneer cubes in a creamy, spiced tomato gravy — a restaurant favorite at home.",
         "", "200g paneer (cubed)\n1/2 cup yogurt\n1 tsp ginger-garlic paste\n1/2 tsp turmeric\n1 tsp red chili powder\n1 tsp garam masala\n2 tomatoes (pureed)\n1/4 cup cream\n1 tbsp butter\n1 bell pepper (cubed)\n1 onion (cubed)\nSalt to taste",
         "1. Marinate paneer in yogurt, ginger-garlic, turmeric, chili powder for 30 mins.\n2. Grill or pan-fry paneer until charred. Set aside.\n3. Heat butter, add tomato puree and cook until thick.\n4. Add garam masala, cream, and salt.\n5. Add grilled paneer, bell pepper, and onion.\n6. Simmer for 3 mins.\n7. Serve hot with naan or roti.", "regular"),

        ("Malai Kofta", "Soft paneer-potato dumplings in a rich, creamy tomato-cashew gravy — a Mughlai delicacy.",
         "", "For kofta: 1 cup paneer (grated), 2 boiled potatoes (mashed), 2 tbsp corn flour, salt, oil for frying\nFor gravy: 2 tomatoes (pureed), 1/4 cup cashew paste, 1/2 tsp turmeric, 1 tsp garam masala, 1 tbsp cream, 1 tbsp butter, salt to taste",
         "1. Mix grated paneer, mashed potatoes, corn flour, and salt. Shape into balls.\n2. Deep fry until golden. Set aside.\n3. Heat butter, add tomato puree and cook until oil separates.\n4. Add cashew paste, turmeric, garam masala, and salt.\n5. Add 1/2 cup water and simmer.\n6. Add cream and kofta balls.\n7. Serve hot with pulao or naan.", "regular"),

        ("Chicken Tikka", "Juicy chicken chunks marinated in yogurt and spices, grilled to smoky perfection.",
         "", "300g chicken (boneless, cubed)\n1/2 cup yogurt\n1 tbsp ginger-garlic paste\n1 tsp red chili powder\n1/2 tsp turmeric\n1 tsp garam masala\n1 tbsp lemon juice\n1 tbsp oil\nSalt to taste\nSkewers",
         "1. Mix yogurt, ginger-garlic paste, spices, lemon juice, oil, and salt.\n2. Marinate chicken for at least 1 hour.\n3. Thread onto skewers.\n4. Grill or bake at 200°C for 15-18 mins, turning once.\n5. Serve hot with mint chutney and onion rings.", "regular"),

        ("Dal Makhani", "A rich, slow-cooked black lentil curry with butter and cream — a Punjabi classic.",
         "", "1 cup whole black urad dal (soaked overnight)\n1/4 cup rajma (soaked overnight)\n2 tomatoes (pureed)\n1 tbsp ginger-garlic paste\n1/2 tsp turmeric\n1 tsp red chili powder\n2 tbsp butter\n1/4 cup cream\nSalt to taste\nFresh coriander",
         "1. Pressure cook soaked dal and rajma until very soft.\n2. Mash lightly.\n3. Heat butter, add ginger-garlic paste and tomato puree.\n4. Cook until oil separates.\n5. Add cooked dal, turmeric, chili powder, and salt.\n6. Simmer on low flame for 20-30 mins, stirring occasionally.\n7. Add cream and butter. Garnish with coriander.\n8. Serve with naan or rice.", "regular"),

        ("Mutton Rogan Josh", "A rich Kashmiri lamb curry slow-cooked with aromatic spices and yogurt gravy.",
         "", "300g mutton (bone-in)\n1 cup yogurt\n2 onions (sliced)\n2 tomatoes (pureed)\n1 tbsp ginger-garlic paste\n1 tsp Kashmiri red chili powder\n1/2 tsp turmeric\n1 tsp garam masala\nWhole spices (cardamom, cloves, cinnamon)\n2 tbsp oil\nSalt to taste",
         "1. Heat oil, add whole spices and onions. Fry until golden.\n2. Add ginger-garlic paste and cook.\n3. Add mutton pieces and sear on high heat.\n4. Add tomato puree, turmeric, chili powder. Cook until oil separates.\n5. Add whisked yogurt gradually, stirring.\n6. Add 1/2 cup water, cover and simmer for 45-60 mins until tender.\n7. Add garam masala and salt.\n8. Serve hot with rice or naan.", "regular"),

        # ---- NEW DIABETES-FRIENDLY RECIPES (10) ----
        ("Barley Vegetable Upma", "A low-GI breakfast made with pearl barley and mixed vegetables — high fiber, slow-release energy.",
         "", "1 cup pearl barley (soaked 2 hours)\n1/2 cup mixed vegetables\n1 onion (chopped)\n1 tsp mustard seeds\n2 green chilies\nFew curry leaves\n1 tbsp oil\nSalt to taste\nLemon juice",
         "1. Drain soaked barley.\n2. Heat oil, add mustard seeds, curry leaves, green chilies.\n3. Add onions and vegetables. Sauté for 3 mins.\n4. Add barley and 2.5 cups water. Salt.\n5. Cover and cook on low flame for 20-25 mins until soft.\n6. Add lemon juice. Serve warm.", "diabetes"),

        ("Bajra Roti with Methi Sabzi", "A traditional Rajasthani meal — millet flatbread with fenugreek greens for blood sugar control.",
         "", "For roti: 1 cup bajra flour, water, salt\nFor sabzi: 2 cups methi leaves (chopped), 1 onion (chopped), 2 green chilies, 1/2 tsp cumin seeds, 1 tbsp oil, salt to taste",
         "1. Knead bajra flour with water and salt into soft dough.\n2. Roll into rotis and cook on tawa with minimal ghee.\n3. For sabzi: heat oil, add cumin seeds, onions, green chilies.\n4. Add methi leaves and cook until wilted.\n5. Add salt and mix well.\n6. Serve bajra roti with methi sabzi.", "diabetes"),

        ("Moong Dal Pancakes (Diabetic)", "Light, protein-rich pancakes made from green gram — perfect low-GI breakfast option.",
         "", "1 cup moong dal (soaked 4 hours)\n1/4 cup oats\n1 green chili\n1/2 inch ginger\n1/4 tsp turmeric\nSalt to taste\nOil for cooking",
         "1. Grind soaked moong dal, oats, green chili, and ginger to batter.\n2. Add turmeric and salt.\n3. Heat non-stick pan, pour batter and spread.\n4. Drizzle minimal oil and cook until golden on both sides.\n5. Serve with mint chutney.", "diabetes"),

        ("Brown Rice Khichdi (Diabetic)", "A comforting one-pot meal with brown rice and moong dal — gentle on blood sugar levels.",
         "", "1/2 cup brown rice\n1/2 cup moong dal\n1 tsp ghee\n1/2 tsp cumin seeds\n1/4 tsp turmeric\n1/2 cup mixed vegetables\nSalt to taste\n3 cups water",
         "1. Wash brown rice and moong dal together.\n2. Heat ghee, add cumin seeds.\n3. Add vegetables and sauté for 2 mins.\n4. Add rice, dal, turmeric, salt, and water.\n5. Pressure cook for 4-5 whistles.\n6. Mash lightly and serve hot with yogurt.", "diabetes"),

        ("Quinoa Biryani (Diabetic)", "A protein-packed, low-GI biryani made with quinoa and fresh vegetables.",
         "", "1 cup quinoa\n1 cup mixed vegetables\n1 onion (sliced)\n1/2 cup yogurt\n1 tsp biryani masala\n1 tbsp ghee\nWhole spices\nFresh mint and coriander\nSalt to taste",
         "1. Rinse quinoa thoroughly.\n2. Heat ghee, add whole spices and onions. Fry until golden.\n3. Add yogurt, biryani masala, and vegetables. Cook 3 mins.\n4. Add quinoa and 2 cups water.\n5. Cover and cook on low flame for 15 mins.\n6. Garnish with mint and coriander. Serve hot.", "diabetes"),

        ("Grilled Fish with Steamed Vegetables (Diabetic)", "A lean protein meal — perfectly grilled fish with fiber-rich steamed vegetables.",
         "", "200g fish fillet\n1 cup mixed vegetables (broccoli, zucchini, carrot)\n1 tsp lemon juice\n1/2 tsp garlic powder\n1 tbsp olive oil\nSalt and pepper to taste\nFresh herbs",
         "1. Season fish with garlic powder, lemon juice, oil, salt, pepper.\n2. Grill fish for 4-5 mins each side.\n3. Steam or sauté vegetables until tender.\n4. Serve grilled fish with vegetables.\n5. Garnish with fresh herbs.", "diabetes"),

        ("Stuffed Bell Peppers with Quinoa (Diabetic)", "Colorful peppers stuffed with quinoa, beans, and spices — low GI, high nutrition.",
         "", "4 bell peppers (mixed colors)\n1 cup cooked quinoa\n1/2 cup black beans\n1/2 cup corn\n1/2 tsp cumin\n1/2 tsp chili powder\n1 tbsp olive oil\nSalt to taste\nCheese for topping (optional)",
         "1. Cut bell peppers in half, remove seeds.\n2. Mix quinoa, beans, corn, cumin, chili powder, oil, salt.\n3. Stuff peppers with mixture.\n4. Top with cheese if using.\n5. Bake at 190°C for 20-25 mins.\n6. Serve hot.", "diabetes"),

        ("Steamed Dal with Brown Rice (Diabetic)", "A light, nutritious combination of steamed lentils over brown rice — ideal diabetic comfort food.",
         "", "1/2 cup toor dal\n1/2 cup brown rice\n1 tsp ghee\n1/2 tsp cumin seeds\n1/4 tsp turmeric\n1 tomato (chopped)\nSalt to taste\nFresh coriander",
         "1. Wash dal and rice separately.\n2. Cook dal with turmeric until soft. Mash.\n3. Cook brown rice until fluffy.\n4. Heat ghee, add cumin seeds and tomatoes.\n5. Add cooked dal and salt. Simmer.\n6. Serve dal over brown rice with coriander.", "diabetes"),

        ("Stir-Fried Tofu with Broccoli (Diabetic)", "A quick, protein-rich stir-fry — tofu and broccoli in light Asian-style sauce.",
         "", "200g firm tofu (cubed)\n2 cups broccoli florets\n2 cloves garlic (minced)\n1 tbsp soy sauce\n1 tsp sesame oil\n1 tbsp oil\nBlack pepper to taste",
         "1. Press tofu and cut into cubes.\n2. Heat oil, fry tofu until golden. Set aside.\n3. In same pan, add sesame oil and garlic.\n4. Add broccoli and stir fry for 3-4 mins.\n5. Add soy sauce and tofu. Toss well.\n6. Serve hot with brown rice.", "diabetes"),

        ("Karela (Bitter Gourd) Stir-Fry with Chana (Diabetic)", "A double diabetes-fighter — bitter gourd with roasted chickpeas for blood sugar regulation.",
         "", "2 medium karela (bitter gourd)\n1/2 cup boiled chickpeas\n1 onion (sliced)\n1/2 tsp cumin seeds\n1/4 tsp turmeric\n1/2 tsp red chili powder\n1 tsp amchur (mango powder)\n1 tbsp oil\nSalt to taste",
         "1. Scrape karela, slice thinly, rub with salt. Rest 15 mins.\n2. Squeeze out bitter water, rinse.\n3. Heat oil, add cumin seeds and onions. Sauté until golden.\n4. Add karela, turmeric, chili powder. Cook on low flame 10 mins.\n5. Add roasted chickpeas and amchur.\n6. Cook 2 more mins and serve as a side dish.", "diabetes"),
    ]
    for r in famous_recipes:
        cur.execute("SELECT COUNT(*) FROM recipe WHERE receipename=?", (r[0],))
        if cur.fetchone()[0] == 0:
            cur.execute(
                "INSERT INTO recipe (receipename, description, videoid, ingredients, instructions, diet_type) VALUES (?, ?, ?, ?, ?, ?)",
                r
            )
    con.commit()
    con.close()

init_db()

# Session auth check helper
def check_auth():
    return 'user_email' in session

# load the model lazily to save memory
_model = None
_model_type = None

def get_model():
    global _model, _model_type
    if _model is not None:
        return _model

    h5_path = os.path.join(BASE_DIR, "Model", "model_v1_inceptionV3.h5")
    tflite_path = os.path.join(BASE_DIR, "Model", "model_v1_inceptionV3.tflite")

    if os.path.exists(tflite_path) and os.path.getsize(tflite_path) > 1000:
        file_size = os.path.getsize(tflite_path) / 1024 / 1024
        logger.info(f"Loading TFLite model ({file_size:.1f} MB)...")
        try:
            import tensorflow as tf
            interpreter = tf.lite.Interpreter(model_path=tflite_path)
            interpreter.allocate_tensors()
            _model = interpreter
            _model_type = "tflite"
            logger.info("TFLite model loaded successfully")
            return _model
        except Exception as e:
            logger.error(f"TFLite load failed: {e}")

    if os.path.exists(h5_path):
        file_size = os.path.getsize(h5_path)
        if file_size < 1000:
            logger.error(f"H5 model is LFS pointer ({file_size} bytes). Run convert_model.py locally.")
            return None
        logger.info(f"Loading H5 model ({file_size / 1024 / 1024:.1f} MB)...")
        try:
            import tensorflow as tf
            tf.get_logger().setLevel('ERROR')
            from tensorflow.keras.models import load_model
            start = time.time()
            _model = load_model(h5_path, compile=False)
            _model_type = "h5"
            logger.info(f"H5 model loaded in {time.time() - start:.1f}s")
            return _model
        except Exception as e:
            logger.error(f"H5 load failed: {e}")

    logger.error("No valid model file found. Run convert_model.py locally and push.")
    return None

# BMI functions
def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)

def get_bmi_category(bmi):
    if bmi < 18.5:
        return 'Underweight'
    elif 18.5 <= bmi < 25:
        return 'Normal'
    else:
        return 'Overweight'
    

# Build dataset for diet plan suggestions
def build_meal_data(all_meals=False, diabetes_only=False):
    data = {
        'MealTime': ['Breakfast']*30 + ['Snack']*30 + ['Lunch']*30 + ['Dinner']*30,
        'BMI_Category': (['Underweight']*10 + ['Normal']*10 + ['Overweight']*10) * 4,
        'Diabetes': ['No']*40 + ['Yes']*80,
        'Calories': [random.randint(150, 500) for _ in range(120)],
        'Weight_g': [random.randint(80, 500) for _ in range(120)],
        'Item': [
            # Breakfast - Non-diabetic (10)
            'Vegetable Upma', 'Boiled Eggs with Toast', 'Fruit Smoothie', 'Vegetable Dosa', 'Idli with Sambar',
            'Masala Dosa', 'Oats with Milk', 'Poha', 'Coconut Chutney with Rice', 'Ragi Porridge',
            # Snack - Non-diabetic (10)
            'Carrot Sticks', 'Cucumber Slices', 'Fruit Bowl', 'Apple', 'Banana Smoothie',
            'Mixed Nuts', 'Peanut Butter Shake', 'Roasted Chickpeas', 'Green Tea with Almonds', 'Buttermilk',
            # Lunch - Non-diabetic (10)
            'Mixed Vegetable Curry', 'Quinoa Salad', 'Tofu Stir Fry', 'Grilled Chicken with Rice', 'Fish Curry with Rice',
            'Paneer Paratha', 'Vegetable Biryani', 'Dal with Brown Rice', 'Lentil Soup', 'Chicken Biryani',
            # Dinner - Non-diabetic (10)
            'Grilled Fish', 'Veg Soup with Brown Bread', 'Moong Dal Khichdi', 'Vegetable Pulao', 'Paneer Bhurji with Roti',
            'Stuffed Paratha', 'Egg Fried Rice', 'Vegetable Stew', 'Clear Vegetable Soup', 'Steamed Vegetables with Tofu',
            # Breakfast - Diabetic (10)
            'Tofu Scramble', 'Quinoa Porridge', 'Moong Dal Chilla', 'Vegetable Dosa with Chutney',
            'Ragi Porridge', 'Boiled Eggs with Spinach', 'Vegetable Poha', 'Avocado Toast',
            'Oats with Almond Milk', 'Low-fat Greek Yogurt with Berries',
            # Snack - Diabetic (10)
            'Roasted Chickpeas', 'Green Tea with Almonds', 'Cucumber Slices', 'Celery Sticks',
            'Apple with Peanut Butter', 'Boiled Chana', 'Mixed Nuts', 'Buttermilk',
            'Carrot and Celery Sticks', 'Mixed Nuts (unsalted)',
            # Lunch - Diabetic (10)
            'Lentil Soup', 'Quinoa Salad', 'Zucchini Stir Fry', 'Chickpea Salad',
            'Vegetable Stew', 'Tofu Stir Fry', 'Dal with Brown Rice', 'Grilled Chicken with Broccoli',
            'Grilled Chicken with Quinoa', 'Lentil Soup with Spinach',
            # Dinner - Diabetic (10)
            'Moong Dal Khichdi', 'Spinach Soup', 'Clear Vegetable Soup', 'Oats Khichdi',
            'Steamed Vegetables with Tofu', 'Tofu and Vegetable Stir Fry', 'Masoor Dal with Quinoa',
            'Vegetable Pulao (with brown rice)', 'Grilled Salmon with Steamed Veggies', 'Spinach and Lentil Soup',
            # New Regular meals (10)
            'Pesarattu', 'Moong Dal Halwa', 'Rava Idli', 'Chole Masala', 'Sabudana Khichdi',
            'Vegetable Rava Upma', 'Egg Curry', 'Aloo Gobi', 'Rajma Rice', 'Bhel Puri',
            # New Diabetic meals (10)
            'Barley Upma', 'Bajra Roti with Sprouts Sabzi', 'Moong Dal Pancakes', 'Brown Rice Khichdi', 'Quinoa Biryani',
            'Grilled Fish with Vegetables', 'Steamed Dal with Brown Rice', 'Stuffed Bell Peppers', 'Stir-Fried Tofu with Broccoli', 'Kadai Paneer',
            # Extra variety items (30)
            'Masala Oats', 'Scrambled Eggs with Spinach', 'Avocado Toast with Whole Grain Bread',
            'Apple with Almond Butter', 'Fresh Fruit Salad', 'Cucumber Slices with Lemon',
            'Roasted Seaweed Snacks', 'Chickpea Salad', 'Grilled Fish with Salad',
            'Vegetable Soup with Whole Grain Bread', 'Stuffed Bell Peppers with Quinoa',
            'Masala Veg Soup', 'Poha with Vegetables', 'Banana Pancakes', 'Nut Butter Sandwich',
            'Multigrain Dosa', 'Sprouts Chaat', 'Stuffed Capsicum', 'Paneer Tikka',
            'Grilled Chicken with Broccoli', 'Tofu and Kale Stir Fry', 'Dal with Brown Rice',
            'Vegetable Salad with Olive Oil', 'Grilled Fish with Salad', 'Stuffed Paratha',
            'Egg Fried Rice', 'Steamed Vegetables with Tofu', 'Clear Vegetable Soup',
            'Paneer Bhurji with Roti', 'Vegetable Pulao',
            'Fruit Smoothie with Yogurt', 'Masala Dosa with Chutney', 'Idli with Coconut Chutney',
            'Vegetable Biryani with Raita', 'Chicken Curry with Rice', 'Fish Tikka',
            'Quinoa Pulao with Vegetables', 'Lemon Rice with Peanuts', 'Palak Paneer with Roti',
            'Mushroom Curry with Brown Rice'
        ]
    }
    df = pd.DataFrame(data)
    if all_meals:
        return df
    if diabetes_only:
        df = df[df['Diabetes'] == 'Yes']
    return df

def get_random_meal(mealtime, bmi_category, df):
    filtered = df[(df['MealTime'] == mealtime) & (df['BMI_Category'] == bmi_category)]
    if filtered.empty:
        return {"Item": "No meal found", "Weight": "-", "Calories": "-", "Ingredients": "", "Instructions": ""}
    selected = filtered.sample(1).iloc[0]
    item_name = selected['Item']
    recipe = MEAL_RECIPES.get(item_name, {"ingredients": "", "instructions": ""})
    return {
        "Item": item_name,
        "Weight": f"{selected['Weight_g']} g",
        "Calories": f"{selected['Calories']} kcal",
        "Ingredients": recipe.get("ingredients", ""),
        "Instructions": recipe.get("instructions", "")
    }
@app.route("/deit", methods=["GET", "POST"])
def homedeit():
    if not check_auth():
        return redirect("/")
    if request.method == "POST":
        weight = float(request.form["weight"])
        height = float(request.form["height"])
        bmi = calculate_bmi(weight, height)
        bmi_category = get_bmi_category(bmi)
        plan_type = request.form.get('plan_type')

        diabetes_only = plan_type == "diabetes"
        df = build_meal_data(all_meals=True, diabetes_only=diabetes_only)

        mealtimes = ['Breakfast', 'Snack', 'Lunch', 'Dinner']
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        plan = []
        for day in days:
            daily_meals = {}
            for meal in mealtimes:
                info = get_random_meal(meal, bmi_category, df)
                daily_meals[meal] = info
            plan.append({"day": day, "meals": daily_meals})

        return render_template("plan.html", bmi=bmi, category=bmi_category, plan=plan)

    return render_template("deit.html")
# Create a function to take and image and predict the class
FOOD_DATA = {
    0: {
        'product_name': 'burger', 'calories': 450, 'serving_size': '1 medium burger (~200g)',
        'protein': '20g', 'carbs': '35g', 'fat': '22g', 'fiber': '2g',
        'vitamins': 'A, B12, Iron', 'minerals': 'Calcium, Iron, Potassium'
    },
    1: {
        'product_name': 'butter_naan', 'calories': 290, 'serving_size': '1 naan (~100g)',
        'protein': '9g', 'carbs': '42g', 'fat': '12g', 'fiber': '1g',
        'vitamins': 'B1, B3', 'minerals': 'Iron, Calcium'
    },
    2: {
        'product_name': 'chai', 'calories': 93, 'serving_size': '1 cup (~240 ml)',
        'protein': '4g', 'carbs': '11g', 'fat': '3g', 'fiber': '0g',
        'vitamins': 'C, Antioxidants', 'minerals': 'Manganese, Potassium'
    },
    3: {
        'product_name': 'chapati', 'calories': 120, 'serving_size': '1 chapati (~40g)',
        'protein': '3g', 'carbs': '18g', 'fat': '3g', 'fiber': '3g',
        'vitamins': 'B1, B3', 'minerals': 'Iron, Selenium'
    },
    4: {
        'product_name': 'chole_bhature', 'calories': 427, 'serving_size': '1 serving (~250g, 2 bhature)',
        'protein': '11g', 'carbs': '50g', 'fat': '20g', 'fiber': '12g',
        'vitamins': 'B6, Folate, K', 'minerals': 'Iron, Magnesium, Potassium'
    },
    5: {
        'product_name': 'dal_makhani', 'calories': 240, 'serving_size': '1 bowl (~150g)',
        'protein': '10g', 'carbs': '24g', 'fat': '12g', 'fiber': '6g',
        'vitamins': 'B1, B6, Folate', 'minerals': 'Iron, Potassium, Magnesium'
    },
    6: {
        'product_name': 'dhokla', 'calories': 160, 'serving_size': '1 serving (~100g)',
        'protein': '6g', 'carbs': '26g', 'fat': '3g', 'fiber': '2g',
        'vitamins': 'B1, B2', 'minerals': 'Iron, Calcium'
    },
    7: {
        'product_name': 'fried_rice', 'calories': 340, 'serving_size': '1 bowl (~200g)',
        'protein': '13g', 'carbs': '46g', 'fat': '13g', 'fiber': '2g',
        'vitamins': 'B1, B3', 'minerals': 'Iron, Selenium'
    },
    8: {
        'product_name': 'idli', 'calories': 39, 'serving_size': '1 idli (~30g)',
        'protein': '2g', 'carbs': '7g', 'fat': '0.1g', 'fiber': '0.3g',
        'vitamins': 'B1, B2', 'minerals': 'Iron, Calcium'
    },
    9: {
        'product_name': 'jalebi', 'calories': 150, 'serving_size': '1 piece (~50g)',
        'protein': '2g', 'carbs': '31g', 'fat': '2g', 'fiber': '0g',
        'vitamins': 'B1', 'minerals': 'Iron'
    },
    10: {
        'product_name': 'kaathi_rolls', 'calories': 300, 'serving_size': '1 roll (~150g)',
        'protein': '12g', 'carbs': '40g', 'fat': '10g', 'fiber': '3g',
        'vitamins': 'B6, B12', 'minerals': 'Iron, Zinc'
    },
    11: {
        'product_name': 'kadai_paneer', 'calories': 250, 'serving_size': '1 bowl (~150g)',
        'protein': '14g', 'carbs': '10g', 'fat': '18g', 'fiber': '3g',
        'vitamins': 'A, B12, K', 'minerals': 'Calcium, Phosphorus'
    },
    12: {
        'product_name': 'kulfi', 'calories': 200, 'serving_size': '1 piece (~100g)',
        'protein': '5g', 'carbs': '25g', 'fat': '10g', 'fiber': '0g',
        'vitamins': 'A, B12, D', 'minerals': 'Calcium, Phosphorus'
    },
    13: {
        'product_name': 'masala_dosa', 'calories': 345, 'serving_size': '1 dosa (~200g)',
        'protein': '7g', 'carbs': '41g', 'fat': '16g', 'fiber': '3g',
        'vitamins': 'B1, B2, B3', 'minerals': 'Iron, Calcium, Potassium'
    },
    14: {
        'product_name': 'momos', 'calories': 35, 'serving_size': '1 momo (~30g)',
        'protein': '1g', 'carbs': '6g', 'fat': '0.5g', 'fiber': '0.5g',
        'vitamins': 'B1, B6', 'minerals': 'Iron, Zinc'
    },
    15: {
        'product_name': 'paani_puri', 'calories': 25, 'serving_size': '1 puri (~10g)',
        'protein': '0.5g', 'carbs': '4g', 'fat': '1g', 'fiber': '0.3g',
        'vitamins': 'C, B6', 'minerals': 'Iron, Potassium'
    },
    16: {
        'product_name': 'pakode', 'calories': 55, 'serving_size': '1 piece (~20g)',
        'protein': '1g', 'carbs': '6g', 'fat': '3g', 'fiber': '0.5g',
        'vitamins': 'B1, B6', 'minerals': 'Iron, Potassium'
    },
    17: {
        'product_name': 'pav_bhaji', 'calories': 406, 'serving_size': '1 plate (~250g)',
        'protein': '10g', 'carbs': '58g', 'fat': '14g', 'fiber': '6g',
        'vitamins': 'A, C, B6', 'minerals': 'Iron, Potassium, Magnesium'
    },
    18: {
        'product_name': 'pizza', 'calories': 270, 'serving_size': '1 slice (~100g)',
        'protein': '11g', 'carbs': '33g', 'fat': '10g', 'fiber': '2g',
        'vitamins': 'A, B12, K', 'minerals': 'Calcium, Phosphorus, Selenium'
    },
    19: {
        'product_name': 'samosa', 'calories': 180, 'serving_size': '1 piece (~50g)',
        'protein': '3g', 'carbs': '18g', 'fat': '11g', 'fiber': '2g',
        'vitamins': 'B1, B6', 'minerals': 'Iron, Potassium'
    }
}

def model_predict(img_path, model):
    from tensorflow.keras.preprocessing import image as keras_image
    logger.info(f"Predicting: {img_path}")
    start = time.time()

    img = keras_image.load_img(img_path, target_size=(299, 299))
    x = keras_image.img_to_array(img)
    x = np.expand_dims(x, axis=0) / 255.0

    if _model_type == "tflite":
        input_details = model.get_input_details()
        output_details = model.get_output_details()
        model.set_tensor(input_details[0]['index'], x.astype(np.float32))
        model.invoke()
        preds = model.get_tensor(output_details[0]['index'])[0]
    else:
        preds = model.predict(x, verbose=0)[0]

    elapsed = time.time() - start
    logger.info(f"Prediction took {elapsed:.2f}s")

    top_3_idx = np.argsort(preds)[-3:][::-1]
    top_3_conf = preds[top_3_idx]

    primary = FOOD_DATA[top_3_idx[0]].copy()
    primary['confidence'] = round(float(top_3_conf[0]) * 100, 1)

    alternatives = []
    for i in range(1, 3):
        alternatives.append({
            'name': FOOD_DATA[top_3_idx[i]]['product_name'].replace('_', ' ').title(),
            'confidence': round(float(top_3_conf[i]) * 100, 1)
        })

    primary['alternatives'] = alternatives
    return primary



@app.route('/logon')
def logon():
	return render_template('signup.html')

@app.route('/')
def login():
	return render_template('signin.html')

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    username = request.form.get('user','')
    name = request.form.get('name','')
    email = request.form.get('email','')
    number = request.form.get('mobile','')
    password = request.form.get('password','')
    
    if not username or not password:
        return render_template("signup.html", error="Username and password are required")
        
    con = sqlite3.connect(os.path.join(BASE_DIR, 'signup.db'))
    cur = con.cursor()
    try:
        cur.execute("insert into `info` (`user`,`email`, `password`,`mobile`,`name`) VALUES (?, ?, ?, ?, ?)",(username,email,password,number,name))
        con.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    finally:
        con.close()
        
    if not success:
        return render_template("signup.html", error="Username already exists. Please choose another one.")
        
    return render_template("signin.html", message="Account created successfully! Please login.")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "GET":
        return render_template("signin.html")

    mail1 = request.form.get('user', '')
    password1 = request.form.get('password', '')

    con = sqlite3.connect(os.path.join(BASE_DIR, 'signup.db'))
    cur = con.cursor()
    cur.execute("SELECT user, password, email FROM info WHERE user = ? AND password = ?", (mail1, password1))
    data = cur.fetchone()
    con.close()

    if data is None:
        return render_template("signin.html", error="Invalid credentials")

    session['user_email'] = data[2]
    return redirect("/prediction")

@app.route('/prediction' , methods=["GET"])
def prediction(): # Main Page
    if not check_auth():
        return redirect("/")
    return render_template('index.html')
@app.route('/logout')
def logout():
    session.clear()  # Remove user from session
    return redirect("/")  # Redirect to login or home page


@app.route('/predict' , methods=['POST'])
def uploads():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401
        
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    f = request.files['file']
    if f.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    model = get_model()
    if model is None:
        return jsonify({"error": "Model not loaded. Please ensure Model/model_v1_inceptionV3.h5 exists."}), 500

    file_path = None
    try:
        uploads_dir = os.path.join(BASE_DIR, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        filename = secure_filename(f.filename)
        if not filename:
            filename = f"upload_{int(time.time())}.jpg"
        
        file_path = os.path.join(uploads_dir, filename)
        f.save(file_path)

        preds = model_predict(file_path, model)
        return jsonify(preds)
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass



@app.route("/viewrecipes")
def view_recipes():
    if not check_auth():
        return redirect("/")
    diet_filter = request.args.get('diet', 'all')
    search_q = request.args.get('q', '')
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'signup.db'))
    if diet_filter == 'all':
        recipes = conn.execute("SELECT * FROM recipe WHERE receipename LIKE ? OR description LIKE ?",
                               (f'%{search_q}%', f'%{search_q}%')).fetchall()
    else:
        recipes = conn.execute("SELECT * FROM recipe WHERE diet_type = ? AND (receipename LIKE ? OR description LIKE ?)",
                               (diet_filter, f'%{search_q}%', f'%{search_q}%')).fetchall()
    conn.close()
    return render_template("receipe.html", recipes=recipes, current_diet=diet_filter)

@app.route("/add", methods=["POST"])
def add_recipe():
    if not check_auth():
        return redirect("/")
    name = request.form["receipename"]
    description = request.form["description"]
    videoid = request.form.get("videoid", "")
    ingredients = request.form.get("ingredients", "")
    instructions = request.form.get("instructions", "")
    diet_type = request.form.get("diet_type", "both")
    with sqlite3.connect(os.path.join(BASE_DIR, 'signup.db')) as conn:
        conn.execute("INSERT INTO recipe (receipename, description, videoid, ingredients, instructions, diet_type) VALUES (?, ?, ?, ?, ?, ?)",
                     (name, description, videoid, ingredients, instructions, diet_type))
    return redirect(url_for("view_recipes"))

@app.route("/edit/<int:recipeid>", methods=["POST"])
def edit_recipe(recipeid):
    if not check_auth():
        return redirect("/")
    name = request.form["receipename"]
    description = request.form["description"]
    videoid = request.form.get("videoid", "")
    ingredients = request.form.get("ingredients", "")
    instructions = request.form.get("instructions", "")
    diet_type = request.form.get("diet_type", "both")
    with sqlite3.connect(os.path.join(BASE_DIR, 'signup.db')) as conn:
        conn.execute("UPDATE recipe SET receipename=?, description=?, videoid=?, ingredients=?, instructions=?, diet_type=? WHERE recipeid=?",
                     (name, description, videoid, ingredients, instructions, diet_type, recipeid))
    return redirect(url_for("view_recipes"))

@app.route("/delete/<int:recipeid>")
def delete_recipe(recipeid):
    if not check_auth():
        return redirect("/")
    with sqlite3.connect(os.path.join(BASE_DIR, 'signup.db')) as conn:
        conn.execute("DELETE FROM recipe WHERE recipeid=?", (recipeid,))
    return redirect(url_for("view_recipes"))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


