from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from link import *
from api.sql import *
import imp, random, os, string
from werkzeug.utils import secure_filename
from flask import current_app
from datetime import datetime

UPLOAD_FOLDER = 'static/product'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

manager = Blueprint('manager', __name__, template_folder='../templates')

def config():
    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    config = current_app.config['UPLOAD_FOLDER'] 
    return config

@manager.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return redirect(url_for('manager.productManager'))

@manager.route('/productManager', methods=['GET', 'POST'])
@login_required
def productManager():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('index'))
        
    if 'delete' in request.values:
        pid = request.values.get('delete')
        data = Record.delete_check(pid)
        
        if(data != None):
            flash('failed')
        else:
            data = Product.get_product(pid)
            Product.delete_product(pid)
    
    elif 'edit' in request.values:
        pid = request.values.get('edit')
        return redirect(url_for('manager.edit', pid=pid))
    
    book_data = book()
    return render_template('productManager.html', book_data = book_data, user=current_user.name)

def book():
    book_row = Product.get_all_product()
    book_data = []
    for i in book_row:
        book = {
            '課程編號': i[0],
            '課程名稱': i[4],
            '課程費用': i[1],
            '教師名稱': i[7],
            '開課時間': i[2],
            '課程描述': i[3],
            '堂數': i[8],
        }
        book_data.append(book)
    return book_data

@manager.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = ""
        while(data != None):
            number = str(random.randrange( 10000, 99999))
            en = random.choice(string.ascii_letters)
            courseID = en + number
            data = Product.get_product(courseID)

        name = request.values.get('name')
        teacher = request.values.get('teacher')
        courseDate = request.values.get('courseDate')
        courseTime = request.values.get('courseTime')
        Week = request.values.get('Week')
        price = request.values.get('price')
        category = request.values.get('category')
        description = request.values.get('description')
        
        # Convert string to date object
        courseDate = datetime.strptime(courseDate, '%Y-%m-%d').date()
        if (len(name) < 1 or len(price) < 1):
            return redirect(url_for('manager.productManager'))

        product_exist = Product.get_product_by_name(name)
        if product_exist:
            return f'''          
            <script> alert('新增失敗！原因：商品名稱重複')
            window.location.href = '{url_for('manager.productManager')}';</script>
            '''

        Product.add_product(
            {'pid' : courseID,
             'name' : name,
             'teacher' : teacher,
             'courseDate' : courseDate,
             'courseTime' : courseTime,
             'Week' : Week,
             'price' : price,
             'category' : category,
             'description' : description,
            }
        )

        return redirect(url_for('manager.productManager'))

    return render_template('productManager.html')

@manager.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('bookstore'))

    if request.method == 'POST':
        Product.update_product(
            {
            'name' : request.values.get('name'),
            'price' : request.values.get('price'),
            'courseDate' : datetime.strptime(request.values.get('courseDate'), '%Y-%m-%d').date(),
            'teacher' : request.values.get('teacher'),
            'courseTime' : request.values.get('courseTime'),
            'Week' : request.values.get('Week'),
            'category' : request.values.get('category'), 
            'description' : request.values.get('description'),
            'pid' : request.values.get('pid')
            }
        )
        
        return redirect(url_for('manager.productManager'))

    else:
        product = show_info()
        return render_template('edit.html', data=product)


def show_info():
    pid = request.args['pid']
    data = Product.get_product(pid)
    name = data[4]
    starttime = data[2]
    price = data[1]
    teacher = data[7]
    category = data[8]
    description = data[3]
    courseTime = data[5]
    week = data[6]

    product = {
        '課程編號': pid,
        '課程名稱': name,
        '教師名稱': teacher,
        '開課日期': starttime,
        '開課時間': courseTime,
        '每週開課日': week,
        '課程費用': price,
        '堂數': category,
        '課程描述': description
    }
    return product


@manager.route('/orderManager', methods=['GET', 'POST'])
@login_required
def orderManager():
    if request.method == 'POST':
        pass
    else:
        order_row = Order_List.get_order()
        order_data = []
        for i in order_row:
            order = {
                '訂單編號': i[0],
                '訂購人': i[1],
                '訂單總價': i[2],
                '訂單時間': i[3]
            }
            order_data.append(order)
            
        orderdetail_row = Order_List.get_orderdetail()
        order_detail = []

        for j in orderdetail_row:
            orderdetail = {
                '訂單編號': j[0],
                '商品名稱': j[1],
                '商品單價': j[2],
                '訂購數量': j[3]
            }
            order_detail.append(orderdetail)

    return render_template('orderManager.html', orderData = order_data, orderDetail = order_detail, user=current_user.name)