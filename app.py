from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import sqlite3
import traceback
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_relojes_' + str(os.environ.get('PORT', 'default'))

if os.environ.get('VERCEL') == '1':
    DATABASE = '/tmp/tienda_relojes.db'
else:
    DATABASE = 'tienda_relojes.db'

if os.environ.get('VERCEL') == '1':
    UPLOAD_FOLDER = '/tmp/uploads'
else:
    UPLOAD_FOLDER = os.path.join('static', 'images')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/test')
def test():
    return f"OK - Port: {os.environ.get('PORT', 'none')}"

@app.route('/error')
def error_test():
    try:
        init_db()
        return "DB initialized OK"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/actualizar-fotos')
def actualizar_fotos():
    imagenes = {
        'Reloj Classic Silver': 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=500',
        'Reloj Sport Runner Pro': 'https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?w=500',
        'Reloj Executive Gold': 'https://images.unsplash.com/photo-1542496658-e33a6d0d50f6?w=500',
        'Reloj Diver Blue': 'https://images.unsplash.com/photo-1548171915-e79a380a2a4b?w=500',
        'Reloj Minimalist Black': 'https://images.unsplash.com/photo-1539874754764-5a96559165b0?w=500',
        'Reloj Smart Watch Pro': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500',
        'Reloj Lady Rose Gold': 'https://images.unsplash.com/photo-1518131672697-613becd4fab5?w=500',
        'Reloj Classic Brown': 'https://images.unsplash.com/photo-1455849318743-b2233052fcff?w=500',
        'Reloj Chronograph Silver': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500',
        'Reloj Skeleton Gold': 'https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?w=500',
        'Reloj Fitness Tracker': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500',
        'Reloj Casual White': 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=500',
    }
    
    conn = get_db()
    cursor = conn.cursor()
    count = 0
    
    for nombre, url in imagenes.items():
        cursor.execute("UPDATE productos SET imagen = ? WHERE nombre LIKE ?", (url, f'%{nombre}%'))
        count += cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return f"Fotos actualizadas: {count} productos"



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if not os.path.exists(UPLOAD_FOLDER):
    try:
        os.makedirs(UPLOAD_FOLDER)
    except:
        pass

def get_db():
    db_path = DATABASE
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Crear tablas automáticamente
    cursor = conn.cursor()
    try:
        cursor.execute('CREATE TABLE IF NOT EXISTS configuracion (id INTEGER PRIMARY KEY AUTOINCREMENT, clave TEXT UNIQUE NOT NULL, valor TEXT)')
        cursor.execute('CREATE TABLE IF NOT EXISTS productos (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, descripcion TEXT, precio REAL NOT NULL, imagen TEXT, categoria TEXT, stock INTEGER DEFAULT 10, tallas TEXT DEFAULT "")')
        cursor.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL)')
        conn.commit()
    except:
        pass
    
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Crear tabla de configuración PRIMERO
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clave TEXT UNIQUE NOT NULL,
            valor TEXT
        )
    ''')
    conn.commit()
    
    # Crear tabla de productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            imagen TEXT,
            categoria TEXT,
            stock INTEGER DEFAULT 10,
            tallas TEXT DEFAULT ''
        )
    ''')
    conn.commit()
    
    # Actualizar fotos de productos si están vacías
    fotos_default = {
        'Reloj Classic Silver': 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=500',
        'Reloj Sport Runner Pro': 'https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?w=500',
        'Reloj Executive Gold': 'https://images.unsplash.com/photo-1542496658-e33a6d0d50f6?w=500',
        'Reloj Diver Blue': 'https://images.unsplash.com/photo-1548171915-e79a380a2a4b?w=500',
        'Reloj Minimalist Black': 'https://images.unsplash.com/photo-1539874754764-5a96559165b0?w=500',
        'Reloj Smart Watch Pro': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500',
        'Reloj Lady Rose Gold': 'https://images.unsplash.com/photo-1518131672697-613becd4fab5?w=500',
        'Reloj Classic Brown': 'https://images.unsplash.com/photo-1455849318743-b2233052fcff?w=500',
        'Reloj Chronograph Silver': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500',
        'Reloj Skeleton Gold': 'https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?w=500',
        'Reloj Fitness Tracker': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500',
        'Reloj Casual White': 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=500',
    }
    for nombre, url in fotos_default.items():
        cursor.execute("UPDATE productos SET imagen = ? WHERE nombre LIKE ? AND (imagen IS NULL OR imagen = '')", (url, f'%{nombre}%'))
    
    conn.commit()
    
    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    
    # Agregar valores de configuración por defecto
    config_default = [
        ('direccion', 'Valencia, Carabobo'),
        ('email_contacto', 'info@chronosstore.com'),
        ('telefono', '+58 412-107-3377'),
        ('nombre_tienda', 'Chronos Store'),
        ('mensaje_whatsapp', 'Hola! Soy {nombre}\n\nMi pedido de relojes:\n{productos}\n\nTotal: ${total}'),
    ]
    for clave, valor in config_default:
        try:
            cursor.execute('INSERT INTO configuracion (clave, valor) VALUES (?, ?)', (clave, valor))
        except:
            pass
    conn.commit()
    
    # Crear usuario admin
    try:
        hashed_password = generate_password_hash('admin123')
        cursor.execute('INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)', ('Admin', 'admin@admin.com', hashed_password))
        conn.commit()
    except:
        pass
    
    # Agregar productos de ejemplo
    cursor.execute('SELECT COUNT(*) FROM productos')
    if cursor.fetchone()[0] == 0:
        productos_ejemplo = [
            ('Reloj Classic Silver', 'Reloj clásico de acero inoxidable, sumergible 50m', 89.99, 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=500', 'clasicos', 'Única'),
            ('Reloj Sport Runner Pro', 'Reloj deportivo con cronómetro y resistencia al agua', 129.99, 'https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?w=500', 'deportivos', 'Única'),
            ('Reloj Executive Gold', 'Reloj ejecutivo con baño en oro, elegante y sofisticado', 159.99, 'https://images.unsplash.com/photo-1542496658-e33a6d0d50f6?w=500', 'premium', 'Única'),
            ('Reloj Diver Blue', 'Reloj de buceo profesional, sumergible 200m', 149.99, 'https://images.unsplash.com/photo-1548171915-e79a380a2a4b?w=500', 'deportivos', 'Única'),
            ('Reloj Minimalist Black', 'Diseño minimalista en negro mate, perfecto para diario', 79.99, 'https://images.unsplash.com/photo-1539874754764-5a96559165b0?w=500', 'clasicos', 'Única'),
            ('Reloj Smart Watch Pro', 'Reloj inteligente con monitor cardíaco y GPS', 199.99, 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500', 'inteligentes', 'Única'),
            ('Reloj Lady Rose Gold', 'Reloj femenino con acabado rose gold y cristal', 119.99, 'https://images.unsplash.com/photo-1518131672697-613becd4fab5?w=500', 'mujer', 'Única'),
            ('Reloj Classic Brown', 'Reloj clásico con correa de cuero genuino', 69.99, 'https://images.unsplash.com/photo-1455849318743-b2233052fcff?w=500', 'clasicos', 'Única'),
            ('Reloj Chronograph Silver', 'Cronógrafo profesional con funciones múltiples', 139.99, 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500', 'premium', 'Única'),
            ('Reloj Skeleton Gold', 'Reloj con mecanismo visible, diseño exclusivo', 179.99, 'https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?w=500', 'premium', 'Única'),
            ('Reloj Fitness Tracker', 'Pulsera inteligente para ejercicios y salud', 89.99, 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500', 'inteligentes', 'Única'),
            ('Reloj Casual White', 'Reloj casual de esfera blanca, resistente', 59.99, 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=500', 'clasicos', 'Única'),
        ]
        cursor.executemany(
            'INSERT INTO productos (nombre, descripcion, precio, imagen, categoria, tallas) VALUES (?, ?, ?, ?, ?, ?)',
            productos_ejemplo
        )
        conn.commit()
    
    conn.close()

def get_config(clave, default=''):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT valor FROM configuracion WHERE clave = ?', (clave,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else default

def set_config(clave, valor):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)', (clave, valor))
    conn.commit()
    conn.close()

def ensure_defaults():
    # Agregar config默认值
    defaults = [
        ('direccion', 'Valencia, Carabobo'),
        ('email_contacto', 'info@chronosstore.com'),
        ('telefono', '+58 412-107-3377'),
        ('nombre_tienda', 'Chronos Store'),
        ('mensaje_whatsapp', 'Hola! Soy {nombre}\n\nMi pedido de relojes:\n{productos}\n\nTotal: ${total}'),
    ]
    conn = get_db()
    cursor = conn.cursor()
    for clave, valor in defaults:
        try:
            cursor.execute('INSERT INTO configuracion (clave, valor) VALUES (?, ?)', (clave, valor))
        except:
            pass
    conn.commit()
    
    # Agregar admin
    try:
        hashed = generate_password_hash('admin123')
        cursor.execute('INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)', ('Admin', 'admin@admin.com', hashed))
        conn.commit()
    except:
        pass
    
    # Agregar productos
    cursor.execute('SELECT COUNT(*) FROM productos')
    if cursor.fetchone()[0] == 0:
        productos = [
            ('Reloj Classic Silver', 'Reloj clásico de acero inoxidable, sumergible 50m', 89.99, 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=500', 'clasicos', 'Única'),
            ('Reloj Sport Runner Pro', 'Reloj deportivo con cronómetro y resistencia al agua', 129.99, 'https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?w=500', 'deportivos', 'Única'),
            ('Reloj Executive Gold', 'Reloj ejecutivo con baño en oro, elegante', 159.99, 'https://images.unsplash.com/photo-1542496658-e33a6d0d50f6?w=500', 'premium', 'Única'),
            ('Reloj Diver Blue', 'Reloj de buceo profesional, sumergible 200m', 149.99, 'https://images.unsplash.com/photo-1548171915-e79a380a2a4b?w=500', 'deportivos', 'Única'),
            ('Reloj Minimalist Black', 'Diseño minimalista en negro mate, perfecto para diario', 79.99, 'https://images.unsplash.com/photo-1539874754764-5a96559165b0?w=500', 'clasicos', 'Única'),
            ('Reloj Smart Watch Pro', 'Reloj inteligente con monitor cardíaco y GPS', 199.99, 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500', 'inteligentes', 'Única'),
            ('Reloj Lady Rose Gold', 'Reloj femenino con acabado rose gold y cristal', 119.99, 'https://images.unsplash.com/photo-1518131672697-613becd4fab5?w=500', 'mujer', 'Única'),
            ('Reloj Classic Brown', 'Reloj clásico con correa de cuero genuino', 69.99, 'https://images.unsplash.com/photo-1455849318743-b2233052fcff?w=500', 'clasicos', 'Única'),
        ]
        for p in productos:
            cursor.execute('INSERT INTO productos (nombre, descripcion, precio, imagen, categoria, tallas) VALUES (?, ?, ?, ?, ?, ?)', p)
        conn.commit()
    conn.close()

def actualizar_fotos_db():
    fotos = {
        'Reloj Classic Silver': 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=500',
        'Reloj Sport Runner Pro': 'https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?w=500',
        'Reloj Executive Gold': 'https://images.unsplash.com/photo-1542496658-e33a6d0d50f6?w=500',
        'Reloj Diver Blue': 'https://images.unsplash.com/photo-1548171915-e79a380a2a4b?w=500',
        'Reloj Minimalist Black': 'https://images.unsplash.com/photo-1539874754764-5a96559165b0?w=500',
        'Reloj Smart Watch Pro': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500',
        'Reloj Lady Rose Gold': 'https://images.unsplash.com/photo-1518131672697-613becd4fab5?w=500',
        'Reloj Classic Brown': 'https://images.unsplash.com/photo-1455849318743-b2233052fcff?w=500',
        'Reloj Chronograph Silver': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500',
        'Reloj Skeleton Gold': 'https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?w=500',
        'Reloj Fitness Tracker': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500',
        'Reloj Casual White': 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=500',
    }
    try:
        conn = get_db()
        cursor = conn.cursor()
        for nombre, url in fotos.items():
            cursor.execute("UPDATE productos SET imagen = ? WHERE nombre LIKE ?", (url, f'%{nombre}%'))
        conn.commit()
        conn.close()
    except:
        pass

@app.context_processor
def inject_config():
    ensure_defaults()
    actualizar_fotos_db()
    return {
        'nombre_tienda': get_config('nombre_tienda', 'Chronos Store'),
        'direccion_tienda': get_config('direccion', ''),
        'email_tienda': get_config('email_contacto', ''),
        'telefono_tienda': get_config('telefono', ''),
    }

@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos LIMIT 8')
    productos = cursor.fetchall()
    conn.close()
    return render_template('index.html', productos=productos)

@app.route('/buscar')
def buscar():
    query = request.args.get('q', '')
    conn = get_db()
    cursor = conn.cursor()
    if query:
        cursor.execute('SELECT * FROM productos WHERE nombre LIKE ? OR descripcion LIKE ?', (f'%{query}%', f'%{query}%'))
    else:
        cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall()
    conn.close()
    return render_template('productos.html', productos=productos, busqueda=query)

@app.route('/productos')
def productos():
    categoria = request.args.get('categoria')
    conn = get_db()
    cursor = conn.cursor()
    if categoria:
        cursor.execute('SELECT * FROM productos WHERE categoria = ?', (categoria,))
    else:
        cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall()
    conn.close()
    return render_template('productos.html', productos=productos, categoria=categoria)

@app.route('/producto/<int:id>')
def producto_detalle(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos WHERE id = ?', (id,))
    producto = cursor.fetchone()
    conn.close()
    if producto:
        return render_template('producto.html', producto=producto)
    return redirect(url_for('productos'))

@app.route('/agregar_carrito/<int:id>', methods=['POST'])
def agregar_carrito(id):
    talla = request.form.get('talla', 'Única')
    carrito = session.get('carrito', {})
    clave = f"{id}_{talla}"
    
    if clave in carrito:
        carrito[clave]['cantidad'] += 1
    else:
        carrito[clave] = {'cantidad': 1, 'talla': talla, 'producto_id': id}
    
    session['carrito'] = carrito
    return redirect(url_for('ver_carrito'))

@app.route('/carrito')
def ver_carrito():
    carrito = session.get('carrito', {})
    productos_carrito = []
    total = 0
    
    if carrito:
        conn = get_db()
        cursor = conn.cursor()
        for clave, item in carrito.items():
            cantidad = item['cantidad']
            talla = item['talla']
            producto_id = item['producto_id']
            cursor.execute('SELECT * FROM productos WHERE id = ?', (producto_id,))
            producto = cursor.fetchone()
            if producto:
                subtotal = producto['precio'] * cantidad
                total += subtotal
                productos_carrito.append({
                    'producto': producto,
                    'cantidad': cantidad,
                    'talla': talla,
                    'subtotal': subtotal,
                    'clave': clave
                })
        conn.close()
    
    return render_template('carrito.html', productos_carrito=productos_carrito, total=total)

@app.route('/eliminar_carrito/<clave>')
def eliminar_carrito(clave):
    carrito = session.get('carrito', {})
    if clave in carrito:
        del carrito[clave]
        session['carrito'] = carrito
    return redirect(url_for('ver_carrito'))

@app.route('/actualizar_carrito/<clave>', methods=['POST'])
def actualizar_carrito(clave):
    nueva_talla = request.form.get('talla')
    carrito = session.get('carrito', {})
    if clave in carrito and nueva_talla:
        producto_id = carrito[clave]['producto_id']
        nuevo_clave = f"{producto_id}_{nueva_talla}"
        carrito[clave]['talla'] = nueva_talla
        
        if nuevo_clave != clave and nuevo_clave not in carrito:
            carrito[nuevo_clave] = carrito.pop(clave)
        
        session['carrito'] = carrito
    return redirect(url_for('ver_carrito'))

@app.route('/vaciar_carrito')
def vaciar_carrito():
    session['carrito'] = {}
    return redirect(url_for('ver_carrito'))

@app.route('/checkout')
def checkout():
    carrito = session.get('carrito', {})
    if not carrito:
        return redirect(url_for('index'))
    
    productos_carrito = []
    total = 0
    
    conn = get_db()
    cursor = conn.cursor()
    for clave, item in carrito.items():
        cantidad = item['cantidad']
        talla = item['talla']
        producto_id = item['producto_id']
        cursor.execute('SELECT * FROM productos WHERE id = ?', (producto_id,))
        producto = cursor.fetchone()
        if producto:
            subtotal = producto['precio'] * cantidad
            total += subtotal
            productos_carrito.append({
                'producto': producto,
                'cantidad': cantidad,
                'talla': talla,
                'subtotal': subtotal,
                'clave': clave
            })
    conn.close()
    
    return render_template('checkout.html', productos_carrito=productos_carrito, total=total)

@app.route('/procesar_pedido', methods=['POST'])
def procesar_pedido():
    carrito = session.get('carrito', {})
    
    productos_carrito = []
    total = 0
    
    conn = get_db()
    cursor = conn.cursor()
    for clave, item in carrito.items():
        cantidad = item['cantidad']
        talla = item['talla']
        producto_id = item['producto_id']
        cursor.execute('SELECT * FROM productos WHERE id = ?', (producto_id,))
        producto = cursor.fetchone()
        if producto:
            subtotal = producto['precio'] * cantidad
            total += subtotal
            productos_carrito.append({
                'nombre': producto['nombre'],
                'precio': producto['precio'],
                'cantidad': cantidad,
                'talla': talla,
                'subtotal': subtotal
            })
    conn.close()
    
    nombre = request.form.get('nombre', '')
    telefono = request.form.get('telefono', '')
    direccion = request.form.get('direccion', '')
    ciudad = request.form.get('ciudad', '')
    pago = request.form.get('pago', '')
    ubicacion = request.form.get('ubicacion', '')
    
    productos_texto = ""
    for item in productos_carrito:
        productos_texto += f"- {item['nombre']} (Talla: {item['talla']}) x{item['cantidad']} = ${item['subtotal']:.2f}\n"
    
    mensaje_template = get_config('mensaje_whatsapp', 'Hola! Soy {nombre}\n\nMi pedido:\n{productos}\n\nTotal: ${total}')
    
    mensaje = mensaje_template.format(
        nombre=nombre,
        productos=productos_texto.strip(),
        total=f"{total:.2f}"
    )
    
    if direccion:
        mensaje += f"\n\n📍 Dirección: {direccion}, {ciudad}"
    if telefono:
        mensaje += f"\n📱 Teléfono: {telefono}"
    if ubicacion:
        mensaje += f"\n🌍 Ubicación: {ubicacion}"
    mensaje += f"\n💳 Pago: {pago}"
    
    telefono_tienda = get_config('telefono', '').replace('+', '').replace(' ', '').replace('-', '')
    
    session['pedido_info'] = {
        'mensaje': mensaje,
        'telefono': telefono_tienda,
        'nombre': nombre,
        'total': total
    }
    
    session['carrito'] = {}
    return redirect(url_for('pedido_exitoso'))

@app.route('/pedido-exitoso')
def pedido_exitoso():
    pedido_info = session.get('pedido_info', {})
    return render_template('pedido_exitoso.html', pedido_info=pedido_info)

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
            user = cursor.fetchone()
            conn.close()
            if user and check_password_hash(user['password'], password):
                session['user'] = user['id']
                return redirect(url_for('index'))
            return render_template('login.html', error='Credenciales incorrectas')
        return render_template('login.html')
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)', (nombre, email, hashed_password))
            conn.commit()
            session['user'] = cursor.lastrowid
            conn.close()
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('register.html', error='Email ya registrado')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/admin/contacto', methods=['GET', 'POST'])
def admin_contacto():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        set_config('nombre_tienda', request.form.get('nombre_tienda'))
        set_config('direccion', request.form.get('direccion'))
        set_config('email_contacto', request.form.get('email_contacto'))
        set_config('telefono', request.form.get('telefono'))
        set_config('mensaje_whatsapp', request.form.get('mensaje_whatsapp'))
        return redirect(url_for('admin_contacto'))
    
    config = {
        'nombre_tienda': get_config('nombre_tienda'),
        'direccion': get_config('direccion'),
        'email_contacto': get_config('email_contacto'),
        'telefono': get_config('telefono'),
        'mensaje_whatsapp': get_config('mensaje_whatsapp', 'Hola! Soy {nombre}\n\nMi pedido:\n{productos}\n\nTotal: ${total}'),
    }
    return render_template('admin_contacto.html', config=config)

@app.route('/admin/credenciales', methods=['GET', 'POST'])
def admin_credenciales():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    error = None
    success = None
    
    if request.method == 'POST':
        email_actual = request.form.get('email_actual')
        email_nuevo = request.form.get('email_nuevo')
        password_actual = request.form.get('password_actual')
        password_nuevo = request.form.get('password_nuevo')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE id = 1')
        user = cursor.fetchone()
        
        if user and password_actual and check_password_hash(user['password'], password_actual):
            if email_nuevo and password_nuevo:
                hashed = generate_password_hash(password_nuevo)
                cursor.execute('UPDATE usuarios SET email = ?, password = ? WHERE id = 1', (email_nuevo, hashed))
                conn.commit()
                success = 'Credenciales actualizadas correctamente'
            elif password_nuevo:
                hashed = generate_password_hash(password_nuevo)
                cursor.execute('UPDATE usuarios SET password = ? WHERE id = 1', (hashed,))
                conn.commit()
                success = 'Contraseña actualizada correctamente'
            elif email_nuevo:
                cursor.execute('UPDATE usuarios SET email = ? WHERE id = 1', (email_nuevo,))
                conn.commit()
                success = 'Email actualizado correctamente'
        else:
            error = 'Contraseña actual incorrecta'
        
        conn.close()
    
    return render_template('admin_credenciales.html', error=error, success=success)

@app.route('/admin/products')
def admin_products():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall()
    conn.close()
    return render_template('admin_products.html', productos=productos)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin/add_product', methods=['GET', 'POST'])
def add_product():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        categoria = request.form['categoria']
        stock = int(request.form['stock'])
        tallas = request.form.get('tallas', '')
        
        imagen = None
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                imagen = filename
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO productos (nombre, descripcion, precio, imagen, categoria, stock, tallas) VALUES (?, ?, ?, ?, ?, ?, ?)', (nombre, descripcion, precio, imagen, categoria, stock, tallas))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_products'))
    return render_template('add_edit_product.html', product=None)

@app.route('/admin/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        categoria = request.form['categoria']
        stock = int(request.form['stock'])
        tallas = request.form.get('tallas', '')
        
        imagen = None
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                imagen = filename
        
        if imagen:
            cursor.execute('UPDATE productos SET nombre=?, descripcion=?, precio=?, imagen=?, categoria=?, stock=?, tallas=? WHERE id=?', (nombre, descripcion, precio, imagen, categoria, stock, tallas, id))
        else:
            cursor.execute('UPDATE productos SET nombre=?, descripcion=?, precio=?, categoria=?, stock=?, tallas=? WHERE id=?', (nombre, descripcion, precio, categoria, stock, tallas, id))
        
        conn.commit()
        conn.close()
        return redirect(url_for('admin_products'))
    cursor.execute('SELECT * FROM productos WHERE id = ?', (id,))
    product = cursor.fetchone()
    conn.close()
    if product:
        return render_template('add_edit_product.html', product=product)
    return redirect(url_for('admin_products'))

@app.route('/admin/delete_product/<int:id>')
def delete_product(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM productos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_products'))

import os

if __name__ == "__main__":
    # Esto permite que el servidor asigne el puerto automáticamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
