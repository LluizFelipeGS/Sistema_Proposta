import pandas as pd
from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///instance/propostas.db"

def extract_propostas_data():
    """Extrai dados da tabela Proposta do banco de dados SQLite."""
    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        
        # Carregar dados da tabela Proposta para um DataFrame do Pandas
        df_propostas = pd.read_sql_table("proposta", conn)
        
        conn.close()
        print("Dados da tabela Proposta extraídos com sucesso!")
        return df_propostas
    except Exception as e:
        print(f"Erro ao extrair dados: {e}")
        return None

def extract_historico_data():
    """Extrai dados da tabela HistoricoAlteracao do banco de dados SQLite."""
    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        
        # Carregar dados da tabela HistoricoAlteracao para um DataFrame do Pandas
        df_historico = pd.read_sql_table("historico_alteracao", conn)
        
        conn.close()
        print("Dados da tabela HistoricoAlteracao extraídos com sucesso!")
        return df_historico
    except Exception as e:
        print(f"Erro ao extrair dados do histórico: {e}")
        return None

if __name__ == "__main__":
    # Exemplo de uso:
    df_propostas = extract_propostas_data()
    if df_propostas is not None:
        print("\nPrimeiras 5 linhas da tabela Proposta:")
        print(df_propostas.head())
        print(f"Total de propostas: {len(df_propostas)}")

    df_historico = extract_historico_data()
    if df_historico is not None:
        print("\nPrimeiras 5 linhas da tabela HistoricoAlteracao:")
        print(df_historico.head())
        print(f"Total de registros de histórico: {len(df_historico)}")

    # Você pode salvar os DataFrames em CSV, Excel, etc., para usar em outras ferramentas
    # df_propostas.to_csv("propostas.csv", index=False)
    # df_historico.to_csv("historico.csv", index=False)


