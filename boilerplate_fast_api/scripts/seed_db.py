import sys
import os

# Adiciona o diretório atual ao sys.path para reconhecer o pacote 'src'
sys.path.append(os.getcwd())

from src.infrastructure.database.session import SessionLocal
from src.infrastructure.database.models.user_model import UserModel
from src.infrastructure.security.password import PasswordHasher

def seed():
    print("🌱 Iniciando o seed do banco de dados...")
    db = SessionLocal()
    try:
        # --- Criar Usuário Admin Padrão ---
        admin_email = "admin@example.com"
        admin_pass = "admin123"
        
        user = db.query(UserModel).filter(UserModel.email == admin_email).first()
        if not user:
            print(f"Criando usuário administrador: {admin_email}...")
            new_admin = UserModel(
                email=admin_email,
                password_hash=PasswordHasher.hash(admin_pass),
                role="admin"
            )
            db.add(new_admin)
            db.commit()
            print(f"✅ Usuário '{admin_email}' com senha '{admin_pass}' criado com sucesso!")
        else:
            print(f"ℹ️ Usuário '{admin_email}' já existe no banco.")

        # --- Criar Segundo Usuário (ID 2) ---
        guest_email = "user@example.com"
        user2 = db.query(UserModel).filter(UserModel.email == guest_email).first()
        if not user2:
            print(f"Criando usuário convidado: {guest_email}...")
            new_guest = UserModel(
                email=guest_email,
                password_hash=PasswordHasher.hash("user123"),
                role="user"
            )
            db.add(new_guest)
            db.commit()
            print(f"✅ Usuário '{guest_email}' (senha: 'user123') criado com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao semear o banco: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
