import requests
import json

# Configurações
BASE_URL = "http://localhost:5000"
USERNAME = "admin"
PASSWORD = "admin"

def test_api():
    """Testa todos os endpoints da API."""
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    print("🔐 Fazendo login...")
    # Fazer login
    login_data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    
    login_response = session.post(f"{BASE_URL}/login", data=login_data)
    
    if login_response.status_code == 200:
        print("✅ Login realizado com sucesso!")
    else:
        print("❌ Erro no login!")
        return
    
    # Testar endpoint de propostas
    print("\n📋 Testando endpoint /api/propostas...")
    propostas_response = session.get(f"{BASE_URL}/api/propostas")
    
    if propostas_response.status_code == 200:
        propostas_data = propostas_response.json()
        print(f"✅ Propostas obtidas: {len(propostas_data['data'])} registros")
        print(f"📊 Total de propostas: {propostas_data['pagination']['total']}")
        
        # Mostrar primeira proposta como exemplo
        if propostas_data['data']:
            print("📄 Exemplo de proposta:")
            print(json.dumps(propostas_data['data'][0], indent=2, ensure_ascii=False))
    else:
        print(f"❌ Erro ao obter propostas: {propostas_response.status_code}")
    
    # Testar endpoint de usuários
    print("\n👥 Testando endpoint /api/usuarios...")
    usuarios_response = session.get(f"{BASE_URL}/api/usuarios")
    
    if usuarios_response.status_code == 200:
        usuarios_data = usuarios_response.json()
        print(f"✅ Usuários obtidos: {len(usuarios_data['data'])} registros")
        
        # Mostrar primeiro usuário como exemplo
        if usuarios_data['data']:
            print("👤 Exemplo de usuário:")
            print(json.dumps(usuarios_data['data'][0], indent=2, ensure_ascii=False))
    else:
        print(f"❌ Erro ao obter usuários: {usuarios_response.status_code}")
    
    # Testar endpoint de histórico
    print("\n📝 Testando endpoint /api/historico...")
    historico_response = session.get(f"{BASE_URL}/api/historico")
    
    if historico_response.status_code == 200:
        historico_data = historico_response.json()
        print(f"✅ Histórico obtido: {len(historico_data['data'])} registros")
        print(f"📊 Total de registros de histórico: {historico_data['pagination']['total']}")
        
        # Mostrar primeiro registro como exemplo
        if historico_data['data']:
            print("📋 Exemplo de registro de histórico:")
            print(json.dumps(historico_data['data'][0], indent=2, ensure_ascii=False))
    else:
        print(f"❌ Erro ao obter histórico: {historico_response.status_code}")
    
    # Testar endpoint de resumo do dashboard
    print("\n📊 Testando endpoint /api/dashboard/resumo...")
    resumo_response = session.get(f"{BASE_URL}/api/dashboard/resumo")
    
    if resumo_response.status_code == 200:
        resumo_data = resumo_response.json()
        print("✅ Resumo do dashboard obtido:")
        print(f"📈 Total de propostas: {resumo_data['totais']['propostas']}")
        print(f"👥 Total de usuários: {resumo_data['totais']['usuarios']}")
        print(f"💰 Valor total: R$ {resumo_data['totais']['valor_total']:,.2f}")
        
        print("\n📊 Propostas por status:")
        for item in resumo_data['propostas_por_status']:
            print(f"  - {item['status']}: {item['count']}")
        
        print("\n🏆 Top vendedores:")
        for item in resumo_data['propostas_por_vendedor'][:5]:
            print(f"  - {item['vendedor']}: {item['count']} propostas")
    else:
        print(f"❌ Erro ao obter resumo: {resumo_response.status_code}")
    
    # Testar filtros na API de propostas
    print("\n🔍 Testando filtros na API de propostas...")
    filtros_response = session.get(f"{BASE_URL}/api/propostas?per_page=5&status=Aprovado")
    
    if filtros_response.status_code == 200:
        filtros_data = filtros_response.json()
        print(f"✅ Propostas filtradas (status=Aprovado): {len(filtros_data['data'])} registros")
    else:
        print(f"❌ Erro ao testar filtros: {filtros_response.status_code}")
    
    print("\n🎉 Teste da API concluído!")

if __name__ == "__main__":
    test_api()

