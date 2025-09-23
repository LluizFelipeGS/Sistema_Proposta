# API do Sistema de Propostas - Documentação

## Visão Geral

A API do Sistema de Propostas permite acesso programático aos dados de propostas, usuários e histórico de alterações em formato JSON. Esta API é ideal para integração com ferramentas de Business Intelligence (BI), criação de dashboards personalizados ou análises de dados.

## Autenticação

A API utiliza autenticação baseada em sessão. É necessário fazer login antes de acessar os endpoints protegidos.

### Login
```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin
```

## Endpoints Disponíveis

### 1. Propostas

#### GET /api/propostas
Retorna lista de propostas com paginação e filtros.

**Parâmetros de Query:**
- `page` (int, opcional): Número da página (padrão: 1)
- `per_page` (int, opcional): Itens por página (padrão: 100, máximo: 1000)
- `status` (string, opcional): Filtrar por status
- `cliente` (string, opcional): Filtrar por nome do cliente
- `vendedor` (string, opcional): Filtrar por vendedor
- `data_inicio` (string, opcional): Data início no formato YYYY-MM-DD
- `data_fim` (string, opcional): Data fim no formato YYYY-MM-DD

**Exemplo de Resposta:**
```json
{
  "data": [
    {
      "id": 1,
      "tipo_contrato": "Plano Saúde A",
      "numero_proposta": "PROP001",
      "cliente_contratante": "Empresa ABC Ltda",
      "quantidade_vidas": 50,
      "vendedor": "Carlos Vendedor",
      "corretora": "Corretora XYZ",
      "data_criacao": "2024-01-15",
      "data_vigencia": "2024-02-01",
      "valor": 15000.0,
      "status": "Aprovado",
      "colaborador": "admin",
      "data_analise": null,
      "realizou_entrevista_medica": null,
      "status_area_medica": null,
      "motivo_declinio": null,
      "responsavel_digitacao": null,
      "data_cadastro_facplan": null,
      "api_facplan": null,
      "data_envio_operadora": null,
      "digitacao_api": null,
      "responsavel_efetivacao": null,
      "data_efetivacao": null,
      "data_implantacao": null,
      "responsavel_geracao": null,
      "data_geracao_boleto": null,
      "observacao": null,
      "conferencia": null,
      "colaborador_devolucao": null,
      "dt_critica_operadora": null,
      "dt_resolvido_quali": null,
      "origem_devolucao": null,
      "status_devolucao": null,
      "motivo_devolucao": null,
      "descricao_devolucao": null
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 100,
    "total": 5,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### 2. Usuários

#### GET /api/usuarios
Retorna lista de usuários do sistema.

**Exemplo de Resposta:**
```json
{
  "data": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@sistema.com",
      "nome_completo": "Administrador do Sistema",
      "cargo": "Administrador",
      "departamento": "TI",
      "telefone": null,
      "ativo": true,
      "data_criacao": "2024-08-29T22:01:45.123456",
      "ultimo_login": "2024-08-29T22:02:30.654321"
    }
  ]
}
```

### 3. Histórico de Alterações

#### GET /api/historico
Retorna histórico de alterações com paginação e filtros.

**Parâmetros de Query:**
- `page` (int, opcional): Número da página (padrão: 1)
- `per_page` (int, opcional): Itens por página (padrão: 100, máximo: 1000)
- `proposta_id` (int, opcional): Filtrar por ID da proposta
- `usuario` (string, opcional): Filtrar por usuário
- `campo` (string, opcional): Filtrar por campo alterado

**Exemplo de Resposta:**
```json
{
  "data": [
    {
      "id": 1,
      "proposta_id": 1,
      "usuario": "admin",
      "campo_alterado": "status",
      "valor_anterior": "Em Análise",
      "valor_novo": "Aprovado",
      "data_alteracao": "2024-08-29T22:15:30.123456"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 100,
    "total": 1,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### 4. Dashboard - Resumo

#### GET /api/dashboard/resumo
Retorna dados agregados para dashboards.

**Exemplo de Resposta:**
```json
{
  "totais": {
    "propostas": 5,
    "usuarios": 1,
    "valor_total": 25420.0
  },
  "propostas_por_status": [
    {"status": "Aprovado", "count": 2},
    {"status": "Em Análise", "count": 1},
    {"status": "Pendente", "count": 1},
    {"status": "Rejeitado", "count": 1}
  ],
  "propostas_por_vendedor": [
    {"vendedor": "Carlos Vendedor", "count": 2},
    {"vendedor": "Ana Vendedora", "count": 2},
    {"vendedor": "Pedro Vendedor", "count": 1}
  ],
  "propostas_por_mes": [
    {"ano": 2024, "mes": 2, "count": 2},
    {"ano": 2024, "mes": 1, "count": 3}
  ]
}
```

## Códigos de Status HTTP

- `200 OK`: Requisição bem-sucedida
- `401 Unauthorized`: Não autenticado (necessário fazer login)
- `404 Not Found`: Endpoint não encontrado
- `500 Internal Server Error`: Erro interno do servidor

## Exemplos de Uso

### Python com requests
```python
import requests

# Fazer login
session = requests.Session()
login_data = {'username': 'admin', 'password': 'admin'}
session.post('http://localhost:5000/login', data=login_data)

# Obter propostas
response = session.get('http://localhost:5000/api/propostas')
propostas = response.json()

# Obter resumo do dashboard
response = session.get('http://localhost:5000/api/dashboard/resumo')
resumo = response.json()
```

### Python com pandas
```python
import pandas as pd
import requests

# Configurar sessão
session = requests.Session()
session.post('http://localhost:5000/login', data={'username': 'admin', 'password': 'admin'})

# Obter dados e converter para DataFrame
response = session.get('http://localhost:5000/api/propostas?per_page=1000')
data = response.json()
df = pd.DataFrame(data['data'])

# Análise dos dados
print(df.groupby('status')['valor'].sum())
```

### Power BI / Tableau
1. Configure uma fonte de dados HTTP/REST
2. URL base: `http://localhost:5000/api/`
3. Autenticação: Configure primeiro uma requisição POST para `/login`
4. Use os endpoints `/api/propostas`, `/api/usuarios`, etc.

### Excel (Power Query)
1. Dados > Obter Dados > De Outras Fontes > Da Web
2. URL: `http://localhost:5000/api/propostas`
3. Configure autenticação se necessário

## Limitações e Considerações

1. **Rate Limiting**: Não implementado atualmente
2. **Paginação**: Máximo de 1000 registros por página
3. **Autenticação**: Baseada em sessão (cookies)
4. **CORS**: Configurado para permitir todas as origens
5. **Formato de Data**: ISO 8601 (YYYY-MM-DDTHH:MM:SS.ffffff)

## Segurança

- Sempre use HTTPS em produção
- Mantenha as credenciais seguras
- Considere implementar API keys para acesso programático
- Monitore o uso da API para detectar abusos

## Suporte

Para dúvidas ou problemas com a API:
1. Verifique se o servidor Flask está rodando
2. Confirme que fez login corretamente
3. Verifique os logs do servidor para erros
4. Teste os endpoints com ferramentas como Postman ou curl

