from app import app, db, Proposta
from datetime import date, datetime

def add_sample_data():
    """Adiciona dados de exemplo no banco de dados."""
    
    with app.app_context():
        # Verificar se já existem propostas
        if Proposta.query.count() > 0:
            print("Já existem propostas no banco de dados.")
            return
        
        # Criar propostas de exemplo
        propostas_exemplo = [
            {
                'tipo_contrato': 'Plano Saúde A',
                'numero_proposta': 'PROP001',
                'cliente_contratante': 'Empresa ABC Ltda',
                'quantidade_vidas': 50,
                'vendedor': 'Carlos Vendedor',
                'corretora': 'Corretora XYZ',
                'data_criacao': date(2024, 1, 15),
                'data_vigencia': date(2024, 2, 1),
                'valor': 15000.00,
                'status': 'Aprovado',
                'colaborador': 'admin'
            },
            {
                'tipo_contrato': 'Plano Saúde B',
                'numero_proposta': 'PROP002',
                'cliente_contratante': 'João Silva',
                'quantidade_vidas': 1,
                'vendedor': 'Ana Vendedora',
                'corretora': 'Corretora ABC',
                'data_criacao': date(2024, 1, 20),
                'data_vigencia': date(2024, 2, 1),
                'valor': 350.00,
                'status': 'Em Análise',
                'colaborador': 'admin'
            },
            {
                'tipo_contrato': 'Plano Odonto C',
                'numero_proposta': 'PROP003',
                'cliente_contratante': 'Maria Santos',
                'quantidade_vidas': 3,
                'vendedor': 'Pedro Vendedor',
                'corretora': 'Corretora 123',
                'data_criacao': date(2024, 1, 25),
                'data_vigencia': date(2024, 3, 1),
                'valor': 850.00,
                'status': 'Pendente',
                'colaborador': 'admin'
            },
            {
                'tipo_contrato': 'Plano Empresarial',
                'numero_proposta': 'PROP004',
                'cliente_contratante': 'Tech Solutions Ltda',
                'quantidade_vidas': 25,
                'vendedor': 'Carlos Vendedor',
                'corretora': 'Corretora XYZ',
                'data_criacao': date(2024, 2, 1),
                'data_vigencia': date(2024, 3, 1),
                'valor': 8500.00,
                'status': 'Aprovado',
                'colaborador': 'admin'
            },
            {
                'tipo_contrato': 'Plano Individual',
                'numero_proposta': 'PROP005',
                'cliente_contratante': 'Roberto Costa',
                'quantidade_vidas': 2,
                'vendedor': 'Ana Vendedora',
                'corretora': 'Corretora ABC',
                'data_criacao': date(2024, 2, 5),
                'data_vigencia': date(2024, 3, 1),
                'valor': 720.00,
                'status': 'Rejeitado',
                'colaborador': 'admin'
            }
        ]
        
        # Adicionar propostas ao banco
        for proposta_data in propostas_exemplo:
            proposta = Proposta()
            for campo, valor in proposta_data.items():
                setattr(proposta, campo, valor)
            
            db.session.add(proposta)
        
        db.session.commit()
        print(f"✅ {len(propostas_exemplo)} propostas de exemplo adicionadas com sucesso!")

if __name__ == "__main__":
    add_sample_data()

