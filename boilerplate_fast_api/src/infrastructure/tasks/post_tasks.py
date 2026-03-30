import time
from faker import Faker
from src.infrastructure.database.session import SessionLocal
from src.infrastructure.repositories.post_sqlalchemy import PostSQLAlchemyRepository
from src.infrastructure.database.models.user_model import UserModel
from src.modules.posts.service import PostService

fake = Faker()

def generate_fake_post_task(author_id: int):
    """
    Background job properties:
    Simula uma latência de processamento em background, 
    abre sua própria conexão/sessão limpa de banco de dados e
    insere um post "fake" atrelado ao usuário solicitante.
    """
    time.sleep(3)  # Simula um trabalho pesado demorado

    db = SessionLocal()
    try:
        repo = PostSQLAlchemyRepository(db)
        service = PostService(repo)
        
        # Gerando dados fakes
        title = fake.sentence(nb_words=6)
        content = fake.text(max_nb_chars=200)
        
        # Inserindo via arquitetura padrão (Service)
        service.create(title=title, content=content, author_id=author_id)
    finally:
        db.close()


def generate_scheduled_fake_post():
    """
    Cron job function that runs according to a schedule to generate a fake post.
    Searches for the first user or creates a 'system' user to accurately map author_id.
    """
    db = SessionLocal()
    try:
        user = db.query(UserModel).first()
        if not user:
            user = UserModel(email="system@cronjob.local", password_hash="dummy", role="system")
            db.add(user)
            db.commit()
            db.refresh(user)

        repo = PostSQLAlchemyRepository(db)
        service = PostService(repo)
        
        # Gerando dados fakes
        title = f"[Scheduled] {fake.sentence(nb_words=6)}"
        content = f"Gerado automaticamente pelo APScheduler.\n\n{fake.text(max_nb_chars=120)}"
        
        # Inserindo
        service.create(title=title, content=content, author_id=user.id)
    finally:
        db.close()
