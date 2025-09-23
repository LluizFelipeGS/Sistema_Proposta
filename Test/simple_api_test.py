from app import app, db, Usuario, Proposta
import json

def test_api_endpoints():
    """Testa os endpoints da API usando o cliente de teste do Flask."""
    
    with app.test_client() as client:
        with app.app_context():
            print("🔐 Fazendo login...")
            
            # Fazer login
            login_response = client.post('/login', data={
                'username': 'admin',
                'password': 'admin'
            }, follow_redirects=True)
            
            print(f"Status do login: {login_response.status_code}")
            
            # Testar endpoint de propostas
            print("\n📋 Testando endpoint /api/propostas...")
            propostas_response = client.get('/api/propostas')
            
            if propostas_response.status_code == 200:
                propostas_data = propostas_response.get_json()
                print(f"✅ Propostas obtidas: {len(propostas_data['data'])} registros")
                print(f"📊 Total de propostas: {propostas_data['pagination']['total']}")
                
                # Mostrar estrutura da primeira proposta
                if propostas_data['data']:
                    print("📄 Campos disponíveis na proposta:")
                    for campo in propostas_data['data'][0].keys():
                        print(f"  - {campo}")
            else:
                print(f"❌ Erro ao obter propostas: {propostas_response.status_code}")
                print(f"Resposta: {propostas_response.get_data(as_text=True)}")
            
            # Testar endpoint de usuários
            print("\n👥 Testando endpoint /api/usuarios...")
            usuarios_response = client.get('/api/usuarios')
            
            if usuarios_response.status_code == 200:
                usuarios_data = usuarios_response.get_json()
                print(f"✅ Usuários obtidos: {len(usuarios_data['data'])} registros")
                
                # Mostrar estrutura do primeiro usuário
                if usuarios_data['data']:
                    print("👤 Campos disponíveis no usuário:")
                    for campo in usuarios_data['data'][0].keys():
                        print(f"  - {campo}")
            else:
                print(f"❌ Erro ao obter usuários: {usuarios_response.status_code}")
            
            # Testar endpoint de resumo do dashboard
            print("\n📊 Testando endpoint /api/dashboard/resumo...")
            resumo_response = client.get('/api/dashboard/resumo')
            
            if resumo_response.status_code == 200:
                resumo_data = resumo_response.get_json()
                print("✅ Resumo do dashboard obtido:")
                print(f"📈 Total de propostas: {resumo_data['totais']['propostas']}")
                print(f"👥 Total de usuários: {resumo_data['totais']['usuarios']}")
                print(f"💰 Valor total: R$ {resumo_data['totais']['valor_total']:,.2f}")
                
                print("\n📊 Estrutura do resumo:")
                for secao in resumo_data.keys():
                    print(f"  - {secao}")
            else:
                print(f"❌ Erro ao obter resumo: {resumo_response.status_code}")
            
            print("\n🎉 Teste da API concluído!")

if __name__ == "__main__":
    test_api_endpoints()

