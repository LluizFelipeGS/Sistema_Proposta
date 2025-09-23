#!/usr/bin/env python3
"""
Script para inicializar o banco de dados Supabase
Cria as tabelas necessárias e um usuário administrador padrão
"""

import os
import sys
from datetime import datetime
from app import app, db
from models import Usuario, Proposta, HistoricoAlteracao, LogAcesso

def init_database():
    """Inicializa o banco de dados criando as tabelas necessárias"""
    try:
        with app.app_context():
            print("Conectando ao banco de dados...")
            
            # Criar todas as tabelas
            db.create_all()
            print("✓ Tabelas criadas com sucesso!")
            
            # Verificar se já existe um usuário admin
            admin_user = Usuario.query.filter_by(username='admin').first()
            
            if not admin_user:
                # Criar usuário administrador padrão
                admin = Usuario()
                admin.username = 'lfsilva'
                admin.email = 'lzgomes2601@gmail.com'
                admin.nome_completo = 'Administrador do Sistema'
                admin.cargo = 'Administrador'
                admin.departamento = 'TI'
                admin.set_password('15k07A')  # Senha padrão - DEVE SER ALTERADA
                
                db.session.add(admin)
                db.session.commit()
                
                print("✓ Usuário administrador criado!")
                print("  Username: admin")
                print("  Senha: {admin.set_password}")
                print("  ⚠️  IMPORTANTE: Altere a senha padrão após o primeiro login!")
            else:
                print("✓ Usuário administrador já existe")
            
            # Testar a conexão fazendo uma consulta simples
            total_usuarios = Usuario.query.count()
            total_propostas = Proposta.query.count()
            
            print(f"✓ Conexão testada com sucesso!")
            print(f"  Total de usuários: {total_usuarios}")
            print(f"  Total de propostas: {total_propostas}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        return False

def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        with app.app_context():
            # Tentar fazer uma consulta simples
            result = db.session.execute(db.text("SELECT 1")).fetchone()
            if result:
                print("✓ Conexão com banco de dados OK")
                return True
            else:
                print("❌ Falha na conexão com banco de dados")
                return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

if __name__ == '__main__':
    print("=== Inicialização do Banco de Dados ===")
    print(f"DATABASE_URL: {app.config.get('SQLALCHEMY_DATABASE_URI', 'NÃO CONFIGURADA')}")
    print()
    
    # Testar conexão primeiro
    if test_connection():
        # Se conexão OK, inicializar banco
        if init_database():
            print("\n✅ Inicialização concluída com sucesso!")
            sys.exit(0)
        else:
            print("\n❌ Falha na inicialização")
            sys.exit(1)
    else:
        print("\n❌ Falha na conexão com banco de dados")
        print("Verifique se:")
        print("1. A variável DATABASE_URL está configurada corretamente")
        print("2. O banco de dados Supabase está acessível")
        print("3. As credenciais estão corretas")
        sys.exit(1)

