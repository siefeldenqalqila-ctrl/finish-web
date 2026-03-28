from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from datetime import datetime
import sqlite3
import secrets
import re
import json
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# إنشاء مجلد رفع الصور إذا لم يكن موجوداً
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DB = "paper.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# تهيئة قاعدة البيانات
def init_db():
    conn = get_db()
    
    # جدول المستخدمين
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE,
            password TEXT NOT NULL,
            type TEXT DEFAULT 'individual',
            company_name TEXT,
            governorate TEXT,
            address TEXT,
            role TEXT NOT NULL DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # جدول المنتجات
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            min_quantity INTEGER DEFAULT 1,
            unit TEXT DEFAULT 'كجم',
            category TEXT,
            image TEXT,
            features TEXT,
            available BOOLEAN DEFAULT 1,
            company_id INTEGER,
            company_name TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES users(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    # جدول الطلبات
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE,
            user_id INTEGER,
            products TEXT,
            quantity INTEGER,
            subtotal REAL,
            delivery_fee REAL,
            total REAL,
            delivery_date TEXT,
            delivery_time TEXT,
            notes TEXT,
            payment_method TEXT,
            status TEXT DEFAULT 'قيد المراجعة',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # إضافة مستخدمين تجريبيين
    cursor = conn.execute("SELECT * FROM users WHERE email = ?", ("admin@ecopaper.com",))
    if not cursor.fetchone():
        conn.execute("""
            INSERT INTO users (name, email, phone, password, type, governorate, address, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("مدير النظام", "admin@ecopaper.com", "01234567890", "admin123", "admin", "القاهرة", "المنطقة الصناعية", "admin"))
    
    # إضافة شركة PaperTech Egypt
    cursor = conn.execute("SELECT * FROM users WHERE email = ?", ("company1@ecopaper.com",))
    if not cursor.fetchone():
        conn.execute("""
            INSERT INTO users (name, email, phone, password, type, company_name, governorate, address, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("PaperTech Egypt", "company1@ecopaper.com", "01234567891", "company123", "company", "PaperTech Egypt", "القاهرة", "المنطقة الصناعية", "company"))
    
    # إضافة شركة EcoPack
    cursor = conn.execute("SELECT * FROM users WHERE email = ?", ("company2@ecopaper.com",))
    if not cursor.fetchone():
        conn.execute("""
            INSERT INTO users (name, email, phone, password, type, company_name, governorate, address, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("EcoPack", "company2@ecopaper.com", "01234567892", "company123", "company", "EcoPack", "الجيزة", "المنطقة الصناعية", "company"))
    
    # إضافة شركة Advanced Recycling Co
    cursor = conn.execute("SELECT * FROM users WHERE email = ?", ("company3@ecopaper.com",))
    if not cursor.fetchone():
        conn.execute("""
            INSERT INTO users (name, email, phone, password, type, company_name, governorate, address, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Advanced Recycling Co", "company3@ecopaper.com", "01234567893", "company123", "company", "Advanced Recycling Co", "الإسكندرية", "المنطقة الصناعية", "company"))
    
    # إضافة مستخدم عادي
    cursor = conn.execute("SELECT * FROM users WHERE email = ?", ("user@example.com",))
    if not cursor.fetchone():
        conn.execute("""
            INSERT INTO users (name, email, phone, password, type, governorate, address, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("أحمد محمد", "user@example.com", "01234567894", "user123", "individual", "القاهرة", "مدينة نصر", "customer"))
    
    # إضافة المنتجات الافتراضية العشرة
    cursor = conn.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]
    
    if product_count == 0:
        # الحصول على ids للشركات
        company1 = conn.execute("SELECT id, company_name FROM users WHERE company_name = ?", ("PaperTech Egypt",)).fetchone()
        company2 = conn.execute("SELECT id, company_name FROM users WHERE company_name = ?", ("EcoPack",)).fetchone()
        company3 = conn.execute("SELECT id, company_name FROM users WHERE company_name = ?", ("Advanced Recycling Co",)).fetchone()
        
        company1_id = company1[0] if company1 else 2
        company2_id = company2[0] if company2 else 3
        company3_id = company3[0] if company3 else 4
        
        company1_name = company1[1] if company1 else "PaperTech Egypt"
        company2_name = company2[1] if company2 else "EcoPack"
        company3_name = company3[1] if company3 else "Advanced Recycling Co"
        
        products_data = [
            (company1_id, "Testliner (ورق تست لاينر)", "يستخدم كطبقة خارجية للكرتون المضلع بقوة تحمل متوسطة.", 7.5, 10, "كجم", "Liner Paper", "/static/images/WhatsApp Image 2026-03-26 at 11.51.48 AM (1).jpeg", json.dumps(["120 – 200 GSM", "قوة ضغط متوسطة", "مقاومة رطوبة متوسطة"]), 1, company1_name),
            (company1_id, "Fluting Paper (ورق فلوتنج)", "طبقة مموجة داخل الكرتون المضلع لزيادة المتانة.", 6.8, 10, "كجم", "Fluting", "/static/images/WhatsApp Image 2026-03-26 at 11.51.48 AM.jpeg", json.dumps(["90 – 150 GSM", "مرونة عالية", "مقاومة ضغط جيدة"]), 1, company1_name),
            (company2_id, "Recycled Kraft Paper (ورق كرافت)", "مناسب لأكياس التسوق والتغليف بقوة شد عالية.", 8.2, 8, "كجم", "Kraft Paper", "/static/images/WhatsApp Image 2026-03-26 at 11.51.50 AM (1).jpeg", json.dumps(["70 – 200 GSM", "مقاومة تمزق عالية", "قوة شد عالية"]), 1, company2_name),
            (company2_id, "Corrugated Cardboard (كرتون مضلع)", "يستخدم في صناديق الشحن والتخزين ومقاوم للصدمات.", 9.5, 15, "كجم", "Corrugated", "/static/images/WhatsApp Image 2026-03-26 at 11.51.49 AM.jpeg", json.dumps(["سمك 3 – 7 مم", "قوة تحمل عالية", "مقاومة صدمات"]), 1, company2_name),
            (company3_id, "Duplex Board – Brown Back", "يستخدم في علب المنتجات بجودة طباعة ممتازة.", 10.5, 12, "كجم", "Duplex Board", "/static/images/WhatsApp Image 2026-03-26 at 11.51.49 AM (6).jpeg", json.dumps(["200 – 450 GSM", "صلابة عالية", "قابل للطباعة ممتاز"]), 1, company3_name),
            (company3_id, "Chipboard / Grey Board", "يستخدم في علب الأحذية والملفات بصلابة عالية.", 6.2, 10, "كجم", "Grey Board", "/static/images/WhatsApp Image 2026-03-26 at 11.51.49 AM (5).jpeg", json.dumps(["سمك 1 – 4 مم", "كثافة عالية", "مقاومة ضغط عالية"]), 1, company3_name),
            (company1_id, "Linerboard (لاينربورد)", "طبقة خارجية قوية للكرتون والتغليف.", 8.7, 12, "كجم", "Linerboard", "/static/images/WhatsApp Image 2026-03-26 at 11.51.49 AM (4).jpeg", json.dumps(["125 – 300 GSM", "مقاومة تمزق عالية", "قوة تحمل عالية"]), 1, company1_name),
            (company2_id, "Brown Wrapping Paper (ورق تغليف بني)", "مناسب لتغليف المنتجات بتكلفة منخفضة.", 5.8, 5, "كجم", "Wrapping Paper", "/static/images/WhatsApp Image 2026-03-26 at 11.51.49 AM (3).jpeg", json.dumps(["60 – 120 GSM", "مرونة عالية", "تكلفة منخفضة"]), 1, company2_name),
            (company3_id, "Paper Core Board (ورق بكر وأنابيب)", "يستخدم في تصنيع بكر الورق والأنابيب الكرتونية.", 9.2, 15, "كجم", "Core Board", "/static/images/WhatsApp Image 2026-03-26 at 11.51.49 AM (2).jpeg", json.dumps(["سماكة عالية", "مقاومة ضغط عالية", "عمر افتراضي طويل"]), 1, company3_name),
            (company2_id, "Recycled Carton Board (كرتون معاد تدويره)", "مناسب لصناعة علب التعبئة بجودة جيدة.", 7.9, 10, "كجم", "Carton Board", "/static/images/WhatsApp Image 2026-03-26 at 11.51.49 AM (1).jpeg", json.dumps(["180 – 350 GSM", "صلابة متوسطة", "قابل للطباعة"]), 1, company2_name)
        ]
        
        for p in products_data:
            conn.execute("""
                INSERT INTO products (company_id, name, description, price, min_quantity, unit, category, image, features, available, company_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, p)
        
        print("✅ تم إضافة 10 منتجات افتراضية")
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

# استدعاء التهيئة
init_db()

# ==================== الصفحات الرئيسية ====================

@app.route("/")
def home():
    if 'user_id' in session:
        return redirect(url_for('base'))
    return redirect(url_for('index'))

@app.route("/index")
def index():
    if 'user_id' in session:
        return redirect(url_for('base'))
    return render_template("index.html")

@app.route("/base")
def base():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
    
    return render_template("home.html", user=user)

# ==================== المصادقة ====================

@app.route("/login")
def login():
    if 'user_id' in session:
        return redirect(url_for('base'))
    return render_template("login.html")

@app.route("/register")
def register():
    if 'user_id' in session:
        return redirect(url_for('base'))
    return render_template("register.html")

@app.route("/forget_password")
def forget_password():
    return render_template("forget_password.html")

@app.route("/otp")
def otp():
    return render_template("otp.html")

@app.route("/reset_password")
def reset_password():
    return render_template("reset_password.html")

@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    orders_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    conn.close()
    
    return render_template("dashboard.html", user=user, orders_count=orders_count)

@app.route("/submit", methods=["POST"])
def submit():
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirmPassword")
    phone = request.form.get("phone")
    userType = request.form.get("userType")
    address = request.form.get("address")
    governorate = request.form.get("governorate")
    company_name = request.form.get("companyName") if userType == "company" else None
    
    if password != confirm_password:
        flash("كلمات المرور غير متطابقة", "error")
        return redirect(url_for("register"))
    
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash("البريد الإلكتروني غير صالح", "error")
        return redirect(url_for("register"))
    
    if not re.match(r"^01[0125][0-9]{8}$", phone):
        flash("رقم الهاتف غير صالح", "error")
        return redirect(url_for("register"))
    
    conn = get_db()
    
    existing = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        conn.close()
        flash("البريد الإلكتروني مسجل بالفعل", "error")
        return redirect(url_for("register"))
    
    existing = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
    if existing:
        conn.close()
        flash("رقم الهاتف مسجل بالفعل", "error")
        return redirect(url_for("register"))
    
    try:
        if userType == "company":
            role = "company"
        else:
            role = "customer"
        
        conn.execute("""
            INSERT INTO users 
            (name, email, password, phone, type, company_name, governorate, address, role, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, password, phone, userType, company_name, governorate, address, role, date))
        
        conn.commit()
        flash("✅ تم إنشاء الحساب بنجاح", "success")
        return redirect(url_for("login"))
    
    except Exception as e:
        flash(f"❌ حدث خطأ: {str(e)}", "error")
        return redirect(url_for("register"))
    
    finally:
        conn.close()

@app.route("/sure", methods=["POST"])
def sure():
    email = request.form.get("email")
    password = request.form.get("password")
    remember = request.form.get("rememberMe")
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    
    if not user:
        conn.close()
        flash("❌ البريد الإلكتروني غير مسجل", "error")
        return redirect(url_for("login"))
    
    if user["password"] != password:
        conn.close()
        flash("❌ كلمة المرور غير صحيحة", "error")
        return redirect(url_for("login"))
    
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["user_email"] = user["email"]
    session["user_role"] = user["role"]
    session["user_type"] = user["type"]
    session["company_name"] = user["company_name"]
    
    if remember:
        session.permanent = True
    
    flash(f"✅ تم تسجيل الدخول بنجاح {user['name']}", "success")
    
    if user["role"] == "admin":
        return redirect(url_for("admin_products"))
    elif user["role"] == "company":
        return redirect(url_for("company_products"))
    else:
        return redirect(url_for("base"))

@app.route("/logout")
def logout():
    session.clear()
    flash("✅ تم تسجيل الخروج بنجاح", "success")
    return redirect(url_for("index"))

# ==================== صفحات المستخدم العادي ====================

@app.route("/products")
def product():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("product.html")

@app.route("/orders-history")
def orders_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("orders-history.html")

@app.route("/profile")
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
    
    return render_template("profile.html", user=user)

@app.route("/create-order")
def create_order():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("order.html")

@app.route("/order-tracking")
def order_tracking():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("order-tracking.html")

@app.route("/order-confirm")
def order_confirm():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("order_confirm.html")

@app.route("/payment")
def payment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("payment.html")

# ==================== صفحات الشركات (Company) ====================

@app.route("/company/products")
def company_products():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
    
    if user["role"] not in ["company", "admin"]:
        flash("❌ ليس لديك صلاحية الوصول إلى هذه الصفحة", "error")
        return redirect(url_for('base'))
    
    return render_template("company_products.html", user=user)

@app.route("/company/orders")
def company_orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    
    if user["role"] not in ["company", "admin"]:
        conn.close()
        flash("❌ ليس لديك صلاحية الوصول إلى هذه الصفحة", "error")
        return redirect(url_for('base'))
    
    orders = conn.execute("""
        SELECT o.*, u.name as user_name, u.phone 
        FROM orders o 
        JOIN users u ON o.user_id = u.id 
        ORDER BY o.created_at DESC
    """).fetchall()
    conn.close()
    
    return render_template("company_orders.html", orders=orders, user=user)

# ==================== صفحات الإدارة (Admin Only) ====================

@app.route("/admin/products")
def admin_products():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
    
    if user["role"] != "admin":
        flash("❌ ليس لديك صلاحية الوصول إلى هذه الصفحة", "error")
        return redirect(url_for('base'))
    
    return render_template("admin_products.html", user=user)

@app.route("/admin/orders")
def admin_orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    
    if user["role"] != "admin":
        conn.close()
        flash("❌ ليس لديك صلاحية الوصول إلى هذه الصفحة", "error")
        return redirect(url_for('base'))
    
    orders = conn.execute("""
        SELECT o.*, u.name as user_name, u.email, u.phone, u.type
        FROM orders o 
        JOIN users u ON o.user_id = u.id 
        ORDER BY o.created_at DESC
    """).fetchall()
    conn.close()
    
    return render_template("admin_orders.html", orders=orders, user=user)

@app.route("/admin/order/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "غير مصرح"})
    
    data = request.get_json()
    new_status = data.get("status")
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    
    if user["role"] != "admin":
        conn.close()
        return jsonify({"success": False, "message": "ليس لديك صلاحية"})
    
    conn.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "تم تحديث حالة الطلب"})

# ==================== API Routes ====================

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    email_or_phone = data.get("emailOrPhone")
    password = data.get("password")
    
    conn = get_db()
    
    user = conn.execute(
        "SELECT * FROM users WHERE email = ? OR phone = ?", 
        (email_or_phone, email_or_phone)
    ).fetchone()
    
    if not user:
        conn.close()
        return jsonify({"success": False, "message": "البريد الإلكتروني أو رقم الهاتف غير مسجل"})
    
    if user["password"] != password:
        conn.close()
        return jsonify({"success": False, "message": "كلمة المرور غير صحيحة"})
    
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["user_role"] = user["role"]
    session["user_type"] = user["type"]
    session["company_name"] = user["company_name"]
    
    user_data = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "phone": user["phone"],
        "type": user["type"],
        "company_name": user["company_name"],
        "governorate": user["governorate"],
        "address": user["address"],
        "role": user["role"],
        "created_at": user["created_at"]
    }
    
    conn.close()
    return jsonify({
        "success": True, 
        "message": f"تم تسجيل الدخول بنجاح {user['name']}",
        "user": user_data
    })

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()
    
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    userType = data.get("userType", "individual")
    governorate = data.get("governorate")
    address = data.get("address")
    company_name = data.get("companyName") if userType == "company" else None
    
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"success": False, "message": "البريد الإلكتروني غير صالح"})
    
    if not re.match(r"^01[0125][0-9]{8}$", phone):
        return jsonify({"success": False, "message": "رقم الهاتف غير صالح"})
    
    conn = get_db()
    
    existing = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"success": False, "message": "البريد الإلكتروني مسجل بالفعل"})
    
    existing = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"success": False, "message": "رقم الهاتف مسجل بالفعل"})
    
    try:
        now = datetime.now().strftime("%Y-%m-%d")
        
        if userType == "company":
            role = "company"
        else:
            role = "customer"
        
        conn.execute("""
            INSERT INTO users 
            (name, email, phone, password, type, company_name, governorate, address, role, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, phone, password, userType, company_name, governorate, address, role, now))
        
        conn.commit()
        
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_role"] = user["role"]
        session["user_type"] = user["type"]
        session["company_name"] = user["company_name"]
        
        conn.close()
        
        return jsonify({
            "success": True, 
            "message": "تم إنشاء الحساب بنجاح",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "phone": user["phone"],
                "type": user["type"],
                "company_name": user["company_name"],
                "role": user["role"]
            }
        })
        
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "message": f"حدث خطأ: {str(e)}"})

@app.route("/api/user-data", methods=["GET"])
def api_user_data():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "غير مصرح"})
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
    
    if not user:
        return jsonify({"success": False, "message": "المستخدم غير موجود"})
    
    return jsonify({
        "success": True,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "phone": user["phone"],
            "type": user["type"],
            "company_name": user["company_name"],
            "governorate": user["governorate"],
            "address": user["address"],
            "role": user["role"],
            "created_at": user["created_at"]
        }
    })

@app.route("/api/update-password", methods=["POST"])
def api_update_password():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "غير مصرح"})
    
    data = request.get_json()
    user_id = data.get("userId")
    new_password = data.get("newPassword")
    
    if int(user_id) != session["user_id"]:
        return jsonify({"success": False, "message": "غير مصرح"})
    
    conn = get_db()
    
    try:
        conn.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (new_password, user_id)
        )
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": "تم تحديث كلمة المرور بنجاح"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"حدث خطأ: {str(e)}"
        })
    finally:
        conn.close()

@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"success": True, "message": "تم تسجيل الخروج بنجاح"})

# ==================== Products API ====================

@app.route("/api/products", methods=["GET"])
def api_get_products():
    """API لجلب جميع المنتجات المتاحة"""
    conn = get_db()
    
    # جلب المنتجات المتاحة فقط
    products = conn.execute("""
        SELECT p.*, u.name as company_name 
        FROM products p
        LEFT JOIN users u ON p.company_id = u.id
        WHERE p.available = 1
        ORDER BY p.created_at DESC
    """).fetchall()
    
    conn.close()
    
    products_list = []
    for p in products:
        product_dict = dict(p)
        # تحويل features من JSON إلى list
        if product_dict["features"]:
            try:
                product_dict["features"] = json.loads(product_dict["features"])
            except:
                product_dict["features"] = []
        else:
            product_dict["features"] = []
        products_list.append(product_dict)
    
    return jsonify({"success": True, "products": products_list})

@app.route("/api/company/products", methods=["GET"])
def api_get_company_products():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "غير مصرح"})
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    
    if user["role"] == "admin":
        products = conn.execute("SELECT * FROM products ORDER BY created_at DESC").fetchall()
    elif user["role"] == "company":
        products = conn.execute("SELECT * FROM products WHERE company_id = ? ORDER BY created_at DESC", (user["id"],)).fetchall()
    else:
        conn.close()
        return jsonify({"success": False, "message": "ليس لديك صلاحية"})
    
    conn.close()
    
    products_list = []
    for p in products:
        product_dict = dict(p)
        if product_dict["features"]:
            try:
                product_dict["features"] = json.loads(product_dict["features"])
            except:
                product_dict["features"] = []
        products_list.append(product_dict)
    
    return jsonify({"success": True, "products": products_list})

@app.route("/api/company/products", methods=["POST"])
def api_create_company_product():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "غير مصرح"})
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    
    if user["role"] not in ["company", "admin"]:
        conn.close()
        return jsonify({"success": False, "message": "ليس لديك صلاحية"})
    
    data = request.get_json()
    print("Received product data:", data)
    
    # التحقق من البيانات المطلوبة
    required_fields = ["name", "description", "price", "minQuantity", "category"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"success": False, "message": f"الحقل {field} مطلوب"})
    
    features_json = json.dumps(data.get("features", []))
    
    # تحديد company_id و company_name
    if user["role"] == "company":
        company_id = user["id"]
        company_name = user["company_name"] or user["name"]
    else:
        company_id = data.get("company_id", user["id"])
        company_name = data.get("company_name", user["name"])
    
    # معالجة رابط الصورة - التأكد من حفظه كما هو
    image_url = data.get("image", "")
    
    try:
        conn.execute("""
            INSERT INTO products (name, description, price, min_quantity, unit, category, image, features, company_id, company_name, created_by, available)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("name"),
            data.get("description"),
            data.get("price"),
            data.get("minQuantity", 1),
            data.get("unit", "كجم"),
            data.get("category"),
            image_url,
            features_json,
            company_id,
            company_name,
            session["user_id"],
            data.get("available", 1)
        ))
        
        conn.commit()
        
        # جلب المنتج المضاف
        product_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        new_product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        
        conn.close()
        
        return jsonify({
            "success": True, 
            "message": "تم إضافة المنتج بنجاح",
            "product": dict(new_product)
        })
        
    except Exception as e:
        conn.close()
        print("Error creating product:", str(e))
        return jsonify({"success": False, "message": f"حدث خطأ: {str(e)}"})

@app.route("/api/company/products/<int:product_id>", methods=["PUT", "DELETE"])
def api_manage_company_product(product_id):
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "غير مصرح"})
    
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    
    if not product:
        conn.close()
        return jsonify({"success": False, "message": "المنتج غير موجود"})
    
    print(f"User role: {user['role']}, User ID: {user['id']}, Product company_id: {product['company_id']}")
    
    # التحقق من الصلاحية
    has_permission = False
    if user["role"] == "admin":
        has_permission = True
    elif user["role"] == "company" and product["company_id"] == user["id"]:
        has_permission = True
    
    if not has_permission:
        conn.close()
        return jsonify({"success": False, "message": f"ليس لديك صلاحية لتعديل هذا المنتج. أنت {user['role']} مع ID {user['id']} والمنتج مملوك لشركة ID {product['company_id']}"})
    
    if request.method == "DELETE":
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "تم حذف المنتج بنجاح"})
    
    else:  # PUT
        data = request.get_json()
        print("Updating product with data:", data)
        
        features_json = json.dumps(data.get("features", []))
        
        # معالجة رابط الصورة - الحفاظ على القيمة المدخلة
        image_url = data.get("image", "")
        
        try:
            conn.execute("""
                UPDATE products 
                SET name = ?, description = ?, price = ?, min_quantity = ?, 
                    unit = ?, category = ?, image = ?, features = ?, available = ?
                WHERE id = ?
            """, (
                data.get("name"),
                data.get("description"),
                data.get("price"),
                data.get("minQuantity"),
                data.get("unit", "كجم"),
                data.get("category"),
                image_url,
                features_json,
                data.get("available", 1),
                product_id
            ))
            
            conn.commit()
            
            # جلب المنتج بعد التحديث
            updated_product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
            
            conn.close()
            return jsonify({
                "success": True, 
                "message": "تم تحديث المنتج بنجاح",
                "product": dict(updated_product)
            })
            
        except Exception as e:
            conn.close()
            print("Error updating product:", str(e))
            return jsonify({"success": False, "message": f"حدث خطأ: {str(e)}"})

# ==================== Orders API ====================

@app.route("/api/orders", methods=["GET", "POST"])
def api_orders():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "غير مصرح"})
    
    if request.method == "GET":
        conn = get_db()
        
        user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
        
        if user["role"] == "admin":
            orders = conn.execute("""
                SELECT o.*, u.name as user_name, u.phone, u.type
                FROM orders o 
                JOIN users u ON o.user_id = u.id 
                ORDER BY o.created_at DESC
            """).fetchall()
        elif user["role"] == "company":
            orders = conn.execute("""
                SELECT o.*, u.name as user_name, u.phone 
                FROM orders o 
                JOIN users u ON o.user_id = u.id 
                ORDER BY o.created_at DESC
            """).fetchall()
        else:
            orders = conn.execute(
                "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", 
                (session["user_id"],)
            ).fetchall()
        
        conn.close()
        
        orders_list = []
        for o in orders:
            order_dict = dict(o)
            if order_dict["products"]:
                try:
                    order_dict["products"] = json.loads(order_dict["products"])
                except:
                    order_dict["products"] = []
            orders_list.append(order_dict)
        
        return jsonify({"success": True, "orders": orders_list})
    
    elif request.method == "POST":
        data = request.get_json()
        print("Received order data:", data)
        
        order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        products_json = json.dumps(data.get("products", []))
        
        conn = get_db()
        try:
            conn.execute("""
                INSERT INTO orders 
                (order_number, user_id, products, quantity, subtotal, delivery_fee, total, 
                 delivery_date, delivery_time, notes, payment_method, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_number,
                session["user_id"],
                products_json,
                data.get("quantity", 0),
                data.get("subtotal", 0),
                data.get("delivery_fee", 0),
                data.get("total", 0),
                data.get("delivery_date"),
                data.get("delivery_time"),
                data.get("notes", ""),
                data.get("payment_method", "cash_on_delivery"),
                "قيد المراجعة"
            ))
            conn.commit()
            
            order_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            conn.close()
            
            return jsonify({
                "success": True, 
                "message": "تم إنشاء الطلب بنجاح",
                "order_id": order_id,
                "order_number": order_number
            })
        except Exception as e:
            conn.close()
            print("Error creating order:", str(e))
            return jsonify({"success": False, "message": f"حدث خطأ: {str(e)}"})

@app.route("/api/forgot-password", methods=["POST"])
def api_forgot_password():
    data = request.get_json()
    email_or_phone = data.get("emailOrPhone")
    
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ? OR phone = ?", 
        (email_or_phone, email_or_phone)
    ).fetchone()
    conn.close()
    
    if user:
        return jsonify({
            "success": True, 
            "message": "تم إرسال رابط استعادة كلمة المرور إلى بريدك الإلكتروني"
        })
    else:
        return jsonify({
            "success": False, 
            "message": "لم يتم العثور على حساب مرتبط بهذا البريد الإلكتروني أو رقم الهاتف"
        })

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)