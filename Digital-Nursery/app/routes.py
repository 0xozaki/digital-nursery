
# Company details route (must be after main_bp is defined)


import os
import json
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, session, flash,jsonify, current_app
from random import choice
from requests import post,get

CART_DATA_FILE = "cart.json"
def get_random_id():
    user_id = ""
    for i in range(11):
        user_id+= choice("1234567890")

    return user_id
main_bp = Blueprint('main', __name__)

def load_cart_data():
    """تحميل بيانات السلة من الملف"""
    if os.path.exists(CART_DATA_FILE):
        try:
            with open(CART_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_cart_data(data):
    """حفظ بيانات السلة إلى الملف"""
    try:
        with open(CART_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving cart data: {e}")
        return False

def load_categories():
    """Load categories from JSON file"""
    try:
        categories_path = os.path.join('categories.json')
        with open(categories_path, 'r', encoding='utf-8') as f:
            categories = json.load(f)
        return categories
    except Exception as e:
        print(f"Error loading categories: {e}")
        return []



products = [
    {
        'id': 1,
        'name': 'Fiddle Leaf Fig',
        'image': 'https://images.unsplash.com/photo-1464983953574-0892a716854b?auto=format&fit=crop&w=300&q=80',
        'price': 24.99,
        'description': 'Popular indoor plant, easy care.',
        'care': 'Bright, indirect light. Water when top inch of soil is dry.'
    },
    {
        'id': 2,
        'name': 'Sunflower Seeds',
        'image': 'https://images.unsplash.com/photo-1501004318641-b39e6451bec6?auto=format&fit=crop&w=300&q=80',
        'price': 3.49,
        'description': 'High germination, perfect for gardens.',
        'care': 'Plant in full sun. Water regularly.'
    },
    {
        'id': 3,
        'name': 'Ceramic Pot',
        'image': 'https://images.unsplash.com/photo-1519864600265-abb23847ef2c?auto=format&fit=crop&w=300&q=80',
        'price': 12.99,
        'description': 'Modern design, drainage hole included.',
        'care': 'Clean with damp cloth. Use for indoor/outdoor plants.'
    }
]


from flask import make_response

@main_bp.route('/companies', endpoint='companies')
def companies():
    # Load companies from companies.json
    companies_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'companies.json')
    try:
        with open(companies_path, encoding='utf-8') as f:
            companies = json.load(f)
    except Exception:
        companies = []
    # Normalize keys for template compatibility
    for comp in companies:
        if 'catagories' in comp:
            comp['categories'] = comp['catagories']
        for cat in comp.get('categories', []):
            if 'products' not in cat:
                cat['products'] = []
    return render_template('companies.html', companies=companies)

# Category products aggregated across companies
@main_bp.route('/category/<path:category_slug>', endpoint='category_products')
def category_products(category_slug):
    # Load categories dictionary (for names and ids)
    categories_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'categories.json')
    categories = []
    try:
        with open(categories_file, encoding='utf-8') as f:
            categories = json.load(f)
    except Exception:
        categories = []

    def normalize(text):
        try:
            return ''.join(ch.lower() for ch in str(text) if ch.isalnum())
        except Exception:
            return ''

    # Build lookup from slug -> display name (prefer English if available)
    slug_to_display = {}
    for c in categories:
        name_en = c.get('name_en') or c.get('name') or ''
        name_ar = c.get('name_ar') or ''
        for name in (name_en, name_ar):
            if name:
                slug = normalize(name)
                slug_to_display[slug] = name_en or name
        # also by id if present
        cid = c.get('id')
        if isinstance(cid, int):
            slug_to_display[normalize(str(cid))] = name_en or name_ar or str(cid)

    normalized_slug = normalize(category_slug.replace('-', ' '))
    target_display_name = slug_to_display.get(normalized_slug)

    # Fallback to raw slug (nice title)
    raw_title = category_slug.replace('-', ' ').strip()
    category_title = target_display_name or raw_title

    # Load companies and aggregate products matching the category
    companies_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'companies.json')
    try:
        with open(companies_path, encoding='utf-8') as f:
            companies = json.load(f)
    except Exception:
        companies = []

    # Normalize keys as elsewhere
    for comp in companies:
        if 'catagories' in comp:
            comp['categories'] = comp['catagories']
        for cat in comp.get('categories', []):
            if 'products' not in cat:
                cat['products'] = []

    results = []
    for comp in companies:
        comp_name = comp.get('name', 'Unknown')
        comp_logo = comp.get('logo')
        matched_products = []
        for cat in comp.get('categories', []):
            cat_name = cat.get('name', '')
            if not cat_name:
                continue
            if target_display_name:
                is_match = normalize(cat_name) == normalize(target_display_name)
            else:
                is_match = normalize(cat_name) == normalized_slug
            if is_match:
                for p in cat.get('products', []):
                    prod = {
                        'name': p.get('name'),
                        'image': p.get('image'),
                        'price': p.get('price'),
                        'details': p.get('details'),
                        'company': comp_name
                    }
                    matched_products.append(prod)
        if matched_products:
            results.append({
                'company_name': comp_name,
                'logo': comp_logo,
                'products': matched_products
            })

    return render_template('compaines_section.html', category_title=category_title, results=results)

# Company details route (must be after main_bp is defined)
@main_bp.route('/company/<int:company_id>', endpoint='company_details')
def company_details(company_id):
    companies_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'companies.json')
    try:
        with open(companies_path, encoding='utf-8') as f:
            companies = json.load(f)
    except Exception:
        companies = []
    # Normalize keys for template compatibility
    for comp in companies:
        if 'catagories' in comp:
            comp['categories'] = comp['catagories']
        for cat in comp.get('categories', []):
            if 'products' not in cat:
                cat['products'] = []
    if 0 <= company_id < len(companies):
        company = companies[company_id]
        # Flatten all products for details page
        all_products = []
        for cat in company.get('categories', []):
            for prod in cat.get('products', []):
                p = prod.copy()
                p['category'] = cat.get('name', '')
                all_products.append(p)
        company['products'] = all_products
        return render_template('company_details.html', company=company)
    else:
        flash('Company not found.', 'danger')
        return redirect(url_for('main.companies'))

@main_bp.route('/settings', endpoint='settings')
def settings():
    if 'user' not in session:
        flash('Please log in to access settings.', 'warning')
        return redirect(url_for('main.login'))
    return render_template('settings.html')

@main_bp.route('/account', endpoint='account')
def account():
    
    username = session['user']
    user_data = None
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
        for u in users:
            if u.get('username') == username:
                user_data = u
                break
    except Exception as d:
        print(d)
        user_data = None
    if not user_data:
        flash('User data not found.', 'danger')
        return redirect(url_for('main.home'))
    return render_template('account_settings.html', user=user_data)

@main_bp.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    categories_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'categories.json')
    try:
        with open(categories_path, encoding='utf-8') as f:
            categories = json.load(f)

        with open("users.json",'r',encoding='utf-8') as json_reader:
            loading_data = json.load(json_reader)
            for account in loading_data:
                if account.get('username'):
                    location = account.get("location")
                    print(location)

        
    except Exception:
        categories = []
    return render_template('home.html', products=products, categories=categories,location=location)
@main_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('main.home'))
    return render_template('product_detail.html', product=product)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        
        try:
            with open("users.json",'r',encoding='utf-8') as json_reader:
                loading_data = json.load(json_reader)
            for account in loading_data:
                if account.get('username') == username and account.get('password_hach') == password:
                    session['user'] = username
                    flash('Logged in successfully.', 'success')
                    return redirect(url_for('main.home'))
        except Exception:
            pass
        flash('Invalid username or password.', 'danger')
        return redirect(url_for('main.login'))
    elif request.method == "GET":
        return render_template("login.html")
@main_bp.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('main.login'))
    username = session['user']
    user_data = None
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
        for u in users:
            if u.get('username') == username:
                user_data = u
                break
    except Exception as d:
        print(d)
        user_data = None
    if not user_data:
        flash('User data not found.', 'danger')
        return redirect(url_for('main.home'))
    return render_template('dashboard.html', user=user_data)

@main_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.home'))

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone_number = request.form.get("phone")
        # Check if user already exists
        try:
            with open("users.json", 'r', encoding='utf-8') as json_reader:
                users = json.load(json_reader)
                
            for user in users:
                if user.get('username') == username:
                    flash('Username already exists.', 'danger')
                    return redirect(url_for('main.login'))
                elif user.get('email') == email:
                    flash('Email already used','danger')
                    return redirect(url_for('main.login'))
                elif user.get("phone") == phone_number:
                    flash('Phone number already used','danger')
                    return redirect(url_for('main.login'))
                    
        except FileNotFoundError:
            users = []
        
        # Create new user

        user_id = get_random_id()
        new_user = {
            "user_id": user_id,
            "phone_number":phone_number,
            "token": "null",
            "password_hach": password,
            "username": username,
            "image": "https://randomuser.me/api/portraits/men/1.jpg",
            "bio": "",
            "role":"user",
            "orders": []
        }
        
        users.append(new_user)
        
        # Save to file
        with open("users.json", 'w', encoding='utf-8') as json_writer:
            json.dump(users, json_writer, indent=2)
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))
    
    return redirect(url_for('main.login'))


@main_bp.route("/settings/account_info")
def settings_details():
    if request.method == "GET":
        return render_template("profile_details.html")


@main_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    try:
        data = request.get_json()
        
        required_fields = ['product_name', 'price', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        user_email = session.get('user') 
        
        cart_data = load_cart_data()
        
        if user_email not in cart_data:
            cart_data[user_email] = {
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'items': [],
                'total': 0.0
            }
        
        # إنشاء عنصر المنتج الجديد
        new_item = {
            'product_name': data['product_name'],
            'price': float(data['price']),
            'quantity': int(data['quantity']),
            'currency': data.get('currency', 'OMR'),
            'added_at': datetime.now().isoformat(),
            'item_id': f"item_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        }
        
        existing_item = None
        for item in cart_data[user_email]['items']:
            if item['product_name'] == new_item['product_name']:
                existing_item = item
                break
        
        if existing_item:
            existing_item['quantity'] += new_item['quantity']
            existing_item['price'] = new_item['price']  
        else:
            cart_data[user_email]['items'].append(new_item)
        
        cart_data[user_email]['total'] = sum(
            item['price'] * item['quantity'] 
            for item in cart_data[user_email]['items']
        )
        
        cart_data[user_email]['updated_at'] = datetime.now().isoformat()
        
        # حفظ البيانات
        if save_cart_data(cart_data):
            return jsonify({
                'success': True,
                'message': 'Product added to cart successfully',
                'cart_summary': {
                    'total_items': len(cart_data[user_email]['items']),
                    'total_amount': cart_data[user_email]['total'],
                    'currency': 'OMR'
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to save cart data'
            }), 500
            
    except Exception as e:
        print(f"Error in add_to_cart: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@main_bp.route('/cart', methods=['GET'])
def get_cart():
    """جلب محتويات السلة للمستخدم"""
    try:
        user_email = session.get('user')
        cart_data = load_cart_data()
        
        if user_email not in cart_data:
            return jsonify({
                'success': True,
                'cart': {
                    'items': [],
                    'total': 0.0,
                    'currency': 'OMR'
                }
            }), 200
        
        user_cart = cart_data[user_email]
        return jsonify({
            'success': True,
            'cart': {
                'items': user_cart['items'],
                'total': user_cart['total'],
                'currency': 'OMR',
                'total_items': len(user_cart['items'])
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_cart: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@main_bp.route('/cart/update', methods=['PUT'])
def update_cart_item():
    """تحديث كمية عنصر في السلة"""
    try:
        data = request.get_json()
        user_email = session.get('user')
        
        required_fields = ['item_id', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        cart_data = load_cart_data()
        
        if user_email not in cart_data:
            return jsonify({
                'success': False,
                'message': 'Cart not found'
            }), 404
        
        # البحث عن العنصر وتحديثه
        item_updated = False
        for item in cart_data[user_email]['items']:
            if item['item_id'] == data['item_id']:
                item['quantity'] = int(data['quantity'])
                item_updated = True
                break
        
        if not item_updated:
            return jsonify({
                'success': False,
                'message': 'Item not found in cart'
            }), 404
        
        # تحديث الإجمالي والوقت
        cart_data[user_email]['total'] = sum(
            item['price'] * item['quantity'] 
            for item in cart_data[user_email]['items']
        )
        cart_data[user_email]['updated_at'] = datetime.now().isoformat()
        
        if save_cart_data(cart_data):
            return jsonify({
                'success': True,
                'message': 'Cart updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update cart'
            }), 500
            
    except Exception as e:
        print(f"Error in update_cart_item: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@main_bp.route('/cart/remove', methods=['DELETE'])
def remove_from_cart():
    """إزالة عنصر من السلة"""
    try:
        data = request.get_json()
        user_email = session.get('user')
        
        if 'item_id' not in data:
            return jsonify({
                'success': False,
                'message': 'Missing item_id'
            }), 400
        
        cart_data = load_cart_data()
        
        if user_email not in cart_data:
            return jsonify({
                'success': False,
                'message': 'Cart not found'
            }), 404
        
        # إزالة العنصر
        original_count = len(cart_data[user_email]['items'])
        cart_data[user_email]['items'] = [
            item for item in cart_data[user_email]['items'] 
            if item['item_id'] != data['item_id']
        ]
        
        if len(cart_data[user_email]['items']) == original_count:
            return jsonify({
                'success': False,
                'message': 'Item not found in cart'
            }), 404
        
        # تحديث الإجمالي والوقت
        cart_data[user_email]['total'] = sum(
            item['price'] * item['quantity'] 
            for item in cart_data[user_email]['items']
        )
        cart_data[user_email]['updated_at'] = datetime.now().isoformat()
        
        if save_cart_data(cart_data):
            return jsonify({
                'success': True,
                'message': 'Item removed from cart'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to remove item'
            }), 500
            
    except Exception as e:
        print(f"Error in remove_from_cart: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@main_bp.route('/cart/clear', methods=['DELETE'])
def clear_cart():
    """تفريغ السلة بالكامل"""
    try:
        user_email = session.get('user')
        cart_data = load_cart_data()
        
        if user_email in cart_data:
            cart_data[user_email]['items'] = []
            cart_data[user_email]['total'] = 0.0
            cart_data[user_email]['updated_at'] = datetime.now().isoformat()
            
            if save_cart_data(cart_data):
                return jsonify({
                    'success': True,
                    'message': 'Cart cleared successfully'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to clear cart'
                }), 500
        else:
            return jsonify({
                'success': True,
                'message': 'Cart is already empty'
            }), 200
            
    except Exception as e:
        print(f"Error in clear_cart: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
    
@main_bp.route("/user_cart",methods=["GET"])
def user_cart():
    if request.method == "GET":
        return render_template("cart.html")
    

@main_bp.route("/change_password",methods=["POST"])
def change_password():
    try:
        data = request.form
        old_password = data.get("current_password")
        new_password = data.get("new_password")
        username = session.get('user')
        
        if not username:
            return jsonify({"error": "User not logged in"}), 401
            
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
            
        user_found = None
        for user in users:
            if user.get('username') == username:
                user_found = user
                break
                
        if not user_found:
            return jsonify({"error": "User not found"}), 404
            
        if user_found.get('password_hach') != old_password:
            return jsonify({"error": "Current password is incorrect"}), 400
            
        user_found['password_hach'] = new_password
        
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
            
        return jsonify({"message": "Password updated successfully"})
        
    except Exception as e:
        return jsonify({"error": "Server error"}), 500

@main_bp.route("/update_profile", methods=["POST"])
def update_profile2():
    try:
        username = session.get('user')
        new_username = username
        phone_number = request.form.get('phone_number')
        location = request.form.get('location')
        bio = request.form.get('bio')
        
        if not username:
            return jsonify({"error": "User not logged in"}), 401
            
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
            
        user_found = None
        for user in users:
            if user.get('username') == username:
                user_found = user
                break
                
        if not user_found:
            return jsonify({"error": "User not found"}), 404
            
        user_found['username'] = new_username
        user_found['phone_number'] = phone_number
        user_found['location'] = location
        user_found['bio'] = bio
        
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
            
        session['user'] = new_username
            
        return jsonify({"message": "Profile updated successfully"})
        
    except Exception as e:
        return jsonify({"error": "Server error"}), 500

@main_bp.route('/api/create-thawani-session', methods=['POST'])
def create_thawani_session():
    try:
        data = request.json
        
        # إعداد بيانات الطلب لـ Thawani
        thawani_data = {
            "client_reference_id": data.get('client_reference_id'),
            "mode": "payment",
            "products": data.get('products', []),
            "success_url": data.get('success_url'),
            "cancel_url": data.get('cancel_url'),
            "metadata": data.get('metadata', {})
        }
        print(thawani_data)
        
        # إرسال الطلب إلى Thawani
        headers = {
            'Content-Type': 'application/json',
            'thawani-api-key': 'l8ZAYKPImEMIIhThZXMhsmqCcrOqXz'
        }
        
        response = post(
            'https://checkout.thawani.om/api/v1/checkout/session',
            headers=headers,
            json=thawani_data
        )
        
        response_data = response.json()
        
        if response_data.get('success') and response_data.get('data'):
            return jsonify({
                'success': True,
                'session_id': response_data['data']['session_id']
            })
        else:
            return jsonify({
                'success': False,
                'message': response_data.get('message', 'Payment session creation failed')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@main_bp.route('/payment/success')
def payment_success():
    return render_template('payment_success.html')

@main_bp.route('/payment/cancel')
def payment_cancel():
    return render_template('payment_cancel.html')

@main_bp.route("/account_info", methods=["GET", "POST"])
def settings_details2():
    if request.method == "GET":
        username = session.get('user')
        if not username:
            flash('Please login first', 'danger')
            return redirect(url_for('main.login'))
        user_data = None
        try:
            with open('users.json', 'r', encoding='utf-8') as f:
                users = json.load(f)
            for u in users:
                if u.get('username') == username:
                    print(username)
                    user_data = {
                        "user_id": u.get('user_id'),
                        "username": u.get('username'),
                        "role": u.get('role', 'user'),
                        "image": u.get('image', 'https://via.placeholder.com/120/388e3c/ffffff?text=User'),
                        "bio": u.get('bio', ''),
                        "phone_number": u.get('phone_number', ''),
                        "location": u.get('location', ''),
                        "orders": u.get('orders', [])
                    }
                    break
        except Exception as d:
            print(d)
            user_data = None
        if not user_data:
            flash('User data not found.', 'danger')
            return redirect(url_for('main.home'))
        return render_template('profile_details.html', user_data=user_data)
    elif request.method == "POST":
        token = request.form.get('token')
        if not token:
            return jsonify({"error": "Token is required"}), 401
        try:
            with open('users.json', 'r', encoding='utf-8') as f:
                users = json.load(f)
            user_found = None
            for user in users:
                if user.get('token') == token:
                    user_found = user
                    break
            if not user_found:
                return jsonify({"error": "Invalid token"}), 401
            user_data = {
                "user_id": user_found.get('user_id'),
                "username": user_found.get('username'),
                "role": user_found.get('role', 'user'),
                "image": user_found.get('image', 'https://via.placeholder.com/120/388e3c/ffffff?text=User'),
                "bio": user_found.get('bio', ''),
                "phone_number": user_found.get('phone_number', ''),
                "location": user_found.get('location', ''),
                "orders": user_found.get('orders', [])
            }
            return jsonify(user_data)
        except Exception as e:
            return jsonify({"error": "Server error"}), 500

@main_bp.route('/api/categories')
def api_categories():
    """API endpoint to get categories"""
    categories = load_categories()
    return jsonify(categories)

@main_bp.route('/categories')
def categories_page():
    """Categories page"""
    categories = load_categories()
    return render_template('categories.html', categories=categories)

@main_bp.route('/update_profile', methods=['POST'])
def update_profile():
    """Update user profile including location"""
    try:
        data = request.get_json()
        location = data.get('location')
        
        data = request.get_json()
        username = session.get("user")
        
        with open("users.json", 'r', encoding='utf-8') as json_reader:
                users = json.load(json_reader)
                
        for user in users:
            if user["username"] == username:
                user["location"] = location

        
        with open("users.json", 'w') as json_writer:
            json.dump(users, json_writer, indent=2)
        
        
        return jsonify({
            'success': True,
            'message': 'Location updated successfully',
            'location': location
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating location: {str(e)}'
        }), 400

@main_bp.route('/get_language', methods=['GET'])
def get_language():
    try:
        username = session.get('user')
        if not username:
            return jsonify({"language": "en"}), 200
            
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
            
        user_found = None
        for user in users:
            if user.get('username') == username:
                user_found = user
                break
                
        if not user_found:
            return jsonify({"error": "User not found"}), 404
            
        language = user_found.get('language', 'en')
            
        return jsonify({"language": language})
    except:
        return jsonify({"language": "en"}), 200
    
@main_bp.route('/update_language', methods=['POST'])
def update_language():
    try:
        username = session.get('user')
        language = request.form.get('language')
        
        if not username:
            return jsonify({"error": "User not logged in"}), 401
            
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
            
        user_found = None
        for i, user in enumerate(users):
            if user.get('username') == username:
                users[i]['language'] = language
                user_found = user
                break
                
        if not user_found:
            return jsonify({"error": "User not found"}), 404
        
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
            
        return jsonify({"message": "Language updated successfully"})
        
    except Exception as e:
        return jsonify({"error": "Server error"}), 500
    
@main_bp.route('/update_language', methods=['POST'])
def update_language2():
    try:
        username = session.get('user')
        language = request.form.get('language')
        
        if not username:
            return jsonify({"error": "User not logged in"}), 401
            
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
            
        user_found = False
        for i, user in enumerate(users):
            if user.get('username') == username:
                users[i]['language'] = language
                user_found = True
                break
                
        if not user_found:
            return jsonify({"error": "User not found"}), 404
        
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
            
        return jsonify({"message": "Language updated successfully"})
        
    except Exception as e:
        return jsonify({"error": "Server error"}), 500



@main_bp.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        with open('categories.json', 'r', encoding='utf-8') as f:
            categories = json.load(f)
        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": "Server error"}), 500

@main_bp.route('/api/companies', methods=['GET'])
def get_companies():
    try:
        with open('companies.json', 'r', encoding='utf-8') as f:
            companies = json.load(f)
        return jsonify(companies)
    except Exception as e:
        return jsonify({"error": "Server error"}), 500

@main_bp.route('/api/products/<category_id>', methods=['GET'])
def get_products_by_category(category_id):
    try:
        with open('companies.json', 'r', encoding='utf-8') as f:
            companies = json.load(f)
        
        category_products = []
        
        for company in companies:
            for cat in company.get('catagories', []):
                if str(cat.get('id')) == str(category_id):
                    for product in cat.get('products', []):
                        product_with_company = product.copy()
                        product_with_company['company_name'] = company['name']
                        product_with_company['company_logo'] = company['logo']
                        category_products.append(product_with_company)
        
        return jsonify(category_products)
    except Exception as e:
        return jsonify({"error": "Server error"}), 500

@main_bp.route('/api/category/<category_id>', methods=['GET'])
def get_category_details(category_id):
    try:
        with open('categories.json', 'r', encoding='utf-8') as f:
            categories = json.load(f)
        
        category = next((cat for cat in categories if str(cat['id']) == str(category_id)), None)
        return jsonify(category if category else {})
    except Exception as e:
        return jsonify({"error": "Server error"}), 500

@main_bp.route('/category/<int:category_id>')
def category_page(category_id):
    return render_template('category.html')


def load_ads_data():
    """تحميل بيانات الإعلانات من ملف JSON"""
    try:
        # المسار إلى ملف الإعلانات
        ads_file_path = os.path.join(current_app.root_path, 'data', 'ads.json')
        
        # إذا لم يكن الملف موجوداً، نرجع إعلانات افتراضية
        if not os.path.exists(ads_file_path):
            return get_default_ads()
        
        with open(ads_file_path, 'r', encoding='utf-8') as f:
            ads_data = json.load(f)
        
        # التأكد من أن البيانات في الصيغة الصحيحة
        if isinstance(ads_data, list):
            return ads_data
        else:
            current_app.logger.error("Invalid ads.json format. Expected list.")
            return get_default_ads()
            
    except Exception as e:
        current_app.logger.error(f"Error loading ads data: {str(e)}")
        return get_default_ads()

def get_default_ads():
    """إرجاع إعلانات افتراضية في حالة وجود خطأ"""
    return [
        {
            "id": 1,
            "title": "عروض خاصة على النباتات",
            "title_en": "Special Offers on Plants",
            "description": "احصل على خصم 20% على جميع النباتات الداخلية",
            "description_en": "Get 20% discount on all indoor plants",
            "image_url": "/static/images/ads/plant-offer.jpg",
            "button_text": "اطلع الآن",
            "button_text_en": "View Now",
            "target_url": "/categories/1",
            "is_active": True,
            "order": 1
        },
        {
            "id": 2,
            "title": "أسمدة بجودة عالية",
            "title_en": "High Quality Fertilizers", 
            "description": "أفضل الأسمدة العضوية لنباتات أكثر صحة",
            "description_en": "Best organic fertilizers for healthier plants",
            "image_url": "/static/images/ads/fertilizers.jpg",
            "button_text": "تسوق الآن",
            "button_text_en": "Shop Now",
            "target_url": "/categories/3",
            "is_active": True,
            "order": 2
        },
        {
            "id": 3,
            "title": "أصص زراعية متنوعة",
            "title_en": "Variety of Planting Pots",
            "description": "تشكيلة واسعة من الأصص بأسعار منافسة",
            "description_en": "Wide variety of pots at competitive prices",
            "image_url": "/static/images/ads/pots.jpg",
            "button_text": "اكتشف المزيد",
            "button_text_en": "Discover More",
            "target_url": "/categories/4",
            "is_active": True,
            "order": 3
        }
    ]

@main_bp.route('/api/ads', methods=['GET'])
def get_ads():
    """إرجاع قائمة الإعلانات النشطة"""
    try:
        ads_data = load_ads_data()
        
        # ترشيح الإعلانات النشطة فقط وترتيبها
        active_ads = [
            ad for ad in ads_data 
            if ad.get('is_active', True)
        ]
        
        # ترتيب الإعلانات حسب حقل order
        active_ads.sort(key=lambda x: x.get('order', 0))
        
        return jsonify(active_ads)
        
    except Exception as e:
        current_app.logger.error(f"Error in get_ads endpoint: {str(e)}")
        return jsonify(get_default_ads())

@main_bp.route('/api/ads/<int:ad_id>/click', methods=['POST'])
def track_ad_click(ad_id):
    """تتبع نقرات الإعلانات (للتتبع والإحصائيات)"""
    try:
        current_app.logger.info(f"Ad {ad_id} was clicked")
        
        # هنا يمكنك إضافة منطق لحفظ إحصائيات النقرات في قاعدة البيانات
        # أو إرسالها إلى نظام تحليلات
        
        return jsonify({
            "status": "success",
            "message": "Click tracked",
            "ad_id": ad_id
        })
        
    except Exception as e:
        current_app.logger.error(f"Error tracking ad click: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to track click"
        }), 500