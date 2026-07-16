import os
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from flask import *
from werkzeug.utils import secure_filename
import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
            videoid TEXT
        )
    ''')
    
    # Seed initial recipes if empty
    cur.execute("SELECT COUNT(*) FROM recipe")
    if cur.fetchone()[0] == 0:
        initial_recipes = [
            ("Healthy Masala Dosa", "A light and crispy South Indian classic made with fermented rice batter, filled with a potato mash.", "S75gIapV3Kk"),
            ("Sprouted Moong Chaat", "High protein and nutrient-rich salad made with sprouted green gram, tossed with chopped onions, tomatoes, and spices.", "aV_j6Zndlco"),
            ("Indian Oats Khichdi", "A wholesome, comforting one-pot meal made with oats, yellow lentils, and loaded with fresh vegetables.", "A3V-vT9cZlc"),
        ]
        cur.executemany("INSERT INTO recipe (receipename, description, videoid) VALUES (?, ?, ?)", initial_recipes)

    # Seed admin user if not exists
    cur.execute("SELECT user FROM info WHERE user = 'admin'")
    if cur.fetchone() is None:
        cur.execute("INSERT INTO info (user, email, password, mobile, name) VALUES (?, ?, ?, ?, ?)",
                    ('admin', 'admin@admin.com', 'admin', '', 'Admin'))
    con.commit()
    con.close()

init_db()

# Session auth check helper
def check_auth():
    return 'user_email' in session

# load the model
Model_path = os.path.join(BASE_DIR, "Model", "model_v1_inceptionV3.h5")
try:
    model = load_model(Model_path)
except Exception as e:
    print(f"Warning: Could not load model: {e}")
    model = None

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
        return {"Item": "No meal found", "Weight": "-", "Calories": "-"}
    selected = filtered.sample(1).iloc[0]
    return {
        "Item": selected['Item'],
        "Weight": f"{selected['Weight_g']} g",
        "Calories": f"{selected['Calories']} kcal"
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
def model_predict(img_path , model):
    print(img_path)
    img = image.load_img(img_path , target_size=(299 , 299))
    x = image.img_to_array(img)
    x = x / 255 
    x = np.expand_dims(x , axis = 0)
    food_data = {
    0: {'product_name': 'burger', 'calories': 400, 'serving_size': '1 medium burger (~200g)'},
    1: {'product_name': 'butter_naan', 'calories': 175, 'serving_size': '1 naan (~100g)'},
    2: {'product_name': 'chai', 'calories': 120, 'serving_size': '1 cup (~240 ml)'},
    3: {'product_name': 'chapati', 'calories': 75, 'serving_size': '1 chapati (~40g)'},
    4: {'product_name': 'chole_bhature', 'calories': 525, 'serving_size': '1 serving (~250g, 2 bhature)'},
    5: {'product_name': 'dal_makhani', 'calories': 325, 'serving_size': '1 bowl (~150g)'},
    6: {'product_name': 'dhokla', 'calories': 150, 'serving_size': '1 serving (~100g)'},
    7: {'product_name': 'fried_rice', 'calories': 275, 'serving_size': '1 bowl (~200g)'},
    8: {'product_name': 'idli', 'calories': 40, 'serving_size': '1 idli (~30g)'},
    9: {'product_name': 'jalebi', 'calories': 150, 'serving_size': '1 piece (~50g)'},
    10: {'product_name': 'kaathi_rolls', 'calories': 300, 'serving_size': '1 roll (~150g)'},
    11: {'product_name': 'kadai_paneer', 'calories': 300, 'serving_size': '1 bowl (~150g)'},
    12: {'product_name': 'kulfi', 'calories': 200, 'serving_size': '1 piece (~100g)'},
    13: {'product_name': 'masala_dosa', 'calories': 350, 'serving_size': '1 dosa (~200g)'},
    14: {'product_name': 'momos', 'calories': 35, 'serving_size': '1 momo (~30g)'},
    15: {'product_name': 'paani_puri', 'calories': 25, 'serving_size': '1 puri (~10g)'},
    16: {'product_name': 'pakode', 'calories': 70, 'serving_size': '1 piece (~20g)'},
    17: {'product_name': 'pav_bhaji', 'calories': 400, 'serving_size': '1 plate (~250g)'},
    18: {'product_name': 'pizza', 'calories': 270, 'serving_size': '1 slice (~100g)'},
    19: {'product_name': 'samosa', 'calories': 130, 'serving_size': '1 piece (~50g)'}
}
    preds = model.predict(x)
    preds = np.argmax(preds , axis = 1)
    print(preds)
    return food_data[preds[0]]



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
        
    if model is None:
        return jsonify({"error": "Model not loaded. Please ensure Model/model_v1_inceptionV3.h5 exists."}), 500

    try:
        # Save the file to ./uploads
        file_path = os.path.join(BASE_DIR , 'uploads' , secure_filename(f.filename))
        f.save(file_path)

        # Make Prediction
        preds = model_predict(file_path, model)
        return jsonify(preds)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



@app.route("/viewrecipes")
def view_recipes():
    if not check_auth():
        return redirect("/")
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'signup.db'))
    recipes = conn.execute("SELECT * FROM recipe").fetchall()
    conn.close()
    return render_template("receipe.html", recipes=recipes)

@app.route("/add", methods=["POST"])
def add_recipe():
    if not check_auth():
        return redirect("/")
    name = request.form["receipename"]
    description = request.form["description"]
    videoid = request.form["videoid"]
    with sqlite3.connect(os.path.join(BASE_DIR, 'signup.db')) as conn:
        conn.execute("INSERT INTO recipe (receipename, description, videoid) VALUES (?, ?, ?)",
                     (name, description, videoid))
    return redirect(url_for("view_recipes"))

@app.route("/edit/<int:recipeid>", methods=["POST"])
def edit_recipe(recipeid):
    if not check_auth():
        return redirect("/")
    name = request.form["receipename"]
    description = request.form["description"]
    videoid = request.form["videoid"]
    with sqlite3.connect(os.path.join(BASE_DIR, 'signup.db')) as conn:
        conn.execute("UPDATE recipe SET receipename=?, description=?, videoid=? WHERE recipeid=?",
                     (name, description, videoid, recipeid))
    return redirect(url_for("view_recipes"))

@app.route("/delete/<int:recipeid>")
def delete_recipe(recipeid):
    if not check_auth():
        return redirect("/")
    with sqlite3.connect(os.path.join(BASE_DIR, 'signup.db')) as conn:
        conn.execute("DELETE FROM recipe WHERE recipeid=?", (recipeid,))
    return redirect(url_for("view_recipes"))

if __name__ == '__main__':
    app.run(debug=True)


