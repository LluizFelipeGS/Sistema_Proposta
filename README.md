# Sistema de Gerenciamento de Propostas

Sistema web desenvolvido em Python Flask para gerenciamento de propostas com funcionalidades de upload de planilhas, cadastro manual, filtros e exportação.

## Funcionalidades

### 1. Upload de Planilhas (.xlsx)
- Permite upload de planilhas Excel com diferentes layouts
- Mapeamento automático de colunas através de dicionário configurável
- Campos não encontrados na planilha podem ser preenchidos manualmente
- Suporte aos seguintes campos da planilha:
  - `contrato` → `tipo_contrato`
  - `oper_propnum` → `numero_proposta`
  - `contratante_nome` → `cliente_contratante`
  - `beneficiarios` → `quantidade_vidas`
  - `vendedor_nome` → `vendedor`
  - `corretora_nome` → `corretora`
  - `data_criacao` → `data_criacao`
  - `data_vigencia` → `data_vigencia`
  - `valor` → `valor`

### 2. Banco de Dados
- **Tabela Propostas**: Armazena todos os dados das propostas
  - Campos importados da planilha
  - Campos preenchidos manualmente pelo usuário
- **Tabela HistoricoAlteracao**: Registra todas as alterações feitas nas propostas
  - Usuário que fez a alteração
  - Campo alterado
  - Valor anterior e novo
  - Data/hora da alteração

### 3. Funcionalidades do Sistema
- **Login de usuários** (admin/admin para teste)
- **Upload de planilhas** com processamento automático
- **Listagem de propostas** com filtros por:
  - Status
  - Cliente
  - Vendedor
  - Período de datas
- **Edição/cadastro manual** com formulário completo
- **Exportação para Excel** dos dados filtrados
- **Histórico de alterações** automático

## Estrutura do Projeto

```
flask_propostas_app/
├── app.py                 # Aplicação Flask principal
├── models.py              # Modelos SQLAlchemy
├── utils.py               # Funções utilitárias
├── requirements.txt       # Dependências
├── templates/             # Templates HTML
│   ├── base.html
│   ├── login.html
│   ├── upload.html
│   ├── propostas.html
│   ├── edit_proposta.html
│   └── new_proposta.html
├── uploads/               # Arquivos enviados
└── propostas.db          # Banco SQLite
```

## Instalação e Execução

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Executar a aplicação
```bash
python app.py
```

### 3. Acessar o sistema
- URL: http://localhost:5000
- Login: admin
- Senha: admin

## Campos do Sistema

### Importados da Planilha
- Tipo de Contrato
- Número da Proposta
- Cliente/Contratante
- Quantidade de Vidas
- Vendedor
- Corretora
- Data de Criação
- Data de Vigência
- Valor

### Preenchidos Manualmente
- Colaborador (preenchido automaticamente com usuário logado)
- Data da Análise
- Realizou Entrevista Médica
- Status Área Médica
- Status
- Motivo Declínio/Rascunho
- Responsável pela Digitação
- Data Cadastro FACPLAN
- API FACPLAN
- Data Envio p/ Operadora
- Digitação/API
- Responsável pela Efetivação
- Data Efetivação
- Data da Implantação
- Responsável pela Geração
- Data Geração do Boleto
- Observação
- Conferência
- Colaborador Devolução
- DT Crítica Operadora Devolução
- DT Resolvido Quali Devolução
- Origem da Devolução
- Status Devolução
- Motivo Devolução
- Descrição Devolução

## Tecnologias Utilizadas

- **Backend**: Python Flask
- **Banco de Dados**: SQLite com SQLAlchemy
- **Frontend**: HTML, CSS, Bootstrap 5
- **Processamento de Planilhas**: pandas, openpyxl
- **Interface**: Bootstrap 5 + Font Awesome

## Recursos Extras

### Mapeamento Manual de Colunas
Caso a planilha tenha colunas com nomes diferentes dos esperados, o sistema permite mapeamento manual campo a campo.

### Histórico de Alterações
Todas as alterações nos campos manuais são registradas automaticamente com:
- Usuário responsável
- Campo alterado
- Valor anterior e novo
- Data/hora da alteração

### Exportação Inteligente
A exportação para Excel mantém os mesmos filtros aplicados na listagem, permitindo exportar apenas os dados relevantes.

## Segurança

- Autenticação simples por sessão
- Validação de tipos de arquivo (apenas .xlsx)
- Sanitização de nomes de arquivo
- Controle de acesso por sessão

## Observações

- O sistema foi desenvolvido para ambiente de desenvolvimento
- Para produção, recomenda-se configurar um servidor WSGI adequado
- O banco SQLite é adequado para volumes pequenos a médios de dados
- Para volumes maiores, considere migrar para PostgreSQL ou MySQL

