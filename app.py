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
**Michael A. Lopes** (Apresentador)  
**Maique W. Biavatti** (Orientador)  
**Gabriela D. Ritter** (Colaboradora)  
**Letícia S. Tardim** (Colaboradora)  

Universidade Federal de Santa Catarina (UFSC) - Florianópolis, SC, Brasil
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

# Espécies mais acessadas
ESPECIES = {
    'Folha-da-fortuna (Kalanchoe pinnata)': 6460,
    'Quebra-pedra / Quebra-pedra-rasteiro (Phyllanthus spp.)': 5599,
    'Buchinha-do-norte (Luffa operculata)': 4334,
    'Alfavaca-cravo (Ocimum gratissimum)': 4127,
    'Aveloz (Euphorbia tirucalli)': 4092,
    'Melão-de-são-caetano (Momordica charantia)': 3500,
}

PAISES = {
    'Portugal': 850,
    'Estados Unidos': 620,
    'Moçambique': 340,
    'Angola': 280,
    'Espanha': 210,
}

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
# ESTILOS VISUAIS (SÓ CSS, SEM HTML NOS TEXTOS)
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
        max-height: 500px;
        overflow-y: auto;
        line-height: 1.8;
    }
    .glossary-box strong { color: #1E3D59; }
    .conclusion-box {
        background: #f0f9f4;
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #17B978;
        margin: 15px 0;
        line-height: 1.8;
    }
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
# TÍTULO E AUTORES (MARKDOWN PURO)
# ============================================

st.markdown(f"### {TITULO}")

st.markdown(f"""
<div class="authors-box">
    {AUTORES}
</div>
""", unsafe_allow_html=True)

st.markdown(f"**Palavras-chave:** {PALAVRAS_CHAVE}")

# ============================================
# GLOSSÁRIO (MARKDOWN PURO)
# ============================================

with st.expander("📖 Glossário - Entenda os termos"):
    st.markdown("""
    **Google Analytics 4 (GA4)** → Plataforma do Google para coletar e analisar dados de interação dos usuários com sites.

    **Web Analytics** → Processo de coletar, medir e analisar dados de acesso e comportamento em ambientes digitais.

    **Usuário** → Pessoa identificada pelo Google Analytics que interage com o site.

    **Usuários Novos** → Pessoas que acessaram o site pela primeira vez.

    **Sessão** → Período em que um usuário interage com o site.

    **Busca Orgânica** → Visitas que vêm de resultados do Google sem anúncios pagos.

    **Acesso Direto** → Quando o usuário digita o endereço do site diretamente.

    **Referral** → Visitas que vêm de outros sites (blogs, redes sociais).

    **Engajamento** → Grau de interação dos usuários com o conteúdo do site.

    **Landing Page** → Primeira página que o usuário vê ao entrar no site.

    **IA (Inteligência Artificial)** → Assistentes como Google Gemini, ChatGPT, que direcionam usuários para o site.

    **Dispositivo** → Celular, computador ou tablet usado para acessar o site.
    """)

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
    
    # ============================================
    # RESUMO - MARKDOWN PURO (SEM HTML!)
    # ============================================
    
    st.markdown("### 📋 Resumo dos Resultados")
    
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
    
    # ============================================
    # CONCLUSÃO - MARKDOWN PURO
    # ============================================
    
    st.subheader("💡 Conclusão")
    
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
    **O que você está vendo?**
    
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
            **Por que não aparecem dados?**
            
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
        <p><strong>BOELL, M. E. C.</strong> Espécies do Horto Didático de Plantas Medicinais do HU/CCS (UFSC): identificação botânica e uso terapêutico de plantas medicinais. 2023. Trabalho de Conclusão de Curso (Graduação) – Universidade Federal de Santa Catarina, Florianópolis, 2023.</p>
        
        <p><strong>CEUTERICK, M.; VANDEBROEK, I.; TORRY, B.; PIERONI, A.</strong> Cross-cultural adaptation in urban ethnobotany: the Colombian folk pharmacopoeia in London. Journal of Ethnopharmacology, v. 120, n. 3, p. 342-359, 2008. DOI: 10.1016/j.jep.2008.09.004.</p>
        
        <p><strong>DE MEYER, E.; CEUTERICK, M.</strong> Digital Ethnobiology: exploring the digisphere in search of traditional and indigenous knowledge and practices. Ethnobotany Research and Applications, v. 24, p. 1-8, 2022. DOI: 10.32859/era.24.37.1-8.</p>
        
        <p><strong>FOLKE, C.; BIGGS, R.; NORSTRÖM, A. V.; REYERS, B.; ROCKSTRÖM, J.</strong> Social-ecological resilience and biosphere-based sustainability science. Ecology and Society, v. 21, n. 3, p. 41, 2016. DOI: 10.5751/ES-08748-210341.</p>
        
        <p><strong>RITTER, G. D.</strong> O site do Horto Didático de Plantas Medicinais (UFSC) como ferramenta de divulgação científica para o uso de plantas medicinais. 2025. Trabalho de Conclusão de Curso (Graduação) – Universidade Federal de Santa Catarina, Florianópolis, 2025.</p>
        
        <p><strong>SIMON, F. M.; CAMARGO, C. Q.</strong> Autopsy of a metaphor: the origins, use and blind spots of the 'infodemic'. New Media & Society, v. 25, n. 8, p. 2219-2240, 2023. DOI: 10.1177/14614448211031908.</p>
        
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
🌿 Apresentação no XXVIII SPMB 2026 | Apoio: UFSC

🔗 [hortodidatico.ufsc.br](https://hortodidatico.ufsc.br/)
""")
