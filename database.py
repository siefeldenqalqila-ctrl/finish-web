import sqlite3
import os
import json

def init_database():
    """إنشاء قاعدة البيانات والجداول"""

    # حذف قاعدة البيانات القديمة إذا وجدت (اختياري)
    if os.path.exists("paper.db"):
        print("⚠️  قاعدة البيانات موجودة بالفعل")
        response = input("هل تريد إنشاء قاعدة بيانات جديدة؟ (y/n): ")
        if response.lower() == 'y':
            os.remove("paper.db")
            print("🗑️  تم حذف قاعدة البيانات القديمة")
        else:
            print("✅ استخدام قاعدة البيانات الموجودة")
            return

    conn = sqlite3.connect("paper.db")
    cur = conn.cursor()

    # جدول المستخدمين
    cur.execute('''
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

    # جدول الطلبات
    cur.execute('''
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

    # جدول المنتجات 🔥 الجديد
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL,
            minQuantity INTEGER,
            unit TEXT,
            category TEXT,
            image TEXT,
            features TEXT,
            available INTEGER DEFAULT 1,
            company_id INTEGER,
            company_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES users(id)
        )
    ''')

    print("👤 جاري إضافة مستخدمين تجريبيين...")

    # مستخدم عادي
    cur.execute("SELECT * FROM users WHERE email=?", ("user@example.com",))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO users
            (name,email,phone,password,type,governorate,address,role)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            "أحمد محمد",
            "user@example.com",
            "01234567890",
            "123456",
            "individual",
            "القاهرة",
            "مدينة نصر",
            "customer"
        ))

    # مستخدم شركة
    cur.execute("SELECT * FROM users WHERE email=?", ("company@example.com",))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO users
            (name,email,phone,password,type,company_name,governorate,address,role)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            "شركة التدوير",
            "company@example.com",
            "01234567891",
            "123456",
            "company",
            "شركة إعادة التدوير",
            "الجيزة",
            "المنطقة الصناعية",
            "company_admin"
        ))

    # مشرف
    cur.execute("SELECT * FROM users WHERE email=?", ("admin@example.com",))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO users
            (name,email,phone,password,type,governorate,address,role)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            "مدير النظام",
            "admin@example.com",
            "01234567892",
            "123456",
            "individual",
            "الإسكندرية",
            "شارع البحر",
            "admin"
        ))

    print("📦 جاري إضافة منتجات تجريبية...")

    company = cur.execute(
        "SELECT id FROM users WHERE email=?",
        ("company@example.com",)
    ).fetchone()

    if company:

        company_id = company[0]

        products = [

            (
                "Testliner",
                "طبقة خارجية للكرتون المضلع",
                7.5,
                10,
                "كجم",
                "Liner Paper",
                "/static/images/testliner.jpeg",
                json.dumps(["120–200 GSM", "قوة ضغط متوسطة"]),
                1,
                company_id,
                "شركة إعادة التدوير"
            ),

            (
                "Fluting Paper",
                "طبقة مموجة داخل الكرتون",
                6.8,
                10,
                "كجم",
                "Fluting",
                "/static/images/fluting.jpeg",
                json.dumps(["مرونة عالية"]),
                1,
                company_id,
                "شركة إعادة التدوير"
            ),

            (
                "Kraft Paper",
                "ورق أكياس قوي",
                8.2,
                8,
                "كجم",
                "Kraft Paper",
                "/static/images/kraft.jpeg",
                json.dumps(["قوة شد عالية"]),
                1,
                company_id,
                "شركة إعادة التدوير"
            )

        ]

        cur.executemany("""
            INSERT INTO products
            (name,description,price,minQuantity,unit,category,image,features,available,company_id,company_name)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, products)

        print("✅ تم إضافة منتجات تجريبية")

    conn.commit()
    conn.close()

    print("\n✅ قاعدة البيانات أصبحت جاهزة بالكامل")

if __name__ == "__main__":
    init_database()