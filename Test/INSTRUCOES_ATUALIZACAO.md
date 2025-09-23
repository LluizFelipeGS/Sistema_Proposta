# Instruções de Atualização - Sistema de Propostas v2.0

## Novas Funcionalidades Implementadas

### 1. Sistema de Perfis de Usuário
- **Modelo de Usuário**: Criado modelo completo com campos para nome, email, cargo, departamento, telefone
- **Autenticação Segura**: Senhas criptografadas com hash
- **Perfil do Usuário**: Tela para visualizar e editar informações pessoais
- **Gerenciamento de Usuários**: Listagem e criação de novos usuários
- **Controle de Sessão**: Sistema de login/logout aprimorado

### 2. Paginação na Listagem de Propostas
- **Visualização Configurável**: 10, 50 ou 100 propostas por página
- **Navegação por Páginas**: Controles de primeira, anterior, próxima e última página
- **Informações de Paginação**: Mostra quantos registros estão sendo exibidos
- **Filtros Mantidos**: Os filtros são preservados durante a navegação entre páginas

## Como Atualizar o Sistema Existente

### Passo 1: Backup dos Dados
```bash
# Faça backup do banco atual (se houver dados importantes)
cp instance/propostas.db instance/propostas_backup.db
```

### Passo 2: Atualizar Arquivos
1. Substitua todos os arquivos do projeto pelos novos
2. Mantenha a pasta `uploads/` se houver arquivos importantes

### Passo 3: Recriar o Banco de Dados
```bash
# Remover banco antigo e criar novo com as tabelas atualizadas
rm -f instance/propostas.db
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Passo 4: Criar Usuário Administrador
```bash
python3 create_admin_user.py
```

### Passo 5: Executar o Sistema
```bash
python3 app.py
```

## Credenciais Padrão
- **Usuário**: admin
- **Senha**: admin

## Novas Rotas Disponíveis
- `/perfil` - Visualizar perfil do usuário
- `/perfil/editar` - Editar perfil do usuário
- `/usuarios` - Listar usuários do sistema
- `/usuarios/novo` - Criar novo usuário

## Melhorias na Interface
- Menu de navegação atualizado com opções de perfil
- Paginação visual na listagem de propostas
- Seletor de quantidade de itens por página
- Informações detalhadas de paginação

## Compatibilidade
- Mantém todas as funcionalidades anteriores
- Upload de planilhas continua funcionando normalmente
- Filtros e exportação para Excel preservados
- Histórico de alterações mantido

## Observações Importantes
1. **Migração de Dados**: Se você tem dados importantes no sistema antigo, será necessário fazer uma migração manual
2. **Usuários Existentes**: O sistema antigo usava autenticação simples. Agora todos os usuários devem ser criados através da interface
3. **Permissões**: Todos os usuários têm as mesmas permissões. Para implementar níveis de acesso, seria necessário desenvolvimento adicional

## Suporte
Para dúvidas ou problemas na atualização, verifique:
1. Se todas as dependências estão instaladas (`pip install -r requirements.txt`)
2. Se o banco de dados foi recriado corretamente
3. Se o usuário administrador foi criado com sucesso

