import sqlite3

# Caminho do banco (ajuste se quiser fora do OneDrive)
DB_PATH = "instance/propostas.db"

# Criação do banco
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Criar tabela "propostas"
cursor.execute("""
CREATE TABLE IF NOT EXISTS propostas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_contrato TEXT NOT NULL,
    numero_proposta TEXT NOT NULL,
    cliente_contratante TEXT NOT NULL,
    quantidade_vidas INTEGER,
    vendedor TEXT,
    corretora TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_vigencia DATE,
    operadora_nome TEXT,
    valor REAL
);
""")

conn.commit()
conn.close()

print(f"✅ Banco criado em {DB_PATH} com tabela 'propostas'")
