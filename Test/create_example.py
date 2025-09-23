import pandas as pd
from datetime import datetime, date

# Dados de exemplo
data = {
    'contrato': ['Plano Saúde A', 'Plano Saúde B', 'Plano Odonto C'],
    'oper_propnum': ['PROP001', 'PROP002', 'PROP003'],
    'contratante_nome': ['Empresa ABC Ltda', 'João Silva', 'Maria Santos'],
    'beneficiarios': [50, 1, 3],
    'vendedor_nome': ['Carlos Vendedor', 'Ana Vendedora', 'Pedro Vendedor'],
    'corretora_nome': ['Corretora XYZ', 'Corretora ABC', 'Corretora 123'],
    'data_criacao': [date(2024, 1, 15), date(2024, 1, 20), date(2024, 1, 25)],
    'data_vigencia': [date(2024, 2, 1), date(2024, 2, 1), date(2024, 3, 1)],
    'valor': [15000.00, 350.00, 850.00]
}

df = pd.DataFrame(data)
df.to_excel('exemplo_planilha.xlsx', index=False)
print("Planilha de exemplo criada com sucesso!")

