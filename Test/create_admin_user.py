from app import app
from models import db, Usuario

def create_admin_user():
    with app.app_context():
        # Verificar se já existe um usuário admin
        admin_user = Usuario.query.filter_by(username='admin').first()
        
        if not admin_user:
            admin = Usuario()
            admin.username = 'lfsilva'
            admin.email = 'lzgomes2601@gmail.com'
            admin.nome_completo = 'Luiz Felipe Gomes'
            admin.cargo = 'Administrador'
            admin.departamento = 'TI'
            admin.set_password('15k07A')
            
            db.session.add(admin)
            db.session.commit()
            print("Usuário administrador criado com sucesso!")
            print("Username: {admin.username}")
        else:
            print("Usuário administrador já existe!")

if __name__ == '__main__':
    create_admin_user()

