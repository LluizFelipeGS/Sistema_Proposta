# manual_migration.py
from app import app, db
from sqlalchemy import text

def add_is_admin_column():
    with app.app_context():
        try:
            connection = db.engine.connect()
            
            # Verificar se a coluna já existe
            result = connection.execute(
                text("PRAGMA table_info(usuario)")
            ).fetchall()
            
            columns = [row[1] for row in result]
            
            if 'is_admin' not in columns:
                print("Adicionando coluna is_admin...")
                connection.execute(
                    text("ALTER TABLE usuario ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
                )
                print("Coluna is_admin adicionada com sucesso!")
                
                # Definir todos os usuários como não-admin por padrão
                connection.execute(
                    text("UPDATE usuario SET is_admin = FALSE")
                )
                print("Valores padrão definidos!")
            else:
                print("Coluna is_admin já existe.")
                
            connection.close()
            
        except Exception as e:
            print(f"Erro na migração: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_is_admin_column()