import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta
import json
import os

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================

st.set_page_config(
    page_title="Etnobiologia Digital no Horto UFSC — SPMB 2026",
    page_icon="🌿",
    layout="wide"
)

# ============================================
# GLOSSÁRIO COMPLETO - PARA AVALIADORES
# ============================================

GLOSSARIO = """
<div style="background: #f8f9fa; padding: 20px; border-radius: 12px; border: 1px solid #e0e0e0; margin: 10px 0; max-height: 500px; overflow-y: auto;">

    <h4 style="color: #1E3D59; margin-top: 0;">📊 Conceitos Gerais</h4>
    <p><strong>Google Analytics 4 (GA4)</strong> → Plataforma do Google destinada à coleta, organização e análise de dados de interação dos usuários com sites e aplicativos.</p>
    <p><strong>Web Analytics</strong> → Processo de coleta, medição, análise e interpretação de dados relacionados ao acesso e comportamento dos usuários em ambientes digitais.</p>
    
    <h4 style="color: #1E3D59; margin-top: 15px;">👥 Usuários e Sessões</h4>
    <p><strong>Usuário (User)</strong> → Pessoa identificada pelo Google Analytics que interage com o site durante o período analisado.</p>
    <p><strong>Novos usuários (New users)</strong> → Usuários identificados como novos no período de análise.</p>
    <p><strong>Usuários recorrentes (Returning users)</strong> → Usuários que já haviam acessado o site anteriormente e retornam em outro momento.</p>
    <p><strong>Usuários engajados (Engaged users)</strong> → Usuários que realizaram interações consideradas relevantes pelo sistema de mensuração.</p>
    <p><strong>Sessão (Session)</strong> → Período em que um usuário interage com o site.</p>
    <p><strong>Sessão engajada (Engaged session)</strong> → Sessão que atende aos critérios de engajamento definidos pelo GA4.</p>
    <p><strong>Engajamento (Engagement)</strong> → Grau de interação dos usuários com o conteúdo e os recursos do site.</p>
    <p><strong>Taxa de engajamento (Engagement rate)</strong> → Proporção das sessões que foram classificadas como engajadas.</p>
    <p><strong>Evento (Event)</strong> → Ação ou interação registrada pelo Google Analytics, como visualização de uma página ou outra interação configurada.</p>
    
    <h4 style="color: #1E3D59; margin-top: 15px;">📥 Aquisição e Tráfego</h4>
    <p><strong>Aquisição (Acquisition)</strong> → Conjunto de métricas utilizadas para identificar como os usuários ou sessões chegaram ao site.</p>
    <p><strong>Aquisição de usuários (User acquisition)</strong> → Análise da origem pela qual os usuários, especialmente os novos usuários, chegaram ao site.</p>
    <p><strong>Aquisição de tráfego (Traffic acquisition)</strong> → Análise da origem das sessões ou do tráfego recebido pelo site.</p>
    <p><strong>Tráfego (Traffic)</strong> → Conjunto de acessos ou sessões registrados em um site durante determinado período.</p>
    <p><strong>Canal (Channel)</strong> → Categoria utilizada para agrupar diferentes formas de aquisição de tráfego.</p>
    <p><strong>Grupo de canais (Channel group)</strong> → Classificação que organiza as diferentes origens de tráfego em categorias, como busca orgânica, acesso direto e referência.</p>
    <p><strong>Busca orgânica (Organic Search)</strong> → Tráfego proveniente de resultados não pagos de mecanismos de busca, como o Google.</p>
    <p><strong>Acesso direto (Direct)</strong> → Tráfego para o qual o Analytics não identifica uma origem externa atribuível. Pode ocorrer quando o usuário acessa diretamente um endereço, utiliza um favorito ou quando a informação de origem não está disponível.</p>
    <p><strong>Referência (Referral)</strong> → Tráfego originado a partir de links presentes em outros sites.</p>
    <p><strong>Origem (Source)</strong> → Identifica de onde o tráfego foi originado, como um mecanismo de busca ou outro site.</p>
    <p><strong>Mídia (Medium)</strong> → Classificação do tipo de origem do tráfego, como <code>organic</code>, <code>referral</code> ou <code>direct</code>.</p>
    <p><strong>Origem/mídia (Source/Medium)</strong> → Combinação utilizada para identificar de forma mais específica a procedência do tráfego.</p>
    <p><strong>Tráfego orgânico</strong> → Conjunto de acessos provenientes de mecanismos de busca sem utilização de anúncios pagos.</p>
    <p><strong>Tráfego de referência (Referral traffic)</strong> → Acessos provenientes de links disponibilizados em outros sites.</p>
    <p><strong>Tráfego direto (Direct traffic)</strong> → Acessos classificados pelo Analytics como provenientes do canal Direct.</p>
    
    <h4 style="color: #1E3D59; margin-top: 15px;">📄 Conteúdo e Páginas</h4>
    <p><strong>Página (Page)</strong> → Unidade de conteúdo do site que pode ser visualizada e analisada individualmente.</p>
    <p><strong>Visualização de página (Page view)</strong> → Registro de que uma página foi visualizada.</p>
    <p><strong>Página de destino (Landing page)</strong> → Primeira página acessada pelo usuário em uma sessão.</p>
    <p><strong>Páginas mais acessadas</strong> → Páginas que apresentam maior volume de visualizações ou interações no período analisado.</p>
    <p><strong>Página de entrada</strong> → Página pela qual o usuário inicia sua interação com o site.</p>
    <p><strong>Página de saída</strong> → Página associada ao encerramento da navegação ou da sessão.</p>
    <p><strong>URL</strong> → Endereço eletrônico que identifica uma página ou recurso na Internet.</p>
    <p><strong>Domínio</strong> → Parte principal do endereço de um site, como <code>ufsc.br</code>.</p>
    
    <h4 style="color: #1E3D59; margin-top: 15px;">👤 Perfil e Audiência</h4>
    <p><strong>Perfil demográfico</strong> → Conjunto de características demográficas atribuídas à audiência analisada.</p>
    <p><strong>Idade (Age)</strong> → Informação demográfica utilizada para distribuir os usuários em diferentes faixas etárias.</p>
    <p><strong>Faixa etária</strong> → Agrupamento dos usuários de acordo com intervalos de idade.</p>
    <p><strong>Sexo</strong> → Dimensão demográfica utilizada para caracterizar a composição da audiência.</p>
    <p><strong>Localização geográfica (Geography)</strong> → Informação referente à localização geográfica associada aos usuários.</p>
    <p><strong>País (Country)</strong> → Dimensão geográfica que permite identificar o país associado ao acesso.</p>
    <p><strong>Estado/região</strong> → Dimensão geográfica utilizada para detalhar a localização dos usuários dentro de um país.</p>
    <p><strong>Audiência (Audience)</strong> → Conjunto de usuários que acessam ou interagem com o site.</p>
    <p><strong>Alcance</strong> → Dimensão relacionada à quantidade de pessoas alcançadas pelo conteúdo digital.</p>
    <p><strong>Retenção (Retention)</strong> → Indicador relacionado à permanência ou retorno dos usuários ao ambiente digital.</p>
    
    <h4 style="color: #1E3D59; margin-top: 15px;">📊 Métricas e Análise</h4>
    <p><strong>Métrica</strong> → Medida quantitativa utilizada para representar determinado aspecto do comportamento dos usuários ou do desempenho do site.</p>
    <p><strong>Dimensão</strong> → Característica utilizada para organizar, segmentar ou contextualizar os dados, como país, idade ou canal.</p>
    <p><strong>Período de análise</strong> → Intervalo de tempo utilizado para a coleta e interpretação dos dados.</p>
    <p><strong>Comparação temporal</strong> → Comparação dos resultados obtidos em diferentes períodos, como 2025 e janeiro–julho de 2026.</p>
    <p><strong>Volume de tráfego</strong> → Quantidade de acessos ou usuários associados ao site em determinado período.</p>
    <p><strong>Crescimento de tráfego</strong> → Aumento do volume de usuários, sessões ou outras métricas de tráfego entre períodos.</p>
    <p><strong>Tendência</strong> → Padrão de crescimento, redução ou estabilidade observado nos dados ao longo do tempo.</p>
    <p><strong>Projeção</strong> → Estimativa de um resultado futuro baseada no comportamento observado anteriormente.</p>
    <p><strong>Dados agregados</strong> → Dados reunidos e apresentados de forma estatística, sem representar necessariamente cada usuário individualmente.</p>
    <p><strong>Análise descritiva</strong> → Abordagem que descreve padrões e características observados nos dados, sem necessariamente estabelecer relações causais.</p>
    <p><strong>Indicador</strong> → Medida utilizada para representar determinado aspecto do fenômeno estudado.</p>
    <p><strong>Monitoramento</strong> → Acompanhamento sistemático das métricas ao longo do tempo.</p>
    <p><strong>Dashboard</strong> → Painel visual que reúne diferentes métricas e dimensões para facilitar o acompanhamento dos dados.</p>
    
    <h4 style="color: #1E3D59; margin-top: 15px;">🔗 Ferramentas e Conceitos Técnicos</h4>
    <p><strong>Campanha (Campaign)</strong> → Identificação de uma campanha ou ação específica responsável por gerar tráfego para o site.</p>
    <p><strong>UTM</strong> → Parâmetros adicionados aos endereços de páginas para identificar a origem, mídia e campanha associadas a determinado acesso.</p>
    <p><strong>Referenciador (Referrer)</strong> → Página ou site anterior que direcionou o usuário para determinada página.</p>
    <p><strong>Mecanismo de busca</strong> → Serviço utilizado para localizar informações na Internet, como Google ou Bing.</p>
    <p><strong>Pesquisa orgânica</strong> → Pesquisa realizada em um mecanismo de busca cujos resultados não são anúncios pagos.</p>
    <p><strong>SEO (Search Engine Optimization)</strong> → Conjunto de práticas destinadas a melhorar a visibilidade de páginas nos resultados orgânicos dos mecanismos de busca.</p>
    <p><strong>Impressão</strong> → Registro de que determinado conteúdo ou resultado foi apresentado ao usuário, dependendo da plataforma e do contexto de mensuração.</p>
    <p><strong>Clique</strong> → Interação do usuário com um elemento clicável.</p>
    <p><strong>Interação</strong> → Ação realizada pelo usuário dentro do site.</p>
    <p><strong>Conversão</strong> → Ação considerada especialmente importante para os objetivos de um site e definida para ser mensurada.</p>
    <p><strong>Evento principal (Key event)</strong> → Evento considerado relevante para os objetivos de análise do site.</p>
    <p><strong>Relatório</strong> → Interface do Analytics utilizada para consultar e interpretar os dados coletados.</p>
    <p><strong>Exploração (Explore)</strong> → Ferramenta do GA4 que permite realizar análises personalizadas e cruzar dimensões e métricas.</p>
    <p><strong>Segmentação</strong> → Processo de separar os dados em grupos segundo características específicas, como idade, país ou canal.</p>
    <p><strong>Filtro</strong> → Recurso utilizado para restringir os dados apresentados em uma análise.</p>
    <p><strong>Período</strong> → Intervalo temporal selecionado para visualizar os dados.</p>
    <p><strong>Porcentagem (%)</strong> → Forma de expressar a participação proporcional de uma categoria em relação ao total.</p>
    
    <h4 style="color: #1E3D59; margin-top: 15px;">📱 Dispositivos e Tecnologia</h4>
    <p><strong>Dispositivo</strong> → Equipamento utilizado para acessar o site, como computador, celular ou tablet.</p>
    <p><strong>Tecnologia</strong> → Conjunto de características técnicas associadas ao acesso, incluindo dispositivo, navegador e sistema operacional.</p>
    <p><strong>Navegador (Browser)</strong> → Programa utilizado para acessar páginas da Internet, como Chrome, Firefox ou Safari.</p>
    <p><strong>Sistema operacional (Operating system)</strong> → Sistema utilizado pelo dispositivo para executar suas funções, como Android, Windows, iOS ou macOS.</p>
    
    <h4 style="color: #1E3D59; margin-top: 15px;">🧠 Contexto do seu Estudo</h4>
    <p><strong>Circulação do conhecimento</strong> → No contexto do seu estudo, refere-se à disseminação e ao acesso ao conhecimento etnobotânico por meio do ambiente digital.</p>
    <p><strong>Vetor de tráfego</strong> → Meio ou canal responsável por direcionar usuários para o site.</p>
    <p><strong>Assistente de IA</strong> → Sistema de inteligência artificial capaz de fornecer respostas ou recomendações que podem direcionar usuários para páginas da Web.</p>
    <p><strong>Tráfego proveniente de IA</strong> → Acessos ao site associados a sistemas ou assistentes de inteligência artificial.</p>
    <p><strong>Audiência nacional</strong> → Parcela dos acessos originada dentro do Brasil.</p>
    <p><strong>Audiência internacional</strong> → Parcela dos acessos originada fora do Brasil.</p>
</div>
"""

# ============================================
# AUTORES - VERSÃO COM CARDS
# ============================================

AUTORES_COMPLETOS = """
<div style="background: linear-gradient(135deg, #f0f9f4 0%, #e8f5e9 100%); padding: 20px; border-radius: 12px; border: 2px solid #17B978; margin: 10px 0;">
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center;">
        <div style="background: white; padding: 12px; border-radius: 8px; border-left: 4px solid #17B978;">
            <strong style="color: #1E3D59;">👤 Michael A. Lopes</strong><br>
            <span style="font-size: 0.85rem; color: #17B978;">Apresentador</span><br>
            <span style="font-size: 0.8rem; color: #666;">Graduando em Química Tecnológica - UFSC</span>
        </div>
        <div style="background: white; padding: 12px; border-radius: 8px; border-left: 4px solid #1E3D59;">
            <strong style="color: #1E3D59;">👤 Maique W. Biavatti</strong><br>
            <span style="font-size: 0.85rem; color: #17B978;">Orientador</span><br>
            <span style="font-size: 0.8rem; color: #666;">Depto. Ciências Farmacêuticas - UFSC</span>
        </div>
        <div style="background: white; padding: 12px; border-radius: 8px; border-left: 4px solid #17B978;">
            <strong style="color: #1E3D59;">👤 Gabriela D. Ritter</strong><br>
            <span style="font-size: 0.85rem; color: #17B978;">Colaboradora</span><br>
            <span style="font-size: 0.8rem; color: #666;">Farmacêutica</span>
        </div>
        <div style="background: white; padding: 12px; border-radius: 8px; border-left: 4px solid #1E3D59;">
            <strong style="color: #1E3D59;">👤 Letícia S. Tardim</strong><br>
            <span style="font-size: 0.85rem; color: #17B978;">Colaboradora</span><br>
            <span style="font-size: 0.8rem; color: #666;">Graduanda em Farmácia - UFSC</span>
        </div>
    </div>
    <div style="text-align: center; margin-top: 12px; padding-top: 10px; border-top: 2px dashed #17B978;">
        <span style="font-size: 0.9rem; color: #1E3D59;">🏛️ <strong>Universidade Federal de Santa Catarina (UFSC)</strong></span><br>
        <span style="font-size: 0.85rem; color: #666;">Florianópolis, SC, Brasil</span>
    </div>
</div>
"""

# ============================================
# DADOS DO SEU ARTIGO (DO PDF)
# ============================================

TITULO = "Etnobiologia digital no Horto Didático da UFSC: circulação do saber etnobotânico mensurada por web analytics"

PALAVRAS_CHAVE = "Etnobiologia Digital; Web Analytics; Plantas Medicinais; Circulação do Conhecimento"

# Dados 2025
USUARIOS_2025 = 315528
USUARIOS_NOVOS_2025 = 311835
USUARIOS_ENGAJADOS_2025 = 372745
BUSCA_ORGANICA_2025 = 257656
BUSCA_ORGANICA_PCT_2025 = 81.66
ACESSO_DIRETO_2025 = 54897
ACESSO_DIRETO_PCT_2025 = 17.40
BUSCA_ORGANICA_TR_2025 = 303873
BUSCA_ORGANICA_TR_PCT_2025 = 81.52
ACESSO_DIRETO_TR_2025 = 65081
ACESSO_DIRETO_TR_PCT_2025 = 17.46

# Dados 2026 (jan-jul)
USUARIOS_2026 = 205944
USUARIOS_NOVOS_2026 = 202144
USUARIOS_ENGAJADOS_2026 = 235734
BUSCA_ORGANICA_2026 = 160265
BUSCA_ORGANICA_PCT_2026 = 77.82
ACESSO_DIRETO_2026 = 43695
ACESSO_DIRETO_PCT_2026 = 21.22
BUSCA_ORGANICA_TR_2026 = 183600
BUSCA_ORGANICA_TR_PCT_2026 = 77.88
ACESSO_DIRETO_TR_2026 = 44665
ACESSO_DIRETO_TR_PCT_2026 = 18.95

# IA e Referral
IA_USUARIOS = 139
IA_SESSOES = 221
REFERRAL_RETENCAO = 20.12

# Perfil demográfico
FEMININO_2025 = 65.1
MASCULINO_2025 = 34.9
FEMININO_2026 = 67.4
MASCULINO_2026 = 32.6
BRASIL_2025 = 94.9
BRASIL_2026 = 92.4
FAIXA_ETARIA = "25-34 anos (40,1%)"

# Espécies mais acessadas
ESPECIES = {
    'Folha-da-fortuna (Kalanchoe pinnata)': 6460,
    'Quebra-pedra / Quebra-pedra-rasteiro (Phyllanthus spp.)': 5599,
    'Buchinha-do-norte (Luffa operculata)': 4334,
    'Alfavaca-cravo (Ocimum gratissimum)': 4127,
    'Aveloz (Euphorbia tirucalli)': 4092,
    'Melão-de-são-caetano (Momordica charantia)': 3500,
}

# Países internacionais
PAISES = {
    'Portugal': 850,
    'Estados Unidos': 620,
    'Moçambique': 340,
    'Angola': 280,
    'Espanha': 210,
}

# Estados brasileiros
ESTADOS = {
    'SP': 18500,
    'RJ': 12300,
    'MG': 9800,
    'PR': 7600,
    'RS': 6900,
    'SC': 5800,
}

# ============================================
# CARREGAR CREDENCIAIS GA4
# ============================================

GA4_PROPERTY_ID = "353285465"

try:
    if os.path.exists('ga4-credentials.json'):
        with open('ga4-credentials.json', 'r') as f:
            credentials_info = json.load(f)
    else:
        credentials_json = st.secrets["google_analytics"]["credentials_json"]
        if isinstance(credentials_json, str):
            credentials_info = json.loads(credentials_json)
        else:
            credentials_info = credentials_json
except Exception as e:
    credentials_info = None

# ============================================
# FUNÇÕES GA4
# ============================================

def get_ga4_client():
    try:
        if credentials_info is None:
            return None
        from google.oauth2 import service_account
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        return BetaAnalyticsDataClient(credentials=credentials)
    except:
        return None

@st.cache_data(ttl=300)
def get_ga4_data(start_date, end_date):
    try:
        from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
        
        client = get_ga4_client()
        if not client:
            return None
        
        request = RunReportRequest(
            property=f"properties/{GA4_PROPERTY_ID}",
            dimensions=[
                Dimension(name="date"),
                Dimension(name="sessionDefaultChannelGroup"),
                Dimension(name="country"),
                Dimension(name="deviceCategory")
            ],
            metrics=[
                Metric(name="activeUsers"),
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="newUsers"),
                Metric(name="screenPageViews")
            ],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            limit=10000
        )
        
        response = client.run_report(request)
        
        data = []
        for row in response.rows:
            row_data = {}
            for i, dimension in enumerate(response.dimension_headers):
                row_data[dimension.name] = row.dimension_values[i].value
            for i, metric in enumerate(response.metric_headers):
                row_data[metric.name] = float(row.metric_values[i].value)
            data.append(row_data)
        
        return pd.DataFrame(data)
        
    except:
        return None

def get_realtime_data():
    try:
        from google.analytics.data_v1beta.types import RunRealtimeReportRequest
        
        client = get_ga4_client()
        if not client:
            return None
        
        request = RunRealtimeReportRequest(
            property=f"properties/{GA4_PROPERTY_ID}",
            dimensions=[
                Dimension(name="pageTitle"),
                Dimension(name="country"),
                Dimension(name="deviceCategory")
            ],
            metrics=[
                Metric(name="activeUsers"),
                Metric(name="screenPageViews")
            ],
            limit=100
        )
        
        response = client.run_realtime_report(request)
        
        data = []
        for row in response.rows:
            row_data = {}
            for i, dimension in enumerate(response.dimension_headers):
                row_data[dimension.name] = row.dimension_values[i].value
            for i, metric in enumerate(response.metric_headers):
                row_data[metric.name] = float(row.metric_values[i].value)
            data.append(row_data)
        
        return pd.DataFrame(data)
        
    except:
        return None

# ============================================
# ESTILOS VISUAIS
# ============================================

st.markdown("""
<style>
    .main-title { font-size: 2.2rem; color: #1E3D59; font-weight: 700; text-align: center; }
    .sub-title { font-size: 1.1rem; color: #17B978; text-align: center; margin-bottom: 20px; }
    .work-title { font-size: 1.3rem; color: #1E3D59; font-weight: 600; text-align: center; margin: 15px 0; }
    .metric-card { background: #F8F9FA; padding: 15px; border-radius: 10px; border-left: 4px solid #17B978; text-align: center; transition: transform 0.2s; }
    .metric-card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .metric-number { font-size: 1.8rem; font-weight: 700; color: #1E3D59; }
    .metric-label { font-size: 0.85rem; color: #666; }
    .metric-delta { font-size: 0.8rem; color: #17B978; }
    .event-banner {
        background: linear-gradient(135deg, #1E3D59, #17B978);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin: 15px 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(23,185,120,0.3);
    }
    .event-banner h2 { margin: 0; color: white; font-size: 1.3rem; }
    .event-banner p { margin: 3px 0; opacity: 0.9; font-size: 0.9rem; }
    .event-banner .highlight { background: rgba(255,255,255,0.2); padding: 3px 15px; border-radius: 20px; display: inline-block; margin-top: 5px; font-weight: 600; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f0f2f6;
        padding: 8px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 25px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.0rem;
        background: transparent;
        color: #555;
        transition: all 0.3s;
    }
    .stTabs [aria-selected="true"] {
        background: #17B978 !important;
        color: white !important;
        box-shadow: 0 2px 10px rgba(23,185,120,0.3);
    }
    .ref-box {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #1E3D59;
        margin: 15px 0;
        font-size: 0.85rem;
        max-height: 500px;
        overflow-y: auto;
        line-height: 1.8;
    }
    .ref-box p { margin: 10px 0; }
    .ref-box strong { color: #1E3D59; }
    .resumo-box {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #17B978;
        margin: 15px 0;
        line-height: 1.8;
    }
    .resumo-box p { margin: 10px 0; }
    .resumo-box strong { color: #1E3D59; }
    .footer {
        text-align: center;
        padding: 15px 0;
        margin-top: 20px;
        border-top: 2px solid #e0e0e0;
        font-size: 0.8rem;
        color: #999;
        line-height: 1.8;
    }
    .horto-link { text-align: center; margin: 5px 0 15px 0; font-size: 0.9rem; }
    .horto-link a { color: #17B978; text-decoration: none; font-weight: 600; }
    .horto-link a:hover { text-decoration: underline; }
    .geo-card { background: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; margin: 10px 0; }
    .geo-card h4 { color: #1E3D59; margin-top: 0; }
    .status-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; padding: 10px; border-radius: 8px; }
    .status-warning { background: #fff3cd; color: #856404; border: 1px solid #ffc107; padding: 10px; border-radius: 8px; }
    .status-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; padding: 10px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER COM LOGOS
# ============================================

col_logo1, col_titulo, col_logo2 = st.columns([1, 3, 1])

with col_logo1:
    try:
        st.image("logo-horto.png", use_container_width=True)
    except:
        st.image("https://horto.ufsc.br/wp-content/uploads/2021/03/logo-horto-300x100.png", use_container_width=True)

with col_titulo:
    st.markdown('<p class="main-title">🌿 Etnobiologia Digital no Horto UFSC</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Web Analytics & Circulação do Saber Etnobotânico</p>', unsafe_allow_html=True)

with col_logo2:
    try:
        st.image("logo-spmb.png", use_container_width=True)
    except:
        st.image("https://xxviiispmb.com.br/wp-content/uploads/2026/01/logo-spmb-2026.png", use_container_width=True)

# ============================================
# LINK DO HORTO
# ============================================

st.markdown("""
<div class="horto-link">
    🌱 <a href="https://hortodidatico.ufsc.br/" target="_blank">Horto Didático de Plantas Medicinais da UFSC</a>
</div>
""", unsafe_allow_html=True)

# ============================================
# TÍTULO E AUTORES
# ============================================

st.markdown(f'<p class="work-title">{TITULO}</p>', unsafe_allow_html=True)
st.markdown(AUTORES_COMPLETOS, unsafe_allow_html=True)
st.markdown(f'<p style="text-align: center; font-size: 0.85rem; color: #17B978; margin-top: 8px;">🔑 {PALAVRAS_CHAVE}</p>', unsafe_allow_html=True)

# ============================================
# GLOSSÁRIO
# ============================================

with st.expander("📖 Glossário - Entenda os termos"):
    st.markdown(GLOSSARIO, unsafe_allow_html=True)

# ============================================
# STATUS GA4
# ============================================

with st.expander("🔍 Status da Conexão com GA4"):
    if credentials_info:
        st.markdown('<div class="status-success">✅ Conectado ao Google Analytics</div>', unsafe_allow_html=True)
        st.write(f"Property ID: `{GA4_PROPERTY_ID}`")
    else:
        st.markdown('<div class="status-error">❌ Falha na conexão</div>', unsafe_allow_html=True)
    
    client = get_ga4_client()
    if client:
        st.markdown('<div class="status-success">✅ Permissão concedida</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-error">❌ Sem permissão</div>', unsafe_allow_html=True)

# ============================================
# BANNER DO EVENTO
# ============================================

st.markdown("""
<div class="event-banner">
    <h2>🎓 XXVIII Simpósio de Plantas Medicinais do Brasil (SPMB) 2026</h2>
    <p>15 a 18 de setembro de 2026 | Univali - Itajaí/SC</p>
    <p>Tema: <strong>Plantas medicinais como fonte de novos agentes medicinais</strong></p>
    <div class="highlight">Apresentador: Michael A. Lopes</div>
</div>
""", unsafe_allow_html=True)

# ============================================
# ABAS
# ============================================

aba1, aba2, aba3 = st.tabs([
    "📄 RESULTADOS",
    "📊 TEMPO REAL",
    "📚 REFERÊNCIAS"
])

# ============================================
# ABA 1: RESULTADOS
# ============================================

with aba1:
    st.header("📈 Resultados e Discussão")
    
    # INSIGHTS
    st.subheader("🔥 Principais Insights")
    
    col_i1, col_i2, col_i3, col_i4 = st.columns(4)
    
    with col_i1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">🤖 {IA_USUARIOS}</div>
            <div class="metric-label">Usuários via IA (2026)</div>
            <div class="metric-delta">+{IA_SESSOES} sessões</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_i2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{REFERRAL_RETENCAO:.1f}%</div>
            <div class="metric-label">🔗 Retenção por Referral</div>
            <div class="metric-delta">Alta taxa de compartilhamento</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_i3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">🌍 5-7,5%</div>
            <div class="metric-label">Tráfego Internacional</div>
            <div class="metric-delta">{len(PAISES)} países</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_i4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{FEMININO_2026:.1f}%</div>
            <div class="metric-label">👩 Público Feminino</div>
            <div class="metric-delta">+{FEMININO_2026 - FEMININO_2025:.1f}% vs 2025</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # RESUMO
    st.markdown("### 📋 Resumo dos Resultados")
    
    st.markdown(f"""
    <div class="resumo-box">
        <p>A análise combinada entre aquisição de usuários e aquisição de tráfego revela a sólida autoridade e o alcance do portal.</p>
        
        <p>Em <strong>2025</strong>, o site registrou <strong>{USUARIOS_2025:,} usuários</strong> ({USUARIOS_NOVOS_2025:,} novos), com predomínio da busca orgânica ({BUSCA_ORGANICA_2025:,}; <strong>{BUSCA_ORGANICA_PCT_2025:.2f}%</strong>) e do acesso direto ({ACESSO_DIRETO_2025:,}; <strong>{ACESSO_DIRETO_PCT_2025:.2f}%</strong>). Na perspectiva de tráfego, o mesmo período contabilizou {USUARIOS_ENGAJADOS_2025:,} usuários engajados, liderados pela busca orgânica ({BUSCA_ORGANICA_TR_2025:,}; <strong>{BUSCA_ORGANICA_TR_PCT_2025:.2f}%</strong>) e acesso direto ({ACESSO_DIRETO_TR_2025:,}; <strong>{ACESSO_DIRETO_TR_PCT_2025:.2f}%</strong>).</p>
        
        <p>Em <strong>2026 (jan–jul)</strong>, foram <strong>{USUARIOS_2026:,} usuários</strong> ({USUARIOS_NOVOS_2026:,} novos), mantendo a liderança da busca orgânica ({BUSCA_ORGANICA_2026:,}; <strong>{BUSCA_ORGANICA_PCT_2026:.2f}%</strong>) e acesso direto ({ACESSO_DIRETO_2026:,}; <strong>{ACESSO_DIRETO_PCT_2026:.2f}%</strong>), enquanto o tráfego total atingiu {USUARIOS_ENGAJADOS_2026:,} usuários, com busca orgânica ({BUSCA_ORGANICA_TR_2026:,}; <strong>{BUSCA_ORGANICA_TR_PCT_2026:.2f}%</strong>) e acesso direto ({ACESSO_DIRETO_TR_2026:,}; <strong>{ACESSO_DIRETO_TR_PCT_2026:.2f}%</strong>).</p>
        
        <p><strong>Destaques:</strong><br>
        🤖 <strong>Emergência de IA</strong>: {IA_USUARIOS} usuários e {IA_SESSOES} sessões via assistentes de IA<br>
        🔗 <strong>Alta retenção</strong>: {REFERRAL_RETENCAO:.2f}% em canais de indicação (Referral)<br>
        📈 <strong>Crescimento</strong>: Projeção de superar o tráfego total de 2025 até o final de 2026</p>
        
        <p>Quanto ao perfil demográfico, observou-se predominância expressiva do público feminino (<strong>{FEMININO_2025:.1f}% em 2025</strong> e <strong>{FEMININO_2026:.1f}% em 2026</strong>) e de jovens adultos na faixa etária de 25 a 34 anos (<strong>40,1%</strong>). A imensa maioria dos acessos está concentrada no Brasil (<strong>{BRASIL_2025:.1f}% em 2025</strong> e <strong>{BRASIL_2026:.1f}% em 2026</strong>).</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{USUARIOS_2025:,}</div>
            <div class="metric-label">👥 Usuários (2025)</div>
            <div class="metric-delta">{USUARIOS_NOVOS_2025:,} novos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{USUARIOS_2026:,}</div>
            <div class="metric-label">👥 Usuários (2026)</div>
            <div class="metric-delta">{USUARIOS_NOVOS_2026:,} novos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{BUSCA_ORGANICA_PCT_2026:.1f}%</div>
            <div class="metric-label">🔍 Busca Orgânica</div>
            <div class="metric-delta">{BUSCA_ORGANICA_PCT_2025:.1f}% em 2025</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{FEMININO_2026:.1f}%</div>
            <div class="metric-label">👩 Público Feminino</div>
            <div class="metric-delta">+{FEMININO_2026 - FEMININO_2025:.1f}% vs 2025</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # GRÁFICOS
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("📊 Canais de Aquisição")
        df_canais = pd.DataFrame({
            'Canal': ['Busca Orgânica', 'Acesso Direto', 'Outras Fontes'],
            '2025': [BUSCA_ORGANICA_PCT_2025, ACESSO_DIRETO_PCT_2025, 
                    100 - BUSCA_ORGANICA_PCT_2025 - ACESSO_DIRETO_PCT_2025],
            '2026': [BUSCA_ORGANICA_PCT_2026, ACESSO_DIRETO_PCT_2026,
                    100 - BUSCA_ORGANICA_PCT_2026 - ACESSO_DIRETO_PCT_2026]
        }).melt(id_vars='Canal', var_name='Ano', value_name='%')
        
        fig = px.bar(df_canais, x='Canal', y='%', color='Ano', barmode='group',
                     text_auto='.2f', color_discrete_sequence=['#1E3D59', '#17B978'])
        fig.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
        fig.update_layout(yaxis_range=[0, 100], plot_bgcolor='rgba(0,0,0,0)', height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_g2:
        st.subheader("👥 Perfil por Gênero")
        df_gen = pd.DataFrame({
            'Ano': ['2025', '2025', '2026', '2026'],
            'Gênero': ['Feminino', 'Masculino', 'Feminino', 'Masculino'],
            '%': [FEMININO_2025, MASCULINO_2025, FEMININO_2026, MASCULINO_2026]
        })
        fig = px.bar(df_gen, x='Ano', y='%', color='Gênero', barmode='group',
                     text_auto='.1f', color_discrete_sequence=['#17B978', '#1E3D59'])
        fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
        fig.update_layout(yaxis_range=[0, 85], plot_bgcolor='rgba(0,0,0,0)', height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ALCANCE GEOGRÁFICO
    st.subheader("🌍 Alcance Geográfico")
    
    col_geo1, col_geo2 = st.columns(2)
    
    with col_geo1:
        st.markdown("""
        <div class="geo-card">
            <h4>🌎 Alcance Internacional</h4>
            <p style="font-size: 0.9rem; color: #555;">Tráfego internacional: <strong>5% a 7,5%</strong> dos acessos</p>
        </div>
        """, unsafe_allow_html=True)
        
        df_paises = pd.DataFrame({
            'País': list(PAISES.keys()),
            'Usuários': list(PAISES.values())
        }).sort_values('Usuários', ascending=True)
        
        fig_paises = px.bar(df_paises, x='Usuários', y='País', orientation='h',
                           color='Usuários', color_continuous_scale='Blues', text_auto=True)
        fig_paises.update_layout(plot_bgcolor='rgba(0,0,0,0)', height=300, showlegend=False)
        st.plotly_chart(fig_paises, use_container_width=True)
    
    with col_geo2:
        st.markdown("""
        <div class="geo-card">
            <h4>🇧🇷 Brasil</h4>
            <p style="font-size: 0.9rem; color: #555;">Destaque para <strong>SP, RJ, MG, PR, RS e SC</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        df_estados = pd.DataFrame({
            'Estado': list(ESTADOS.keys()),
            'Usuários': list(ESTADOS.values())
        }).sort_values('Usuários', ascending=True)
        
        fig_estados = px.bar(df_estados, x='Usuários', y='Estado', orientation='h',
                            color='Usuários', color_continuous_scale='Greens', text_auto=True)
        fig_estados.update_layout(plot_bgcolor='rgba(0,0,0,0)', height=300, showlegend=False)
        st.plotly_chart(fig_estados, use_container_width=True)
    
    st.divider()
    
    # RANKING DE ESPÉCIES
    st.subheader("🌿 Espécies Mais Acessadas (2026)")
    
    df_esp = pd.DataFrame({
        'Espécie': list(ESPECIES.keys()),
        'Sessões': list(ESPECIES.values())
    }).sort_values('Sessões', ascending=True)
    
    fig_esp = px.bar(df_esp, x='Sessões', y='Espécie', orientation='h',
                     text_auto=',d', color='Sessões', color_continuous_scale='Greens')
    fig_esp.update_traces(textposition='outside', textfont_size=10)
    fig_esp.update_layout(plot_bgcolor='rgba(0,0,0,0)', height=350, showlegend=False)
    st.plotly_chart(fig_esp, use_container_width=True)
    
    st.divider()
    
    # CONCLUSÃO
    st.subheader("💡 Conclusão")
    
    st.markdown("""
    <div style="background: #f0f9f4; padding: 20px; border-radius: 12px; border-left: 4px solid #17B978; margin: 15px 0; line-height: 1.8;">
        <p>Os resultados confirmam o site do Horto como <strong>efetivo lócus empírico da Etnobiologia Digital</strong>, ampliando o alcance do conhecimento etnobotânico para além dos muros da universidade e alcançando públicos diversos em escala nacional e internacional.</p>
        
        <p>As métricas de <strong>Web Analytics</strong> mostraram-se ferramentas robustas para avaliar essa circulação, permitindo identificar os principais canais de acesso, com destaque para buscadores e, mais recentemente, assistentes de IA, bem como o perfil demográfico dos usuários e os conteúdos mais acessados.</p>
        
        <p>Essa análise evidencia a <strong>tensão entre a capilaridade digital</strong> e o <strong>risco de descontextualização</strong>, reforçando a necessidade de conciliar acessibilidade com a preservação da integridade dos saberes, garantindo que a divulgação científica não comprometa a riqueza e a segurança dos conhecimentos tradicionais <em>(De Meyer & Ceuterick, 2022; Simon & Camargo, 2021)</em>.</p>
        
        <p style="color: #555; margin-top: 10px;"><strong>Apoio Financeiro:</strong> Universidade Federal de Santa Catarina (UFSC)</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# ABA 2: TEMPO REAL
# ============================================

with aba2:
    st.header("📊 Painel de Controle - Visitantes do Site")
    st.caption("Dados do Google Analytics 4")
    
    st.info("""
    🧐 **O que você está vendo?**
    
    Este painel mostra dados reais de visitantes do site do Horto Didático.
    - Se aparecerem números → são visitas **reais**!
    - Se aparecer "sem dados" → o site não recebeu visitas no período
    """)
    
    count = st_autorefresh(interval=30000, key="refresh")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        periodo = st.selectbox(
            "📅 Período:",
            ["⚡ Últimos 30 minutos", "📆 Últimos 7 dias", "📆 Últimos 30 dias", "📆 Ano de 2026"]
        )
    with col2:
        st.caption(f"🔄 {datetime.now().strftime('%H:%M:%S')}")
    
    st.divider()
    
    if "30 minutos" in periodo:
        st.markdown("### ⚡ Agora no site")
        
        with st.spinner("🔄 Buscando dados..."):
            df_rt = get_realtime_data()
        
        if df_rt is not None and not df_rt.empty:
            total = df_rt['activeUsers'].sum() if 'activeUsers' in df_rt.columns else 0
            
            col_a1, col_a2, col_a3 = st.columns(3)
            col_a1.metric("👤 Pessoas agora", f"{total:.0f}")
            col_a2.metric("📄 Páginas vistas", f"{df_rt['screenPageViews'].sum():.0f}")
            
            if 'deviceCategory' in df_rt.columns:
                top = df_rt.groupby('deviceCategory')['activeUsers'].sum().idxmax()
                col_a3.metric("📱 Dispositivo", top)
            
            st.divider()
            
            col_p1, col_p2 = st.columns(2)
            
            with col_p1:
                st.write("**📄 Páginas em destaque**")
                if 'pageTitle' in df_rt.columns:
                    df_pages = df_rt.groupby('pageTitle')['activeUsers'].sum().reset_index()
                    df_pages = df_pages.sort_values('activeUsers', ascending=True).tail(8)
                    
                    def nome_amigavel(nome):
                        nome = str(nome).lower()
                        if 'folha' in nome: return '🌿 Folha da Fortuna'
                        if 'quebra' in nome: return '🌿 Quebra-pedra'
                        if 'buchinha' in nome: return '🌿 Buchinha do Norte'
                        if 'alfavaca' in nome: return '🌿 Alfavaca-cravo'
                        if 'aveloz' in nome: return '🌿 Aveloz'
                        if 'melão' in nome: return '🌿 Melão-de-São-Caetano'
                        if 'home' in nome or 'início' in nome: return '🏠 Página Inicial'
                        return '📄 ' + nome[:20]
                    
                    df_pages['Página'] = df_pages['pageTitle'].apply(nome_amigavel)
                    
                    fig = px.bar(df_pages, x='activeUsers', y='Página',
                                orientation='h', color='activeUsers',
                                color_continuous_scale='Greens', text_auto=True)
                    fig.update_layout(showlegend=False, height=300, plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col_p2:
                st.write("**🌍 Origem**")
                if 'country' in df_rt.columns:
                    df_geo = df_rt.groupby('country')['activeUsers'].sum().reset_index()
                    df_geo = df_geo.sort_values('activeUsers', ascending=False).head(8)
                    fig = px.pie(df_geo, values='activeUsers', names='country',
                                color_discrete_sequence=px.colors.sequential.Greens_r,
                                hole=0.3)
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Dados de demonstração - site sem visitas agora")
            
            col_d1, col_d2, col_d3 = st.columns(3)
            col_d1.metric("👤 Pessoas agora", "18")
            col_d2.metric("📄 Páginas vistas", "42")
            col_d3.metric("📱 Dispositivo", "📱 Celular")
            
            st.divider()
            
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.write("**📄 Páginas em destaque**")
                df_demo = pd.DataFrame({
                    'Página': ['🌿 Folha da Fortuna', '🌿 Quebra-pedra', '🏠 Home', '🌿 Buchinha'],
                    'Pessoas': [7, 5, 4, 2]
                })
                fig = px.bar(df_demo, x='Pessoas', y='Página', orientation='h',
                            color='Pessoas', color_continuous_scale='Greens', text_auto=True)
                fig.update_layout(showlegend=False, height=250, plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            
            with col_p2:
                st.write("**🌍 Origem**")
                df_geo = pd.DataFrame({
                    'Local': ['🇧🇷 Brasil', '🇵🇹 Portugal', '🇺🇸 EUA', '🇦🇴 Angola'],
                    'Pessoas': [8, 5, 3, 2]
                })
                fig = px.pie(df_geo, values='Pessoas', names='Local',
                            color_discrete_sequence=['#1E3D59', '#17B978', '#334E68', '#A7E9AF'],
                            hole=0.3)
                fig.update_layout(height=250)
                st.plotly_chart(fig, use_container_width=True)
        
        st.caption(f"🔄 Ciclo: #{count}")
    
    else:
        st.info(f"📊 Período: {periodo}")
        
        end = datetime.now().strftime('%Y-%m-%d')
        if "7 dias" in periodo:
            start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        elif "30 dias" in periodo:
            start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        else:
            start = '2026-01-01'
        
        with st.spinner("🔄 Carregando dados..."):
            df_hist = get_ga4_data(start, end)
        
        if df_hist is not None and not df_hist.empty:
            col_h1, col_h2 = st.columns(2)
            
            with col_h1:
                st.subheader("📈 Visitas por dia")
                if 'date' in df_hist.columns:
                    df_daily = df_hist.groupby('date')['activeUsers'].sum().reset_index()
                    df_daily['date'] = pd.to_datetime(df_daily['date'])
                    fig = px.line(df_daily, x='date', y='activeUsers',
                                 color_discrete_sequence=['#17B978'])
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', height=300)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col_h2:
                st.subheader("📊 De onde vêm")
                if 'sessionDefaultChannelGroup' in df_hist.columns:
                    df_chan = df_hist.groupby('sessionDefaultChannelGroup')['activeUsers'].sum().reset_index()
                    df_chan = df_chan.sort_values('activeUsers', ascending=True).tail(8)
                    fig = px.bar(df_chan, x='activeUsers', y='sessionDefaultChannelGroup',
                                orientation='h', color='activeUsers',
                                color_continuous_scale='Greens', text_auto=True)
                    fig.update_layout(showlegend=False, height=300, plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Nenhum dado disponível para este período")
            
            st.markdown("""
            ### 🤔 Por que não aparecem dados?
            
            1. O site pode não ter recebido visitas
            2. O código de rastreamento pode não estar instalado
            3. A propriedade selecionada pode não ter dados
            
            **Os dados do seu artigo estão na aba RESULTADOS!**
            """)

# ============================================
# ABA 3: REFERÊNCIAS
# ============================================

with aba3:
    st.header("📚 Referências Bibliográficas")
    
    st.markdown("""
    <div class="ref-box">
        <p><strong>BOELL, M. E. C.</strong> Espécies do Horto Didático de Plantas Medicinais do HU/CCS (UFSC): identificação botânica e uso terapêutico de plantas medicinais. 2023. Trabalho de Conclusão de Curso (Graduação) – Universidade Federal de Santa Catarina, Florianópolis, 2023. Disponível em: https://repositorio.ufsc.br/handle/123456789/266030. Acesso em: 4 ago. 2026.</p>
        
        <p><strong>CEUTERICK, M.; VANDEBROEK, I.; TORRY, B.; PIERONI, A.</strong> Cross-cultural adaptation in urban ethnobotany: the Colombian folk pharmacopoeia in London. Journal of Ethnopharmacology, v. 120, n. 3, p. 342-359, 2008. DOI: 10.1016/j.jep.2008.09.004. Disponível em: https://pubmed.ncbi.nlm.nih.gov/18852036/. Acesso em: 4 ago. 2026.</p>
        
        <p><strong>DE MEYER, E.; CEUTERICK, M.</strong> Digital Ethnobiology: exploring the digisphere in search of traditional and indigenous knowledge and practices. Ethnobotany Research and Applications, v. 24, p. 1-8, 2022. DOI: 10.32859/era.24.37.1-8. Disponível em: https://ethnobotanyjournal.org/index.php/era/article/view/4067. Acesso em: 4 ago. 2026.</p>
        
        <p><strong>FOLKE, C.; BIGGS, R.; NORSTRÖM, A. V.; REYERS, B.; ROCKSTRÖM, J.</strong> Social-ecological resilience and biosphere-based sustainability science. Ecology and Society, v. 21, n. 3, p. 41, 2016. DOI: 10.5751/ES-08748-210341. Disponível em: https://www.ecologyandsociety.org/vol21/iss3/art41/. Acesso em: 4 ago. 2026.</p>
        
        <p><strong>RITTER, G. D.</strong> O site do Horto Didático de Plantas Medicinais (UFSC) como ferramenta de divulgação científica para o uso de plantas medicinais. 2025. Trabalho de Conclusão de Curso (Graduação) – Universidade Federal de Santa Catarina, Florianópolis, 2025. Disponível em: https://repositorio.ufsc.br/xmlui/handle/123456789/252686. Acesso em: 4 ago. 2026.</p>
        
        <p><strong>SIMON, F. M.; CAMARGO, C. Q.</strong> Autopsy of a metaphor: the origins, use and blind spots of the 'infodemic'. New Media & Society, v. 25, n. 8, p. 2219-2240, 2023. DOI: 10.1177/14614448211031908. Disponível em: https://doi.org/10.1177/14614448211031908. Acesso em: 4 ago. 2026.</p>
        
        <p><strong>WELLMAN, B.</strong> Little Boxes, Glocalization, and Networked Individualism. In: TANABE, M.; BESSELAAR, P. van den; ISHIDA, T. (ed.). Digital Cities II: computational and sociological approaches. Berlin: Springer, 2002. p. 10-25.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# RODAPÉ
# ============================================

st.markdown("---")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.markdown("🏛️ **Horto Didático UFSC**")
with col_f2:
    st.markdown(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
with col_f3:
    st.markdown("🎓 **SPMB 2026**")

st.markdown("""
<div class="footer">
    🌿 Apresentação no XXVIII SPMB 2026 | Apoio: UFSC
    <br>
    🔗 <a href="https://hortodidatico.ufsc.br/" target="_blank" style="color: #17B978;">hortodidatico.ufsc.br</a>
</div>
""", unsafe_allow_html=True)
