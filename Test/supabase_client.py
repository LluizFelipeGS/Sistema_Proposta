from supabase import create_client, Client
import os

# Substitua pelas credenciais do seu projeto
SUPABASE_URL = "postgresql://postgres:[15k07A26l.@]@db.cnijerxppxuwfihdfmci.supabase.co:5432/postgres"
SUPABASE_KEY = "15Ke26lz07AY@.202420032002"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Inserir uma proposta
def inserir_proposta(dados: dict):
    response = supabase.table("propostas").insert(dados).execute()
    return response.data

# Buscar propostas
def listar_propostas():
    response = supabase.table("propostas").select("*").execute()
    return response.data

# Exemplo de uso
if __name__ == "__main__":
    # Inserir registro de teste
    nova = {
        "tipo_contrato": "Adesão",
        "numero_proposta": "12345",
        "cliente_contratante": "João Silva",
        "quantidade_vidas": 4,
        "vendedor": "Maria Souza",
        "corretora": "Corretora XP",
        "data_vigencia": "2025-09-01",
        "operadora_nome": "Unimed",
        "valor": 1500.75,
    }
    print("Inserindo proposta:", inserir_proposta(nova))

    # Listar todas
    print("Listando propostas:", listar_propostas())
