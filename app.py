from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging
from datetime import datetime
import pandas as pd
from models import db, Proposta, HistoricoAlteracao, Usuario, LogAcesso
from config import Config
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta



#----------------linha de codigo Hml----------------------------

#app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///propostas.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SECRET_KEY'] = '15Ke26lz07AY@.202420032002'
#app.config['UPLOAD_FOLDER'] = 'uploads'

# Configurar CORS para permitir acesso externo
#CORS(app)

# Configurar logging para produção
#if not app.debug:
#    logging.basicConfig(level=logging.INFO)

# Verificar se a configuração do banco está presente
#if not app.config.get('SQLALCHEMY_DATABASE_URI'):
#    app.logger.error("DATABASE_URL não configurada!")
#    raise ValueError("DATABASE_URL é obrigatória para funcionamento da aplicação")


#if not os.path.exists(app.config['UPLOAD_FOLDER']):
#    os.makedirs(app.config['UPLOAD_FOLDER'])

#db.init_app(app)

#-------------------Fim hml------------------------------------

#----------------linha de codigo Produção----------------------

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///propostas.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev_secret")
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), "uploads")

CORS(app)

if not app.debug:
    logging.basicConfig(level=logging.INFO)

db.init_app(app)

from flask_migrate import Migrate

migrate = Migrate(app, db)

#-------------------Fim Produção-------------------------------

from Test.utils import read_excel_file, map_columns, identify_missing_fields, convert_date_columns, convert_numeric_columns

COLUMN_MAPPING = {
    'contrato': 'tipo_contrato',
    'oper_propnum': 'numero_proposta',
    'contratante_nome': 'cliente_contratante',
    'beneficiarios': 'quantidade_vidas',
    'vendedor_nome': 'vendedor',
    'corretora_nome': 'corretora',
    'data_criacao': 'data_criacao',
    'data_vigencia': 'data_vigencia',
    'operadora': 'operadora_nome',
    'valor': 'valor',
}

# Campos obrigatórios da planilha
REQUIRED_FIELDS = [
    'tipo_contrato', 'numero_proposta', 'cliente_contratante', 
    'quantidade_vidas', 'vendedor', 'corretora', 
    'data_criacao', 'data_vigencia', 'valor', 'operadora_nome'
]

# ===== FUNÇÕES DE LOGGING =====
def registrar_alteracao(proposta_id, usuario, campo, valor_anterior, valor_novo):
    """Registra uma alteração no histórico."""
    try:
        # Converter valores None para string vazia para comparação
        str_valor_anterior = str(valor_anterior) if valor_anterior is not None else ''
        str_valor_novo = str(valor_novo) if valor_novo is not None else ''
        
        if str_valor_anterior != str_valor_novo:
            historico = HistoricoAlteracao(
                proposta_id=proposta_id,
                usuario=usuario,
                campo_alterado=campo,
                valor_anterior=str_valor_anterior,
                valor_novo=str_valor_novo
            )
            db.session.add(historico)
            return True
        return False
    except Exception as e:
        # Log do erro sem interromper o fluxo principal
        print(f"Erro ao registrar alteração: {e}")
        return False

def registrar_acesso(acao, detalhes=None):
    """Registra acesso e ações dos usuários."""
    try:
        log = LogAcesso(
            usuario=session.get('user', 'Anônimo'),
            acao=acao,
            ip=request.remote_addr,
            detalhes=detalhes
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Erro ao registrar acesso: {e}")

# ===== MIDDLEWARE DE LOGGING =====
@app.before_request
def before_request():
    """Registra acesso a todas as rotas."""
    if request.endpoint and request.endpoint not in ['static', 'favicon']:
        registrar_acesso(f'Acesso à {request.endpoint}', f'Path: {request.path}')

# ===== ROTAS PRINCIPAIS =====
@app.route('/')
def index():
    registrar_acesso('Página inicial acessada')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Buscar usuário no banco de dados
        usuario = Usuario.query.filter_by(username=username, ativo=True).first()
        
        if usuario and usuario.check_password(password):
            session['user_id'] = usuario.id
            session['user'] = usuario.username
            session['nome_completo'] = usuario.nome_completo
            
            # Atualizar último login
            usuario.ultimo_login = datetime.utcnow()
            db.session.commit()
            
            registrar_acesso('Login realizado com sucesso', f'Usuário: {username}')
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('propostas'))
        else:
            registrar_acesso('Tentativa de login falhou', f'Usuário: {username}')
            flash('Credenciais inválidas!', 'error')
    
    registrar_acesso('Página de login acessada')
    return render_template('login.html')

@app.route('/logout')
def logout():
    registrar_acesso('Logout realizado', f'Usuário: {session.get("user")}')
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/perfil')
def perfil():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    usuario = Usuario.query.get(session['user_id'])
    registrar_acesso('Perfil visualizado', f'Usuário: {usuario.username}')
    return render_template('perfil.html', usuario=usuario)

@app.route('/perfil/editar', methods=['GET', 'POST'])
def editar_perfil():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    usuario = Usuario.query.get(session['user_id'])
    
    try:
        roles = Role.query.all()
    except Exception as e:

        roles = []
        flash('Sistema de papéis não disponível no momento.', 'warning')
    
    if request.method == 'POST':
        campos_alterados = []
        if usuario.nome_completo != request.form['nome_completo']:
            campos_alterados.append('nome_completo')
        if usuario.email != request.form['email']:
            campos_alterados.append('email')
        if usuario.departamento != request.form['departamento']:
            campos_alterados.append('departamento')
        if usuario.telefone != request.form['telefone']:
            campos_alterados.append('telefone')
        
        # CORREÇÃO: Verificar se role_id existe antes de comparar
        try:
            if 'role_id' in request.form and request.form['role_id']:
                new_role_id = int(request.form['role_id'])
                if usuario.role_id != new_role_id:
                    campos_alterados.append('cargo/role')
                    usuario.role_id = new_role_id
        except (ValueError, TypeError):
            # Se houver erro ao converter role_id, ignorar
            pass

        usuario.nome_completo = request.form['nome_completo']
        usuario.email = request.form['email']
        usuario.departamento = request.form['departamento']
        usuario.telefone = request.form['telefone']
        
        if request.form['nova_senha']:
            if usuario.check_password(request.form['senha_atual']):
                usuario.set_password(request.form['nova_senha'])
                campos_alterados.append('senha')
                flash('Perfil e senha atualizados com sucesso!', 'success')
            else:
                flash('Senha atual incorreta!', 'error')
                return render_template('editar_perfil.html', usuario=usuario, roles=roles)
        else:
            flash('Perfil atualizado com sucesso!', 'success')
        
        db.session.commit()
        
        if campos_alterados:
            registrar_acesso('Perfil editado', f'Campos alterados: {", ".join(campos_alterados)}')
        
        return redirect(url_for('perfil'))
    
    registrar_acesso('Edição de perfil acessada')
    return render_template('editar_perfil.html', usuario=usuario, roles=roles)

@app.route('/usuarios')
def usuarios():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    usuarios_list = Usuario.query.all()
    registrar_acesso('Lista de usuários visualizada')
    return render_template('usuarios.html', usuarios=usuarios_list)

@app.route('/usuarios/novo', methods=['GET', 'POST'])
def novo_usuario():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # CORREÇÃO: Use Role.query.all() em vez de roles.query.all()
    try:
        roles = Role.query.all()
        if not roles:
            # Se não houver roles, criar uma padrão
            default_role = Role(nome='Usuário')
            db.session.add(default_role)
            db.session.commit()
            roles = [default_role]
    except Exception as e:
        # Se houver erro, usar lista vazia
        roles = []
        flash('Sistema de papéis não disponível no momento.', 'warning')
    
    if request.method == 'POST':
        try:
            if Usuario.query.filter_by(username=request.form['username']).first():
                flash('Nome de usuário já existe!', 'error')
                return render_template('novo_usuario.html', roles=roles)
            
            if Usuario.query.filter_by(email=request.form['email']).first():
                flash('Email já está em uso!', 'error')
                return render_template('novo_usuario.html', roles=roles)
            
            usuario = Usuario()
            usuario.username = request.form['username']
            usuario.email = request.form['email']
            usuario.nome_completo = request.form['nome_completo']
            usuario.departamento = request.form['departamento']
            usuario.telefone = request.form['telefone']
            usuario.set_password(request.form['password'])
            
            # CORREÇÃO: Verificar se role_id existe antes de usar
            if roles and 'role_id' in request.form and request.form['role_id']:
                usuario.role_id = int(request.form['role_id'])
            else:
                # Usar primeiro role disponível como padrão
                usuario.role_id = roles[0].id if roles else None
            
            db.session.add(usuario)
            db.session.commit()
            
            registrar_acesso('Novo usuário criado', f'Usuário: {usuario.username}')
            flash('Usuário criado com sucesso!', 'success')
            return redirect(url_for('usuarios'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar usuário: {str(e)}', 'error')
            return render_template('novo_usuario.html', roles=roles)
    
    registrar_acesso('Criação de usuário acessada')
    return render_template('novo_usuario.html', roles=roles)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        if "file" not in request.files:
            flash("Nenhum arquivo selecionado!", "error")
            return redirect(request.url)
        
        file = request.files["file"]
        if file.filename == "":
            flash("Nenhum arquivo selecionado!", "error")
            return redirect(request.url)
        
        # Obter a opção de sobrepor duplicatas
        sobrepor_duplicatas = request.form.get("sobrepor_duplicatas") == "on"
        
        if file and file.filename.endswith(".xlsx"):
            filename = secure_filename(file.filename)
            # Acessar app.config['UPLOAD_FOLDER'] aqui é seguro, pois já foi definido
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            
            # Processar planilha
            df = read_excel_file(file_path)
            if df is not None:
                # Mapear colunas
                df_mapped = map_columns(df, COLUMN_MAPPING)
                
                # Identificar campos faltantes
                missing_fields = identify_missing_fields(df_mapped, REQUIRED_FIELDS)
                
                # Converter tipos de dados
                date_columns = ["data_criacao", "data_vigencia"]
                numeric_columns = ["quantidade_vidas", "valor"]
                
                df_mapped = convert_date_columns(df_mapped, date_columns)
                df_mapped = convert_numeric_columns(df_mapped, numeric_columns)
                
                # Contadores para estatísticas
                propostas_novas = 0
                propostas_atualizadas = 0
                propostas_duplicadas = 0
                
                # Salvar dados no banco
                for _, row in df_mapped.iterrows():
                    numero_proposta = (
                       str(row["numero_proposta"]).strip()
                       if "numero_proposta" in df_mapped.columns and pd.notna(row["numero_proposta"])
                       else None
                    )
                    
                    # Verificar se a proposta já existe
                    proposta_existente = None
                    if numero_proposta:
                        proposta_existente = Proposta.query.filter_by(numero_proposta=numero_proposta).first()
                    
                    if proposta_existente:
                        if sobrepor_duplicatas:
                            # Atualizar proposta existente
                            for field in REQUIRED_FIELDS:
                                if field in df_mapped.columns and pd.notna(row[field]):
                                    valor_anterior = getattr(proposta_existente, field)
                                    valor_novo = row[field]
                                    
                                    # Registrar alteração se o valor mudou
                                    if registrar_alteracao(
                                        proposta_existente.id, 
                                        session["user"], 
                                        field, 
                                        valor_anterior, 
                                        valor_novo
                                    ):
                                        setattr(proposta_existente, field, valor_novo)
                            
                            propostas_atualizadas += 1
                        else:
                            # Ignorar proposta duplicada
                            propostas_duplicadas += 1
                            continue
                    else:
                        # Criar nova proposta
                        proposta = Proposta()
                        
                        # Preencher campos da planilha
                        for field in REQUIRED_FIELDS:
                            if field in df_mapped.columns:
                                setattr(proposta, field, row[field] if pd.notna(row[field]) else None)
                        
                        # Adicionar colaborador logado
                        proposta.colaborador = session["user"]
                        
                        db.session.add(proposta)
                        # Fazer commit imediatamente para obter o ID
                        db.session.flush()  # Isso atribui um ID sem fazer commit final
                        
                        # Registrar criação via upload - AGORA COM ID VÁLIDO
                        historico = HistoricoAlteracao(
                            proposta_id=proposta.id,  # Agora proposta.id tem valor
                            usuario=session["user"],
                            campo_alterado="CRIAÇÃO",
                            valor_anterior=None,
                            valor_novo="Proposta criada via upload de planilha"
                        )
                        db.session.add(historico)
                        
                        propostas_novas += 1
                
                # Fazer commit final de tudo
                db.session.commit()
                
                # Mensagem de sucesso com estatísticas
                mensagem = f"Planilha processada com sucesso! "
                if propostas_novas > 0:
                    mensagem += f"{propostas_novas} novas propostas importadas. "
                if propostas_atualizadas > 0:
                    mensagem += f"{propostas_atualizadas} propostas atualizadas. "
                if propostas_duplicadas > 0:
                    mensagem += f"{propostas_duplicadas} propostas duplicadas ignoradas."
                
                registrar_acesso("Upload de planilha processado", mensagem)
                flash(mensagem, "success")
                return redirect(url_for("propostas"))
            else:
                registrar_acesso("Erro no processamento de planilha", "Arquivo inválido ou corrompido")
                flash("Erro ao processar a planilha!", "error")
        else:
            registrar_acesso("Tentativa de upload com formato inválido", f"Arquivo: {file.filename}")
            flash("Formato de arquivo inválido! Use apenas .xlsx", "error")
    
    registrar_acesso("Página de upload acessada")
    return render_template("upload.html")

@app.route('/propostas')
def propostas():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    
    query = Proposta.query
    filters = {}

    # Obter filtros
    status_filter = request.args.get('status')
    operadora_filter = request.args.get('operadora')    
    vendedor_filter = request.args.get('vendedor')
    data_vigencia = request.args.get('data_vigencia')
    # Aplicar filtros e construir dicionário de filters para o template
    if status_filter:
        query = query.filter(Proposta.status == status_filter)
        filters['status'] = status_filter
    
    if operadora_filter:
        query = query.filter(Proposta.operadora_nome == operadora_filter)
        filters['operadora'] = operadora_filter
    
    if vendedor_filter:
        query = query.filter(Proposta.vendedor == vendedor_filter)
        filters['vendedor'] = vendedor_filter
    
    if data_vigencia:
        query = query.filter(Proposta.data_vigencia >= data_vigencia)
        filters['data_vigencia'] = data_vigencia

    # Paginação
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    propostas = pagination.items

    base_query = Proposta.query
    
    # Operadoras que existem na base (com pelo menos uma proposta)
    operadoras = [o[0] for o in base_query.with_entities(Proposta.operadora_nome)
                    .filter(Proposta.operadora_nome.isnot(None))
                    .distinct()
                    .order_by(Proposta.operadora_nome)
                    .all() if o[0]]
    
    # Vendedores que existem na base (com pelo menos uma proposta)
    vendedores = [v[0] for v in base_query.with_entities(Proposta.vendedor)
                    .filter(Proposta.vendedor.isnot(None))
                    .distinct()
                    .order_by(Proposta.vendedor)
                    .all() if v[0]]
    
    # Status que existem na base (com pelo menos uma proposta)
    status_list = [s[0] for s in base_query.with_entities(Proposta.status)
                    .filter(Proposta.status.isnot(None))
                    .distinct()
                    .order_by(Proposta.status)
                    .all() if s[0]]
    


    registrar_acesso('Lista de propostas visualizada', f'Filtros aplicados: {filters}')
    return render_template(
        "propostas.html",
        propostas=propostas,
        pagination=pagination,
        per_page=per_page,
        filters=filters,
        operadoras=operadoras,
        vendedores=vendedores,
        status_list=status_list,
    )
    
@app.route('/propostas/edit/<int:id>', methods=['GET', 'POST'])
def edit_proposta(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    proposta = Proposta.query.get_or_404(id)

    if proposta.locked_by and proposta.locked_by != session["user"]:
        if datetime.utcnow() > proposta.locked_at + timedelta(minutes=15):
            proposta.locked_by = None
            proposta.locked_at = None
        else:
            flash(f"A proposta está bloqueado para edição por {proposta.locked_by}.", "warning")
            return redirect(url_for("propostas"))
      
    if request.method == 'POST':
        # Campos para verificar alterações
        campos_manuais = [
            'data_analise', 'realizou_entrevista_medica', 'status_area_medica', 'status',
            'motivo_declinio', 'responsavel_digitacao', 'data_cadastro_facplan', 'api_facplan',
            'data_envio_operadora', 'digitacao_api', 'responsavel_efetivacao', 'data_efetivacao',
            'data_implantacao', 'responsavel_geracao', 'data_geracao_boleto', 'observacao',
            'conferencia', 'colaborador_devolucao', 'dt_critica_operadora', 'dt_resolvido_quali',
            'origem_devolucao', 'status_devolucao', 'motivo_devolucao', 'descricao_devolucao'
        ]
        
        # Registrar alterações
        campos_alterados = []
        for campo in campos_manuais:
            valor_anterior = getattr(proposta, campo)
            
            if campo in ['data_analise', 'data_cadastro_facplan', 'data_envio_operadora', 
                        'data_efetivacao', 'data_implantacao', 'data_geracao_boleto', 
                        'dt_critica_operadora', 'dt_resolvido_quali']:
                valor_novo = datetime.strptime(request.form[campo], '%Y-%m-%d').date() if request.form[campo] else None
            else:
                valor_novo = request.form[campo] if request.form[campo] else None
            
            if registrar_alteracao(proposta.id, session['user'], campo, valor_anterior, valor_novo):
                setattr(proposta, campo, valor_novo)
                campos_alterados.append(campo)

        proposta.locked_by = session["user"]
        proposta.locked_at = datetime.utcnow()
        
        db.session.commit()
        
        if campos_alterados:
            registrar_acesso('Proposta editada', f'Proposta ID: {id}, Campos alterados: {", ".join(campos_alterados)}')
        
        flash('Proposta atualizada com sucesso!', 'success')
        return redirect(url_for('propostas'))
    
    proposta.locked_by = session["user"]
    proposta.locked_at = datetime.utcnow()
    db.session.commit()
    
    registrar_acesso('Edição de proposta acessada', f'Proposta ID: {id}')
    return render_template('edit_proposta.html', proposta=proposta)

@app.route('/propostas/liberar/<int:id>', methods=['POST'])
def liberar_proposta(id):
    proposta = Proposta.query.get_or_404(id)
    if proposta.locked_by == session.get("user"):
        proposta.locked_by = None
        proposta.locked_at = None
        db.session.commit()
    return "", 204

@app.route('/propostas/new', methods=['GET', 'POST'])
def new_proposta():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        proposta = Proposta()
        
        # Preencher campos básicos
        proposta.tipo_contrato = request.form['tipo_contrato']
        proposta.numero_proposta = request.form['numero_proposta']
        proposta.cliente_contratante = request.form['cliente_contratante']
        proposta.quantidade_vidas = int(request.form['quantidade_vidas']) if request.form['quantidade_vidas'] else None
        proposta.vendedor = request.form['vendedor']
        proposta.corretora = request.form['corretora']
        proposta.data_criacao = datetime.strptime(request.form['data_criacao'], '%Y-%m-%d').date() if request.form['data_criacao'] else None
        proposta.data_vigencia = datetime.strptime(request.form['data_vigencia'], '%Y-%m-%d').date() if request.form['data_vigencia'] else None
        proposta.valor = float(request.form['valor']) if request.form['valor'] else None
        proposta.operadora_nome = request.form['operadora_nome']

        # Colaborador logado
        proposta.colaborador = session['user']
        
        db.session.add(proposta)
        db.session.commit()
        
        # REGISTRAR CRIAÇÃO DA PROPOSTA
        historico = HistoricoAlteracao(
            proposta_id=proposta.id,
            usuario=session['user'],
            campo_alterado='CRIAÇÃO',
            valor_anterior=None,
            valor_novo='Proposta criada manualmente'
        )
        db.session.add(historico)
        db.session.commit()
        
        registrar_acesso('Nova proposta criada', f'Proposta ID: {proposta.id}, Número: {proposta.numero_proposta}')
        flash('Proposta criada com sucesso!', 'success')
        return redirect(url_for('propostas'))
    
    registrar_acesso('Criação de proposta acessada')
    return render_template('new_proposta.html')

@app.route('/propostas/delete/<int:id>', methods=['POST'])
def delete_proposta(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        proposta = Proposta.query.get_or_404(id)
        numero_proposta = proposta.numero_proposta or str(proposta.id)

        HistoricoAlteracao.query.filter_by(proposta_id=proposta.id).delete()

        historico = HistoricoAlteracao(
            proposta_id=proposta.id,
            usuario=session['user'],
            campo_alterado='EXCLUSÃO',
            valor_anterior=f'Proposta {numero_proposta}',
            valor_novo=None
        )
        db.session.add(historico)

        db.session.delete(proposta)
        db.session.commit()

        registrar_acesso('Proposta excluída', f'Proposta ID: {id}, Número: {numero_proposta}')
        flash('Proposta excluída com sucesso!', 'success')

    except Exception as e:
        db.session.rollback()
        registrar_acesso('Erro ao excluir proposta', f'Erro: {str(e)}')
        flash('Erro ao excluir proposta!', 'error')
        print(f"Erro ao excluir proposta: {e}")

    return redirect(url_for('propostas'))

@app.route('/export_excel')
def export_excel():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Aplicar os mesmos filtros da listagem
    status_filter = request.args.get('status', '')
    cliente_filter = request.args.get('cliente', '')
    vendedor_filter = request.args.get('vendedor', '')
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    operadora_filter = request.args.get('operadora_nome', '')
    
    # Query base
    query = Proposta.query
    
    # Aplicar filtros
    if status_filter:
        query = query.filter(Proposta.status.like(f'%{status_filter}%'))
    if operadora_filter:
        query = query.filter(Proposta.operadora_nome.like(f'%{operadora_filter}%'))
    if cliente_filter:
        query = query.filter(Proposta.cliente_contratante.like(f'%{cliente_filter}%'))
    if vendedor_filter:
        query = query.filter(Proposta.vendedor.like(f'%{vendedor_filter}%'))
    if data_inicio:
        query = query.filter(Proposta.data_criacao >= datetime.strptime(data_inicio, '%Y-%m-%d').date())
    if data_fim:
        query = query.filter(Proposta.data_criacao <= datetime.strptime(data_fim, '%Y-%m-%d').date())
    
    propostas_list = query.all()
    
    # Criar DataFrame
    data = []
    for proposta in propostas_list:
        data.append({
            'ID': proposta.id,
            'Tipo Contrato': proposta.tipo_contrato,
            'Número Proposta': proposta.numero_proposta,
            'Operadora': proposta.operadora_nome,
            'Cliente/Contratante': proposta.cliente_contratante,
            'Quantidade Vidas': proposta.quantidade_vidas,
            'Vendedor': proposta.vendedor,
            'Corretora': proposta.corretora,
            'Data Criação': proposta.data_criacao.strftime('%d/%m/%Y') if proposta.data_criacao else '',
            'Data Vigência': proposta.data_vigencia.strftime('%d/%m/%Y') if proposta.data_vigencia else '',
            'Valor': proposta.valor,
            'Colaborador': proposta.colaborador,
            'Data Análise': proposta.data_analise.strftime('%d/%m/%Y') if proposta.data_analise else '',
            'Entrevista Médica': proposta.realizou_entrevista_medica,
            'Status Área Médica': proposta.status_area_medica,
            'Status': proposta.status,
            'Motivo Declínio': proposta.motivo_declinio,
            'Colaborador Analise': proposta.colaborador,
            'Responsável Digitação': proposta.responsavel_digitacao,
            'Data Cadastro FACPLAN': proposta.data_cadastro_facplan.strftime('%d/%m/%Y') if proposta.data_cadastro_facplan else '',
            'API FACPLAN': proposta.api_facplan,
            'Data Envio Operadora': proposta.data_envio_operadora.strftime('%d/%m/%Y') if proposta.data_envio_operadora else '',
            'Digitação/API': proposta.digitacao_api,
            'Responsável Efetivação': proposta.responsavel_efetivacao,
            'Data Efetivação': proposta.data_efetivacao.strftime('%d/%m/%Y') if proposta.data_efetivacao else '',
            'Data Implantação': proposta.data_implantacao.strftime('%d/%m/%Y') if proposta.data_implantacao else '',
            'Responsável Geração': proposta.responsavel_geracao,
            'Data Geração Boleto': proposta.data_geracao_boleto.strftime('%d/%m/%Y') if proposta.data_geracao_boleto else '',
            'Observação': proposta.observacao,
            'Conferência': proposta.conferencia,
            'Colaborador Digitação': proposta.colaborador,
            'Colaborador Devolução': proposta.colaborador_devolucao,
            'DT Crítica Operadora': proposta.dt_critica_operadora.strftime('%d/%m/%Y') if proposta.dt_critica_operadora else '',
            'DT Resolvido Quali': proposta.dt_resolvido_quali.strftime('%d/%m/%Y') if proposta.dt_resolvido_quali else '',
            'Origem Devolução': proposta.origem_devolucao,
            'Status Devolução': proposta.status_devolucao,
            'Motivo Devolução': proposta.motivo_devolucao,
            'Descrição Devolução': proposta.descricao_devolucao
        })
    
    df = pd.DataFrame(data)
    
    # Salvar arquivo Excel
    filename = f'propostas_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df.to_excel(filepath, index=False)
    
    registrar_acesso('Exportação Excel realizada', f'Arquivo: {filename}, Registros: {len(propostas_list)}')
    
    # Retornar arquivo para download
    return send_file(filepath, as_attachment=True, download_name=filename)

# ===== ROTAS DE LOGS =====
@app.route('/logs')
def visualizar_logs():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 50
    tipo_log = request.args.get('tipo', 'alteracoes')  # 'alteracoes' ou 'acessos'
    
    if tipo_log == 'acessos':
        query = LogAcesso.query
        usuario_filter = request.args.get('usuario', '')
        acao_filter = request.args.get('acao', '')
        
        if usuario_filter:
            query = query.filter(LogAcesso.usuario.ilike(f'%{usuario_filter}%'))
        if acao_filter:
            query = query.filter(LogAcesso.acao.ilike(f'%{acao_filter}%'))
        
        logs = query.order_by(LogAcesso.data_hora.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        template = 'logs_acessos.html'
    else:
        query = HistoricoAlteracao.query
        usuario_filter = request.args.get('usuario', '')
        campo_filter = request.args.get('campo', '')
        proposta_id_filter = request.args.get('proposta_id', '')
        
        if usuario_filter:
            query = query.filter(HistoricoAlteracao.usuario.ilike(f'%{usuario_filter}%'))
        if campo_filter:
            query = query.filter(HistoricoAlteracao.campo_alterado.ilike(f'%{campo_filter}%'))
        if proposta_id_filter:
            query = query.filter(HistoricoAlteracao.proposta_id == proposta_id_filter)
        
        logs = query.order_by(HistoricoAlteracao.data_alteracao.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        template = 'logs_alteracoes.html'
    
    registrar_acesso('Logs do sistema visualizados', f'Tipo: {tipo_log}')
    return render_template(template, logs=logs, tipo_log=tipo_log)

# ===== ENDPOINTS DA API =====
@app.route('/api/propostas', methods=['GET'])
def api_propostas():
    """API endpoint para obter propostas em formato JSON."""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    registrar_acesso('API de propostas acessada')
    
    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    
    # Validar per_page (máximo 1000 para evitar sobrecarga)
    if per_page > 1000:
        per_page = 1000
    
    # Filtros
    status_filter = request.args.get('status', '')
    operadora_filter = request.args.get('operadora', '')
    cliente_filter = request.args.get('cliente', '')
    vendedor_filter = request.args.get('vendedor', '')
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    numero_proposta_filter = request.args.get('numero_proposta', '')
    
    # Query base
    query = Proposta.query
    
    # Aplicar filtros
    if status_filter:
        query = query.filter(Proposta.status.ilike(f'%{status_filter}%'))
    if operadora_filter:
        query = query.filter(Proposta.operadora_nome.ilike(f'%{operadora_filter}%'))
    if cliente_filter:
        query = query.filter(Proposta.cliente_contratante.ilike(f'%{cliente_filter}%'))
    if vendedor_filter:
        query = query.filter(Proposta.vendedor.ilike(f'%{vendedor_filter}%'))
    if numero_proposta_filter:
        query = query.filter(Proposta.numero_proposta.ilike(f'%{numero_proposta_filter}%'))
    if data_inicio:
        try:
            query = query.filter(Proposta.data_criacao >= datetime.strptime(data_inicio, '%Y-%m-%d').date())
        except ValueError:
            pass
    if data_fim:
        try:
            query = query.filter(Proposta.data_criacao <= datetime.strptime(data_fim, '%Y-%m-%d').date())
        except ValueError:
            pass
    
    # Ordenação
    order_by = request.args.get('order_by', 'id')
    order_dir = request.args.get('order_dir', 'desc')
    
    if hasattr(Proposta, order_by):
        if order_dir.lower() == 'asc':
            query = query.order_by(getattr(Proposta, order_by).asc())
        else:
            query = query.order_by(getattr(Proposta, order_by).desc())
    else:
        query = query.order_by(Proposta.id.desc())
    
    # Aplicar paginação
    propostas_paginadas = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    # Converter para JSON
    propostas_json = []
    for proposta in propostas_paginadas.items:
        proposta_dict = {
            'id': proposta.id,
            'tipo_contrato': proposta.tipo_contrato,
            'numero_proposta': proposta.numero_proposta,
            'operadora': proposta.operadora_nome,
            'cliente_contratante': proposta.cliente_contratante,
            'quantidade_vidas': proposta.quantidade_vidas,
            'vendedor': proposta.vendedor,
            'corretora': proposta.corretora,
            'data_criacao': proposta.data_criacao.isoformat() if proposta.data_criacao else None,
            'data_vigencia': proposta.data_vigencia.isoformat() if proposta.data_vigencia else None,
            'valor': float(proposta.valor) if proposta.valor else None,
            'colaborador': proposta.colaborador,
            'data_analise': proposta.data_analise.isoformat() if proposta.data_analise else None,
            'realizou_entrevista_medica': proposta.realizou_entrevista_medica,
            'status_area_medica': proposta.status_area_medica,
            'status': proposta.status,
            'motivo_declinio': proposta.motivo_declinio,
            'responsavel_digitacao': proposta.responsavel_digitacao,
            'data_cadastro_facplan': proposta.data_cadastro_facplan.isoformat() if proposta.data_cadastro_facplan else None,
            'api_facplan': proposta.api_facplan,
            'data_envio_operadora': proposta.data_envio_operadora.isoformat() if proposta.data_envio_operadora else None,
            'digitacao_api': proposta.digitacao_api,
            'responsavel_efetivacao': proposta.responsavel_efetivacao,
            'data_efetivacao': proposta.data_efetivacao.isoformat() if proposta.data_efetivacao else None,
            'data_implantacao': proposta.data_implantacao.isoformat() if proposta.data_implantacao else None,
            'responsavel_geracao': proposta.responsavel_geracao,
            'data_geracao_boleto': proposta.data_geracao_boleto.isoformat() if proposta.data_geracao_boleto else None,
            'observacao': proposta.observacao,
            'conferencia': proposta.conferencia,
            'colaborador_devolucao': proposta.colaborador_devolucao,
            'dt_critica_operadora': proposta.dt_critica_operadora.isoformat() if proposta.dt_critica_operadora else None,
            'dt_resolvido_quali': proposta.dt_resolvido_quali.isoformat() if proposta.dt_resolvido_quali else None,
            'origem_devolucao': proposta.origem_devolucao,
            'status_devolucao': proposta.status_devolucao,
            'motivo_devolucao': proposta.motivo_devolucao,
            'descricao_devolucao': proposta.descricao_devolucao,
            'data_criacao_registro': proposta.data_criacao.isoformat() if proposta.data_criacao else None,
            'data_ultima_alteracao': proposta.data_ultima_alteracao.isoformat() if proposta.data_ultima_alteracao else None
        }
        propostas_json.append(proposta_dict)
    
    # Metadados de paginação
    response_data = {
        'success': True,
        'data': propostas_json,
        'pagination': {
            'page': propostas_paginadas.page,
            'per_page': propostas_paginadas.per_page,
            'total': propostas_paginadas.total,
            'pages': propostas_paginadas.pages,
            'has_next': propostas_paginadas.has_next,
            'has_prev': propostas_paginadas.has_prev
        },
        'filters': {
            'status': status_filter,
            'operadora': operadora_filter,
            'cliente': cliente_filter,
            'vendedor': vendedor_filter,
            'numero_proposta': numero_proposta_filter,
            'data_inicio': data_inicio,
            'data_fim': data_fim
        }
    }
    
    return jsonify(response_data)

@app.route('/api/propostas/<int:id>', methods=['GET'])
def api_proposta_detalhes(id):
    """API endpoint para obter detalhes de uma proposta específica."""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    registrar_acesso(f'API de detalhes da proposta {id} acessada')
    
    proposta = Proposta.query.get_or_404(id)
    
    proposta_dict = {
        'id': proposta.id,
        'tipo_contrato': proposta.tipo_contrato,
        'numero_proposta': proposta.numero_proposta,
        'operadora': proposta.operadora_nome,
        'cliente_contratante': proposta.cliente_contratante,
        'quantidade_vidas': proposta.quantidade_vidas,
        'vendedor': proposta.vendedor,
        'corretora': proposta.corretora,
        'data_criacao': proposta.data_criacao.isoformat() if proposta.data_criacao else None,
        'data_vigencia': proposta.data_vigencia.isoformat() if proposta.data_vigencia else None,
        'valor': float(proposta.valor) if proposta.valor else None,
        'colaborador': proposta.colaborador,
        'data_analise': proposta.data_analise.isoformat() if proposta.data_analise else None,
        'realizou_entrevista_medica': proposta.realizou_entrevista_medica,
        'status_area_medica': proposta.status_area_medica,
        'status': proposta.status,
        'motivo_declinio': proposta.motivo_declinio,
        'responsavel_digitacao': proposta.responsavel_digitacao,
        'data_cadastro_facplan': proposta.data_cadastro_facplan.isoformat() if proposta.data_cadastro_facplan else None,
        'api_facplan': proposta.api_facplan,
        'data_envio_operadora': proposta.data_envio_operadora.isoformat() if proposta.data_envio_operadora else None,
        'digitacao_api': proposta.digitacao_api,
        'responsavel_efetivacao': proposta.responsavel_efetivacao,
        'data_efetivacao': proposta.data_efetivacao.isoformat() if proposta.data_efetivacao else None,
        'data_implantacao': proposta.data_implantacao.isoformat() if proposta.data_implantacao else None,
        'responsavel_geracao': proposta.responsavel_geracao,
        'data_geracao_boleto': proposta.data_geracao_boleto.isoformat() if proposta.data_geracao_boleto else None,
        'observacao': proposta.observacao,
        'conferencia': proposta.conferencia,
        'colaborador_devolucao': proposta.colaborador_devolucao,
        'dt_critica_operadora': proposta.dt_critica_operadora.isoformat() if proposta.dt_critica_operadora else None,
        'dt_resolvido_quali': proposta.dt_resolvido_quali.isoformat() if proposta.dt_resolvido_quali else None,
        'origem_devolucao': proposta.origem_devolucao,
        'status_devolucao': proposta.status_devolucao,
        'motivo_devolucao': proposta.motivo_devolucao,
        'descricao_devolucao': proposta.descricao_devolucao,
        'data_criacao_registro': proposta.data_criacao.isoformat() if proposta.data_criacao else None,
        'data_ultima_alteracao': proposta.data_ultima_alteracao.isoformat() if proposta.data_ultima_alteracao else None
    }
    
    return jsonify({'success': True, 'data': proposta_dict})

@app.route('/api/usuarios', methods=['GET'])
def api_usuarios():
    """API endpoint para obter usuários em formato JSON."""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    registrar_acesso('API de usuários acessada')
    
    # Filtros
    ativo_filter = request.args.get('ativo', '')
    departamento_filter = request.args.get('departamento', '')
    
    query = Usuario.query
    
    if ativo_filter.lower() in ['true', '1', 'yes']:
        query = query.filter(Usuario.ativo == True)
    elif ativo_filter.lower() in ['false', '0', 'no']:
        query = query.filter(Usuario.ativo == False)
    
    if departamento_filter:
        query = query.filter(Usuario.departamento.ilike(f'%{departamento_filter}%'))
    
    usuarios = query.order_by(Usuario.nome_completo.asc()).all()
    
    usuarios_json = []
    for usuario in usuarios:
        usuario_dict = {
            'id': usuario.id,
            'username': usuario.username,
            'email': usuario.email,
            'nome_completo': usuario.nome_completo,
            'cargo': usuario.cargo,
            'departamento': usuario.departamento,
            'telefone': usuario.telefone,
            'ativo': usuario.ativo,
            'data_criacao': usuario.data_criacao.isoformat() if usuario.data_criacao else None,
            'ultimo_login': usuario.ultimo_login.isoformat() if usuario.ultimo_login else None
        }
        usuarios_json.append(usuario_dict)
    
    return jsonify({'success': True, 'data': usuarios_json, 'total': len(usuarios_json)})

@app.route('/api/historico', methods=['GET'])
def api_historico():
    """API endpoint para obter histórico de alterações em formato JSON."""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    registrar_acesso('API de histórico acessada')
    
    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    
    # Validar per_page
    if per_page > 1000:
        per_page = 1000
    
    # Filtros opcionais
    proposta_id = request.args.get('proposta_id', type=int)
    usuario_filter = request.args.get('usuario', '')
    campo_filter = request.args.get('campo', '')
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    
    # Query base
    query = HistoricoAlteracao.query
    
    # Aplicar filtros
    if proposta_id:
        query = query.filter(HistoricoAlteracao.proposta_id == proposta_id)
    if usuario_filter:
        query = query.filter(HistoricoAlteracao.usuario.ilike(f'%{usuario_filter}%'))
    if campo_filter:
        query = query.filter(HistoricoAlteracao.campo_alterado.ilike(f'%{campo_filter}%'))
    if data_inicio:
        try:
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(HistoricoAlteracao.data_alteracao >= data_inicio_dt)
        except ValueError:
            pass
    if data_fim:
        try:
            data_fim_dt = datetime.strptime(data_fim + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            query = query.filter(HistoricoAlteracao.data_alteracao <= data_fim_dt)
        except ValueError:
            pass
    
    # Ordenar por data mais recente
    query = query.order_by(HistoricoAlteracao.data_alteracao.desc())
    
    # Aplicar paginação
    historico_paginado = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    # Converter para JSON
    historico_json = []
    for registro in historico_paginado.items:
        registro_dict = {
            'id': registro.id,
            'proposta_id': registro.proposta_id,
            'usuario': registro.usuario,
            'campo_alterado': registro.campo_alterado,
            'valor_anterior': registro.valor_anterior,
            'valor_novo': registro.valor_novo,
            'data_alteracao': registro.data_alteracao.isoformat() if registro.data_alteracao else None,
            'proposta_numero': Proposta.query.get(registro.proposta_id).numero_proposta if registro.proposta_id else None
        }
        historico_json.append(registro_dict)
    
    # Metadados de paginação
    response_data = {
        'success': True,
        'data': historico_json,
        'pagination': {
            'page': historico_paginado.page,
            'per_page': historico_paginado.per_page,
            'total': historico_paginado.total,
            'pages': historico_paginado.pages,
            'has_next': historico_paginado.has_next,
            'has_prev': historico_paginado.has_prev
        }
    }
    
    return jsonify(response_data)

@app.route('/api/dashboard/resumo', methods=['GET'])
def api_dashboard_resumo():
    """API endpoint para obter dados resumidos para dashboard."""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    registrar_acesso('API de dashboard acessada')
    
    # Estatísticas gerais
    total_propostas = Proposta.query.count()
    total_usuarios = Usuario.query.filter_by(ativo=True).count()
    
    # Propostas por status
    propostas_por_status = db.session.query(
        Proposta.status, 
        db.func.count(Proposta.id).label('count')
    ).group_by(Proposta.status).all()
    
    status_data = [{'status': status or 'Sem Status', 'count': count} for status, count in propostas_por_status]
    
    # Propostas por operadora (top 10)
    propostas_por_operadora = db.session.query(
        Proposta.operadora_nome, 
        db.func.count(Proposta.id).label('count')
    ).filter(Proposta.operadora_nome.isnot(None)).group_by(Proposta.operadora_nome).order_by(db.func.count(Proposta.id).desc()).limit(10).all()
    
    operadora_data = [{'operadora': operadora, 'count': count} for operadora, count in propostas_por_operadora]
    
    # Propostas por vendedor (top 10)
    propostas_por_vendedor = db.session.query(
        Proposta.vendedor, 
        db.func.count(Proposta.id).label('count')
    ).filter(Proposta.vendedor.isnot(None)).group_by(Proposta.vendedor).order_by(db.func.count(Proposta.id).desc()).limit(10).all()
    
    vendedor_data = [{'vendedor': vendedor, 'count': count} for vendedor, count in propostas_por_vendedor]
    
    # Valor total das propostas
    valor_total = db.session.query(db.func.sum(Proposta.valor)).scalar() or 0
    
    # Propostas dos últimos 30 dias
    from datetime import timedelta
    trinta_dias_atras = datetime.now() - timedelta(days=30)
    propostas_30_dias = Proposta.query.filter(Proposta.data_criacao >= trinta_dias_atras.date()).count()
    
    # Propostas criadas hoje
    hoje = datetime.now().date()
    propostas_hoje = Proposta.query.filter(db.func.date(Proposta.data_criacao) == hoje).count()
    
    # Média de propostas por dia (últimos 30 dias)
    media_diaria = propostas_30_dias / 30 if propostas_30_dias > 0 else 0
    
    resumo_data = {
        'success': True,
        'totais': {
            'propostas': total_propostas,
            'usuarios': total_usuarios,
            'valor_total': float(valor_total),
            'propostas_30_dias': propostas_30_dias,
            'propostas_hoje': propostas_hoje,
            'media_diaria': round(media_diaria, 2)
        },
        'propostas_por_status': status_data,
        'propostas_por_operadora': operadora_data,
        'propostas_por_vendedor': vendedor_data,
        'periodo_consulta': {
            'data_inicio': trinta_dias_atras.date().isoformat(),
            'data_fim': datetime.now().date().isoformat()
        }
    }
    
    return jsonify(resumo_data)

@app.route('/api/estatisticas/avancadas', methods=['GET'])
def api_estatisticas_avancadas():
    """API endpoint para estatísticas avançadas."""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    registrar_acesso('API de estatísticas avançadas acessada')
    
    # Filtros de período
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    query = Proposta.query
    
    if data_inicio:
        try:
            query = query.filter(Proposta.data_criacao >= datetime.strptime(data_inicio, '%Y-%m-%d').date())
        except ValueError:
            pass
    
    if data_fim:
        try:
            query = query.filter(Proposta.data_criacao <= datetime.strptime(data_fim, '%Y-%m-%d').date())
        except ValueError:
            pass
    
    # Estatísticas por status
    status_stats = db.session.query(
        Proposta.status,
        db.func.count(Proposta.id).label('quantidade'),
        db.func.sum(Proposta.valor).label('valor_total'),
        db.func.avg(Proposta.valor).label('valor_medio')
    ).group_by(Proposta.status).all()
    
    # Evolução mensal
    from sqlalchemy import extract
    evolucao_mensal = db.session.query(
        extract('year', Proposta.data_criacao).label('ano'),
        extract('month', Proposta.data_criacao).label('mes'),
        db.func.count(Proposta.id).label('quantidade'),
        db.func.sum(Proposta.valor).label('valor_total')
    ).filter(Proposta.data_criacao.isnot(None)).group_by(
        extract('year', Proposta.data_criacao),
        extract('month', Proposta.data_criacao)
    ).order_by(
        extract('year', Proposta.data_criacao).desc(),
        extract('month', Proposta.data_criacao).desc()
    ).limit(12).all()
    
    evolucao_data = []
    for ano, mes, quantidade, valor_total in evolucao_mensal:
        evolucao_data.append({
            'ano': int(ano),
            'mes': int(mes),
            'quantidade': quantidade,
            'valor_total': float(valor_total) if valor_total else 0
        })
    
    response_data = {
        'success': True,
        'estatisticas_status': [
            {
                'status': status or 'Sem Status',
                'quantidade': quantidade,
                'valor_total': float(valor_total) if valor_total else 0,
                'valor_medio': float(valor_medio) if valor_medio else 0
            }
            for status, quantidade, valor_total, valor_medio in status_stats
        ],
        'evolucao_mensal': evolucao_data,
        'periodo_consulta': {
            'data_inicio': data_inicio,
            'data_fim': data_fim
        }
    }
    
    return jsonify(response_data)

from functools import wraps
from flask import session, redirect, url_for, flash
from models import Usuario, Role

def permission_required(permission_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get("user_id")
            if not user_id:
                flash("Você precisa estar logado.", "error")
                return redirect(url_for("login"))

            usuario = Usuario.query.get(user_id)
            if not usuario:
                flash("Acesso negado!", "error")
                return redirect(url_for("index"))

            # CORREÇÃO: Verificar se o usuário tem role e permissões
            if not usuario.role or not hasattr(usuario.role, 'permissions'):
                flash("Você não tem permissão para acessar esta funcionalidade.", "error")
                return redirect(url_for("index"))

            # Verifica se o papel do usuário possui a permissão
            has_permission = any(p.nome == permission_name for p in usuario.role.permissions)
            if not has_permission:
                flash("Você não tem permissão para acessar esta funcionalidade.", "error")
                return redirect(url_for("index"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/usuarios/delete/<int:id>', methods=['POST'])
@permission_required('deletar_usuario')
def delete_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    flash("Usuário excluído com sucesso!", "success")
    return redirect(url_for("usuarios"))

@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    
    try:
        roles = Role.query.all()
    except:
        roles = []

    if request.method == 'POST':
        usuario.nome_completo = request.form['nome_completo']
        usuario.email = request.form['email']
        usuario.departamento = request.form['departamento']
        usuario.telefone = request.form['telefone']
        
        if 'role_id' in request.form and request.form['role_id']:
            usuario.role_id = int(request.form['role_id'])

        if request.form['nova_senha']:
            usuario.set_password(request.form['nova_senha'])
        
        db.session.commit()
        flash("Usuário atualizado com sucesso!", "success")
        return redirect(url_for("usuarios"))

    return render_template("editar_usuario.html", usuario=usuario, roles=roles)

@app.route('/usuarios/toggle/<int:id>', methods=['POST'])
def toggle_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    if usuario.id == session.get("user_id"):
        flash("Você não pode desativar o seu próprio usuário.", "error")
        return redirect(url_for("usuarios"))

    usuario.ativo = not usuario.ativo
    db.session.commit()

    if usuario.ativo:
        flash(f"Usuário {usuario.username} ativado com sucesso!", "success")
    else:
        flash(f"Usuário {usuario.username} desativado com sucesso!", "warning")

    return redirect(url_for("usuarios"))

if __name__ == '__main__':
    with app.app_context():
        try:
          
            db.create_all()
            
     
            if Role.query.count() == 0:
                admin_role = Role(nome='Administrador')
                user_role = Role(nome='Usuário')
                db.session.add_all([admin_role, user_role])
                db.session.commit()
                print("Roles padrão criados: Administrador, Usuário")
            
            app.logger.info("Tabelas do banco de dados criadas/verificadas com sucesso")
        except Exception as e:
            app.logger.error(f"Erro ao criar tabelas do banco: {e}")
            raise
    

    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=debug_mode
    )