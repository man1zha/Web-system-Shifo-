import sqlite3, os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

DB_PATH    = os.path.join(os.path.dirname(__file__), 'database.db')
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def create_svg(filename, color, text):
    svg = '''<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%%" stop-color="{c}" stop-opacity="0.3"/>
    <stop offset="100%%" stop-color="{c}" stop-opacity="0.08"/>
  </linearGradient></defs>
  <rect width="300" height="300" fill="url(#g)" rx="16"/>
  <rect x="60" y="70" width="180" height="130" rx="16" fill="white" opacity="0.9"/>
  <circle cx="150" cy="110" r="30" fill="{c}" opacity="0.15"/>
  <rect x="120" y="95" width="60" height="8" rx="4" fill="{c}" opacity="0.5"/>
  <rect x="130" y="110" width="40" height="6" rx="3" fill="{c}" opacity="0.3"/>
  <rect x="125" y="123" width="50" height="6" rx="3" fill="{c}" opacity="0.3"/>
  <rect x="75" y="160" width="150" height="3" rx="2" fill="{c}" opacity="0.2"/>
  <text x="150" y="185" font-family="Arial,sans-serif" font-size="12" font-weight="600"
        text-anchor="middle" fill="#1C2B4B" opacity="0.8">{t}</text>
</svg>'''.format(c=color, t=text[:24])
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    return filename

now = datetime.now()

PRODUCTS = [
    {'name_ru':'Парацетамол 500мг','name_tj':'Парасетамол 500мг',
     'desc_ru':'Обезболивающее и жаропонижающее. Устраняет головную боль, зубную боль, боли при простуде. Действующее вещество: парацетамол 500 мг. Таблетки, 10 шт.',
     'desc_tj':'Доруи зидди дард ва таббурандаи ҳарорат. Таблеткаҳо, 10 дона.',
     'price':8.50,'stock':150,'cat_ru':'Обезболивающие','cat_tj':'Доруи зидди дард',
     'img':'paracetamol.svg','color':'#1A73E8','rx':0,
     'expiry':(now+timedelta(days=400)).strftime('%Y-%m-%d')},
    {'name_ru':'Амоксициллин 500мг','name_tj':'Амоксисиллин 500мг',
     'desc_ru':'Антибиотик широкого спектра. Капсулы, 20 шт. Только по рецепту врача.',
     'desc_tj':'Антибиотики васеъамал. Капсулаҳо, 20 дона. Танҳо бо нусхаи духтур.',
     'price':45.00,'stock':60,'cat_ru':'Антибиотики','cat_tj':'Антибиотикҳо',
     'img':'amoxicillin.svg','color':'#E53935','rx':1,
     'expiry':(now+timedelta(days=25)).strftime('%Y-%m-%d')},
    {'name_ru':'Витамин C 1000мг','name_tj':'Витамин С 1000мг',
     'desc_ru':'Аскорбиновая кислота — антиоксидант. Шипучие таблетки, 30 шт.',
     'desc_tj':'Кислотаи аскорбинӣ. Таблеткаҳои ҷӯшон, 30 дона.',
     'price':25.00,'stock':200,'cat_ru':'Витамины','cat_tj':'Витаминҳо',
     'img':'vitamin_c.svg','color':'#FF6F00','rx':0,
     'expiry':(now+timedelta(days=550)).strftime('%Y-%m-%d')},
    {'name_ru':'Но-шпа 40мг','name_tj':'Но-шпа 40мг',
     'desc_ru':'Спазмолитик на основе дротаверина. Таблетки, 100 шт.',
     'desc_tj':'Зидди спазм. Таблеткаҳо, 100 дона.',
     'price':32.00,'stock':90,'cat_ru':'Спазмолитики','cat_tj':'Зидди спазм',
     'img':'noshpa.svg','color':'#2E7D32','rx':0,
     'expiry':(now+timedelta(days=75)).strftime('%Y-%m-%d')},
    {'name_ru':'Лоратадин 10мг','name_tj':'Лоратадин 10мг',
     'desc_ru':'Антигистаминный препарат 2-го поколения. Таблетки, 10 шт.',
     'desc_tj':'Доруи антигистаминии насли дуввум. Таблеткаҳо, 10 дона.',
     'price':18.00,'stock':75,'cat_ru':'Аллергия','cat_tj':'Аллергия',
     'img':'loratadin.svg','color':'#7B1FA2','rx':0,
     'expiry':(now+timedelta(days=160)).strftime('%Y-%m-%d')},
    {'name_ru':'Омепразол 20мг','name_tj':'Омепразол 20мг',
     'desc_ru':'Ингибитор протонной помпы. Капсулы, 30 шт. Принимать до еды.',
     'desc_tj':'Ингибитори помпаи протон. Капсулаҳо, 30 дона.',
     'price':38.00,'stock':50,'cat_ru':'Желудок','cat_tj':'Меъда',
     'img':'omeprazol.svg','color':'#0097A7','rx':0,
     'expiry':(now+timedelta(days=300)).strftime('%Y-%m-%d')},
    {'name_ru':'Валидол','name_tj':'Валидол',
     'desc_ru':'Седативное средство. Таблетки подъязычные, 10 шт.',
     'desc_tj':'Доруи таскинбахш. Таблеткаҳои зеризабонӣ, 10 дона.',
     'price':6.00,'stock':180,'cat_ru':'Сердце и сосуды','cat_tj':'Дил ва рагҳо',
     'img':'validol.svg','color':'#E53935','rx':0,
     'expiry':(now+timedelta(days=15)).strftime('%Y-%m-%d')},
    {'name_ru':'Complivit Мультивитамины','name_tj':'Complivit Мултивитаминҳо',
     'desc_ru':'Комплекс 11 витаминов и 8 минералов. Таблетки, 60 шт.',
     'desc_tj':'Маҷмӯи 11 витамин ва 8 минерал. Таблеткаҳо, 60 дона.',
     'price':55.00,'stock':100,'cat_ru':'Витамины','cat_tj':'Витаминҳо',
     'img':'complivit.svg','color':'#FF6F00','rx':0,
     'expiry':(now+timedelta(days=480)).strftime('%Y-%m-%d')},
    {'name_ru':'Ибупрофен 400мг','name_tj':'Ибупрофен 400мг',
     'desc_ru':'НПВС — снимает боль и температуру. Таблетки, 20 шт.',
     'desc_tj':'Доруи зидди илтиҳоб. Таблеткаҳо, 20 дона.',
     'price':14.00,'stock':120,'cat_ru':'Обезболивающие','cat_tj':'Доруи зидди дард',
     'img':'ibuprofen.svg','color':'#1A73E8','rx':0,
     'expiry':(now+timedelta(days=200)).strftime('%Y-%m-%d')},
    {'name_ru':'Активированный уголь','name_tj':'Ангишти фаъол',
     'desc_ru':'Сорбент. При отравлениях. Таблетки, 50 шт.',
     'desc_tj':'Сорбенти табиӣ. Таблеткаҳо, 50 дона.',
     'price':4.50,'stock':250,'cat_ru':'Желудок','cat_tj':'Меъда',
     'img':'ugol.svg','color':'#424242','rx':0,
     'expiry':(now+timedelta(days=700)).strftime('%Y-%m-%d')},
    {'name_ru':'Цитрамон П','name_tj':'Ситрамон П',
     'desc_ru':'Анальгетик: аспирин + парацетамол + кофеин. Таблетки, 10 шт.',
     'desc_tj':'Анальгетики якҷоя. Таблеткаҳо, 10 дона.',
     'price':7.00,'stock':160,'cat_ru':'Обезболивающие','cat_tj':'Доруи зидди дард',
     'img':'citramon.svg','color':'#FF6F00','rx':0,
     'expiry':(now+timedelta(days=50)).strftime('%Y-%m-%d')},
    {'name_ru':'Супрастин 25мг','name_tj':'Супрастин 25мг',
     'desc_ru':'Антигистаминный препарат 1-го поколения. Таблетки, 20 шт.',
     'desc_tj':'Доруи антигистаминии насли аввал. Таблеткаҳо, 20 дона.',
     'price':22.00,'stock':85,'cat_ru':'Аллергия','cat_tj':'Аллергия',
     'img':'suprastin.svg','color':'#7B1FA2','rx':0,
     'expiry':(now+timedelta(days=120)).strftime('%Y-%m-%d')},
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
        phone TEXT, address TEXT, is_admin INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name_ru TEXT NOT NULL, name_tj TEXT,
        description_ru TEXT, description_tj TEXT,
        price REAL NOT NULL, stock INTEGER DEFAULT 0,
        category_ru TEXT, category_tj TEXT,
        image TEXT,
        requires_prescription INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        expiry_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL, total_price REAL NOT NULL,
        status TEXT DEFAULT 'new', address TEXT, phone TEXT, comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL, product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL, price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL, product_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id))''')

    # Добавляем колонку image если её нет
    existing = [row[1] for row in c.execute('PRAGMA table_info(products)').fetchall()]
    if 'image' not in existing:
        c.execute('ALTER TABLE products ADD COLUMN image TEXT')
        print('Колонка image добавлена!')
    if 'expiry_date' not in existing:
        c.execute('ALTER TABLE products ADD COLUMN expiry_date DATE')
        print('Колонка expiry_date добавлена!')

    c.execute('DELETE FROM products')
    for p in PRODUCTS:
        img = create_svg(p['img'], p['color'], p['name_ru'])
        c.execute('''INSERT INTO products
            (name_ru,name_tj,description_ru,description_tj,price,stock,
             category_ru,category_tj,image,requires_prescription,expiry_date)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
            (p['name_ru'],p['name_tj'],p['desc_ru'],p['desc_tj'],
             p['price'],p['stock'],p['cat_ru'],p['cat_tj'],
             img,p['rx'],p['expiry']))

    print(str(len(PRODUCTS)) + ' товаров добавлено!')

    c.execute('SELECT COUNT(*) FROM users WHERE is_admin=1')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO users (name,email,password,is_admin) VALUES (?,?,?,?)',
            ('Администратор','admin@apteka.tj',generate_password_hash('admin123'),1))
        print('Администратор создан: admin@apteka.tj / admin123')

    conn.commit()
    conn.close()
    print('База данных готова!')

if __name__ == '__main__':
    init_db()
