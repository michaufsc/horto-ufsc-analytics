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
# DADOS DO SEU ARTIGO
# ============================================

TITULO = "Etnobiologia digital no Horto Didático da UFSC: circulação do saber etnobotânico mensurada por web analytics"

AUTORES = """
**Michael A. Lopes**¹ (Apresentador)  
**Maique W. Biavatti**² (Orientadora)  
**Gabriela D. Ritter**³ (Colaboradora)  
**Letícia S. Tardim**⁴ (Colaboradora)  

¹Universidade Federal de Santa Catarina – UFSC, Graduando em Química Tecnológica, Florianópolis, SC, Brasil.  
²Universidade Federal de Santa Catarina – UFSC, Departamento de Ciências Farmacêuticas, Florianópolis, SC, Brasil.  
³Farmacêutica, Florianópolis, SC, Brasil.  
⁴Universidade Federal de Santa Catarina – UFSC, Graduanda em Farmácia, Florianópolis, SC, Brasil.
"""

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

# Espécies mais acessadas (dados do Google Analytics)
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
    .authors-box { 
        text-align: center; 
        background: #f8f9fa; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #e0e0e0; 
        margin: 10px 0; 
        line-height: 1.8;
    }
    .metric-card { 
        background: #F8F9FA; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 4px solid #17B978; 
        text-align: center; 
        transition: transform 0.2s; 
    }
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
    .glossary-box {
        background: #f8f9fa;
        padding: 15px 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 10px 0;
        line-height: 1.8;
    }
    .glossary-box strong { color: #1E3D59; }
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

st.markdown(f"### {TITULO}")

st.markdown(f"""
<div class="authors-box">
    {AUTORES}
</div>
""", unsafe_allow_html=True)

st.markdown(f"**Palavras-chave:** {PALAVRAS_CHAVE}")

# ============================================
# GLOSSÁRIO - EXPANDER COM TÍTULO DESTACADO
# ============================================

st.markdown("### 📖 Glossário de Termos Técnicos")

with st.expander("🔍 Clique aqui para ver o significado dos termos", expanded=False):
    st.markdown("""
    <div class="glossary-box">
        <p><strong>Google Analytics 4 (GA4)</strong> → Plataforma do Google para coletar e analisar dados de interação dos usuários com sites.</p>
        <p><strong>Web Analytics</strong> → Processo de coletar, medir e analisar dados de acesso e comportamento em ambientes digitais.</p>
        <p><strong>Usuário</strong> → Pessoa identificada pelo Google Analytics que interage com o site.</p>
        <p><strong>Usuários Novos</strong> → Pessoas que acessaram o site pela primeira vez.</p>
        <p><strong>Sessão</strong> → Período em que um usuário interage com o site.</p>
        <p><strong>Busca Orgânica</strong> → Visitas que vêm de resultados do Google sem anúncios pagos.</p>
        <p><strong>Acesso Direto</strong> → Quando o usuário digita o endereço do site diretamente.</p>
        <p><strong>Referral</strong> → Visitas que vêm de outros sites (blogs, redes sociais).</p>
        <p><strong>Engajamento</strong> → Grau de interação dos usuários com o conteúdo do site.</p>
        <p><strong>Landing Page</strong> → Primeira página que o usuário vê ao entrar no site.</p>
        <p><strong>IA (Inteligência Artificial)</strong> → Assistentes como Google Gemini, ChatGPT, que direcionam usuários para o site.</p>
        <p><strong>Dispositivo</strong> → Celular, computador ou tablet usado para acessar o site.</p>
    </div>
    """, unsafe_allow_html=True)

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
    <p style="margin-top: 5px; font-weight: 600;">Apresentador: Michael A. Lopes</p>
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
    
    # RELATÓRIOS ANALISADOS
    st.subheader("📊 Relatórios do Google Analytics Analisados")
    
    st.markdown("""
    <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; margin: 10px 0;">
        <p><strong>📥 Aquisição de usuários</strong> → Análise da origem pela qual os usuários, especialmente os novos usuários, chegaram ao site.</p>
        <p><strong>📥 Aquisição de tráfego</strong> → Análise da origem das sessões ou do tráfego recebido pelo site.</p>
        <p><strong>👥 Perfil demográfico</strong> → Características da audiência: sexo, idade e localização geográfica.</p>
        <p><strong>📄 Engajamento</strong> → Eventos e interações dos usuários com o conteúdo do site.</p>
        <p><strong>🌿 Conteúdo</strong> → Páginas e espécies medicinais mais acessadas.</p>
        <p style="font-size: 0.85rem; color: #666; margin-top: 10px;">📅 Período analisado: Ano completo de 2025 e janeiro a julho de 2026</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # RESUMO
    st.markdown("### 📋 Resumo dos Resultados")
    
    with st.expander("📊 Clique para ver o resumo completo", expanded=True):
        st.markdown(f"""
        A análise combinada entre aquisição de usuários e aquisição de tráfego revela a sólida autoridade e o alcance do portal.

        Em **2025**, o site registrou **{USUARIOS_2025:,} usuários** ({USUARIOS_NOVOS_2025:,} novos), com predomínio da busca orgânica ({BUSCA_ORGANICA_2025:,}; **{BUSCA_ORGANICA_PCT_2025:.2f}%**) e do acesso direto ({ACESSO_DIRETO_2025:,}; **{ACESSO_DIRETO_PCT_2025:.2f}%**). Na perspectiva de tráfego, o mesmo período contabilizou {USUARIOS_ENGAJADOS_2025:,} usuários engajados, liderados pela busca orgânica ({BUSCA_ORGANICA_TR_2025:,}; **{BUSCA_ORGANICA_TR_PCT_2025:.2f}%**) e acesso direto ({ACESSO_DIRETO_TR_2025:,}; **{ACESSO_DIRETO_TR_PCT_2025:.2f}%**).

        Em **2026 (jan–jul)**, foram **{USUARIOS_2026:,} usuários** ({USUARIOS_NOVOS_2026:,} novos), mantendo a liderança da busca orgânica ({BUSCA_ORGANICA_2026:,}; **{BUSCA_ORGANICA_PCT_2026:.2f}%**) e acesso direto ({ACESSO_DIRETO_2026:,}; **{ACESSO_DIRETO_PCT_2026:.2f}%**), enquanto o tráfego total atingiu {USUARIOS_ENGAJADOS_2026:,} usuários, com busca orgânica ({BUSCA_ORGANICA_TR_2026:,}; **{BUSCA_ORGANICA_TR_PCT_2026:.2f}%**) e acesso direto ({ACESSO_DIRETO_TR_2026:,}; **{ACESSO_DIRETO_TR_PCT_2026:.2f}%**).

        **Destaques:**
        - 🤖 **Emergência de IA**: {IA_USUARIOS} usuários e {IA_SESSOES} sessões via assistentes de IA
        - 🔗 **Alta retenção**: {REFERRAL_RETENCAO:.2f}% em canais de indicação (Referral)
        - 📈 **Crescimento**: Projeção de superar o tráfego total de 2025 até o final de 2026

        Quanto ao perfil demográfico, observou-se predominância expressiva do público feminino (**{FEMININO_2025:.1f}% em 2025** e **{FEMININO_2026:.1f}% em 2026**) e de jovens adultos na faixa etária de 25 a 34 anos (**40,1%**). A imensa maioria dos acessos está concentrada no Brasil (**{BRASIL_2025:.1f}% em 2025** e **{BRASIL_2026:.1f}% em 2026**).
        """)
    
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
    
    with st.expander("🌎 Clique para ver o alcance internacional e nacional"):
        
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
                <h4>🇧🇷 Distribuição no Brasil</h4>
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
    
    # RANKING DE ESPÉCIES - VERSÃO MELHORADA
    st.subheader("🌿 Ranking de Espécies Mais Acessadas em 2026")
    st.caption("Dados do Google Analytics - espécies com maior volume de acessos no período")
    
    # Criar DataFrame e ordenar (da mais acessada para a menos)
    df_esp = pd.DataFrame({
        'Espécie': list(ESPECIES.keys()),
        'Sessões de Entrada': list(ESPECIES.values())
    }).sort_values('Sessões de Entrada', ascending=True)
    
    # Criar gráfico com cores mais bonitas
    fig_esp = px.bar(
        df_esp,
        x='Sessões de Entrada',
        y='Espécie',
        orientation='h',
        text_auto='.0f',
        color='Sessões de Entrada',
        color_continuous_scale=px.colors.sequential.Greens_r,
        labels={'Sessões de Entrada': 'Sessões de Entrada', 'Espécie': ''}
    )
    
    # Ajustar o texto das barras
    fig_esp.update_traces(
        textposition='outside',
        textfont_size=12,
        textfont_color='#1E3D59',
        hovertemplate='<b>%{y}</b><br>Sessões: %{x:,.0f}<extra></extra>'
    )
    
    # Ajustar o layout
    fig_esp.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        height=450,
        showlegend=False,
        margin=dict(l=0, r=30, t=20, b=20),
        xaxis=dict(
            title='Sessões de Entrada',
            title_font_size=12,
            tickfont_size=11,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        yaxis=dict(
            title='',
            tickfont_size=13,
            tickangle=0
        ),
        hovermode='y unified'
    )
    
    # Exibir o gráfico
    st.plotly_chart(fig_esp, use_container_width=True)
    
    # Adicionar uma nota sobre os dados
    st.caption("💡 Passe o mouse sobre as barras para ver detalhes das espécies")
    
    st.divider()
    
    # CONCLUSÃO
    st.subheader("💡 Conclusão")
    
    with st.expander("📄 Clique para ler a conclusão completa", expanded=True):
        st.markdown("""
        Os resultados confirmam o site do Horto como **efetivo lócus empírico da Etnobiologia Digital**, ampliando o alcance do conhecimento etnobotânico para além dos muros da universidade e alcançando públicos diversos em escala nacional e internacional.

        As métricas de **Web Analytics** mostraram-se ferramentas robustas para avaliar essa circulação, permitindo identificar os principais canais de acesso, com destaque para buscadores e, mais recentemente, assistentes de IA, bem como o perfil demográfico dos usuários e os conteúdos mais acessados.

        Essa análise evidencia a **tensão entre a capilaridade digital** e o **risco de descontextualização**, reforçando a necessidade de conciliar acessibilidade com a preservação da integridade dos saberes, garantindo que a divulgação científica não comprometa a riqueza e a segurança dos conhecimentos tradicionais *(De Meyer & Ceuterick, 2022; Simon & Camargo, 2021)*.

        **Apoio Financeiro:** Universidade Federal de Santa Catarina (UFSC)
        """)

# ============================================
# ABA 2: TEMPO REAL
# ============================================

with aba2:
    st.header("📊 Painel de Controle - Visitantes do Site")
    st.caption("Dados do Google Analytics 4")
    
    st.info("""
    👋 **Bem-vindo ao painel de visitantes!**
    
    Aqui você vê quantas pessoas estão acessando o site do Horto agora e nos últimos dias.
    
    - ✅ Números VERDES → são visitas **reais** que aconteceram!
    - ⚠️ Se aparecer "sem dados" → significa que não houve visitas no período (isso é normal)
    - 📅 Use o menu abaixo para ver diferentes períodos
    """)
    
    count = st_autorefresh(interval=30000, key="refresh")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        periodo = st.selectbox(
            "📅 Escolha o período:",
            ["⚡ Agora (últimos 30 min)", "📆 Últimos 7 dias", "📆 Últimos 30 dias", "📆 Ano de 2026"],
            help="Selecione um período para ver os dados de visitantes"
        )
    with col2:
        st.caption(f"🔄 Atualização: a cada 30s")
        st.caption(f"⏱️ {datetime.now().strftime('%H:%M:%S')}")
    
    st.divider()
    
    # MODO TEMPO REAL
    if "Agora" in periodo:
        st.markdown("### 🟢 Quem está no site AGORA?")
        
        with st.spinner("🔄 Buscando visitantes ativos..."):
            df_rt = get_realtime_data()
        
        if df_rt is not None and not df_rt.empty:
            total = df_rt['activeUsers'].sum() if 'activeUsers' in df_rt.columns else 0
            
            col_a1, col_a2, col_a3 = st.columns(3)
            
            with col_a1:
                st.markdown(f"""
                <div style="background: #f0f9f4; padding: 25px; border-radius: 12px; text-align: center; border: 2px solid #17B978;">
                    <div style="font-size: 3rem; font-weight: 700; color: #1E3D59;">{total:.0f}</div>
                    <div style="font-size: 1rem; color: #555;">👤 Pessoas no site<br><span style="font-size: 0.8rem; color: #999;">neste exato momento</span></div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_a2:
                page_views = df_rt['screenPageViews'].sum() if 'screenPageViews' in df_rt.columns else 0
                st.markdown(f"""
                <div style="background: #f0f9f4; padding: 25px; border-radius: 12px; text-align: center; border: 2px solid #17B978;">
                    <div style="font-size: 3rem; font-weight: 700; color: #1E3D59;">{page_views:.0f}</div>
                    <div style="font-size: 1rem; color: #555;">📄 Páginas visitadas<br><span style="font-size: 0.8rem; color: #999;">nos últimos 30 min</span></div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_a3:
                if 'deviceCategory' in df_rt.columns:
                    device_counts = df_rt.groupby('deviceCategory')['activeUsers'].sum()
                    top_device = device_counts.idxmax() if not device_counts.empty else "N/A"
                    device_map = {'mobile': '📱 Celular', 'desktop': '💻 Computador', 'tablet': '📟 Tablet'}
                    top_device_display = device_map.get(top_device.lower(), top_device)
                    st.markdown(f"""
                    <div style="background: #f0f9f4; padding: 25px; border-radius: 12px; text-align: center; border: 2px solid #17B978;">
                        <div style="font-size: 2.5rem; font-weight: 700; color: #1E3D59;">{top_device_display}</div>
                        <div style="font-size: 1rem; color: #555;">📱 Dispositivo mais usado<br><span style="font-size: 0.8rem; color: #999;">acessando agora</span></div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.divider()
            
            st.markdown("#### 📊 O que as pessoas estão vendo?")
            
            col_p1, col_p2 = st.columns(2)
            
            with col_p1:
                st.markdown("**📄 Páginas mais visitadas agora**")
                if 'pageTitle' in df_rt.columns:
                    df_pages = df_rt.groupby('pageTitle')['activeUsers'].sum().reset_index()
                    df_pages = df_pages.sort_values('activeUsers', ascending=True).tail(6)
                    
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
                    fig.update_layout(
                        showlegend=False,
                        height=280,
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis_title="👤 Pessoas",
                        yaxis_title="",
                        margin=dict(l=0, r=0, t=0, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("💡 Passe o mouse sobre as barras para ver detalhes")
            
            with col_p2:
                st.markdown("**🌍 De onde vêm os visitantes**")
                if 'country' in df_rt.columns:
                    df_geo = df_rt.groupby('country')['activeUsers'].sum().reset_index()
                    df_geo = df_geo.sort_values('activeUsers', ascending=False).head(6)
                    
                    flags = {
                        'Brazil': '🇧🇷 Brasil',
                        'Portugal': '🇵🇹 Portugal',
                        'United States': '🇺🇸 EUA',
                        'Angola': '🇦🇴 Angola',
                        'Mozambique': '🇲🇿 Moçambique',
                        'Spain': '🇪🇸 Espanha'
                    }
                    df_geo['Local'] = df_geo['country'].apply(lambda x: flags.get(x, f'🌍 {x}'))
                    
                    fig = px.pie(df_geo, values='activeUsers', names='Local',
                                color_discrete_sequence=['#1E3D59', '#17B978', '#334E68', '#4CAF50', '#66BB6A', '#81C784'],
                                hole=0.3)
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(height=280, margin=dict(l=0, r=0, t=0, b=0))
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("💡 Clique nas fatias para ver detalhes")
        
        else:
            st.info("📊 **Demonstração** - O site não teve visitas nos últimos 30 minutos.")
            st.markdown("""
            Isso é **normal** se:
            - O site está com pouco tráfego agora
            - Você está testando o app fora do horário de pico
            
            Os dados abaixo são apenas para mostrar como o painel funciona:
            """)
            
            col_d1, col_d2, col_d3 = st.columns(3)
            
            with col_d1:
                st.markdown("""
                <div style="background: #f0f9f4; padding: 25px; border-radius: 12px; text-align: center; border: 2px solid #17B978;">
                    <div style="font-size: 3rem; font-weight: 700; color: #1E3D59;">18</div>
                    <div style="font-size: 1rem; color: #555;">👤 Pessoas no site</div>
                    <div style="font-size: 0.8rem; color: #999;">(dados ilustrativos)</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_d2:
                st.markdown("""
                <div style="background: #f0f9f4; padding: 25px; border-radius: 12px; text-align: center; border: 2px solid #17B978;">
                    <div style="font-size: 3rem; font-weight: 700; color: #1E3D59;">42</div>
                    <div style="font-size: 1rem; color: #555;">📄 Páginas visitadas</div>
                    <div style="font-size: 0.8rem; color: #999;">(dados ilustrativos)</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_d3:
                st.markdown("""
                <div style="background: #f0f9f4; padding: 25px; border-radius: 12px; text-align: center; border: 2px solid #17B978;">
                    <div style="font-size: 2.5rem; font-weight: 700; color: #1E3D59;">📱 Celular</div>
                    <div style="font-size: 1rem; color: #555;">Dispositivo mais usado</div>
                    <div style="font-size: 0.8rem; color: #999;">(dados ilustrativos)</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            
            col_d4, col_d5 = st.columns(2)
            
            with col_d4:
                st.write("**📄 Páginas mais visitadas (exemplo)**")
                df_demo = pd.DataFrame({
                    'Página': ['🌿 Folha da Fortuna', '🌿 Quebra-pedra', '🏠 Página Inicial', '🌿 Buchinha'],
                    'Pessoas': [7, 5, 4, 2]
                })
                fig = px.bar(df_demo, x='Pessoas', y='Página', orientation='h',
                            color='Pessoas', color_continuous_scale='Greens', text_auto=True)
                fig.update_layout(showlegend=False, height=250, plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            
            with col_d5:
                st.write("**🌍 Origem dos visitantes (exemplo)**")
                df_geo = pd.DataFrame({
                    'Local': ['🇧🇷 Brasil', '🇵🇹 Portugal', '🇺🇸 EUA', '🇦🇴 Angola'],
                    'Pessoas': [8, 5, 3, 2]
                })
                fig = px.pie(df_geo, values='Pessoas', names='Local',
                            color_discrete_sequence=['#1E3D59', '#17B978', '#334E68', '#A7E9AF'],
                            hole=0.3)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=250)
                st.plotly_chart(fig, use_container_width=True)
        
        st.caption(f"🔄 Atualizado automaticamente a cada 30 segundos | Ciclo: #{count}")
    
    # MODO HISTÓRICO
    else:
        st.markdown(f"### 📊 Visitas na **{periodo.replace('📆 ', '')}**")
        
        end = datetime.now().strftime('%Y-%m-%d')
        if "7 dias" in periodo:
            start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            label = "última semana"
        elif "30 dias" in periodo:
            start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            label = "último mês"
        else:
            start = '2026-01-01'
            label = "2026"
        
        with st.spinner(f"🔄 Carregando dados da {label}..."):
            df_hist = get_ga4_data(start, end)
        
        if df_hist is not None and not df_hist.empty:
            
            # Resumo simples
            total_pessoas = df_hist['totalUsers'].sum() if 'totalUsers' in df_hist.columns else 0
            total_visitas = df_hist['sessions'].sum() if 'sessions' in df_hist.columns else 0
            
            col_r1, col_r2 = st.columns(2)
            
            with col_r1:
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; text-align: center; border-left: 4px solid #17B978;">
                    <div style="font-size: 2rem; font-weight: 700; color: #1E3D59;">{total_pessoas:,.0f}</div>
                    <div style="font-size: 0.9rem; color: #555;">👤 Pessoas diferentes visitaram o site</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_r2:
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; text-align: center; border-left: 4px solid #17B978;">
                    <div style="font-size: 2rem; font-weight: 700; color: #1E3D59;">{total_visitas:,.0f}</div>
                    <div style="font-size: 0.9rem; color: #555;">📊 Visitas (sessões) no total</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            
            # Gráficos
            col_h1, col_h2 = st.columns(2)
            
            with col_h1:
                st.subheader("📈 Pessoas por dia")
                if 'date' in df_hist.columns:
                    df_daily = df_hist.groupby('date')['activeUsers'].sum().reset_index()
                    df_daily['date'] = pd.to_datetime(df_daily['date'])
                    fig = px.line(df_daily, x='date', y='activeUsers',
                                 color_discrete_sequence=['#17B978'],
                                 labels={'date': 'Data', 'activeUsers': '👤 Pessoas'})
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        hovermode='x unified',
                        height=300,
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("💡 Cada ponto representa quantas pessoas visitaram o site naquele dia")
            
            with col_h2:
                st.subheader("📊 De onde vieram")
                if 'sessionDefaultChannelGroup' in df_hist.columns:
                    df_chan = df_hist.groupby('sessionDefaultChannelGroup')['activeUsers'].sum().reset_index()
                    df_chan = df_chan.sort_values('activeUsers', ascending=True).tail(6)
                    
                    canal_map = {
                        'Organic Search': '🔍 Busca no Google',
                        'Direct': '🏠 Digitaram o endereço',
                        'Referral': '🔗 Indicação de outro site',
                        'Social': '📱 Redes Sociais',
                        'Email': '✉️ Email'
                    }
                    df_chan['Canal'] = df_chan['sessionDefaultChannelGroup'].apply(
                        lambda x: canal_map.get(x, x)
                    )
                    
                    fig = px.bar(df_chan, x='activeUsers', y='Canal',
                                orientation='h', color='activeUsers',
                                color_continuous_scale='Greens', text_auto=True)
                    fig.update_layout(
                        showlegend=False,
                        height=300,
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis_title="👤 Pessoas",
                        yaxis_title="",
                        margin=dict(l=0, r=0, t=0, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("💡 Como as pessoas chegaram ao site")
        
        else:
            st.warning("⚠️ Nenhum dado disponível para este período")
            
            st.markdown("""
            ### 🤔 Por que não aparecem dados?
            
            **Motivos mais comuns:**
            1. O site não recebeu visitas nesse período
            2. O código de rastreamento do Google Analytics pode não estar instalado no site
            
            **O que fazer:**
            - ✅ Tente selecionar um período mais longo
            - ✅ Os dados do seu artigo estão disponíveis na aba **RESULTADOS**
            - ✅ Você pode apresentar com os dados do artigo, que são os da sua pesquisa!
            """)

# ============================================
# ABA 3: REFERÊNCIAS
# ============================================

with aba3:
    st.header("📚 Referências Bibliográficas")
    
    st.markdown("""
    **BOELL, M. E. C.** Espécies do Horto Didático de Plantas Medicinais do HU/CCS (UFSC): identificação botânica e uso terapêutico de plantas medicinais. 2023. Trabalho de Conclusão de Curso (Graduação) – Universidade Federal de Santa Catarina, Florianópolis, 2023.

    **CEUTERICK, M.; VANDEBROEK, I.; TORRY, B.; PIERONI, A.** Cross-cultural adaptation in urban ethnobotany: the Colombian folk pharmacopoeia in London. Journal of Ethnopharmacology, v. 120, n. 3, p. 342-359, 2008. DOI: 10.1016/j.jep.2008.09.004.

    **DE MEYER, E.; CEUTERICK, M.** Digital Ethnobiology: exploring the digisphere in search of traditional and indigenous knowledge and practices. Ethnobotany Research and Applications, v. 24, p. 1-8, 2022. DOI: 10.32859/era.24.37.1-8.

    **FOLKE, C.; BIGGS, R.; NORSTRÖM, A. V.; REYERS, B.; ROCKSTRÖM, J.** Social-ecological resilience and biosphere-based sustainability science. Ecology and Society, v. 21, n. 3, p. 41, 2016. DOI: 10.5751/ES-08748-210341.

    **RITTER, G. D.** O site do Horto Didático de Plantas Medicinais (UFSC) como ferramenta de divulgação científica para o uso de plantas medicinais. 2025. Trabalho de Conclusão de Curso (Graduação) – Universidade Federal de Santa Catarina, Florianópolis, 2025.

    **SIMON, F. M.; CAMARGO, C. Q.** Autopsy of a metaphor: the origins, use and blind spots of the 'infodemic'. New Media & Society, v. 25, n. 8, p. 2219-2240, 2023. DOI: 10.1177/14614448211031908.

    **WELLMAN, B.** Little Boxes, Glocalization, and Networked Individualism. In: TANABE, M.; BESSELAAR, P. van den; ISHIDA, T. (ed.). Digital Cities II: computational and sociological approaches. Berlin: Springer, 2002. p. 10-25.
    """)

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
🌿 Apresentação no XXVIII SPMB 2026 | Apoio: UFSC

🔗 [hortodidatico.ufsc.br](https://hortodidatico.ufsc.br/)
""")
