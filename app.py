from flask import Flask, render_template, request, jsonify, redirect, url_for
from model import database, User, validate_phone
app = Flask(__name__)

@app.route('/', methods=['Get', 'POST'])
def home():

    query = request.form.get('query')
    if query:
        # جستجو در پایگاه داده (بر اساس نام یا شماره تلفن)
        users = User.select().where(
            (User.name.contains(query)) |
            (User.telephone.contains(query)) |
            (User.coldrooms_code.contains(query))
        )
    else:
        # اگر جستجویی وجود ندارد، تمام کاربران را واکشی کن
        users = User.select()

    return render_template('index.html', users=users)

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
    coldrooms_code = request.form['coldrooms_code']
    coldrooms_phone = validate_phone(request.form['coldrooms_phone'])

    if not telephone:
        return render_template('index.html', message='شماره تلفن نامعتبر است.', error=True, users=users)

    try:
        # ذخیره اطلاعات در دیتابیس
        User.create(
            name=name,
            telephone=telephone,
            coldrooms_code=coldrooms_code,
            coldrooms_phone=coldrooms_phone
        )
        users = User.select()  # بارگذاری مجدد کاربران از دیتابیس
        return render_template('index.html', message='اطلاعات با موفقیت ثبت شد.', error=False, users=users)
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # چاپ خطا در کنسول سرور
        users = User.select()  # بارگذاری مجدد کاربران از دیتابیس
        return render_template('index.html', message=f'خطا در ذخیره اطلاعات: {str(e)}', error=True, users=users)

if __name__ == "__main__":
    app.run()
