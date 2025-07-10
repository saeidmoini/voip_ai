from flask import Flask, render_template, request, redirect, url_for, flash, make_response, Response, jsonify
from src.model import User, validate_phone, LoginUser
import uuid
import datetime
from peewee import DoesNotExist
import json
from app.pricing import increase_all_prices


app = Flask(__name__)
app.secret_key = '8907654321'

@app.route('/', methods=['Get', 'POST'])
def index():
    users = User.select()
    auth_token = request.cookies.get('auth_token')

    if not auth_token:
        flash('لطفاً ابتدا وارد شوید', 'warning')
        return redirect(url_for('login'))

    try:
        login_user = LoginUser.get(LoginUser.auth_token == auth_token)
    except LoginUser.DoesNotExist:
        flash('لطفاً ابتدا وارد شوید', 'warning')
        return redirect(url_for('login'))

    return render_template('index.html', username=login_user.username, users=users)

@app.route('/price-panel', methods=['Get', 'POST'])
def price_panel_page():
    users = User.select()
    auth_token = request.cookies.get('auth_token')

    if not auth_token:
        flash('لطفاً ابتدا وارد شوید', 'warning')
        return redirect(url_for('login'))

    try:
        login_user = LoginUser.get(LoginUser.auth_token == auth_token)
    except LoginUser.DoesNotExist:
        flash('لطفاً ابتدا وارد شوید', 'warning')
        return redirect(url_for('login'))

    with open("static/Pricing.json", "r") as f:
        price_data = json.load(f)

    return render_template('price_panel.html', username=login_user.username, price_data=price_data)

@app.route('/api/increase-prices', methods=['POST'])
def increase_price_api():
    users = User.select()
    auth_token = request.cookies.get('auth_token')

    if not auth_token:
        return Response("login requered to use this api"), 401

    try:
        login_user = LoginUser.get(LoginUser.auth_token == auth_token)
    except LoginUser.DoesNotExist:
        return Response("login requered to use this api"), 401

    try:
        increase_value = float(request.args.get('increase_value'))
    except Exception as e:
        return Response("Error in increase prices"), 500

    try:
        if increase_value :
            increase_all_prices(percentage_increase=increase_value)
            return Response("prices increased successful"), 200
        else:
            return Response("increase_value requered to use this api"), 400
    except Exception as e:
        return Response("Error in increase prices"), 500

@app.route('/api/get-prd-explain-text', methods=['GET'])
def get_prd_explain_text():
    try:
        with open("static/editable_invoice_data.json", "r") as f:
            data = json.load(f)
        
        return jsonify({"text": data["product_explain_text"]})
    except Exception as e:
        return Response("Error in get prd explain text"), 500

@app.route('/api/get-description-text', methods=['GET'])
def get_description_text():
    try:
        with open("static/editable_invoice_data.json", "r") as f:
            data = json.load(f)

        return jsonify({"text": data["description_text"]})
    except Exception as e:
        return Response("Error in get description text"), 500

@app.route('/api/set-prd-explain-text', methods=['POST'])
def set_prd_explain_text():
    try:
        data = request.get_json()
        with open("static/editable_invoice_data.json", "r") as f:
            existing_data = json.load(f)
            existing_data["product_explain_text"] = data["text"]
        with open("static/editable_invoice_data.json", "w") as f:
                json.dump(existing_data, f)
        return Response("Text updated successfully"), 200
    except Exception as e:
        return Response("Error in set prd explain text"), 500
    
@app.route('/api/set-description-text', methods=['POST'])
def set_description_text():
    try:
        data = request.get_json()
        with open("static/editable_invoice_data.json", "r") as f:
            existing_data = json.load(f)
            existing_data["description_text"] = data["text"]
        with open("static/editable_invoice_data.json", "w") as f:
                json.dump(existing_data, f)
        
        return Response("Text updated successfully"), 200
    except Exception as e:
        return Response("Error in set description text"), 500



# مسیر حذف کاربر
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        user = User.get(user_id)  # پیدا کردن کاربر بر اساس شناسه
        user.delete_instance()  # حذف کاربر از دیتابیس
        print(f"User with id {user_id} deleted successfully.")  # چاپ پیغام در کنسول
        return redirect(url_for('index'))  # بازگشت به صفحه اصلی بعد از حذف
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # چاپ خطا در کنسول
        return redirect(url_for('index'))  # در صورت خطا، بازگشت به صفحه اصلی


@app.route('/add_user', methods=['POST'])
def add_user():
    users = User.select()  # بارگذاری مجدد کاربران از دیتابیس
    name = request.form['name']
    telephone = validate_phone(request.form['telephone'])
    city = request.form['city']
    coldrooms_code = request.form['coldrooms_code']
    coldrooms_phone = validate_phone(request.form['coldrooms_phone'])

    if not telephone:
        return render_template('index.html', message='شماره تلفن نامعتبر است.', error=True, users=users)

    try:
        # ذخیره اطلاعات در دیتابیس
        User.create(
            name=name,
            telephone=telephone,
            city=city,
            coldrooms_code=coldrooms_code,
            coldrooms_phone=coldrooms_phone
        )
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # چاپ خطا در کنسول سرور
        return redirect(url_for('index'))


@app.route('/edit_user', methods=['POST'])
def edit_user():
    users = User.select()
    id = request.form.get('id')

    if not id:
        return render_template('index.html', message='شناسه کاربر نامعتبر است.', error=True, users=users)

    try:
        user = User.get(User.id == id)
        rows_updated = User.update(
            name=request.form['name'],
            telephone=validate_phone(request.form['telephone']),
            city=request.form['city'],
            coldrooms_code=request.form['coldrooms_code'],
            coldrooms_phone=validate_phone(request.form['coldrooms_phone'])
        ).where(User.id == user.id).execute()

        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return render_template('index.html', message='خطا در ویرایش کاربر', error=True, users=users)


# مسیر صفحه لاگین
@app.route('/login', methods=['Get', 'POST'])
def login():
    auth_token = request.cookies.get('auth_token')

    if not auth_token:
        print("User not found")
        return render_template('login.html')

    try:
        user = LoginUser.get(LoginUser.auth_token == auth_token)
        return redirect(url_for('index'))
    except:
        print("User not found")
        return render_template('login.html')


# چک کردن اعتبارات ورود کاربر
@app.route('/check_login', methods=['POST'])
def check_login():
    username = request.form['username']
    password = request.form['password']
    try:
        user = LoginUser.get(LoginUser.username == username)
    except DoesNotExist:
        flash('Username does not exist', 'danger')
        return redirect(url_for('login'))

    if user.password == password:
        # ایجاد توکن منحصر به فرد
        auth_token = str(uuid.uuid4())

        # ذخیره توکن در دیتابیس
        LoginUser.update(auth_token=auth_token).where(LoginUser.id == user.id).execute()

        # تنظیم کوکی
        resp = make_response(redirect(url_for('index')))
        expires = datetime.datetime.now() + datetime.timedelta(days=100)
        resp.set_cookie('auth_token', auth_token, expires=expires, httponly=True)

        return resp
    else:
        flash('نام کاربری یا رمز عبور نادرست است', 'danger')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    auth_token = request.cookies.get('auth_token')

    if auth_token:
        # حذف توکن از دیتابیس
        LoginUser.update(auth_token=None).where(LoginUser.auth_token == auth_token).execute()

    # حذف کوکی
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('auth_token', '', expires=0)

    return resp


if __name__ == '__main__':
    app.run(debug=True)
