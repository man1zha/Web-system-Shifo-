from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
import os
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

TRANSLATIONS = {
    'ru': {
        'lang': 'ru', 'lang_name': 'RU',
        'home': 'Главная', 'products': 'Лекарства',
        'favorites': 'Избранное', 'cart': 'Корзина',
        'profile': 'Профиль', 'login': 'Войти',
        'register': 'Регистрация', 'logout': 'Выйти',
        'search_placeholder': 'Поиск лекарств...',
        'add_to_cart': 'В корзину',
        'in_stock': 'В наличии', 'out_of_stock': 'Нет в наличии',
        'prescription': 'Рецепт', 'som': 'сом',
        'categories': 'Категории', 'new_arrivals': 'Новые поступления',
        'view_all': 'Смотреть все',
        'pharmacy_name': 'Аптека Шифо',
        'hero_title': 'Ваше здоровье — наша забота',
        'hero_desc': 'Заказывайте лекарства онлайн с доставкой по Душанбе.',
        'btn_catalog': 'Смотреть лекарства', 'btn_how': 'Как это работает?',
        'fast_delivery': 'Быстрая доставка', 'fast_delivery_desc': 'Доставим за 2-3 часа',
        'original': 'Оригинальные лекарства', 'original_desc': 'Только сертифицированные',
        'prices': 'Выгодные цены', 'prices_desc': 'Ниже чем в обычных аптеках',
        'consult': 'Консультация', 'consult_desc': 'Фармацевт ответит бесплатно',
        'how_works': 'Как это работает?',
        'step1_title': 'Найдите лекарство', 'step1_desc': 'Поиск или выбор категории',
        'step2_title': 'Добавьте в корзину', 'step2_desc': 'Выберите количество',
        'step3_title': 'Оформите заказ', 'step3_desc': 'Укажите адрес доставки',
        'step4_title': 'Получите заказ', 'step4_desc': 'Доставка 2-3 часа',
        'order_title': 'Оформление заказа', 'order_btn': 'Подтвердить заказ',
        'your_name': 'Ваше имя', 'your_phone': 'Номер телефона',
        'your_address': 'Адрес доставки', 'comment': 'Комментарий',
        'total': 'Итого', 'filter': 'Применить фильтр',
        'reset': 'Сбросить фильтры', 'all_categories': 'Все категории',
        'cart_empty': 'Корзина пуста', 'cart_empty_desc': 'Добавьте лекарства из каталога',
        'go_to_products': 'Перейти к товарам', 'checkout': 'Оформить заказ',
        'order_success': 'Заказ оформлен!', 'my_orders': 'Мои заказы',
        'no_orders': 'Заказов пока нет',
        'status_new': 'Новый', 'status_processing': 'В обработке',
        'status_delivered': 'Доставлен', 'status_cancelled': 'Отменён',
        'address': 'г. Душанбе, ул. Рудаки 12',
        'phone': '+992 37 123-45-67', 'hours': 'Пн–Вс: 8:00 – 22:00',
        'registered': 'Уже есть аккаунт?', 'not_registered': 'Нет аккаунта?',
        'password': 'Пароль', 'confirm_password': 'Повторите пароль', 'email': 'Email',
        'cat_pain': 'Обезболивающие', 'cat_vitamins': 'Витамины',
        'cat_antibiotics': 'Антибиотики', 'cat_allergy': 'Аллергия',
        'cat_stomach': 'Желудок', 'cat_heart': 'Сердце и сосуды',
    },
    'tj': {
        'lang': 'tj', 'lang_name': 'TJ',
        'home': 'Асосӣ', 'products': 'Доруҳо',
        'favorites': 'Интихобиҳо', 'cart': 'Сабад',
        'profile': 'Профил', 'login': 'Ворид шав',
        'register': 'Сабт шав', 'logout': 'Баромад',
        'search_placeholder': 'Ҷустуҷӯи дору...',
        'add_to_cart': 'Ба сабад',
        'in_stock': 'Мавҷуд аст', 'out_of_stock': 'Мавҷуд нест',
        'prescription': 'Нусха', 'som': 'сомонӣ',
        'categories': 'Категорияҳо', 'new_arrivals': 'Воридоти нав',
        'view_all': 'Ҳама',
        'pharmacy_name': 'Дорухонаи Шифо',
        'hero_title': 'Саломатии шумо — ғамхории мост',
        'hero_desc': 'Доруҳоро тавассути интернет фармоиш диҳед.',
        'btn_catalog': 'Дидани доруҳо', 'btn_how': 'Чӣ тавр кор мекунад?',
        'fast_delivery': 'Расонидани зуд', 'fast_delivery_desc': 'Дар 2-3 соат',
        'original': 'Доруҳои аслӣ', 'original_desc': 'Танҳо сертификатшуда',
        'prices': 'Нархҳои дастрас', 'prices_desc': 'Аз дорухонаҳои маъмулӣ камтар',
        'consult': 'Машварат', 'consult_desc': 'Фармасевт ройгон ҷавоб медиҳад',
        'how_works': 'Чӣ тавр кор мекунад?',
        'step1_title': 'Дору ёбед', 'step1_desc': 'Ҷустуҷӯ ё категория',
        'step2_title': 'Ба сабад илова кунед', 'step2_desc': 'Миқдорро интихоб кунед',
        'step3_title': 'Фармоиш диҳед', 'step3_desc': 'Суроғаро нишон диҳед',
        'step4_title': 'Фармоишро гиред', 'step4_desc': 'Расонидан 2-3 соат',
        'order_title': 'Расмикунонии фармоиш', 'order_btn': 'Тасдиқи фармоиш',
        'your_name': 'Номи шумо', 'your_phone': 'Рақами телефон',
        'your_address': 'Суроғаи расонидан', 'comment': 'Шарҳ',
        'total': 'Ҳамагӣ', 'filter': 'Истифодаи филтр',
        'reset': 'Нест кардан', 'all_categories': 'Ҳамаи категорияҳо',
        'cart_empty': 'Сабад холӣ аст', 'cart_empty_desc': 'Аз каталог дору илова кунед',
        'go_to_products': 'Рафтан ба молҳо', 'checkout': 'Расмикунонӣ',
        'order_success': 'Фармоиш расмӣ шуд!', 'my_orders': 'Фармоишҳои ман',
        'no_orders': 'Ҳанӯз фармоише нест',
        'status_new': 'Нав', 'status_processing': 'Дар коркард',
        'status_delivered': 'Расонида шуд', 'status_cancelled': 'Бекор карда шуд',
        'address': 'Душанбе, кӯч. Рӯдакӣ 12',
        'phone': '+992 37 123-45-67', 'hours': 'Дш–Як: 8:00 – 22:00',
        'registered': 'Аллакай ҳисоб дорӣ?', 'not_registered': 'Ҳисоб надорӣ?',
        'password': 'Парол', 'confirm_password': 'Паролро такрор кун',
        'email': 'Почтаи электронӣ',
        'cat_pain': 'Дардвасозон', 'cat_vitamins': 'Витаминҳо',
        'cat_antibiotics': 'Антибиотикҳо', 'cat_allergy': 'Аллергия',
        'cat_stomach': 'Меъда', 'cat_heart': 'Дил ва рагҳо',
    },
    'en': {
        'lang': 'en', 'lang_name': 'EN',
        'home': 'Home', 'products': 'Medicines',
        'favorites': 'Favorites', 'cart': 'Cart',
        'profile': 'Profile', 'login': 'Login',
        'register': 'Register', 'logout': 'Logout',
        'search_placeholder': 'Search medicines...',
        'add_to_cart': 'Add to Cart',
        'in_stock': 'In Stock', 'out_of_stock': 'Out of Stock',
        'prescription': 'Rx', 'som': 'som',
        'categories': 'Categories', 'new_arrivals': 'New Arrivals',
        'view_all': 'View all',
        'pharmacy_name': 'Shifo Pharmacy',
        'hero_title': 'Your Health — Our Care',
        'hero_desc': 'Order medicines online with delivery in Dushanbe.',
        'btn_catalog': 'Browse Medicines', 'btn_how': 'How it works?',
        'fast_delivery': 'Fast Delivery', 'fast_delivery_desc': 'Within 2-3 hours',
        'original': 'Original Medicines', 'original_desc': 'Only certified products',
        'prices': 'Best Prices', 'prices_desc': 'Lower than regular pharmacies',
        'consult': 'Consultation', 'consult_desc': 'Free pharmacist advice',
        'how_works': 'How it works?',
        'step1_title': 'Find Medicine', 'step1_desc': 'Search or browse categories',
        'step2_title': 'Add to Cart', 'step2_desc': 'Choose quantity',
        'step3_title': 'Place Order', 'step3_desc': 'Enter delivery address',
        'step4_title': 'Receive Order', 'step4_desc': 'Delivery in 2-3 hours',
        'order_title': 'Place Order', 'order_btn': 'Confirm Order',
        'your_name': 'Your Name', 'your_phone': 'Phone Number',
        'your_address': 'Delivery Address', 'comment': 'Comment',
        'total': 'Total', 'filter': 'Apply Filter',
        'reset': 'Clear Filters', 'all_categories': 'All Categories',
        'cart_empty': 'Cart is Empty', 'cart_empty_desc': 'Add medicines from catalog',
        'go_to_products': 'Go to Products', 'checkout': 'Checkout',
        'order_success': 'Order Placed!', 'my_orders': 'My Orders',
        'no_orders': 'No orders yet',
        'status_new': 'New', 'status_processing': 'Processing',
        'status_delivered': 'Delivered', 'status_cancelled': 'Cancelled',
        'address': 'Dushanbe, Rudaki St. 12',
        'phone': '+992 37 123-45-67', 'hours': 'Mon–Sun: 8:00 – 22:00',
        'registered': 'Already have an account?', 'not_registered': 'No account?',
        'password': 'Password', 'confirm_password': 'Confirm Password', 'email': 'Email',
        'cat_pain': 'Pain Relief', 'cat_vitamins': 'Vitamins',
        'cat_antibiotics': 'Antibiotics', 'cat_allergy': 'Allergy',
        'cat_stomach': 'Stomach', 'cat_heart': 'Heart & Vessels',
    }
}

def get_t():
    lang = session.get('lang', 'ru')
    return TRANSLATIONS.get(lang, TRANSLATIONS['ru'])

def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

@app.context_processor
def inject_globals():
    def get_expiry_count():
        try:
            db = get_db()
            count = db.execute("""
                SELECT COUNT(*) FROM products
                WHERE is_active = 1
                  AND expiry_date IS NOT NULL
                  AND expiry_date != ''
                  AND date(expiry_date) <= date('now', '+30 days')
                  AND date(expiry_date) >= date('now')
            """).fetchone()[0]
            db.close()
            return count
        except Exception:
            return 0
    return dict(get_expiry_count=get_expiry_count, t=get_t())

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Доступ только для администратора!', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            flash('Войдите в аккаунт!', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ── Язык ─────────────────────────────────────────────────
@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in TRANSLATIONS:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

# ── Главная ───────────────────────────────────────────────
@app.route('/')
def index():
    t = get_t()
    db = get_db()
    products = db.execute(
        'SELECT * FROM products WHERE is_active = 1 ORDER BY created_at DESC LIMIT 8'
    ).fetchall()
    db.close()
    return render_template('index.html', products=products, t=t)

# ── Каталог ───────────────────────────────────────────────
@app.route('/products')
def products():
    t = get_t()
    lang = session.get('lang', 'ru')
    db = get_db()
    search   = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    name_field = 'name_ru' if lang != 'tj' else 'name_tj'
    cat_field  = 'category_ru' if lang != 'tj' else 'category_tj'
    desc_field = 'description_ru' if lang != 'tj' else 'description_tj'
    if search and category:
        items = db.execute(
            'SELECT * FROM products WHERE is_active=1 AND ' + name_field + ' LIKE ? AND ' + cat_field + '=? ORDER BY ' + name_field,
            ('%' + search + '%', category)
        ).fetchall()
    elif search:
        items = db.execute(
            'SELECT * FROM products WHERE is_active=1 AND (' + name_field + ' LIKE ? OR ' + desc_field + ' LIKE ?) ORDER BY ' + name_field,
            ('%' + search + '%', '%' + search + '%')
        ).fetchall()
    elif category:
        items = db.execute(
            'SELECT * FROM products WHERE is_active=1 AND ' + cat_field + '=? ORDER BY ' + name_field,
            (category,)
        ).fetchall()
    else:
        items = db.execute(
            'SELECT * FROM products WHERE is_active=1 ORDER BY ' + name_field
        ).fetchall()
    categories = db.execute(
        'SELECT DISTINCT ' + cat_field + ' as category FROM products WHERE is_active=1 AND ' + cat_field + ' IS NOT NULL AND ' + cat_field + ' != ""'
    ).fetchall()
    db.close()
    return render_template('products.html', products=items, categories=categories,
                           search=search, current_category=category, t=t)

@app.route('/search')
def search():
    q = request.args.get('q', '')
    return redirect(url_for('products', search=q))

# ── Авторизация ───────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    t = get_t()
    if request.method == 'POST':
        name      = request.form.get('name', '').strip()
        email     = request.form.get('email', '').strip()
        phone     = request.form.get('phone', '').strip()
        password  = request.form.get('password', '').strip()
        password2 = request.form.get('password2', '').strip()
        if not name or not email or not password:
            flash('Заполните все поля!', 'danger')
            return redirect(url_for('register'))
        if password != password2:
            flash('Пароли не совпадают!', 'danger')
            return redirect(url_for('register'))
        if len(password) < 6:
            flash('Пароль минимум 6 символов!', 'danger')
            return redirect(url_for('register'))
        db = get_db()
        if db.execute('SELECT id FROM users WHERE email=?', (email,)).fetchone():
            flash('Email уже занят!', 'danger')
            db.close()
            return redirect(url_for('register'))
        db.execute('INSERT INTO users (name, email, phone, password) VALUES (?,?,?,?)',
                   (name, email, phone, generate_password_hash(password)))
        db.commit()
        user = db.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
        db.close()
        session['user_id']   = user['id']
        session['user_name'] = user['name']
        session['is_admin']  = False
        flash('Добро пожаловать, ' + name + '!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', t=t)

@app.route('/login', methods=['GET', 'POST'])
def login():
    t = get_t()
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
        db.close()
        if user and check_password_hash(user['password'], password):
            session['user_id']   = user['id']
            session['user_name'] = user['name']
            session['is_admin']  = bool(user['is_admin'])
            flash('Добро пожаловать, ' + user['name'] + '!', 'success')
            return redirect(url_for('admin_index') if user['is_admin'] else url_for('index'))
        flash('Неверный email или пароль!', 'danger')
    return render_template('login.html', t=t)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    t = get_t()
    db = get_db()
    user   = db.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
    orders = db.execute('SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC', (session['user_id'],)).fetchall()
    db.close()
    return render_template('profile.html', user=user, orders=orders, t=t)

@app.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    t = get_t()
    db = get_db()
    order = db.execute('SELECT * FROM orders WHERE id=? AND user_id=?', (order_id, session['user_id'])).fetchone()
    if not order:
        flash('Заказ не найден!', 'danger')
        return redirect(url_for('profile'))
    items = db.execute(
        'SELECT oi.*, p.name_ru as product_name FROM order_items oi JOIN products p ON oi.product_id=p.id WHERE oi.order_id=?',
        (order_id,)
    ).fetchall()
    db.close()
    return render_template('order_detail.html', order=order, items=items, t=t)

@app.route('/favorites')
@login_required
def favorites():
    t = get_t()
    db = get_db()
    items = db.execute(
        'SELECT p.* FROM products p JOIN favorites f ON p.id=f.product_id WHERE f.user_id=?',
        (session['user_id'],)
    ).fetchall()
    db.close()
    return render_template('favorites.html', products=items, t=t)

@app.route('/favorites/toggle/<int:product_id>', methods=['POST'])
@login_required
def favorites_toggle(product_id):
    db = get_db()
    existing = db.execute('SELECT id FROM favorites WHERE user_id=? AND product_id=?',
                          (session['user_id'], product_id)).fetchone()
    if existing:
        db.execute('DELETE FROM favorites WHERE user_id=? AND product_id=?',
                   (session['user_id'], product_id))
        is_fav = False
    else:
        db.execute('INSERT INTO favorites (user_id, product_id) VALUES (?,?)',
                   (session['user_id'], product_id))
        is_fav = True
    db.commit()
    db.close()
    return jsonify({'success': True, 'is_favorite': is_fav})

# ── Корзина ───────────────────────────────────────────────
@app.route('/cart')
def cart():
    t = get_t()
    lang = session.get('lang', 'ru')
    cart_items = session.get('cart', {})
    products_in_cart = []
    total = 0
    if cart_items:
        db = get_db()
        for product_id, quantity in cart_items.items():
            product = db.execute('SELECT * FROM products WHERE id=?', (product_id,)).fetchone()
            if product:
                item_total = product['price'] * quantity
                total += item_total
                products_in_cart.append({'product': product, 'quantity': quantity, 'item_total': item_total, 'lang': lang})
        db.close()
    return render_template('cart.html', cart_items=products_in_cart, total=total, t=t)

@app.route('/cart/add/<int:product_id>', methods=['POST'])
def cart_add(product_id):
    cart = session.get('cart', {})
    key  = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    session['cart'] = cart
    session.modified = True
    return jsonify({'success': True, 'cart_count': sum(cart.values())})

@app.route('/cart/remove/<int:product_id>', methods=['POST'])
def cart_remove(product_id):
    cart = session.get('cart', {})
    cart.pop(str(product_id), None)
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/cart/update/<int:product_id>', methods=['POST'])
def cart_update(product_id):
    cart     = session.get('cart', {})
    key      = str(product_id)
    quantity = int(request.form.get('quantity', 1))
    if quantity <= 0:
        cart.pop(key, None)
    else:
        cart[key] = quantity
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('cart'))

# ── Заказ ─────────────────────────────────────────────────
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    t = get_t()
    lang = session.get('lang', 'ru')
    cart_items = session.get('cart', {})
    if not cart_items:
        flash('Корзина пуста!', 'danger')
        return redirect(url_for('cart'))
    db = get_db()
    if request.method == 'POST':
        name    = request.form.get('name', '').strip()
        phone   = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        comment = request.form.get('comment', '').strip()
        if not name or not phone or not address:
            flash('Заполните все обязательные поля!', 'danger')
            db.close()
            return redirect(url_for('checkout'))
        total = 0
        for product_id, quantity in cart_items.items():
            product = db.execute('SELECT * FROM products WHERE id=?', (product_id,)).fetchone()
            if product:
                total += product['price'] * quantity
        user_id = session.get('user_id', 1)
        cursor  = db.execute(
            'INSERT INTO orders (user_id, total_price, status, address, phone, comment) VALUES (?,?,?,?,?,?)',
            (user_id, total, 'new', address, phone, comment)
        )
        order_id = cursor.lastrowid
        for product_id, quantity in cart_items.items():
            product = db.execute('SELECT * FROM products WHERE id=?', (product_id,)).fetchone()
            if product:
                db.execute('INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?,?,?,?)',
                           (order_id, product_id, quantity, product['price']))
        db.commit()
        db.close()
        session.pop('cart', None)
        flash('Заказ №' + str(order_id) + ' оформлен!', 'success')
        return redirect(url_for('order_success', order_id=order_id))
    products_in_cart = []
    total = 0
    for product_id, quantity in cart_items.items():
        product = db.execute('SELECT * FROM products WHERE id=?', (product_id,)).fetchone()
        if product:
            item_total = product['price'] * quantity
            total += item_total
            products_in_cart.append({'product': product, 'quantity': quantity, 'item_total': item_total, 'lang': lang})
    db.close()
    return render_template('checkout.html', cart_items=products_in_cart, total=total, t=t)

@app.route('/order/success/<int:order_id>')
def order_success(order_id):
    t = get_t()
    return render_template('order_success.html', order_id=order_id, t=t)

# ── Админ: вход ───────────────────────────────────────────
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        db   = get_db()
        user = db.execute('SELECT * FROM users WHERE email=? AND is_admin=1', (email,)).fetchone()
        db.close()
        if user and check_password_hash(user['password'], password):
            session['user_id']    = user['id']
            session['is_admin']   = True
            session['admin_name'] = user['name']
            return redirect(url_for('admin_index'))
        flash('Неверный email или пароль!', 'danger')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

# ── Админ: главная ────────────────────────────────────────
@app.route('/admin')
@admin_required
def admin_index():
    db = get_db()
    total_products = db.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    total_orders   = db.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    new_orders     = db.execute("SELECT COUNT(*) FROM orders WHERE status='new'").fetchone()[0]
    total_users    = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    recent_orders  = db.execute('SELECT * FROM orders ORDER BY created_at DESC LIMIT 5').fetchall()
    db.close()
    return render_template('admin/index.html',
        total_products=total_products, total_orders=total_orders,
        new_orders=new_orders, total_users=total_users,
        recent_orders=recent_orders)

# ── Админ: товары ─────────────────────────────────────────
@app.route('/admin/products')
@admin_required
def admin_products():
    db = get_db()
    items = db.execute('SELECT * FROM products ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('admin/products.html', products=items)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_product_add():
    db = get_db()
    cats_ru = [r[0] for r in db.execute(
        "SELECT DISTINCT category_ru FROM products WHERE category_ru IS NOT NULL AND category_ru != '' ORDER BY category_ru"
    ).fetchall()]
    cats_tj = [r[0] for r in db.execute(
        "SELECT DISTINCT category_tj FROM products WHERE category_tj IS NOT NULL AND category_tj != '' ORDER BY category_tj"
    ).fetchall()]
    if request.method == 'POST':
        name_ru     = request.form.get('name_ru', '').strip()
        name_tj     = request.form.get('name_tj', '').strip()
        desc_ru     = request.form.get('description_ru', '').strip()
        desc_tj     = request.form.get('description_tj', '').strip()
        price       = request.form.get('price', '').strip()
        stock       = request.form.get('stock', '0').strip()
        expiry_date = request.form.get('expiry_date', '').strip() or None
        requires_rx = 1 if request.form.get('requires_prescription') else 0
        cat_ru_sel  = request.form.get('category_ru_select', '').strip()
        cat_ru_new  = request.form.get('category_ru_new', '').strip()
        cat_ru      = cat_ru_new if cat_ru_sel == '__new__' else cat_ru_sel
        cat_tj_sel  = request.form.get('category_tj_select', '').strip()
        cat_tj_new  = request.form.get('category_tj_new', '').strip()
        cat_tj      = cat_tj_new if cat_tj_sel == '__new__' else cat_tj_sel
        if not name_ru or not price:
            flash('Название и цена обязательны!', 'danger')
            db.close()
            return render_template('admin/product_form.html', product=None, action='add', cats_ru=cats_ru, cats_tj=cats_tj)
        try:
            price_val = float(price)
            stock_val = int(stock) if stock else 0
        except ValueError:
            flash('Цена и остаток должны быть числами!', 'danger')
            db.close()
            return render_template('admin/product_form.html', product=None, action='add', cats_ru=cats_ru, cats_tj=cats_tj)
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(upload_path)
                image_filename = filename
        db.execute(
            'INSERT INTO products (name_ru, name_tj, description_ru, description_tj, price, stock, category_ru, category_tj, requires_prescription, expiry_date, image) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
            (name_ru, name_tj, desc_ru, desc_tj, price_val, stock_val, cat_ru, cat_tj, requires_rx, expiry_date, image_filename)
        )
        db.commit()
        db.close()
        flash('Товар «' + name_ru + '» добавлен!', 'success')
        return redirect(url_for('admin_products'))
    db.close()
    return render_template('admin/product_form.html', product=None, action='add', cats_ru=cats_ru, cats_tj=cats_tj)

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_product_edit(product_id):
    db = get_db()
    product = db.execute('SELECT * FROM products WHERE id=?', (product_id,)).fetchone()
    if not product:
        flash('Товар не найден!', 'danger')
        db.close()
        return redirect(url_for('admin_products'))
    cats_ru = [r[0] for r in db.execute(
        "SELECT DISTINCT category_ru FROM products WHERE category_ru IS NOT NULL AND category_ru != '' ORDER BY category_ru"
    ).fetchall()]
    cats_tj = [r[0] for r in db.execute(
        "SELECT DISTINCT category_tj FROM products WHERE category_tj IS NOT NULL AND category_tj != '' ORDER BY category_tj"
    ).fetchall()]
    if request.method == 'POST':
        name_ru     = request.form.get('name_ru', '').strip()
        name_tj     = request.form.get('name_tj', '').strip()
        desc_ru     = request.form.get('description_ru', '').strip()
        desc_tj     = request.form.get('description_tj', '').strip()
        price       = request.form.get('price', '').strip()
        stock       = request.form.get('stock', '0').strip()
        expiry_date = request.form.get('expiry_date', '').strip() or None
        is_active   = 1 if request.form.get('is_active') else 0
        requires_rx = 1 if request.form.get('requires_prescription') else 0
        cat_ru_sel  = request.form.get('category_ru_select', '').strip()
        cat_ru_new  = request.form.get('category_ru_new', '').strip()
        cat_ru      = cat_ru_new if cat_ru_sel == '__new__' else cat_ru_sel
        cat_tj_sel  = request.form.get('category_tj_select', '').strip()
        cat_tj_new  = request.form.get('category_tj_new', '').strip()
        cat_tj      = cat_tj_new if cat_tj_sel == '__new__' else cat_tj_sel
        if not name_ru or not price:
            flash('Название и цена обязательны!', 'danger')
            db.close()
            return render_template('admin/product_form.html', product=product, action='edit', cats_ru=cats_ru, cats_tj=cats_tj)
        try:
            price_val = float(price)
            stock_val = int(stock) if stock else 0
        except ValueError:
            flash('Цена и остаток должны быть числами!', 'danger')
            db.close()
            return render_template('admin/product_form.html', product=product, action='edit', cats_ru=cats_ru, cats_tj=cats_tj)
        image_filename = product['image']
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(upload_path)
                image_filename = filename
        db.execute(
            'UPDATE products SET name_ru=?, name_tj=?, description_ru=?, description_tj=?, price=?, stock=?, category_ru=?, category_tj=?, is_active=?, requires_prescription=?, expiry_date=?, image=? WHERE id=?',
            (name_ru, name_tj, desc_ru, desc_tj, price_val, stock_val, cat_ru, cat_tj, is_active, requires_rx, expiry_date, image_filename, product_id)
        )
        db.commit()
        db.close()
        flash('Товар обновлён!', 'success')
        return redirect(url_for('admin_products'))
    db.close()
    return render_template('admin/product_form.html', product=product, action='edit', cats_ru=cats_ru, cats_tj=cats_tj)

@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def admin_product_delete(product_id):
    db = get_db()
    db.execute('DELETE FROM products WHERE id=?', (product_id,))
    db.commit()
    db.close()
    flash('Товар удалён!', 'success')
    return redirect(url_for('admin_products'))

# ── Админ: заказы ─────────────────────────────────────────
@app.route('/admin/orders')
@admin_required
def admin_orders():
    db = get_db()
    orders = db.execute('SELECT * FROM orders ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/orders/<int:order_id>')
@admin_required
def admin_order_detail(order_id):
    db = get_db()
    order = db.execute('SELECT * FROM orders WHERE id=?', (order_id,)).fetchone()
    if not order:
        flash('Заказ не найден!', 'danger')
        db.close()
        return redirect(url_for('admin_orders'))
    items = db.execute(
        'SELECT oi.*, p.name_ru as product_name FROM order_items oi JOIN products p ON oi.product_id=p.id WHERE oi.order_id=?',
        (order_id,)
    ).fetchall()
    db.close()
    return render_template('admin/order_detail.html', order=order, items=items)

@app.route('/admin/orders/status/<int:order_id>', methods=['POST'])
@admin_required
def admin_order_status(order_id):
    status = request.form.get('status')
    db = get_db()
    db.execute('UPDATE orders SET status=? WHERE id=?', (status, order_id))
    db.commit()
    db.close()
    flash('Статус обновлён!', 'success')
    return redirect(url_for('admin_order_detail', order_id=order_id))

# ── Сроки годности ────────────────────────────────────────
@app.route('/admin/expiry')
@admin_required
def admin_expiry():
    db = get_db()
    red = db.execute("""
        SELECT *, CAST(julianday(expiry_date) - julianday('now') AS INTEGER) as days_left
        FROM products WHERE is_active=1 AND expiry_date IS NOT NULL AND expiry_date != ''
        AND date(expiry_date) >= date('now') AND date(expiry_date) <= date('now', '+30 days')
        ORDER BY expiry_date ASC
    """).fetchall()
    orange = db.execute("""
        SELECT *, CAST(julianday(expiry_date) - julianday('now') AS INTEGER) as days_left
        FROM products WHERE is_active=1 AND expiry_date IS NOT NULL AND expiry_date != ''
        AND date(expiry_date) > date('now', '+30 days') AND date(expiry_date) <= date('now', '+90 days')
        ORDER BY expiry_date ASC
    """).fetchall()
    yellow = db.execute("""
        SELECT *, CAST(julianday(expiry_date) - julianday('now') AS INTEGER) as days_left
        FROM products WHERE is_active=1 AND expiry_date IS NOT NULL AND expiry_date != ''
        AND date(expiry_date) > date('now', '+90 days') AND date(expiry_date) <= date('now', '+180 days')
        ORDER BY expiry_date ASC
    """).fetchall()
    db.close()
    return render_template('admin/expiry.html', red=red, orange=orange, yellow=yellow)
@app.route('/admin/set_lang/<lang>')
@admin_required
def admin_set_lang(lang):
    if lang in ['ru', 'tj', 'en']:
        session['lang'] = lang
    referrer = request.referrer or ''
    if '/admin' in referrer:
        return redirect(referrer)
    return redirect(url_for('admin_index'))
if __name__ == '__main__':
    app.run(debug=True)
