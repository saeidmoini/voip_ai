from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Response, flash, \
    make_response
from src.model import User, validate_phone, LoginUser
from myhash import generate_password_hash, check_password_hash
import uuid
import datetime

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
        print("User not found 2")
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
        print(f"Username: {username}, Password: {password}")
        us = LoginUser.select()
        for u in us:
            print(f"User: {u.username}, Password: {u.password}")

        user = LoginUser.get(LoginUser.username == username)
        print(check_password_hash(user.password, password))
    except LoginUser.DoesNotExist:
        flash('نام کاربری یا رمز عبور نادرست است', 'danger')
        return redirect(url_for('login'))

    if check_password_hash(user.password, password):
        # ایجاد توکن منحصر به فرد
        auth_token = str(uuid.uuid4())

        # ذخیره توکن در دیتابیس
        LoginUser.update(auth_token=auth_token).where(LoginUser.id == user.id).execute()

        # تنظیم کوکی
        resp = make_response(redirect(url_for('index')))
        expires = datetime.datetime.now() + datetime.timedelta(days=100)
        resp.set_cookie('auth_token', auth_token, expires=expires, httponly=True, secure=True)

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
