
import bcrypt

# Hash a password
def generate_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Check a password
def check_password(input_password, saved_password):
    try:
        return bcrypt.checkpw(input_password.encode('utf-8'), saved_password.encode('utf-8'))
    except ValueError as e:
        print("Invalid:", e)
        return False

