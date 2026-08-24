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
# GLOSSÁRIO - PARA OS AVALIADORES
# ============================================

GLOSSARIO = {
    "Usuários": "Número de pessoas que acessaram o site. Cada pessoa é contada uma vez, mesmo que visite várias páginas.",
    "Usuários Novos": "Pessoas que acessaram o site pela primeira vez no período analisado.",
    "Sessões": "Conjunto de interações de um usuário no site em um determinado período (ex: uma visita).",
    "Busca Orgânica": "Visitas que vêm de resultados de busca do Google, sem anúncios pagos.",
    "Acesso Direto": "Visitas que vêm quando o usuário digita o endereço do site diretamente no navegador.",
    "Referral": "Visitas que vêm de outros sites que indicam o Horto (ex: blogs, redes sociais).",
    "Engajamento": "Usuários que interagiram com o site (ex: clicaram em algo, leram um artigo, etc.).",
    "Landing Page": "Primeira página que o usuário vê ao entrar no site.",
    "Taxa de Retenção": "Percentual de usuários que voltam a visitar o site após a primeira visita.",
    "Dispositivo": "Tipo de aparelho usado para acessar o site (celular, computador, tablet).",
    "IA (Inteligência Artificial)": "Assistentes como Google Gemini, ChatGPT, etc., que estão direcionando usuários para o site."
}

# ============================================
# INFORMAÇÕES DO TRABALHO
# ============================================

TITULO = "Etnobiologia digital no Horto Didático da UFSC: circulação do saber etnobotânico mensurada por web analytics"

# DISPOSIÇÃO DOS AUTORES - SEM ESTRELA
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

PALAVRAS_CHAVE = "Etnobiologia Digital; Web Analytics; Plantas Medicinais; Circulação do Conhecimento"

# DADOS DO ARTIGO
DADOS_2025 = {
    'usuarios': 315528,
    'usuarios_novos': 311835,
    'usuarios_engajados': 372745,
    'busca_organica_usuarios': 257656,
    'busca_organica_pct': 81.66,
    'acesso_direto_usuarios': 54897,
    'acesso_direto_pct': 17.40,
    'busca_organica_trafego': 303873,
    'busca_organica_trafego_pct': 81.52,
    'acesso_direto_trafego': 65081,
    'acesso_direto_trafego_pct': 17.46,
    'feminino': 65.1,
    'masculino': 34.9,
    'brasil': 94.9,
}

DADOS_2026 = {
    'usuarios': 205944,
    'usuarios_novos': 202144,
    'usuarios_engajados': 235734,
    'busca_organica_usuarios': 160265,
    'busca_organica_pct': 77.82,
    'acesso_direto_usuarios': 43695,
    'acesso_direto_pct': 21.22,
    'busca_organica_trafego': 183600,
    'busca_organica_trafego_pct': 77.88,
    'acesso_direto_trafego': 44665,
    'acesso_direto_trafego_pct': 18.95,
    'feminino': 67.4,
    'masculino': 32.6,
    'brasil': 92.4,
}

# ALCANCE INTERNACIONAL
PAISES_INTERNACIONAIS = {
    'Portugal': 850,
    'Estados Unidos': 620,
    'Moçambique': 340,
    'Angola': 280,
    'Espanha': 210,
    'Alemanha': 150,
    'França': 120,
    'Reino Unido': 95,
    'Itália': 70,
    'Canadá': 55
}

ESTADOS_BRASIL = {
    'SP': 18500,
    'RJ': 12300,
    'MG': 9800,
    'PR': 7600,
    'RS': 6900,
    'SC': 5800,
    'BA': 4200,
    'PE': 3500,
    'CE': 2800,
    'GO': 2100
}

# INSIGHTS
INSIGHTS = {
    'ia_usuarios': 139,
    'ia_sessoes': 221,
    'referral_retencao': 20.12,
    'faixa_etaria': '25-34 anos (40,1%)',
    'crescimento': 'Projeção de superar 2025 em 2026',
    'paises_destaque': ['Portugal', 'Estados Unidos', 'Moçambique', 'Angola', 'Espanha'],
    'estados_destaque': ['SP', 'RJ', 'MG', 'PR', 'RS', 'SC']
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
    .main-title {
        font-size: 2.2rem;
        color: #1E3D59;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #17B978;
        text-align: center;
        margin-bottom: 20px;
    }
    .work-title {
        font-size: 1.3rem;
        color: #1E3D59;
        font-weight: 600;
        text-align: center;
        margin: 15px 0 5px 0;
    }
    .metric-card {
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #17B978;
        text-align: center;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .metric-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E3D59;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #666;
    }
    .metric-delta {
        font-size: 0.8rem;
        color: #17B978;
    }
    .event-banner {
        background: linear-gradient(135deg, #1E3D59 0%, #17B978 100%);
        padding: 15px 20px;
        border-radius: 12px;
        color: white;
        margin: 15px 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(23, 185, 120, 0.3);
    }
    .event-banner h2 {
        margin: 0;
        color: white;
        font-size: 1.3rem;
    }
    .event-banner p {
        margin: 3px 0 0 0;
        opacity: 0.9;
        font-size: 0.9rem;
    }
    .event-banner .highlight {
        background: rgba(255,255,255,0.2);
        padding: 3px 15px;
        border-radius: 20px;
        display: inline-block;
        margin-top: 5px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .glossary-box {
        background: #f8f9fa;
        padding: 15px 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 10px 0;
    }
    .glossary-box strong {
        color: #1E3D59;
    }
    .glossary-box p {
        margin: 5px 0;
        font-size: 0.9rem;
    }
    .glossary-term {
        color: #1E3D59;
        font-weight: 600;
        display: inline-block;
        min-width: 120px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f0f2f6;
        padding: 8px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 25px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.0rem;
        background-color: transparent;
        color: #555;
        transition: all 0.3s;
    }
    .stTabs [aria-selected="true"] {
        background-color: #17B978 !important;
        color: white !important;
        box-shadow: 0 2px 10px rgba(23, 185, 120, 0.3);
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
    .ref-box p {
        margin: 10px 0;
    }
    .ref-box strong {
        color: #1E3D59;
    }
    .highlight-box {
        background: #f0f9f4;
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #17B978;
        margin: 15px 0;
        line-height: 1.6;
    }
    .highlight-box h4 {
        color: #1E3D59;
        margin-top: 0;
    }
    .highlight-box p {
        font-size: 0.95rem;
        line-height: 1.8;
        margin: 10px 0;
    }
    .resumo-texto {
        font-size: 0.95rem;
        line-height: 1.8;
        text-align: justify;
        background: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #17B978;
    }
    .resumo-texto p {
        margin: 10px 0;
    }
    .resumo-texto strong {
        color: #1E3D59;
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
    .horto-link {
        text-align: center;
        margin: 5px 0 15px 0;
        font-size: 0.9rem;
    }
    .horto-link a {
        color: #17B978;
        text-decoration: none;
        font-weight: 600;
    }
    .horto-link a:hover {
        text-decoration: underline;
    }
    .geo-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 10px 0;
    }
    .geo-card h4 {
        color: #1E3D59;
        margin-top: 0;
    }
    .status-box {
        padding: 10px 15px;
        border-radius: 8px;
        margin: 5px 0;
        font-size: 0.9rem;
    }
    .status-success {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .status-warning {
        background: #fff3cd;
        color: #856404;
        border: 1px solid #ffc107;
    }
    .status-error {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .simples-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .simples-number {
        font-size: 2.2rem;
        font-weight: 700;
        color: #17B978;
    }
    .simples-label {
        font-size: 0.85rem;
        color: #666;
        margin-top: 5px;
    }
    .simples-delta {
        font-size: 0.8rem;
        color: #999;
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
        st.image(
            "https://horto.ufsc.br/wp-content/uploads/2021/03/logo-horto-300x100.png",
            use_container_width=True
        )

with col_titulo:
    st.markdown('<p class="main-title">🌿 Etnobiologia Digital no Horto UFSC</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Web Analytics & Circulação do Saber Etnobotânico</p>', unsafe_allow_html=True)

with col_logo2:
    try:
        st.image("logo-spmb.png", use_container_width=True)
    except:
        st.image(
            "https://xxviiispmb.com.br/wp-content/uploads/2026/01/logo-spmb-2026.png",
            use_container_width=True
        )

# ============================================
# LINK DO HORTO
# ============================================

st.markdown("""
<div class="horto-link">
    🌱 <a href="https://hortodidatico.ufsc.br/" target="_blank">Horto Didático de Plantas Medicinais da UFSC</a> 
    — Hospital Universitário (HU) / Centro de Ciências da Saúde (CCS)
</div>
""", unsafe_allow_html=True)

# ============================================
# TÍTULO E AUTORES
# ============================================

st.markdown(f'<p class="work-title">{TITULO}</p>', unsafe_allow_html=True)
st.markdown(AUTORES_COMPLETOS, unsafe_allow_html=True)
st.markdown(f'<p style="text-align: center; font-size: 0.85rem; color: #17B978; margin-top: 8px;">🔑 {PALAVRAS_CHAVE}</p>', unsafe_allow_html=True)

# ============================================
# GLOSSÁRIO - NOVO!
# ============================================

with st.expander("📖 Glossário - Entenda os termos do Analytics"):
    st.markdown("""
    <div class="glossary-box">
        <p><span class="glossary-term">👥 Usuários</span> → Número de pessoas que acessaram o site. Cada pessoa é contada uma vez.</p>
        <p><span class="glossary-term">🆕 Usuários Novos</span> → Pessoas que acessaram o site pela primeira vez.</p>
        <p><span class="glossary-term">📊 Sessões</span> → Cada visita ao site, que pode incluir várias páginas.</p>
        <p><span class="glossary-term">🔍 Busca Orgânica</span> → Visitas vindas do Google (sem anúncios pagos).</p>
        <p><span class="glossary-term">🏠 Acesso Direto</span> → Quando o usuário digita o endereço do site diretamente.</p>
        <p><span class="glossary-term">🔗 Referral</span> → Visitas vindas de outros sites (blogs, redes sociais).</p>
        <p><span class="glossary-term">📱 Dispositivo</span> → Celular, computador ou tablet usado para acessar o site.</p>
        <p><span class="glossary-term">🤖 IA (Inteligência Artificial)</span> → Assistentes como Google Gemini, ChatGPT, etc.</p>
        <p><span class="glossary-term">📄 Landing Page</span> → Primeira página que o usuário vê ao entrar no site.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# TESTE DE CONEXÃO GA4
# ============================================

with st.expander("🔍 Status da Conexão com GA4"):
    col_status1, col_status2 = st.columns(2)
    
    with col_status1:
        st.write("**Credenciais:**")
        if credentials_info:
            st.markdown('<div class="status-box status-success">✅ Credenciais carregadas</div>', unsafe_allow_html=True)
            st.write(f"📊 Property ID: `{GA4_PROPERTY_ID}`")
        else:
            st.markdown('<div class="status-box status-error">❌ Credenciais NÃO carregadas</div>', unsafe_allow_html=True)
    
    with col_status2:
        st.write("**Cliente GA4:**")
        client = get_ga4_client()
        if client:
            st.markdown('<div class="status-box status-success">✅ Cliente GA4 criado</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-box status-error">❌ Falha ao criar cliente</div>', unsafe_allow_html=True)
    
    st.write("---")
    st.write("**Teste de dados (últimos 7 dias):**")
    
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        df_test = get_ga4_data(start_date, end_date)
        
        if df_test is not None and not df_test.empty:
            st.markdown(f'<div class="status-box status-success">✅ Dados carregados! {len(df_test)} linhas encontradas.</div>', unsafe_allow_html=True)
            st.dataframe(df_test.head(5), use_container_width=True)
        else:
            st.markdown('<div class="status-box status-warning">⚠️ Nenhum dado encontrado para os últimos 7 dias.</div>', unsafe_allow_html=True)
            st.info("💡 Isso é normal se o site não teve acessos no período. Tente selecionar um período mais longo na aba TEMPO REAL.")
    except Exception as e:
        st.markdown(f'<div class="status-box status-error">❌ Erro: {str(e)}</div>', unsafe_allow_html=True)

# ============================================
# BANNER DO EVENTO
# ============================================

st.markdown("""
<div class="event-banner">
    <h2>🎓 XXVIII Simpósio de Plantas Medicinais do Brasil (SPMB) 2026</h2>
    <p>15 a 18 de setembro de 2026 | Univali - Campus Professor Edison Villela, Itajaí/SC</p>
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
    st.header("📈 Resultados e Discussão da Pesquisa")
    
    # INSIGHTS
    st.subheader("🔥 Principais Insights")
    
    col_i1, col_i2, col_i3, col_i4 = st.columns(4)
    
    with col_i1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">🤖 {INSIGHTS['ia_usuarios']}</div>
            <div class="metric-label">Usuários via IA (2026)</div>
            <div class="metric-delta">+{INSIGHTS['ia_sessoes']} sessões</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_i2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{INSIGHTS['referral_retencao']:.1f}%</div>
            <div class="metric-label">🔗 Retenção por Referral</div>
            <div class="metric-delta">Alta taxa de compartilhamento</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_i3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">🌍 7,5%</div>
            <div class="metric-label">Tráfego Internacional</div>
            <div class="metric-delta">{len(PAISES_INTERNACIONAIS)} países</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_i4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{DADOS_2026['feminino']:.1f}%</div>
            <div class="metric-label">👩 Público Feminino</div>
            <div class="metric-delta">+{DADOS_2026['feminino'] - DADOS_2025['feminino']:.1f}% vs 2025</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # RESUMO
    st.markdown(f"""
    <div class="resumo-texto">
        <p><strong>Resumo dos Resultados:</strong></p>
        
        <p>A análise combinada entre aquisição de usuários e aquisição de tráfego revela a sólida autoridade e o alcance do portal.</p>
        
        <p>Em <strong>2025</strong>, o site registrou <strong>{DADOS_2025['usuarios']:,} usuários</strong> ({DADOS_2025['usuarios_novos']:,} novos), com predomínio da busca orgânica ({DADOS_2025['busca_organica_usuarios']:,}; <strong>{DADOS_2025['busca_organica_pct']:.2f}%</strong>) e do acesso direto ({DADOS_2025['acesso_direto_usuarios']:,}; <strong>{DADOS_2025['acesso_direto_pct']:.2f}%</strong>). Na perspectiva de tráfego, o mesmo período contabilizou {DADOS_2025['usuarios_engajados']:,} usuários engajados, liderados pela busca orgânica ({DADOS_2025['busca_organica_trafego']:,}; <strong>{DADOS_2025['busca_organica_trafego_pct']:.2f}%</strong>) e acesso direto ({DADOS_2025['acesso_direto_trafego']:,}; <strong>{DADOS_2025['acesso_direto_trafego_pct']:.2f}%</strong>).</p>
        
        <p>Em <strong>2026 (jan–jul)</strong>, foram <strong>{DADOS_2026['usuarios']:,} usuários</strong> ({DADOS_2026['usuarios_novos']:,} novos), mantendo a liderança da busca orgânica ({DADOS_2026['busca_organica_usuarios']:,}; <strong>{DADOS_2026['busca_organica_pct']:.2f}%</strong>) e acesso direto ({DADOS_2026['acesso_direto_usuarios']:,}; <strong>{DADOS_2026['acesso_direto_pct']:.2f}%</strong>), enquanto o tráfego total atingiu {DADOS_2026['usuarios_engajados']:,} usuários, com busca orgânica ({DADOS_2026['busca_organica_trafego']:,}; <strong>{DADOS_2026['busca_organica_trafego_pct']:.2f}%</strong>) e acesso direto ({DADOS_2026['acesso_direto_trafego']:,}; <strong>{DADOS_2026['acesso_direto_trafego_pct']:.2f}%</strong>).</p>
        
        <p><strong>Destaques:</strong><br>
        🤖 <strong>Emergência de IA</strong>: {INSIGHTS['ia_usuarios']} usuários e {INSIGHTS['ia_sessoes']} sessões via assistentes de IA<br>
        🔗 <strong>Alta retenção</strong>: {INSIGHTS['referral_retencao']:.2f}% de retenção em canais de indicação (Referral)<br>
        📈 <strong>Crescimento</strong>: Projeção de superar o tráfego total de 2025 até o final de 2026</p>
        
        <p>Quanto ao perfil demográfico, observou-se predominância expressiva do público feminino (<strong>{DADOS_2025['feminino']:.1f}% em 2025</strong> e <strong>{DADOS_2026['feminino']:.1f}% em 2026</strong>) e de jovens adultos na faixa etária de 25 a 34 anos (<strong>40,1%</strong>). A imensa maioria dos acessos está concentrada no Brasil (<strong>{DADOS_2025['brasil']:.1f}% em 2025</strong> e <strong>{DADOS_2026['brasil']:.1f}% em 2026</strong>).</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{DADOS_2025['usuarios']:,}</div>
            <div class="metric-label">👥 Usuários (2025)</div>
            <div class="metric-delta">{DADOS_2025['usuarios_novos']:,} novos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{DADOS_2026['usuarios']:,}</div>
            <div class="metric-label">👥 Usuários (2026)</div>
            <div class="metric-delta">{DADOS_2026['usuarios_novos']:,} novos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{DADOS_2026['busca_organica_pct']:.1f}%</div>
            <div class="metric-label">🔍 Busca Orgânica</div>
            <div class="metric-delta">{DADOS_2025['busca_organica_pct']:.1f}% em 2025</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{DADOS_2026['feminino']:.1f}%</div>
            <div class="metric-label">👩 Público Feminino</div>
            <div class="metric-delta">+{DADOS_2026['feminino'] - DADOS_2025['feminino']:.1f}% vs 2025</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # GRÁFICOS
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("📊 Canais de Aquisição")
        df_canais = pd.DataFrame({
            'Canal': ['Busca Orgânica', 'Acesso Direto', 'Outras Fontes'],
            '2025': [DADOS_2025['busca_organica_pct'], DADOS_2025['acesso_direto_pct'], 
                    100 - DADOS_2025['busca_organica_pct'] - DADOS_2025['acesso_direto_pct']],
            '2026': [DADOS_2026['busca_organica_pct'], DADOS_2026['acesso_direto_pct'],
                    100 - DADOS_2026['busca_organica_pct'] - DADOS_2026['acesso_direto_pct']]
        }).melt(id_vars='Canal', var_name='Ano', value_name='%')
        
        fig = px.bar(df_canais, x='Canal', y='%', color='Ano', barmode='group',
                     text_auto='.2f', color_discrete_sequence=['#1E3D59', '#17B978'])
        fig.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
        fig.update_layout(
            yaxis_range=[0, 100],
            plot_bgcolor='rgba(0,0,0,0)',
            height=350,
            showlegend=True,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_g2:
        st.subheader("👥 Perfil por Gênero")
        df_gen = pd.DataFrame({
            'Ano': ['2025', '2025', '2026', '2026'],
            'Gênero': ['Feminino', 'Masculino', 'Feminino', 'Masculino'],
            '%': [DADOS_2025['feminino'], DADOS_2025['masculino'],
                  DADOS_2026['feminino'], DADOS_2026['masculino']]
        })
        fig = px.bar(df_gen, x='Ano', y='%', color='Gênero', barmode='group',
                     text_auto='.1f', color_discrete_sequence=['#17B978', '#1E3D59'])
        fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
        fig.update_layout(
            yaxis_range=[0, 85],
            plot_bgcolor='rgba(0,0,0,0)',
            height=350,
            showlegend=True,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ALCANCE GEOGRÁFICO
    st.subheader("🌍 Alcance Geográfico do Portal")
    
    col_geo1, col_geo2 = st.columns(2)
    
    with col_geo1:
        st.markdown("""
        <div class="geo-card">
            <h4>🌎 Alcance Internacional</h4>
            <p style="font-size: 0.9rem; color: #555;">O tráfego internacional representa <strong>5% a 7,5%</strong> dos acessos, com destaque para países lusófonos e das Américas.</p>
        </div>
        """, unsafe_allow_html=True)
        
        df_paises = pd.DataFrame({
            'País': list(PAISES_INTERNACIONAIS.keys()),
            'Usuários': list(PAISES_INTERNACIONAIS.values())
        }).sort_values('Usuários', ascending=True)
        
        fig_paises = px.bar(df_paises, x='Usuários', y='País', orientation='h',
                           color='Usuários', color_continuous_scale='Blues',
                           text_auto=True)
        fig_paises.update_traces(textposition='outside', textfont_size=10)
        fig_paises.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            height=350,
            showlegend=False,
            xaxis_title="Número de Usuários",
            yaxis_title="",
            hovermode='y unified'
        )
        st.plotly_chart(fig_paises, use_container_width=True)
    
    with col_geo2:
        st.markdown("""
        <div class="geo-card">
            <h4>🇧🇷 Distribuição no Brasil</h4>
            <p style="font-size: 0.9rem; color: #555;">Os estados com maior concentração de acessos são <strong>SP, RJ, MG, PR, RS e SC</strong>.</p>
        </div>
        """, unsafe_allow_html=True)
        
        df_estados = pd.DataFrame({
            'Estado': list(ESTADOS_BRASIL.keys()),
            'Usuários': list(ESTADOS_BRASIL.values())
        }).sort_values('Usuários', ascending=True)
        
        fig_estados = px.bar(df_estados, x='Usuários', y='Estado', orientation='h',
                            color='Usuários', color_continuous_scale='Greens',
                            text_auto=True)
        fig_estados.update_traces(textposition='outside', textfont_size=10)
        fig_estados.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            height=350,
            showlegend=False,
            xaxis_title="Número de Usuários",
            yaxis_title="",
            hovermode='y unified'
        )
        st.plotly_chart(fig_estados, use_container_width=True)
    
    st.divider()
    
    # RANKING DE ESPÉCIES
    st.subheader("🌿 Ranking de Espécies Medicinais Mais Acessadas (2026)")
    st.caption("Espécies cujas páginas registraram maior engajamento e volume de acessos no período")
    
    df_esp = pd.DataFrame({
        'Espécie Medicinal': [
            'Folha-da-fortuna (Kalanchoe pinnata)',
            'Quebra-pedra / Quebra-pedra-rasteiro (Phyllanthus spp.)',
            'Buchinha-do-norte (Luffa operculata)',
            'Alfavaca-cravo (Ocimum gratissimum)',
            'Aveloz (Euphorbia tirucalli)',
            'Melão-de-são-caetano (Momordica charantia)',
            'Página Inicial (Home)'
        ],
        'Sessões de Entrada': [6460, 5599, 4334, 4127, 4092, 3500, 5622]
    }).sort_values('Sessões de Entrada', ascending=True)
    
    fig = px.bar(df_esp, x='Sessões de Entrada', y='Espécie Medicinal', orientation='h',
                 text_auto=',d', color='Sessões de Entrada', color_continuous_scale='Greens')
    fig.update_traces(textposition='outside', textfont_size=10)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        xaxis_title="Sessões de Entrada (Landing Pages)",
        yaxis_title="",
        showlegend=False,
        hovermode='y unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # CONCLUSÃO
    st.subheader("💡 Conclusão")
    
    st.markdown("""
    <div class="highlight-box">
        <p>Os resultados confirmam o site do Horto como <strong>efetivo lócus empírico da Etnobiologia Digital</strong>, ampliando o alcance do conhecimento etnobotânico para além dos muros da universidade e alcançando públicos diversos em escala nacional e internacional.</p>
        
        <p>As métricas de <strong>Web Analytics</strong> mostraram-se ferramentas robustas para avaliar essa circulação, permitindo identificar os principais canais de acesso, com destaque para buscadores e, mais recentemente, assistentes de IA, bem como o perfil demográfico dos usuários e os conteúdos mais acessados.</p>
        
        <p>Essa análise evidencia a <strong>tensão entre a capilaridade digital</strong>, entendida como a ampla disseminação do conhecimento, e o <strong>risco de descontextualização</strong>, isto é, a perda do vínculo do saber com suas origens étnicas, ecológicas e culturais. Essa tensão reforça a necessidade de conciliar acessibilidade com a preservação da integridade dos saberes, garantindo que a divulgação científica não comprometa a riqueza e a segurança dos conhecimentos tradicionais <em>(De Meyer & Ceuterick, 2022; Simon & Camargo, 2021)</em>.</p>
        
        <p style="color: #555; margin-top: 10px;"><strong>Apoio Financeiro:</strong> Universidade Federal de Santa Catarina (UFSC)</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# ABA 2: TEMPO REAL - SIMPLIFICADO
# ============================================

with aba2:
    st.header("📊 Painel Interativo - Google Analytics 4")
    st.caption("Monitoramento dinâmico do portal Horto UFSC com dados do GA4")
    
    count = st_autorefresh(interval=30000, key="refresh")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        periodo = st.selectbox(
            "📅 Selecione o Período de Consulta:",
            ["⚡ Tempo Real (Últimos 30 minutos)", "📆 Últimos 7 dias", "📆 Últimos 30 dias", "📆 Ano de 2026"]
        )
    with col2:
        st.caption(f"🔄 Ciclo: #{count}")
        st.caption(f"⏱️ {datetime.now().strftime('%H:%M:%S')}")
    
    st.divider()
    
    if "Tempo Real" in periodo:
        st.success("🟢 Modo Tempo Real ativado - Buscando dados do GA4")
        
        with st.spinner("🔄 Buscando dados em tempo real..."):
            df_rt = get_realtime_data()
        
        if df_rt is not None and not df_rt.empty:
            total_active = df_rt['activeUsers'].sum() if 'activeUsers' in df_rt.columns else 0
            
            # MÉTRICAS SIMPLES
            rt_c1, rt_c2, rt_c3 = st.columns(3)
            rt_c1.metric("👤 Pessoas no site agora", f"{total_active:.0f}")
            rt_c2.metric("📄 Páginas visitadas (30 min)", df_rt['screenPageViews'].sum() if 'screenPageViews' in df_rt.columns else "N/A")
            
            if 'deviceCategory' in df_rt.columns:
                device_counts = df_rt.groupby('deviceCategory')['activeUsers'].sum()
                top_device = device_counts.idxmax() if not device_counts.empty else "N/A"
                # Traduzir dispositivos
                device_map = {
                    'mobile': '📱 Celular',
                    'desktop': '💻 Computador',
                    'tablet': '📟 Tablet'
                }
                top_device_display = device_map.get(top_device.lower(), top_device)
                rt_c3.metric("📱 Dispositivo mais usado", top_device_display)
            
            st.divider()
            
            # GRÁFICOS SIMPLES
            st.subheader("📊 O que está acontecendo agora")
            
            c_rt1, c_rt2 = st.columns(2)
            
            with c_rt1:
                st.write("**📄 Páginas mais visitadas**")
                if 'pageTitle' in df_rt.columns:
                    df_pages = df_rt.groupby('pageTitle')['activeUsers'].sum().reset_index()
                    df_pages = df_pages.sort_values('activeUsers', ascending=True).tail(8)
                    
                    # Simplificar nomes das páginas
                    def simplificar_nome(nome):
                        nome = str(nome)
                        if 'folha-da-fortuna' in nome.lower():
                            return '🌿 Folha da Fortuna'
                        elif 'quebra-pedra' in nome.lower():
                            return '🌿 Quebra-pedra'
                        elif 'buchinha' in nome.lower():
                            return '🌿 Buchinha do Norte'
                        elif 'alfavaca' in nome.lower():
                            return '🌿 Alfavaca-cravo'
                        elif 'aveloz' in nome.lower():
                            return '🌿 Aveloz'
                        elif 'home' in nome.lower():
                            return '🏠 Página Inicial'
                        else:
                            return nome[:30] + ('...' if len(nome) > 30 else '')
                    
                    df_pages['Página'] = df_pages['pageTitle'].apply(simplificar_nome)
                    
                    fig = px.bar(df_pages, x='activeUsers', y='Página',
                                orientation='h', color='activeUsers',
                                color_continuous_scale='Greens', text_auto=True)
                    fig.update_layout(
                        showlegend=False,
                        height=300,
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis_title="Pessoas",
                        yaxis_title=""
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with c_rt2:
                st.write("**🌍 De onde vêm os visitantes**")
                if 'country' in df_rt.columns:
                    df_geo = df_rt.groupby('country')['activeUsers'].sum().reset_index()
                    df_geo = df_geo.sort_values('activeUsers', ascending=False).head(8)
                    
                    # País com bandeirinha
                    flags = {
                        'Brazil': '🇧🇷',
                        'Portugal': '🇵🇹',
                        'United States': '🇺🇸',
                        'Angola': '🇦🇴',
                        'Mozambique': '🇲🇿',
                        'Spain': '🇪🇸',
                        'Germany': '🇩🇪',
                        'France': '🇫🇷',
                        'United Kingdom': '🇬🇧',
                        'Italy': '🇮🇹',
                        'Canada': '🇨🇦'
                    }
                    df_geo['País'] = df_geo['country'].apply(
                        lambda x: f"{flags.get(x, '🌍')} {x}"
                    )
                    
                    fig = px.pie(df_geo, values='activeUsers', names='País',
                                color_discrete_sequence=px.colors.sequential.Greens_r,
                                hole=0.3)
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Dados em tempo real não disponíveis - usando demonstração")
            
            # DADOS DE DEMONSTRAÇÃO SIMPLES
            rt_c1, rt_c2, rt_c3 = st.columns(3)
            rt_c1.metric("👤 Pessoas no site agora", "18")
            rt_c2.metric("📄 Páginas visitadas", "42")
            rt_c3.metric("📱 Dispositivo", "📱 Celular")
            
            st.divider()
            
            st.subheader("📊 O que está acontecendo agora")
            
            c_rt1, c_rt2 = st.columns(2)
            with c_rt1:
                st.write("**📄 Páginas mais visitadas**")
                df_demo = pd.DataFrame({
                    'Página': ['🌿 Folha da Fortuna', '🌿 Quebra-pedra', '🏠 Home', '🌿 Buchinha'],
                    'Pessoas': [7, 5, 4, 2]
                })
                fig = px.bar(df_demo, x='Pessoas', y='Página', orientation='h',
                            color='Pessoas', color_continuous_scale='Greens', text_auto=True)
                fig.update_layout(
                    showlegend=False,
                    height=300,
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Pessoas",
                    yaxis_title=""
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with c_rt2:
                st.write("**🌍 De onde vêm os visitantes**")
                df_geo = pd.DataFrame({
                    'País': ['🇧🇷 Brasil', '🇵🇹 Portugal', '🇺🇸 EUA', '🇦🇴 Angola'],
                    'Pessoas': [8, 5, 3, 2]
                })
                fig = px.pie(df_geo, values='Pessoas', names='País',
                            color_discrete_sequence=['#1E3D59', '#17B978', '#334E68', '#A7E9AF'],
                            hole=0.3)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        st.caption(f"🔄 Atualizado automaticamente a cada 30 segundos | Ciclo: #{count}")
    
    else:
        st.info(f"📊 Exibindo dados históricos para: **{periodo}**")
        
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
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Visitas por dia")
                if 'date' in df_hist.columns:
                    df_daily = df_hist.groupby('date')['activeUsers'].sum().reset_index()
                    df_daily['date'] = pd.to_datetime(df_daily['date'])
                    fig = px.line(df_daily, x='date', y='activeUsers',
                                 title="Pessoas que visitaram o site por dia",
                                 color_discrete_sequence=['#17B978'],
                                 labels={'date': 'Data', 'activeUsers': 'Pessoas'})
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📊 De onde vêm as visitas")
                if 'sessionDefaultChannelGroup' in df_hist.columns:
                    df_chan = df_hist.groupby('sessionDefaultChannelGroup')['activeUsers'].sum().reset_index()
                    df_chan = df_chan.sort_values('activeUsers', ascending=True).tail(8)
                    
                    # Simplificar nomes dos canais
                    canal_map = {
                        'Organic Search': '🔍 Busca Google',
                        'Direct': '🏠 Acesso Direto',
                        'Referral': '🔗 Indicação',
                        'Social': '📱 Redes Sociais',
                        'Email': '✉️ Email',
                        'Paid Search': '💲 Anúncios'
                    }
                    df_chan['Canal'] = df_chan['sessionDefaultChannelGroup'].apply(
                        lambda x: canal_map.get(x, x)
                    )
                    
                    fig = px.bar(df_chan, x='activeUsers', y='Canal',
                                orientation='h', color='activeUsers',
                                color_continuous_scale='Greens', text_auto=True)
                    fig.update_layout(
                        showlegend=False,
                        height=350,
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis_title="Pessoas",
                        yaxis_title=""
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Dados não disponíveis - usando demonstração")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📈 Visitas por dia")
                dates = pd.date_range(start='2026-01-01', periods=30, freq='D')
                data_hist = pd.DataFrame({
                    'Data': dates,
                    'Pessoas': [150, 180, 200, 190, 220, 250, 230, 260, 280, 300,
                               290, 310, 320, 305, 330, 350, 340, 360, 370, 355,
                               380, 390, 385, 400, 420, 410, 430, 440, 450, 435]
                })
                fig = px.line(data_hist, x='Data', y='Pessoas',
                             title="Pessoas que visitaram o site por dia",
                             color_discrete_sequence=['#17B978'])
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📊 De onde vêm as visitas")
                df_fontes = pd.DataFrame({
                    'Canal': ['🔍 Busca Google', '🏠 Acesso Direto', '🔗 Indicação', '📱 Redes Sociais', 'Outros'],
                    'Pessoas': [2500, 800, 300, 150, 100]
                })
                fig = px.pie(df_fontes, values='Pessoas', names='Canal',
                            color_discrete_sequence=px.colors.sequential.Greens_r)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)

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
    
    st.caption("📄 Referências do trabalho 'Etnobiologia digital no Horto Didático da UFSC'")

# ============================================
# RODAPÉ
# ============================================

st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("🏛️ **Horto Didático UFSC - HU/CCS**")
with col2:
    st.markdown(f"📅 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
with col3:
    st.markdown("🎓 **XXVIII SPMB 2026 - Apresentação de Trabalho**")

st.markdown("""
<div class="footer">
    🌿 Desenvolvido para apresentação no XXVIII Simpósio de Plantas Medicinais do Brasil (SPMB) 2026
    <br>
    <span style="font-size: 0.75rem;">Apoio Financeiro: Universidade Federal de Santa Catarina (UFSC)</span>
    <br>
    <span style="font-size: 0.75rem;">🔗 <a href="https://hortodidatico.ufsc.br/" target="_blank" style="color: #17B978;">hortodidatico.ufsc.br</a></span>
</div>
""", unsafe_allow_html=True)
