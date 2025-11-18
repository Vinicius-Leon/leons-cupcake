from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(senha):
    return generate_password_hash(senha)

def verify_password(hash_senha, senha_digitada):
    return check_password_hash(hash_senha, senha_digitada)