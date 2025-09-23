import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json

# Configurações
BASE_URL = "http://localhost:5000"
USERNAME = "admin"
PASSWORD = "admin"

class PropostasAPI:
    """Cliente para consumir a API do sistema de propostas."""
    
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.session = requests.Session()
        self.login(username, password)
    
    def login(self, username, password):
        """Faz login na API."""
        login_data = {'username': username, 'password': password}
        response = self.session.post(f"{self.base_url}/login", data=login_data)
        if response.status_code != 200:
            raise Exception("Erro no login")
        print("✅ Login realizado com sucesso!")
    
    def get_propostas(self, **filtros):
        """Obtém propostas da API com filtros opcionais."""
        response = self.session.get(f"{self.base_url}/api/propostas", params=filtros)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro ao obter propostas: {response.status_code}")
    
    def get_usuarios(self):
        """Obtém usuários da API."""
        response = self.session.get(f"{self.base_url}/api/usuarios")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro ao obter usuários: {response.status_code}")
    
    def get_dashboard_resumo(self):
        """Obtém dados resumidos para dashboard."""
        response = self.session.get(f"{self.base_url}/api/dashboard/resumo")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro ao obter resumo: {response.status_code}")

def criar_dashboard():
    """Cria um dashboard com gráficos usando os dados da API."""
    
    # Conectar à API
    api = PropostasAPI(BASE_URL, USERNAME, PASSWORD)
    
    # Obter dados
    print("📊 Obtendo dados da API...")
    propostas_data = api.get_propostas(per_page=1000)  # Obter todas as propostas
    resumo_data = api.get_dashboard_resumo()
    
    # Converter para DataFrame
    df_propostas = pd.DataFrame(propostas_data['data'])
    
    if df_propostas.empty:
        print("❌ Nenhuma proposta encontrada!")
        return
    
    # Configurar estilo dos gráficos
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Dashboard - Sistema de Propostas', fontsize=16, fontweight='bold')
    
    # Gráfico 1: Propostas por Status
    status_data = resumo_data['propostas_por_status']
    status_df = pd.DataFrame(status_data)
    
    axes[0, 0].pie(status_df['count'], labels=status_df['status'], autopct='%1.1f%%', startangle=90)
    axes[0, 0].set_title('Distribuição por Status')
    
    # Gráfico 2: Propostas por Vendedor
    vendedor_data = resumo_data['propostas_por_vendedor']
    vendedor_df = pd.DataFrame(vendedor_data)
    
    if not vendedor_df.empty:
        axes[0, 1].bar(vendedor_df['vendedor'], vendedor_df['count'])
        axes[0, 1].set_title('Propostas por Vendedor')
        axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Gráfico 3: Valor das Propostas
    if 'valor' in df_propostas.columns:
        df_propostas['valor'] = pd.to_numeric(df_propostas['valor'], errors='coerce')
        valores_por_status = df_propostas.groupby('status')['valor'].sum()
        
        axes[1, 0].bar(valores_por_status.index, valores_por_status.values)
        axes[1, 0].set_title('Valor Total por Status')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
    
    # Gráfico 4: Propostas por Mês
    mes_data = resumo_data['propostas_por_mes']
    if mes_data:
        mes_df = pd.DataFrame(mes_data)
        mes_df['periodo'] = mes_df['ano'].astype(str) + '-' + mes_df['mes'].astype(str).str.zfill(2)
        
        axes[1, 1].plot(mes_df['periodo'], mes_df['count'], marker='o')
        axes[1, 1].set_title('Propostas por Mês')
        axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('dashboard_propostas.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Exibir estatísticas
    print("\n📈 ESTATÍSTICAS GERAIS:")
    print(f"Total de Propostas: {resumo_data['totais']['propostas']}")
    print(f"Total de Usuários: {resumo_data['totais']['usuarios']}")
    print(f"Valor Total: R$ {resumo_data['totais']['valor_total']:,.2f}")
    
    print("\n📊 PROPOSTAS POR STATUS:")
    for item in status_data:
        print(f"  {item['status']}: {item['count']} propostas")
    
    print("\n🏆 TOP VENDEDORES:")
    for item in vendedor_data[:5]:
        print(f"  {item['vendedor']}: {item['count']} propostas")

def exemplo_analise_avancada():
    """Exemplo de análise mais avançada usando pandas."""
    
    api = PropostasAPI(BASE_URL, USERNAME, PASSWORD)
    
    # Obter todas as propostas
    propostas_data = api.get_propostas(per_page=1000)
    df = pd.DataFrame(propostas_data['data'])
    
    if df.empty:
        print("❌ Nenhuma proposta encontrada!")
        return
    
    # Converter tipos de dados
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    df['quantidade_vidas'] = pd.to_numeric(df['quantidade_vidas'], errors='coerce')
    df['data_criacao'] = pd.to_datetime(df['data_criacao'])
    
    print("\n🔍 ANÁLISE AVANÇADA:")
    
    # Estatísticas descritivas
    print("\n📊 Estatísticas de Valor:")
    print(df['valor'].describe())
    
    # Análise por vendedor
    print("\n👥 Análise por Vendedor:")
    vendedor_stats = df.groupby('vendedor').agg({
        'valor': ['count', 'sum', 'mean'],
        'quantidade_vidas': 'sum'
    }).round(2)
    print(vendedor_stats)
    
    # Análise temporal
    print("\n📅 Análise Temporal:")
    df['mes_ano'] = df['data_criacao'].dt.to_period('M')
    temporal_stats = df.groupby('mes_ano').agg({
        'valor': ['count', 'sum'],
        'quantidade_vidas': 'sum'
    })
    print(temporal_stats)

if __name__ == "__main__":
    try:
        print("🚀 Iniciando criação do dashboard...")
        criar_dashboard()
        
        print("\n🔍 Executando análise avançada...")
        exemplo_analise_avancada()
        
        print("\n✅ Dashboard criado com sucesso!")
        print("📁 Arquivo salvo: dashboard_propostas.png")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("💡 Certifique-se de que o servidor Flask está rodando em http://localhost:5000")

