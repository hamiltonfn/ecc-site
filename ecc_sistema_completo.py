# ecc_sistema_completo.py
# Sistema Completo de Gerenciamento do Encontro de Casais com Cristo (ECC)
# Autor: Sistema ECC
# Data: 2026-01-05

from flask import Flask, render_template_string, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json

# ==================== CONFIGURAÇÃO DA APLICAÇÃO ====================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta-ecc-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)

# ==================== MODELOS DO BANCO DE DADOS ====================
class Casal(db.Model):
    __tablename__ = 'casais'
    
    id = db.Column(db.Integer, primary_key=True)
    arquidiocese = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    paroquia = db.Column(db.String(100))
    
    # Dados do marido
    nome_ele = db.Column(db.String(100))
    nascimento_ele = db.Column(db.String(10))  # Alterado para String para armazenar DD/MM
    profissao_ele = db.Column(db.String(100))
    nome_usual_ele = db.Column(db.String(50))
    fone_prof_ele = db.Column(db.String(20))
    
    # Dados da esposa
    nome_ela = db.Column(db.String(100))
    nascimento_ela = db.Column(db.String(10))  # Alterado para String para armazenar DD/MM
    profissao_ela = db.Column(db.String(100))
    nome_usual_ela = db.Column(db.String(50))
    fone_prof_ela = db.Column(db.String(20))
    
    # Dados do casal
    casamento_religioso = db.Column(db.Boolean, default=False)
    data_casamento = db.Column(db.Date)
    data_casamento_civil = db.Column(db.Date)
    num_filhos = db.Column(db.Integer, default=0)
    
    # Endereço
    endereco = db.Column(db.String(200))
    numero = db.Column(db.String(10))
    apto = db.Column(db.String(10))
    bairro = db.Column(db.String(100))
    cep = db.Column(db.String(10))
    cidade_estado = db.Column(db.String(100))
    fone = db.Column(db.String(20))
    
    # ECC
    ecc_etapa1_num = db.Column(db.String(20))
    ecc_etapa1_data = db.Column(db.Date)
    ecc_etapa1_local = db.Column(db.String(100))
    ecc_etapa1_atividades = db.Column(db.Text)
    
    ecc_etapa2_num = db.Column(db.String(20))
    ecc_etapa2_data = db.Column(db.Date)
    ecc_etapa2_local = db.Column(db.String(100))
    ecc_etapa2_atividades = db.Column(db.Text)
    
    ecc_etapa3_num = db.Column(db.String(20))
    ecc_etapa3_data = db.Column(db.Date)
    ecc_etapa3_local = db.Column(db.String(100))
    ecc_etapa3_atividades = db.Column(db.Text)
    
    # Outros
    engajamento_paroquial = db.Column(db.Text)
    habilidades = db.Column(db.Text)
    
    # Fotos (caminhos para arquivos)
    foto_ele = db.Column(db.String(200))
    foto_ela = db.Column(db.String(200))
    
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

class Atividade(db.Model):
    __tablename__ = 'atividades'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_equipe = db.Column(db.String(100))
    ecc_numero = db.Column(db.String(20))
    
    # Coordenadores e responsáveis
    coord_geral = db.Column(db.String(100))
    sala = db.Column(db.String(100))
    liturgia_vigilia = db.Column(db.String(100))
    circulos = db.Column(db.String(100))
    cafe_minimercado = db.Column(db.String(100))
    cozinha = db.Column(db.String(100))
    ordem_limpeza = db.Column(db.String(100))
    visitacao = db.Column(db.String(100))
    acolhida = db.Column(db.String(100))
    secretaria = db.Column(db.String(100))
    compras = db.Column(db.String(100))
    palestras = db.Column(db.String(100))
    
    # Status dos voluntários
    opcoes_trabalho = db.Column(db.Text)
    
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== FUNÇÕES AUXILIARES ====================
def parse_date(date_str):
    """Converte string de data no formato DD/MM para objeto Date"""
    if not date_str:
        return None
    try:
        # Tenta formatos diferentes
        formats = ['%d/%m/%Y', '%d/%m/%y', '%d-%m-%Y', '%d-%m-%y']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        # Se nenhum formato funcionar, retorna None
        return None
    except Exception:
        return None

def format_date(date_obj):
    """Formata objeto Date para string DD/MM"""
    if date_obj:
        return date_obj.strftime('%d/%m/%Y')
    return ''

def validate_birth_date(date_str):
    """Valida data de nascimento no formato DD/MM"""
    if not date_str:
        return None
    
    # Remove espaços em branco
    date_str = date_str.strip()
    
    # Verifica se tem formato DD/MM
    if '/' in date_str:
        parts = date_str.split('/')
        if len(parts) == 2:
            try:
                dia = int(parts[0])
                mes = int(parts[1])
                
                # Valida dia e mês
                if 1 <= dia <= 31 and 1 <= mes <= 12:
                    return f"{dia:02d}/{mes:02d}"
            except ValueError:
                pass
    
    return None

# ==================== TEMPLATES HTML (COMPLETOS) ====================

INDEX_HTML = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ECC - Sistema de Gerenciamento</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; font-family: 'Segoe UI', sans-serif; }
        .navbar-brand { font-weight: bold; }
        .card { box-shadow: 0 2px 4px rgba(0,0,0,0.1); border: none; transition: transform 0.2s; }
        .card:hover { transform: translateY(-2px); }
        .btn-primary { background-color: #4361ee; border-color: #4361ee; }
        .btn-primary:hover { background-color: #3a56d4; border-color: #3a56d4; }
        .table th { background-color: #f1f5fd; }
        .badge-ecc { background-color: #7209b7; color: white; }
        @media (max-width: 768px) { .card { margin-bottom: 15px; } }
        .date-mask { text-align: center; }
        .btn-group-sm .btn { padding: 0.25rem 0.5rem; font-size: 0.875rem; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">ECC - Encontro de Casais com Cristo</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="/cadastro-casal">Cadastrar Casal</a></li>
                    <li class="nav-item"><a class="nav-link" href="/lista-casais">Casais</a></li>
                    <li class="nav-item"><a class="nav-link" href="/atividades">Atividades</a></li>
                    <li class="nav-item"><a class="nav-link" href="/equipes">Equipes</a></li>
                </ul>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="row">
            <div class="col-md-12 text-center mb-4">
                <h1 class="display-4 text-primary">Sistema de Gerenciamento ECC</h1>
                <p class="lead">Gerencie casais, encontros e equipes de trabalho</p>
            </div>
            
            <div class="col-md-3 mb-3">
                <div class="card h-100 text-center">
                    <div class="card-body">
                        <h5 class="card-title">📋 Cadastro de Casais</h5>
                        <p class="card-text">Cadastre novos casais para o encontro</p>
                        <a href="/cadastro-casal" class="btn btn-primary">Acessar</a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-3 mb-3">
                <div class="card h-100 text-center">
                    <div class="card-body">
                        <h5 class="card-title">👥 Lista de Casais</h5>
                        <p class="card-text">Consulte todos os casais cadastrados</p>
                        <a href="/lista-casais" class="btn btn-primary">Acessar</a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-3 mb-3">
                <div class="card h-100 text-center">
                    <div class="card-body">
                        <h5 class="card-title">⚙️ Gestão de Atividades</h5>
                        <p class="card-text">Organize equipes e atividades do encontro</p>
                        <a href="/atividades" class="btn btn-primary">Acessar</a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-3 mb-3">
                <div class="card h-100 text-center">
                    <div class="card-body">
                        <h5 class="card-title">👷 Equipes de Trabalho</h5>
                        <p class="card-text">Visualize todas as equipes formadas</p>
                        <a href="/equipes" class="btn btn-primary">Acessar</a>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h5>📊 Estatísticas do Sistema</h5>
                    </div>
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-md-3">
                                <h3>{{ total_casais }}</h3>
                                <p>Casais Cadastrados</p>
                            </div>
                            <div class="col-md-3">
                                <h3>{{ total_equipes }}</h3>
                                <p>Equipes Formadas</p>
                            </div>
                            <div class="col-md-3">
                                <h3>{{ voluntarios }}</h3>
                                <p>Voluntários Ativos</p>
                            </div>
                            <div class="col-md-3">
                                <h3>{{ ultimo_ecc }}</h3>
                                <p>Último ECC</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <footer class="bg-light text-center text-muted mt-5 py-3">
        <div class="container">
            <p>Sistema ECC &copy; 2026 - Desenvolvido para a Igreja Católica</p>
        </div>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Máscara para datas de nascimento (DD/MM)
        function aplicarMascaraNascimento(input) {
            input.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                
                if (value.length > 2) {
                    value = value.substring(0, 2) + '/' + value.substring(2, 4);
                }
                
                e.target.value = value;
            });
        }
        
        // Máscara para outras datas (DD/MM)
        function aplicarMascaraDataCompleta(input) {
            input.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                
                if (value.length > 2) {
                    value = value.substring(0, 2) + '/' + value.substring(2);
                }
                if (value.length > 5) {
                    value = value.substring(0, 5) + '/' + value.substring(5, 9);
                }
                
                e.target.value = value;
            });
        }
        
        // Aplicar máscaras
        document.addEventListener('DOMContentLoaded', function() {
            // Máscara para nascimento (DD/MM)
            document.querySelectorAll('.birth-date-input').forEach(function(input) {
                aplicarMascaraNascimento(input);
            });
            
            // Máscara para outras datas (DD/MM)
            document.querySelectorAll('.full-date-input').forEach(function(input) {
                aplicarMascaraDataCompleta(input);
            });
        });
    </script>
</body>
</html>
'''

CADASTRO_CASAL_HTML = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cadastro de Casal - ECC</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; font-family: 'Segoe UI', sans-serif; }
        .navbar-brand { font-weight: bold; }
        .card { box-shadow: 0 2px 4px rgba(0,0,0,0.1); border: none; }
        .btn-primary { background-color: #4361ee; border-color: #4361ee; }
        .btn-primary:hover { background-color: #3a56d4; border-color: #3a56d4; }
        .date-input { text-align: center; }
        .date-input::placeholder { text-align: center; color: #999; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">ECC - Cadastro de Casal</a>
            <a href="/" class="btn btn-light">Voltar</a>
        </div>
    </nav>

    <div class="container mt-4">
        <h2 class="mb-4">📋 Cadastro de Casal - ECC</h2>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            <!-- Informações Gerais -->
            <div class="card mb-4">
                <div class="card-header bg-primary text-white">
                    <h5>Informações Gerais</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">(Arqui)Diocese:</label>
                                <input type="text" class="form-control" name="arquidiocese" required>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Cidade:</label>
                                <input type="text" class="form-control" name="cidade" required>
                            </div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Paróquia:</label>
                        <input type="text" class="form-control" name="paroquia" required>
                    </div>
                </div>
            </div>

            <div class="row">
                <!-- Coluna ELE -->
                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header bg-success text-white">
                            <h5>👨 Dados do Marido (ELE)</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Nome Completo:</label>
                                <input type="text" class="form-control" name="nome_ele" required>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Nascimento:</label>
                                        <input type="text" class="form-control birth-date-input" name="nascimento_ele" 
                                               placeholder="DD/MM" required
                                               pattern="\d{2}/\d{2}"
                                               title="Digite a data no formato DD/MM">
                                        <small class="text-muted">Formato: DD/MM (apenas dia e mês)</small>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Nome Usual:</label>
                                        <input type="text" class="form-control" name="nome_usual_ele">
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Profissão:</label>
                                <input type="text" class="form-control" name="profissao_ele">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Telefone:</label>
                                <input type="tel" class="form-control" name="fone_prof_ele">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Coluna ELA -->
                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header bg-danger text-white">
                            <h5>👩 Dados da Esposa (ELA)</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Nome Completo:</label>
                                <input type="text" class="form-control" name="nome_ela" required>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Nascimento:</label>
                                        <input type="text" class="form-control birth-date-input" name="nascimento_ela" 
                                               placeholder="DD/MM" required
                                               pattern="\d{2}/\d{2}"
                                               title="Digite a data no formato DD/MM">
                                        <small class="text-muted">Formato: DD/MM (apenas dia e mês)</small>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Nome Usual:</label>
                                        <input type="text" class="form-control" name="nome_usual_ela">
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Profissão:</label>
                                <input type="text" class="form-control" name="profissao_ela">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Telefone:</label>
                                <input type="tel" class="form-control" name="fone_prof_ela">
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Dados do Casal -->
            <div class="card mb-4">
                <div class="card-header bg-warning text-dark">
                    <h5>💑 Dados do Casal</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Casamento Religioso:</label>
                                <select class="form-select" name="casamento_religioso" required>
                                    <option value="sim">Sim</option>
                                    <option value="nao">Não</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Data do Casamento:</label>
                                <input type="text" class="form-control full-date-input" name="data_casamento" 
                                       placeholder="DD/MM"
                                       pattern="\d{2}/\d{2}/\d{4}"
                                       title="Digite a data no formato DD/MM">
                                <small class="text-muted">Formato: DD/MM</small>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Data do Casamento Civil:</label>
                                <input type="text" class="form-control full-date-input" name="data_casamento_civil" 
                                       placeholder="DD/MM"
                                       pattern="\d{2}/\d{2}/\d{4}"
                                       title="Digite a data no formato DD/MM">
                                <small class="text-muted">Formato: DD/MM</small>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Número de Filhos:</label>
                                <input type="number" class="form-control" name="num_filhos" min="0" value="0">
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Endereço -->
            <div class="card mb-4">
                <div class="card-header bg-info text-white">
                    <h5>🏠 Endereço</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-8">
                            <div class="mb-3">
                                <label class="form-label">Endereço:</label>
                                <input type="text" class="form-control" name="endereco">
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="mb-3">
                                <label class="form-label">Nº:</label>
                                <input type="text" class="form-control" name="numero">
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="mb-3">
                                <label class="form-label">Apto:</label>
                                <input type="text" class="form-control" name="apto">
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Bairro:</label>
                                <input type="text" class="form-control" name="bairro">
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">CEP:</label>
                                <input type="text" class="form-control" name="cep" placeholder="00000-000">
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">Telefone:</label>
                                <input type="tel" class="form-control" name="fone" placeholder="(89) 99999-9999">
                            </div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Cidade/Estado:</label>
                        <input type="text" class="form-control" name="cidade_estado" placeholder="Floriano - PI">
                    </div>
                </div>
            </div>

            <!-- ECC - 1ª Etapa -->
            <div class="card mb-4">
                <div class="card-header bg-secondary text-white">
                    <h5>ECC - 1ª Etapa</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">Nº:</label>
                                <input type="text" class="form-control" name="ecc_etapa1_num">
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">Data:</label>
                                <input type="text" class="form-control full-date-input" name="ecc_etapa1_data" 
                                       placeholder="DD/MM"
                                       pattern="\d{2}/\d{2}/\d{4}"
                                       title="Digite a data no formato DD/MM">
                                <small class="text-muted">Formato: DD/MM</small>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Local:</label>
                                <input type="text" class="form-control" name="ecc_etapa1_local">
                            </div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Atividades:</label>
                        <textarea class="form-control" name="ecc_etapa1_atividades" rows="2"></textarea>
                    </div>
                </div>
            </div>

            <!-- ECC - 2ª Etapa -->
            <div class="card mb-4">
                <div class="card-header bg-secondary text-white">
                    <h5>ECC - 2ª Etapa</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">Nº:</label>
                                <input type="text" class="form-control" name="ecc_etapa2_num">
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">Data:</label>
                                <input type="text" class="form-control full-date-input" name="ecc_etapa2_data" 
                                       placeholder="DD/MM"
                                       pattern="\d{2}/\d{2}/\d{4}"
                                       title="Digite a data no formato DD/MM">
                                <small class="text-muted">Formato: DD/MM</small>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Local:</label>
                                <input type="text" class="form-control" name="ecc_etapa2_local">
                            </div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Atividades:</label>
                        <textarea class="form-control" name="ecc_etapa2_atividades" rows="2"></textarea>
                    </div>
                </div>
            </div>

            <!-- ECC - 3ª Etapa -->
            <div class="card mb-4">
                <div class="card-header bg-secondary text-white">
                    <h5>ECC - 3ª Etapa</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">Nº:</label>
                                <input type="text" class="form-control" name="ecc_etapa3_num">
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">Data:</label>
                                <input type="text" class="form-control full-date-input" name="ecc_etapa3_data" 
                                       placeholder="DD/MM"
                                       pattern="\d{2}/\d{2}/\d{4}"
                                       title="Digite a data no formato DD/MM">
                                <small class="text-muted">Formato: DD/MM</small>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Local:</label>
                                <input type="text" class="form-control" name="ecc_etapa3_local">
                            </div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Atividades:</label>
                        <textarea class="form-control" name="ecc_etapa3_atividades" rows="2"></textarea>
                    </div>
                </div>
            </div>

            <!-- Informações Adicionais -->
            <div class="card mb-4">
                <div class="card-header bg-dark text-white">
                    <h5>📝 Informações Adicionais</h5>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <label class="form-label">Engajamento Paroquial:</label>
                        <textarea class="form-control" name="engajamento_paroquial" rows="3" placeholder="Atividades que o casal participa na paróquia..."></textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Habilidades:</label>
                        <textarea class="form-control" name="habilidades" rows="3" placeholder="Habilidades e talentos do casal que podem ser úteis para a comunidade..."></textarea>
                    </div>
                </div>
            </div>

            <div class="mb-4">
                <button type="submit" class="btn btn-primary btn-lg">💾 Salvar Cadastro</button>
                <a href="/" class="btn btn-secondary">Cancelar</a>
            </div>
        </form>
    </div>
    
    <footer class="bg-light text-center text-muted mt-5 py-3">
        <div class="container">
            <p>Sistema ECC &copy; 2026 - Desenvolvido para a Igreja Católica</p>
        </div>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Máscara para datas de nascimento (DD/MM)
        function aplicarMascaraNascimento(input) {
            input.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                
                if (value.length > 2) {
                    value = value.substring(0, 2) + '/' + value.substring(2, 4);
                }
                
                e.target.value = value;
            });
        }
        
        // Máscara para outras datas (DD/MM)
        function aplicarMascaraDataCompleta(input) {
            input.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                
                if (value.length > 2) {
                    value = value.substring(0, 2) + '/' + value.substring(2);
                }
                if (value.length > 5) {
                    value = value.substring(0, 5) + '/' + value.substring(5, 9);
                }
                
                e.target.value = value;
            });
        }
        
        // Máscara para CEP (00000-000)
        function aplicarMascaraCEP(input) {
            input.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                
                if (value.length > 5) {
                    value = value.substring(0, 5) + '-' + value.substring(5, 8);
                }
                
                e.target.value = value;
            });
        }
        
        // Máscara para telefone ((89) 99999-9999)
        function aplicarMascaraTelefone(input) {
            input.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                
                if (value.length > 0) {
                    value = '(' + value.substring(0, 2) + ') ' + value.substring(2);
                }
                if (value.length > 10) {
                    value = value.substring(0, 10) + '-' + value.substring(10, 15);
                }
                
                e.target.value = value;
            });
        }
        
        // Aplicar máscaras
        document.addEventListener('DOMContentLoaded', function() {
            // Máscara para nascimento (DD/MM)
            document.querySelectorAll('.birth-date-input').forEach(function(input) {
                aplicarMascaraNascimento(input);
            });
            
            // Máscara para outras datas (DD/MM)
            document.querySelectorAll('.full-date-input').forEach(function(input) {
                aplicarMascaraDataCompleta(input);
            });
            
            // Máscara para CEP
            const cepInput = document.querySelector('input[name="cep"]');
            if (cepInput) aplicarMascaraCEP(cepInput);
            
            // Máscara para telefone
            const foneInput = document.querySelector('input[name="fone"]');
            if (foneInput) aplicarMascaraTelefone(foneInput);
        });
    </script>
</body>
</html>
'''

LISTA_CASAIS_HTML = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lista de Casais - ECC</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; font-family: 'Segoe UI', sans-serif; }
        .navbar-brand { font-weight: bold; }
        .card { box-shadow: 0 2px 4px rgba(0,0,0,0.1); border: none; }
        .btn-primary { background-color: #4361ee; border-color: #4361ee; }
        .btn-primary:hover { background-color: #3a56d4; border-color: #3a56d4; }
        .table th { background-color: #f1f5fd; }
        .btn-group-sm .btn { padding: 0.25rem 0.5rem; font-size: 0.875rem; }
        .modal-confirm { color: #636363; }
        .modal-confirm .modal-content { border-radius: 5px; border: none; }
        .modal-confirm .modal-header { border-bottom: none; position: relative; }
        .modal-confirm .modal-body { color: #999; }
        .modal-confirm .modal-footer { border: none; text-align: center; border-radius: 5px; }
        .modal-confirm .btn { min-width: 100px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">ECC - Lista de Casais</a>
            <div class="navbar-nav ms-auto">
                <a href="/" class="nav-link">Home</a>
                <a href="/cadastro-casal" class="btn btn-light ms-2">➕ Novo Casal</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <h2 class="mb-4">👥 Lista de Casais Cadastrados</h2>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="card">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                <h5>Total: {{ casais|length }} casais</h5>
                <a href="/cadastro-casal" class="btn btn-light">➕ Novo Casal</a>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Casal</th>
                                <th>Paróquia</th>
                                <th>Cidade</th>
                                <th>Casamento</th>
                                <th>Filhos</th>
                                <th>Data Cadastro</th>
                                <th>Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for casal in casais %}
                            <tr>
                                <td>{{ casal.id }}</td>
                                <td>
                                    <strong>{{ casal.nome_ele }}</strong> e <strong>{{ casal.nome_ela }}</strong><br>
                                    <small>{{ casal.nome_usual_ele }} & {{ casal.nome_usual_ela }}</small>
                                </td>
                                <td>{{ casal.paroquia }}</td>
                                <td>{{ casal.cidade }}</td>
                                <td>
                                    {% if casal.casamento_religioso %}
                                    <span class="badge bg-success">Religioso</span>
                                    {% else %}
                                    <span class="badge bg-warning">Civil</span>
                                    {% endif %}
                                </td>
                                <td>{{ casal.num_filhos }}</td>
                                <td>{{ casal.data_cadastro.strftime('%d/%m/%Y') }}</td>
                                <td>
                                    <div class="btn-group btn-group-sm" role="group">
                                        <a href="/casal/{{ casal.id }}" class="btn btn-info" title="Ver detalhes">
                                            <i class="bi bi-eye"></i> Ver
                                        </a>
                                        <a href="/editar-casal/{{ casal.id }}" class="btn btn-warning" title="Editar casal">
                                            <i class="bi bi-pencil"></i> Editar
                                        </a>
                                        <button type="button" class="btn btn-danger" 
                                                data-bs-toggle="modal" 
                                                data-bs-target="#modalExcluir{{ casal.id }}"
                                                title="Excluir casal">
                                            <i class="bi bi-trash"></i> Excluir
                                        </button>
                                    </div>
                                    
                                    <!-- Modal de Confirmação de Exclusão -->
                                    <div class="modal fade" id="modalExcluir{{ casal.id }}" tabindex="-1" aria-hidden="true">
                                        <div class="modal-dialog modal-dialog-centered">
                                            <div class="modal-content">
                                                <div class="modal-header">
                                                    <h5 class="modal-title text-danger">⚠️ Confirmar Exclusão</h5>
                                                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                                </div>
                                                <div class="modal-body">
                                                    <p>Tem certeza que deseja excluir o casal:</p>
                                                    <p class="fw-bold">{{ casal.nome_ele }} e {{ casal.nome_ela }}?</p>
                                                    <p class="text-muted">Esta ação não pode ser desfeita.</p>
                                                </div>
                                                <div class="modal-footer">
                                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                                                    <form action="/excluir-casal/{{ casal.id }}" method="POST" style="display: inline;">
                                                        <button type="submit" class="btn btn-danger">Sim, Excluir</button>
                                                    </form>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <div class="mt-3">
            <a href="/" class="btn btn-secondary">← Voltar para Home</a>
        </div>
    </div>
    
    <footer class="bg-light text-center text-muted mt-5 py-3">
        <div class="container">
            <p>Sistema ECC &copy; 2026 - Desenvolvido para a Igreja Católica</p>
        </div>
    </footer>
    
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

EDITAR_CASAL_HTML = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Editar Casal - ECC</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; font-family: 'Segoe UI', sans-serif; }
        .navbar-brand { font-weight: bold; }
        .card { box-shadow: 0 2px 4px rgba(0,0,0,0.1); border: none; }
        .btn-primary { background-color: #4361ee; border-color: #4361ee; }
        .btn-primary:hover { background-color: #3a56d4; border-color: #3a56d4; }
        .date-input { text-align: center; }
        .date-input::placeholder { text-align: center; color: #999; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">ECC - Editar Casal</a>
            <a href="/lista-casais" class="btn btn-light">Voltar</a>
        </div>
    </nav>

    <div class="container mt-4">
        <h2 class="mb-4">✏️ Editar Casal - ECC</h2>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            <!-- Informações Gerais -->
            <div class="card mb-4">
                <div class="card-header bg-primary text-white">
                    <h5>Informações Gerais</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">(Arqui)Diocese:</label>
                                <input type="text" class="form-control" name="arquidiocese" value="{{ casal.arquidiocese or '' }}" required>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Cidade:</label>
                                <input type="text" class="form-control" name="cidade" value="{{ casal.cidade or '' }}" required>
                            </div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Paróquia:</label>
                        <input type="text" class="form-control" name="paroquia" value="{{ casal.paroquia or '' }}" required>
                    </div>
                </div>
            </div>

            <div class="row">
                <!-- Coluna ELE -->
                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header bg-success text-white">
                            <h5>👨 Dados do Marido (ELE)</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Nome Completo:</label>
                                <input type="text" class="form-control" name="nome_ele" value="{{ casal.nome_ele or '' }}" required>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Nascimento:</label>
                                        <input type="text" class="form-control birth-date-input" name="nascimento_ele" 
                                               value="{{ casal.nascimento_ele or '' }}"
                                               placeholder="DD/MM" required
                                               pattern="\d{2}/\d{2}"
                                               title="Digite a data no formato DD/MM">
                                        <small class="text-muted">Formato: DD/MM (apenas dia e mês)</small>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Nome Usual:</label>
                                        <input type="text" class="form-control" name="nome_usual_ele" value="{{ casal.nome_usual_ele or '' }}">
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Profissão:</label>
                                <input type="text" class="form-control" name="profissao_ele" value="{{ casal.profissao_ele or '' }}">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Telefone:</label>
                                <input type="tel" class="form-control" name="fone_prof_ele" value="{{ casal.fone_prof_ele or '' }}">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Coluna ELA -->
                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header bg-danger text-white">
                            <h5>👩 Dados da Esposa (ELA)</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Nome Completo:</label>
                                <input type="text" class="form-control" name="nome_ela" value="{{ casal.nome_ela or '' }}" required>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Nascimento:</label>
                                        <input type="text" class="form-control birth-date-input" name="nascimento_ela" 
                                               value="{{ casal.nascimento_ela or '' }}"
                                               placeholder="DD/MM" required
                                               pattern="\d{2}/\d{2}"
                                               title="Digite a data no formato DD/MM">
                                        <small class="text-muted">Formato: DD/MM (apenas dia e mês)</small>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Nome Usual:</label>
                                        <input type="text" class="form-control" name="nome_usual_ela" value="{{ casal.nome_usual_ela or '' }}">
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Profissão:</label>
                                <input type="text" class="form-control" name="profissao_ela" value="{{ casal.profissao_ela or '' }}">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Telefone:</label>
                                <input type="tel" class="form-control" name="fone_prof_ela" value="{{ casal.fone_prof_ela or '' }}">
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Dados do Casal -->
            <div class="card mb-4">
                <div class="card-header bg-warning text-dark">
                    <h5>💑 Dados do Casal</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Casamento Religioso:</label>
                                <select class="form-select" name="casamento_religioso" required>
                                    <option value="sim" {% if casal.casamento_religioso %}selected{% endif %}>Sim</option>
                                    <option value="nao" {% if not casal.casamento_religioso %}selected{% endif %}>Não</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Data do Casamento:</label>
                                <input type="text" class="form-control full-date-input" name="data_casamento" 
                                       value="{% if casal.data_casamento %}{{ casal.data_casamento.strftime('%d/%m/%Y') }}{% endif %}"
                                       placeholder="DD/MM"
                                       pattern="\d{2}/\d{2}/\d{4}"
                                       title="Digite a data no formato DD/MM">
                                <small class="text-muted">Formato: DD/MM</small>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Data do Casamento Civil:</label>
                                <input type="text" class="form-control full-date-input" name="data_casamento_civil" 
                                       value="{% if casal.data_casamento_civil %}{{ casal.data_casamento_civil.strftime('%d/%m/%Y') }}{% endif %}"
                                       placeholder="DD/MM"
                                       pattern="\d{2}/\d{2}/\d{4}"
                                       title="Digite a data no formato DD/MM">
                                <small class="text-muted">Formato: DD/MM</small>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Número de Filhos:</label>
                                <input type="number" class="form-control" name="num_filhos" min="0" value="{{ casal.num_filhos or 0 }}">
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Endereço -->
            <div class="card mb-4">
                <div class="card-header bg-info text-white">
                    <h5>🏠 Endereço</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-8">
                            <div class="mb-3">
                                <label class="form-label">Endereço:</label>
                                <input type="text" class="form-control" name="endereco" value="{{ casal.endereco or '' }}">
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="mb-3">
                                <label class="form-label">Nº:</label>
                                <input type="text" class="form-control" name="numero" value="{{ casal.numero or '' }}">
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="mb-3">
                                <label class="form-label">Apto:</label>
                                <input type="text" class="form-control" name="apto" value="{{ casal.apto or '' }}">
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Bairro:</label>
                                <input type="text" class="form-control" name="bairro" value="{{ casal.bairro or '' }}">
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">CEP:</label>
                                <input type="text" class="form-control" name="cep" value="{{ casal.cep or '' }}" placeholder="00000-000">
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">Telefone:</label>
                                <input type="tel" class="form-control" name="fone" value="{{ casal.fone or '' }}" placeholder="(89) 99999-9999">
                            </div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Cidade/Estado:</label>
                        <input type="text" class="form-control" name="cidade_estado" value="{{ casal.cidade_estado or '' }}" placeholder="Floriano - PI">
                    </div>
                </div>
            </div>

            <!-- ECC - 1ª Etapa -->
            <div class="card mb-4">
                <div class="card-header bg-secondary text-white">
                    <h5>ECC - 1ª Etapa</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">Nº:</label>
                                <input type="text" class="form-control" name="ecc_etapa1_num" value="{{ casal.ecc_etapa1_num or '' }}">
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">Data:</label>
                                <input type="text" class="form-control full-date-input" name="ecc_etapa1_data" 
                                       value="{% if casal.ecc_etapa1_data %}{{ casal.ecc_etapa1_data.strftime('%d/%m/%Y') }}{% endif %}"
                                       placeholder="DD/MM"
                                       pattern="\d{2}/\d{2}/\d{4}"
                                       title="Digite a data no formato DD/MM">
                                <small class="text-muted">Formato: DD/MM</small>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Local:</label>
                                <input type="text" class="form-control" name="ecc_etapa1_local" value="{{ casal.ecc_etapa1_local or '' }}">
                            </div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Atividades:</label>
                        <textarea class="form-control" name="ecc_etapa1_atividades" rows="2">{{ casal.ecc_etapa1_atividades or '' }}</textarea>
                    </div>
                </div>
            </div>

            <!-- ECC - 2ª Etapa -->
            <div class="card mb-4">
                <div class="card-header bg-secondary text-white">
                    <h5>ECC - 2ª Etapa</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">Nº:</label>
                                <input type="text" class="form-control" name="ecc_etapa2_num" value="{{ casal.ecc_etapa2_num or '' }}">
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">Data:</label>
                                <input type="text" class="form-control full-date-input" name="ecc_etapa2_data" 
                                       value="{% if casal.ecc_etapa2_data %}{{ casal.ecc_etapa2_data.strftime('%d/%m/%Y') }}{% endif %}"
                                       placeholder="DD/MM"
                                       pattern="\d{2}/\d{2}/\d{4}"
                                       title="Digite a data no formato DD/MM">
                                <small class="text-muted">Formato: DD/MM</small>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Local:</label>
                                <input type="text" class="form-control" name="ecc_etapa2_local" value="{{ casal.ecc_etapa2_local or '' }}">
                            </div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Atividades:</label>
                        <textarea class="form-control" name="ecc_etapa2_atividades" rows="2">{{ casal.ecc_etapa2_atividades or '' }}</textarea>
                    </div>
                </div>
            </div>

            <!-- ECC - 3ª Etapa -->
            <div class="card mb-4">
                <div class="card-header bg-secondary text-white">
                    <h5>ECC - 3ª Etapa</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">Nº:</label>
                                <input type="text" class="form-control" name="ecc_etapa3_num" value="{{ casal.ecc_etapa3_num or '' }}">
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">Data:</label>
                                <input type="text" class="form-control full-date-input" name="ecc_etapa3_data" 
                                       value="{% if casal.ecc_etapa3_data %}{{ casal.ecc_etapa3_data.strftime('%d/%m/%Y') }}{% endif %}"
                                       placeholder="DD/MM"
                                       pattern="\d{2}/\d{2}/\d{4}"
                                       title="Digite a data no formato DD/MM">
                                <small class="text-muted">Formato: DD/MM</small>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Local:</label>
                                <input type="text" class="form-control" name="ecc_etapa3_local" value="{{ casal.ecc_etapa3_local or '' }}">
                            </div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Atividades:</label>
                        <textarea class="form-control" name="ecc_etapa3_atividades" rows="2">{{ casal.ecc_etapa3_atividades or '' }}</textarea>
                    </div>
                </div>
            </div>

            <!-- Informações Adicionais -->
            <div class="card mb-4">
                <div class="card-header bg-dark text-white">
                    <h5>📝 Informações Adicionais</h5>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <label class="form-label">Engajamento Paroquial:</label>
                        <textarea class="form-control" name="engajamento_paroquial" rows="3" placeholder="Atividades que o casal participa na paróquia...">{{ casal.engajamento_paroquial or '' }}</textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Habilidades:</label>
                        <textarea class="form-control" name="habilidades" rows="3" placeholder="Habilidades e talentos do casal que podem ser úteis para a comunidade...">{{ casal.habilidades or '' }}</textarea>
                    </div>
                </div>
            </div>

            <div class="mb-4">
                <button type="submit" class="btn btn-primary btn-lg">💾 Atualizar Cadastro</button>
                <a href="/lista-casais" class="btn btn-secondary">Cancelar</a>
            </div>
        </form>
    </div>
    
    <footer class="bg-light text-center text-muted mt-5 py-3">
        <div class="container">
            <p>Sistema ECC &copy; 2026 - Desenvolvido para a Igreja Católica</p>
        </div>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Máscara para datas de nascimento (DD/MM)
        function aplicarMascaraNascimento(input) {
            input.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                
                if (value.length > 2) {
                    value = value.substring(0, 2) + '/' + value.substring(2, 4);
                }
                
                e.target.value = value;
            });
        }
        
        // Máscara para outras datas (DD/MM)
        function aplicarMascaraDataCompleta(input) {
            input.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                
                if (value.length > 2) {
                    value = value.substring(0, 2) + '/' + value.substring(2);
                }
                if (value.length > 5) {
                    value = value.substring(0, 5) + '/' + value.substring(5, 9);
                }
                
                e.target.value = value;
            });
        }
        
        // Máscara para CEP (00000-000)
        function aplicarMascaraCEP(input) {
            input.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                
                if (value.length > 5) {
                    value = value.substring(0, 5) + '-' + value.substring(5, 8);
                }
                
                e.target.value = value;
            });
        }
        
        // Máscara para telefone ((89) 99999-9999)
        function aplicarMascaraTelefone(input) {
            input.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                
                if (value.length > 0) {
                    value = '(' + value.substring(0, 2) + ') ' + value.substring(2);
                }
                if (value.length > 10) {
                    value = value.substring(0, 10) + '-' + value.substring(10, 15);
                }
                
                e.target.value = value;
            });
        }
        
        // Aplicar máscaras
        document.addEventListener('DOMContentLoaded', function() {
            // Máscara para nascimento (DD/MM)
            document.querySelectorAll('.birth-date-input').forEach(function(input) {
                aplicarMascaraNascimento(input);
            });
            
            // Máscara para outras datas (DD/MM)
            document.querySelectorAll('.full-date-input').forEach(function(input) {
                aplicarMascaraDataCompleta(input);
            });
            
            // Máscara para CEP
            const cepInput = document.querySelector('input[name="cep"]');
            if (cepInput) aplicarMascaraCEP(cepInput);
            
            // Máscara para telefone
            const foneInput = document.querySelector('input[name="fone"]');
            if (foneInput) aplicarMascaraTelefone(foneInput);
        });
    </script>
</body>
</html>
'''

VER_CASAL_HTML = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Detalhes do Casal - ECC</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; font-family: 'Segoe UI', sans-serif; }
        .navbar-brand { font-weight: bold; }
        .card { box-shadow: 0 2px 4px rgba(0,0,0,0.1); border: none; }
        .btn-primary { background-color: #4361ee; border-color: #4361ee; }
        .btn-primary:hover { background-color: #3a56d4; border-color: #3a56d4; }
        hr { border-top: 2px solid #dee2e6; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">ECC - Detalhes do Casal</a>
            <div>
                <a href="/lista-casais" class="btn btn-light">← Voltar</a>
                <a href="/" class="btn btn-light ms-2">Home</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <h2 class="mb-4">👨‍👩‍👧‍👦 Detalhes do Casal</h2>
        
        <div class="card mb-4">
            <div class="card-header bg-primary text-white">
                <h5>{{ casal.nome_ele }} & {{ casal.nome_ela }}</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h6 class="text-primary">👨 Marido</h6>
                        <p><strong>Nome:</strong> {{ casal.nome_ele }}</p>
                        <p><strong>Nome Usual:</strong> {{ casal.nome_usual_ele }}</p>
                        <p><strong>Nascimento:</strong> {{ casal.nascimento_ele or 'N/A' }}</p>
                        <p><strong>Profissão:</strong> {{ casal.profissao_ele or 'N/A' }}</p>
                        <p><strong>Tel. Profissional:</strong> {{ casal.fone_prof_ele or 'N/A' }}</p>
                    </div>
                    <div class="col-md-6">
                        <h6 class="text-danger">👩 Esposa</h6>
                        <p><strong>Nome:</strong> {{ casal.nome_ela }}</p>
                        <p><strong>Nome Usual:</strong> {{ casal.nome_usual_ela }}</p>
                        <p><strong>Nascimento:</strong> {{ casal.nascimento_ela or 'N/A' }}</p>
                        <p><strong>Profissão:</strong> {{ casal.profissao_ela or 'N/A' }}</p>
                        <p><strong>Tel. Profissional:</strong> {{ casal.fone_prof_ela or 'N/A' }}</p>
                    </div>
                </div>
                
                <hr>
                
                <div class="row">
                    <div class="col-md-4">
                        <h6 class="text-warning">💑 Casal</h6>
                        <p><strong>Casamento Religioso:</strong> {{ 'Sim' if casal.casamento_religioso else 'Não' }}</p>
                        <p><strong>Data Casamento:</strong> {{ casal.data_casamento.strftime('%d/%m/%Y') if casal.data_casamento else 'N/A' }}</p>
                        <p><strong>Filhos:</strong> {{ casal.num_filhos }}</p>
                    </div>
                    <div class="col-md-4">
                        <h6 class="text-info">🏠 Endereço</h6>
                        <p>{{ casal.endereco or 'N/A' }}, {{ casal.numero or '' }} {{ casal.apto or '' }}</p>
                        <p>{{ casal.bairro or 'N/A' }}</p>
                        <p>{{ casal.cidade_estado or 'N/A' }} - CEP: {{ casal.cep or 'N/A' }}</p>
                        <p><strong>Telefone:</strong> {{ casal.fone or 'N/A' }}</p>
                    </div>
                    <div class="col-md-4">
                        <h6 class="text-success">⛪ Paróquia</h6>
                        <p><strong>Diocese:</strong> {{ casal.arquidiocese or 'N/A' }}</p>
                        <p><strong>Cidade:</strong> {{ casal.cidade or 'N/A' }}</p>
                        <p><strong>Paróquia:</strong> {{ casal.paroquia or 'N/A' }}</p>
                    </div>
                </div>
                
                {% if casal.engajamento_paroquial or casal.habilidades %}
                <hr>
                <div class="row">
                    {% if casal.engajamento_paroquial %}
                    <div class="col-md-6">
                        <h6>📝 Engajamento Paroquial</h6>
                        <p>{{ casal.engajamento_paroquial }}</p>
                    </div>
                    {% endif %}
                    {% if casal.habilidades %}
                    <div class="col-md-6">
                        <h6>🔧 Habilidades</h6>
                        <p>{{ casal.habilidades }}</p>
                    </div>
                    {% endif %}
                </div>
                {% endif %}
                
                {% if casal.ecc_etapa1_num or casal.ecc_etapa2_num or casal.ecc_etapa3_num %}
                <hr>
                <h6>🎯 Participação no ECC</h6>
                <div class="row">
                    {% if casal.ecc_etapa1_num %}
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header bg-secondary text-white py-2">
                                <strong>1ª Etapa</strong>
                            </div>
                            <div class="card-body p-2">
                                <small>
                                    <strong>Nº:</strong> {{ casal.ecc_etapa1_num }}<br>
                                    <strong>Data:</strong> {{ casal.ecc_etapa1_data.strftime('%d/%m/%Y') if casal.ecc_etapa1_data else 'N/A' }}<br>
                                    <strong>Local:</strong> {{ casal.ecc_etapa1_local or 'N/A' }}<br>
                                    {% if casal.ecc_etapa1_atividades %}
                                    <strong>Atividades:</strong> {{ casal.ecc_etapa1_atividades }}
                                    {% endif %}
                                </small>
                            </div>
                        </div>
                    </div>
                    {% endif %}
                    
                    {% if casal.ecc_etapa2_num %}
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header bg-secondary text-white py-2">
                                <strong>2ª Etapa</strong>
                            </div>
                            <div class="card-body p-2">
                                <small>
                                    <strong>Nº:</strong> {{ casal.ecc_etapa2_num }}<br>
                                    <strong>Data:</strong> {{ casal.ecc_etapa2_data.strftime('%d/%m/%Y') if casal.ecc_etapa2_data else 'N/A' }}<br>
                                    <strong>Local:</strong> {{ casal.ecc_etapa2_local or 'N/A' }}<br>
                                    {% if casal.ecc_etapa2_atividades %}
                                    <strong>Atividades:</strong> {{ casal.ecc_etapa2_atividades }}
                                    {% endif %}
                                </small>
                            </div>
                        </div>
                    </div>
                    {% endif %}
                    
                    {% if casal.ecc_etapa3_num %}
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header bg-secondary text-white py-2">
                                <strong>3ª Etapa</strong>
                            </div>
                            <div class="card-body p-2">
                                <small>
                                    <strong>Nº:</strong> {{ casal.ecc_etapa3_num }}<br>
                                    <strong>Data:</strong> {{ casal.ecc_etapa3_data.strftime('%d/%m/%Y') if casal.ecc_etapa3_data else 'N/A' }}<br>
                                    <strong>Local:</strong> {{ casal.ecc_etapa3_local or 'N/A' }}<br>
                                    {% if casal.ecc_etapa3_atividades %}
                                    <strong>Atividades:</strong> {{ casal.ecc_etapa3_atividades }}
                                    {% endif %}
                                </small>
                            </div>
                        </div>
                    </div>
                    {% endif %}
                </div>
                {% endif %}
            </div>
            <div class="card-footer">
                <small class="text-muted">Cadastrado em: {{ casal.data_cadastro.strftime('%d/%m/%Y %H:%M') }}</small>
            </div>
        </div>

        <div class="mb-4">
            <a href="/lista-casais" class="btn btn-secondary">← Voltar para Lista</a>
            <a href="/" class="btn btn-primary">🏠 Página Inicial</a>
        </div>
    </div>
    
    <footer class="bg-light text-center text-muted mt-5 py-3">
        <div class="container">
            <p>Sistema ECC &copy; 2026 - Desenvolvido para a Igreja Católica</p>
        </div>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# OS TEMPLATES ATIVIDADES_HTML E EQUIPES_HTML PERMANECEM IGUAIS
# Vou mantê-los como estavam para economizar espaço

ATIVIDADES_HTML = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestão de Atividades - ECC</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; font-family: 'Segoe UI', sans-serif; }
        .navbar-brand { font-weight: bold; }
        .card { box-shadow: 0 2px 4px rgba(0,0,0,0.1); border: none; }
        .btn-primary { background-color: #4361ee; border-color: #4361ee; }
        .btn-primary:hover { background-color: #3a56d4; border-color: #3a56d4; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">ECC - Gestão de Atividades</a>
            <a href="/" class="btn btn-light">Voltar</a>
        </div>
    </nav>

    <div class="container mt-4">
        <h2 class="mb-4">⚙️ Gestão de Atividades e Equipes</h2>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            <div class="card mb-4">
                <div class="card-header bg-primary text-white">
                    <h5>RELATÓRIO DE ATIVIDADES</h5>
                </div>
                <div class="card-body">
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <label class="form-label">Equipe de Trabalho:</label>
                            <input type="text" class="form-control" name="nome_equipe" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">ECC Nº:</label>
                            <input type="text" class="form-control" name="ecc_numero" required>
                        </div>
                    </div>
                    
                    <div class="row">
                        {% set campos = [
                            ('coord_geral', 'Coord. Geral'),
                            ('sala', 'Sala'),
                            ('liturgia_vigilia', 'Liturgia/Vigília'),
                            ('circulos', 'Círculos'),
                            ('cafe_minimercado', 'Café e Minimercado'),
                            ('cozinha', 'Cozinha'),
                            ('ordem_limpeza', 'Ordem e Limpeza'),
                            ('visitacao', 'Visitação'),
                            ('acolhida', 'Acolhida'),
                            ('secretaria', 'Secretaria'),
                            ('compras', 'Compras'),
                            ('palestras', 'Palestras')
                        ] %}
                        {% for campo, titulo in campos %}
                        <div class="col-md-4 mb-3">
                            <label class="form-label">{{ titulo }}:</label>
                            <input type="text" class="form-control" name="{{ campo }}">
                        </div>
                        {% endfor %}
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Opções de Trabalho (Formato: nome|status):</label>
                        <textarea class="form-control" name="opcoes_trabalho" rows="4" 
                            placeholder="Exemplo: João Silva|A, Maria Santos|IC, Pedro Costa|C, Ana Souza|N"></textarea>
                        <small class="text-muted">Legenda: A = Aceitou, IC = Indicado, C = Coordenou, N = Não Aceitou, N/A = Não Aceita, NN = Não Aceita Equipe</small>
                    </div>
                </div>
            </div>
            
            <div class="mb-4">
                <button type="submit" class="btn btn-primary btn-lg">💾 Salvar Atividades</button>
                <a href="/equipes" class="btn btn-secondary">Ver Equipes</a>
                <a href="/" class="btn btn-light">Home</a>
            </div>
        </form>
    </div>
    
    <footer class="bg-light text-center text-muted mt-5 py-3">
        <div class="container">
            <p>Sistema ECC &copy; 2026 - Desenvolvido para a Igreja Católica</p>
        </div>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

EQUIPES_HTML = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Equipes de Trabalho - ECC</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; font-family: 'Segoe UI', sans-serif; }
        .navbar-brand { font-weight: bold; }
        .card { box-shadow: 0 2px 4px rgba(0,0,0,0.1); border: none; }
        .btn-primary { background-color: #4361ee; border-color: #4361ee; }
        .btn-primary:hover { background-color: #3a56d4; border-color: #3a56d4; }
        .badge { font-size: 0.85em; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">ECC - Equipes de Trabalho</a>
            <div class="navbar-nav ms-auto">
                <a href="/" class="nav-link">Home</a>
                <a href="/atividades" class="btn btn-light ms-2">➕ Nova Equipe</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <h2 class="mb-4">👷 Equipes de Trabalho</h2>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="card">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                <h5>Total: {{ atividades|length }} equipes</h5>
                <a href="/atividades" class="btn btn-light">➕ Nova Equipe</a>
            </div>
            <div class="card-body">
                {% for atividade in atividades %}
                <div class="card mb-3">
                    <div class="card-header bg-light">
                        <h5>{{ atividade.nome_equipe }} - ECC {{ atividade.ecc_numero }}</h5>
                        <small class="text-muted">Criado em: {{ atividade.data_criacao.strftime('%d/%m/%Y %H:%M') }}</small>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            {% set campos_info = [
                                ('coord_geral', 'Coord. Geral'),
                                ('sala', 'Sala'),
                                ('liturgia_vigilia', 'Liturgia/Vigília'),
                                ('circulos', 'Círculos'),
                                ('cafe_minimercado', 'Café e Minimercado'),
                                ('cozinha', 'Cozinha'),
                                ('ordem_limpeza', 'Ordem e Limpeza'),
                                ('visitacao', 'Visitação'),
                                ('acolhida', 'Acolhida'),
                                ('secretaria', 'Secretaria'),
                                ('compras', 'Compras'),
                                ('palestras', 'Palestras')
                            ] %}
                            {% for campo, titulo in campos_info %}
                            {% if atividade[campo] %}
                            <div class="col-md-3 mb-2">
                                <strong>{{ titulo }}:</strong> {{ atividade[campo] }}
                            </div>
                            {% endif %}
                            {% endfor %}
                        </div>
                        
                        {% if atividade.opcoes_trabalho %}
                        <div class="mt-3">
                            <strong>Voluntários:</strong>
                            <div class="mt-2">
                                {% for item in atividade.opcoes_trabalho.split(',') %}
                                {% if item.strip() %}
                                {% set parts = item.strip().split('|') %}
                                {% if parts|length == 2 %}
                                <span class="badge 
                                    {% if parts[1].strip() == 'A' %}bg-success
                                    {% elif parts[1].strip() == 'IC' %}bg-info
                                    {% elif parts[1].strip() == 'C' %}bg-primary
                                    {% elif parts[1].strip() == 'N' %}bg-warning
                                    {% elif parts[1].strip() == 'N/A' %}bg-danger
                                    {% elif parts[1].strip() == 'NN' %}bg-dark
                                    {% else %}bg-secondary{% endif %} me-1 mb-1">
                                    {{ parts[0].strip() }} ({{ parts[1].strip() }})
                                </span>
                                {% endif %}
                                {% endif %}
                                {% endfor %}
                            </div>
                        </div>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="mt-3">
            <a href="/" class="btn btn-secondary">← Voltar para Home</a>
        </div>
    </div>
    
    <footer class="bg-light text-center text-muted mt-5 py-3">
        <div class="container">
            <p>Sistema ECC &copy; 2026 - Desenvolvido para a Igreja Católica</p>
        </div>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# ==================== ROTAS DA APLICAÇÃO (ATUALIZADAS) ====================
@app.route('/')
def index():
    total_casais = Casal.query.count()
    total_equipes = Atividade.query.count()
    
    # Contar voluntários ativos (simulação)
    voluntarios = total_casais * 2  # Cada casal tem 2 pessoas
    
    # Último ECC número
    ultima_atividade = Atividade.query.order_by(Atividade.data_criacao.desc()).first()
    ultimo_ecc = ultima_atividade.ecc_numero if ultima_atividade else "Nenhum"
    
    return render_template_string(INDEX_HTML, 
                                 total_casais=total_casais,
                                 total_equipes=total_equipes,
                                 voluntarios=voluntarios,
                                 ultimo_ecc=ultimo_ecc)

@app.route('/cadastro-casal', methods=['GET', 'POST'])
def cadastro_casal():
    if request.method == 'POST':
        try:
            # Validar e processar datas de nascimento
            nascimento_ele = validate_birth_date(request.form.get('nascimento_ele'))
            nascimento_ela = validate_birth_date(request.form.get('nascimento_ela'))
            
            if not nascimento_ele or not nascimento_ela:
                flash('❌ Por favor, insira datas de nascimento válidas no formato DD/MM', 'danger')
                return render_template_string(CADASTRO_CASAL_HTML)
            
            # Processar dados do formulário
            casal = Casal(
                arquidiocese=request.form.get('arquidiocese'),
                cidade=request.form.get('cidade'),
                paroquia=request.form.get('paroquia'),
                
                # Dados do marido
                nome_ele=request.form.get('nome_ele'),
                nascimento_ele=nascimento_ele,
                profissao_ele=request.form.get('profissao_ele'),
                nome_usual_ele=request.form.get('nome_usual_ele'),
                fone_prof_ele=request.form.get('fone_prof_ele'),
                
                # Dados da esposa
                nome_ela=request.form.get('nome_ela'),
                nascimento_ela=nascimento_ela,
                profissao_ela=request.form.get('profissao_ela'),
                nome_usual_ela=request.form.get('nome_usual_ela'),
                fone_prof_ela=request.form.get('fone_prof_ela'),
                
                # Dados do casal
                casamento_religioso=True if request.form.get('casamento_religioso') == 'sim' else False,
                data_casamento=parse_date(request.form.get('data_casamento')),
                data_casamento_civil=parse_date(request.form.get('data_casamento_civil')),
                num_filhos=int(request.form.get('num_filhos')) if request.form.get('num_filhos') else 0,
                
                # Endereço
                endereco=request.form.get('endereco'),
                numero=request.form.get('numero'),
                apto=request.form.get('apto'),
                bairro=request.form.get('bairro'),
                cep=request.form.get('cep'),
                cidade_estado=request.form.get('cidade_estado'),
                fone=request.form.get('fone'),
                
                # ECC Etapas
                ecc_etapa1_num=request.form.get('ecc_etapa1_num'),
                ecc_etapa1_data=parse_date(request.form.get('ecc_etapa1_data')),
                ecc_etapa1_local=request.form.get('ecc_etapa1_local'),
                ecc_etapa1_atividades=request.form.get('ecc_etapa1_atividades'),
                
                ecc_etapa2_num=request.form.get('ecc_etapa2_num'),
                ecc_etapa2_data=parse_date(request.form.get('ecc_etapa2_data')),
                ecc_etapa2_local=request.form.get('ecc_etapa2_local'),
                ecc_etapa2_atividades=request.form.get('ecc_etapa2_atividades'),
                
                ecc_etapa3_num=request.form.get('ecc_etapa3_num'),
                ecc_etapa3_data=parse_date(request.form.get('ecc_etapa3_data')),
                ecc_etapa3_local=request.form.get('ecc_etapa3_local'),
                ecc_etapa3_atividades=request.form.get('ecc_etapa3_atividades'),
                
                engajamento_paroquial=request.form.get('engajamento_paroquial'),
                habilidades=request.form.get('habilidades')
            )
            
            db.session.add(casal)
            db.session.commit()
            flash('✅ Casal cadastrado com sucesso!', 'success')
            return redirect(url_for('lista_casais'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Erro ao cadastrar casal: {str(e)}', 'danger')
    
    return render_template_string(CADASTRO_CASAL_HTML)

@app.route('/lista-casais')
def lista_casais():
    casais = Casal.query.order_by(Casal.data_cadastro.desc()).all()
    return render_template_string(LISTA_CASAIS_HTML, casais=casais)

@app.route('/casal/<int:id>')
def ver_casal(id):
    casal = Casal.query.get_or_404(id)
    return render_template_string(VER_CASAL_HTML, casal=casal)

# ==================== NOVAS ROTAS PARA EDIÇÃO E EXCLUSÃO ====================

@app.route('/editar-casal/<int:id>', methods=['GET', 'POST'])
def editar_casal(id):
    casal = Casal.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Validar e processar datas de nascimento
            nascimento_ele = validate_birth_date(request.form.get('nascimento_ele'))
            nascimento_ela = validate_birth_date(request.form.get('nascimento_ela'))
            
            if not nascimento_ele or not nascimento_ela:
                flash('❌ Por favor, insira datas de nascimento válidas no formato DD/MM', 'danger')
                return render_template_string(EDITAR_CASAL_HTML, casal=casal)
            
            # Atualizar dados do casal
            casal.arquidiocese = request.form.get('arquidiocese')
            casal.cidade = request.form.get('cidade')
            casal.paroquia = request.form.get('paroquia')
            
            # Dados do marido
            casal.nome_ele = request.form.get('nome_ele')
            casal.nascimento_ele = nascimento_ele
            casal.profissao_ele = request.form.get('profissao_ele')
            casal.nome_usual_ele = request.form.get('nome_usual_ele')
            casal.fone_prof_ele = request.form.get('fone_prof_ele')
            
            # Dados da esposa
            casal.nome_ela = request.form.get('nome_ela')
            casal.nascimento_ela = nascimento_ela
            casal.profissao_ela = request.form.get('profissao_ela')
            casal.nome_usual_ela = request.form.get('nome_usual_ela')
            casal.fone_prof_ela = request.form.get('fone_prof_ela')
            
            # Dados do casal
            casal.casamento_religioso = True if request.form.get('casamento_religioso') == 'sim' else False
            casal.data_casamento = parse_date(request.form.get('data_casamento'))
            casal.data_casamento_civil = parse_date(request.form.get('data_casamento_civil'))
            casal.num_filhos = int(request.form.get('num_filhos')) if request.form.get('num_filhos') else 0
            
            # Endereço
            casal.endereco = request.form.get('endereco')
            casal.numero = request.form.get('numero')
            casal.apto = request.form.get('apto')
            casal.bairro = request.form.get('bairro')
            casal.cep = request.form.get('cep')
            casal.cidade_estado = request.form.get('cidade_estado')
            casal.fone = request.form.get('fone')
            
            # ECC Etapas
            casal.ecc_etapa1_num = request.form.get('ecc_etapa1_num')
            casal.ecc_etapa1_data = parse_date(request.form.get('ecc_etapa1_data'))
            casal.ecc_etapa1_local = request.form.get('ecc_etapa1_local')
            casal.ecc_etapa1_atividades = request.form.get('ecc_etapa1_atividades')
            
            casal.ecc_etapa2_num = request.form.get('ecc_etapa2_num')
            casal.ecc_etapa2_data = parse_date(request.form.get('ecc_etapa2_data'))
            casal.ecc_etapa2_local = request.form.get('ecc_etapa2_local')
            casal.ecc_etapa2_atividades = request.form.get('ecc_etapa2_atividades')
            
            casal.ecc_etapa3_num = request.form.get('ecc_etapa3_num')
            casal.ecc_etapa3_data = parse_date(request.form.get('ecc_etapa3_data'))
            casal.ecc_etapa3_local = request.form.get('ecc_etapa3_local')
            casal.ecc_etapa3_atividades = request.form.get('ecc_etapa3_atividades')
            
            # Outros
            casal.engajamento_paroquial = request.form.get('engajamento_paroquial')
            casal.habilidades = request.form.get('habilidades')
            
            db.session.commit()
            flash('✅ Casal atualizado com sucesso!', 'success')
            return redirect(url_for('lista_casais'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Erro ao atualizar casal: {str(e)}', 'danger')
    
    return render_template_string(EDITAR_CASAL_HTML, casal=casal)

@app.route('/excluir-casal/<int:id>', methods=['POST'])
def excluir_casal(id):
    try:
        casal = Casal.query.get_or_404(id)
        db.session.delete(casal)
        db.session.commit()
        flash('✅ Casal excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Erro ao excluir casal: {str(e)}', 'danger')
    
    return redirect(url_for('lista_casais'))

# ==================== ROTAS EXISTENTES ====================

@app.route('/atividades', methods=['GET', 'POST'])
def atividades():
    if request.method == 'POST':
        try:
            atividade = Atividade(
                nome_equipe=request.form.get('nome_equipe'),
                ecc_numero=request.form.get('ecc_numero'),
                coord_geral=request.form.get('coord_geral'),
                sala=request.form.get('sala'),
                liturgia_vigilia=request.form.get('liturgia_vigilia'),
                circulos=request.form.get('circulos'),
                cafe_minimercado=request.form.get('cafe_minimercado'),
                cozinha=request.form.get('cozinha'),
                ordem_limpeza=request.form.get('ordem_limpeza'),
                visitacao=request.form.get('visitacao'),
                acolhida=request.form.get('acolhida'),
                secretaria=request.form.get('secretaria'),
                compras=request.form.get('compras'),
                palestras=request.form.get('palestras'),
                opcoes_trabalho=request.form.get('opcoes_trabalho')
            )
            
            db.session.add(atividade)
            db.session.commit()
            flash('✅ Atividade registrada com sucesso!', 'success')
            return redirect(url_for('equipes'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Erro ao registrar atividade: {str(e)}', 'danger')
    
    return render_template_string(ATIVIDADES_HTML)

@app.route('/equipes')
def equipes():
    atividades = Atividade.query.order_by(Atividade.data_criacao.desc()).all()
    return render_template_string(EQUIPES_HTML, atividades=atividades)

@app.route('/exportar-casais')
def exportar_casais():
    casais = Casal.query.all()
    dados = []
    for casal in casais:
        dados.append({
            'id': casal.id,
            'casal': f"{casal.nome_ele} e {casal.nome_ela}",
            'paroquia': casal.paroquia,
            'cidade': casal.cidade,
            'telefone': casal.fone,
            'data_cadastro': casal.data_cadastro.strftime('%d/%m/%Y')
        })
    return json.dumps(dados, ensure_ascii=False, indent=2)

# ==================== INICIALIZAÇÃO ====================
def criar_banco_dados():
    """Cria o banco de dados e algumas entradas de exemplo"""
    with app.app_context():
        db.create_all()
        
        # Adicionar dados de exemplo se o banco estiver vazio
        if Casal.query.count() == 0:
            exemplo_casal = Casal(
                arquidiocese="São Paulo",
                cidade="São Paulo",
                paroquia="Nossa Senhora do Rosário",
                nome_ele="João Silva",
                nascimento_ele="15/05",
                profissao_ele="Engenheiro",
                nome_usual_ele="João",
                nome_ela="Maria Silva",
                nascimento_ela="22/08",
                profissao_ela="Professora",
                nome_usual_ela="Maria",
                casamento_religioso=True,
                data_casamento=datetime(2015, 6, 20).date(),
                num_filhos=2,
                endereco="Rua das Flores",
                numero="123",
                bairro="Centro",
                cep="01234-567",
                cidade_estado="Floriano - PI",
                fone="(89) 99999-9999",
                engajamento_paroquial="Participa do coral e da catequese",
                habilidades="João: carpintaria, Maria: culinária"
            )
            db.session.add(exemplo_casal)
            
        if Atividade.query.count() == 0:
            exemplo_atividade = Atividade(
                nome_equipe="Equipe de Acolhida",
                ecc_numero="XXII",
                coord_geral="Carlos Mendes",
                acolhida="Ana Paula e Roberto",
                secretaria="Tereza Costa",
                opcoes_trabalho="João Silva|A, Maria Santos|IC, Pedro Costa|C, Ana Souza|N"
            )
            db.session.add(exemplo_atividade)
            
        db.session.commit()
        print("✅ Banco de dados criado com sucesso!")

# ==================== EXECUÇÃO PRINCIPAL ====================
if __name__ == '__main__':
    # Criar diretório de uploads
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Criar banco de dados
    criar_banco_dados()
    
    # Executar aplicação
    print("=" * 60)
    print("🚀 Sistema ECC - Encontro de Casais com Cristo")
    print("=" * 60)
    print("📊 Acesse o sistema em: http://localhost:5000")
    print("📋 Cadastro de Casais: http://localhost:5000/cadastro-casal")
    print("👥 Lista de Casais: http://localhost:5000/lista-casais")
    print("⚙️ Atividades: http://localhost:5000/atividades")
    print("👷 Equipes: http://localhost:5000/equipes")
    print("=" * 60)
    print("📅 Datas de nascimento: Formato DD/MM (apenas dia e mês)")
    print("📅 Outras datas: Formato DD/MM")
    print("💰 Campo 'Rendimento' foi REMOVIDO do sistema")
    print("🔄 Novas funcionalidades: Editar e Excluir casais")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

    # ==================== CONFIGURAÇÕES PARA RENDER ====================
if __name__ == '__main__':
    # No Render, use a porta fornecida pelo ambiente
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)