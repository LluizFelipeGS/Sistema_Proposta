import sqlite3
import os

DB_PATH = "instance/propostas.db"

# remove o arquivo do banco antigo (se existir)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("🗑️ Banco antigo removido.")

# cria novo banco
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# recria a tabela
cursor.execute("""
CREATE TABLE propostas (
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

print("✅ Novo banco criado com tabela 'propostas' limpa.")
