
import sys
from app import app, db
from models import Usuario, Proposta, HistoricoAlteracao, LogAcesso, Domain, Permission, Role
from datetime import datetime


def init_database():
    """Cria tabelas do banco se não existirem"""
    with app.app_context():
        print("Conectando ao banco de dados...")
        db.create_all()
        print("✓ Tabelas criadas/verificadas com sucesso!")


def seed_roles():
    """Cria os domínios, permissões e roles padrão"""
    with app.app_context():
        # Limpar registros antigos (⚠️ cuidado em produção!)
        db.session.query(Role).delete()
        db.session.query(Permission).delete()
        db.session.query(Domain).delete()
        db.session.commit()

        # ===== DOMÍNIOS =====
        dominios = {
            "usuarios": "Gerenciar usuários do sistema",
            "propostas": "Gerenciar propostas jurídicas",
            "logs": "Acessar logs do sistema"
        }

        domain_objs = {}
        for nome, desc in dominios.items():
            d = Domain(nome=nome, descricao=desc)
            db.session.add(d)
            domain_objs[nome] = d
        db.session.commit()

        # ===== PERMISSÕES =====
        permissoes = {
            "usuarios": ["criar_usuario", "editar_usuario", "deletar_usuario", "listar_usuarios"],
            "propostas": ["criar_proposta", "editar_proposta", "deletar_proposta", "listar_propostas"],
            "logs": ["ver_logs"]
        }

        perm_objs = {}
        for dominio, perms in permissoes.items():
            for p in perms:
                perm = Permission(nome=p, domain=domain_objs[dominio])
                db.session.add(perm)
                perm_objs[p] = perm
        db.session.commit()

        # ===== ROLES =====
        admin_role = Role(nome="admin")
        admin_role.permissions = list(perm_objs.values())

        advogado_role = Role(nome="advogado")
        advogado_role.permissions = [p for k, p in perm_objs.items() if k not in ["criar_usuario", "ver_logs"]]

        assistente_role = Role(nome="assistente")
        assistente_role.permissions = [p for k, p in perm_objs.items() if k not in ["criar_usuario", "ver_logs", "deletar_proposta", "deletar_usuario"]]

        analista_role = Role(nome="analista")
        analista_role.permissions = advogado_role.permissions

        supervisao_role = Role(nome="supervisao")
        supervisao_role.permissions = list(perm_objs.values())

        db.session.add_all([admin_role, advogado_role, assistente_role, analista_role, supervisao_role])
        db.session.commit()

        print("✓ Roles, Domains e Permissions criados com sucesso!")


def create_admin_user():
    """Cria usuário admin padrão se não existir"""
    with app.app_context():
        admin_user = Usuario.query.filter_by(username="lfsilva").first()
        if not admin_user:
            admin_role = Role.query.filter_by(nome="luiz Felipe").first()
            if not admin_role:
                print("❌ Role 'admin' não encontrada. Rode seed_roles primeiro.")
                return

            admin = Usuario(
                username="lfsilva",
                email="admin@sistema.com",
                nome_completo="Administrador do Sistema",
                cargo="Administrador",
                departamento="TI"
            )
            admin.set_password("15k07A")  
            admin.role_id = admin_role.id

            db.session.add(admin)
            db.session.commit()
            print("✓ Usuário administrador criado")
        else:
            print("✓ Usuário administrador já existe")


if __name__ == "__main__":
    print("=== Inicialização do Banco ===")
    init_database()
    seed_roles()
    create_admin_user()
    print("\n✅ Banco inicializado com sucesso!")
