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
# INFORMAÇÕES DO TRABALHO
# ============================================

TITULO = "Etnobiologia digital no Horto Didático da UFSC: circulação do saber etnobotânico mensurada por web analytics"

AUTORES_COMPLETOS = """
**Michael A. Lopes**¹ (Apresentador)  
**Maique W. Biavatti**²  
**Gabriela D. Ritter**³  
**Laura S. Tardim**⁴  

¹UFSC - Graduando em Química Tecnológica  
²UFSC - Depto. Ciências Farmacêuticas  
³Farmacêutica  
⁴UFSC - Graduanda em Farmácia
"""

PALAVRAS_CHAVE = "Etnobiologia Digital; Web Analytics; Plantas Medicinais; Circulação do Conhecimento"

# Dados do artigo
DADOS_2025 = {
    'usuarios': 315528,
    'usuarios_novos': 311835,
    'feminino': 65.1,
    'masculino': 34.9,
    'brasil': 94.9,
    'busca_organica': 81.66,
    'acesso_direto': 17.40
}

DADOS_2026 = {
    'usuarios': 205944,
    'usuarios_novos': 202144,
    'feminino': 67.4,
    'masculino': 32.6,
    'brasil': 92.4,
    'busca_organica': 77.82,
    'acesso_direto': 21.22
}

# ============================================
# CARREGAR CREDENCIAIS GA4
# ============================================

GA4_PROPERTY_ID = "750410485227"

if os.path.exists('ga4-credentials.json'):
    try:
        with open('ga4-credentials.json', 'r') as f:
            credentials_info = json.load(f)
    except:
        credentials_info = None
else:
    try:
        credentials_json = st.secrets["google_analytics"]["credentials_json"]
        if isinstance(credentials_json, str):
            credentials_info = json.loads(credentials_json)
        else:
            credentials_info = credentials_json
    except:
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
    /* Cabeçalhos */
    .main-title {
        font-size: 2.0rem;
        color: #1E3D59;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 1.0rem;
        color: #17B978;
        text-align: center;
        margin-bottom: 20px;
    }
    .work-title {
        font-size: 1.2rem;
        color: #1E3D59;
        font-weight: 600;
        text-align: center;
        margin: 10px 0;
    }
    .authors {
        font-size: 0.95rem;
        color: #555;
        text-align: center;
        line-height: 1.6;
    }
    
    /* Cards */
    .metric-card {
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #17B978;
        text-align: center;
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
    
    /* Banner */
    .event-banner {
        background: linear-gradient(135deg, #1E3D59 0%, #17B978 100%);
        padding: 15px 20px;
        border-radius: 10px;
        color: white;
        margin: 15px 0;
        text-align: center;
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
    
    /* Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f0f2f6;
        padding: 8px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 25px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.0rem;
        background-color: transparent;
        color: #555;
    }
    .stTabs [aria-selected="true"] {
        background-color: #17B978 !important;
        color: white !important;
    }
    
    /* Referências */
    .ref-box {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #1E3D59;
        margin: 15px 0;
        font-size: 0.85rem;
        max-height: 500px;
        overflow-y: auto;
        line-height: 1.6;
    }
    .ref-box p {
        margin: 8px 0;
    }
    .ref-box strong {
        color: #1E3D59;
    }
    
    /* Box de destaque */
    .highlight-box {
        background: #f0f9f4;
        padding: 15px 20px;
        border-radius: 10px;
        border-left: 4px solid #17B978;
        margin: 10px 0;
    }
    .highlight-box h4 {
        color: #1E3D59;
        margin-top: 0;
    }
    
    /* Rodapé */
    .footer {
        text-align: center;
        padding: 15px 0;
        margin-top: 20px;
        border-top: 2px solid #e0e0e0;
        font-size: 0.8rem;
        color: #999;
    }
    
    /* Logo container */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER COM LOGOS
# ============================================

col_logo1, col_titulo, col_logo2 = st.columns([1, 3, 1])

with col_logo1:
    st.image(
        "https://horto.ufsc.br/wp-content/uploads/2021/03/logo-horto-300x100.png",
        use_container_width=True
    )

with col_titulo:
    st.markdown('<p class="main-title">🌿 Etnobiologia Digital no Horto UFSC</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Web Analytics & Circulação do Saber Etnobotânico</p>', unsafe_allow_html=True)

with col_logo2:
    st.image(
        "https://xxviiispmb.com.br/wp-content/uploads/2026/01/logo-spmb-2026.png",
        use_container_width=True
    )

# ============================================
# TÍTULO DO TRABALHO E AUTORES
# ============================================

st.markdown(f"""
<div style="text-align: center; margin: 10px 0;">
    <p class="work-title">{TITULO}</p>
    <div class="authors">{AUTORES_COMPLETOS}</div>
    <p style="font-size: 0.85rem; color: #17B978; margin-top: 5px;">🔑 {PALAVRAS_CHAVE}</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# BANNER DO EVENTO
# ============================================

st.markdown("""
<div class="event-banner">
    <h2>🎓 XXVIII SPMB 2026</h2>
    <p>15 a 18 de setembro | Univali - Itajaí/SC | Tema: Plantas medicinais como fonte de novos agentes medicinais</p>
    <div class="highlight">🌟 Apresentação: Michael A. Lopes</div>
</div>
""", unsafe_allow_html=True)

# ============================================
# ABAS
# ============================================

aba1, aba2, aba3 = st.tabs([
    "📊 RESULTADOS",
    "📈 TEMPO REAL",
    "📚 REFERÊNCIAS"
])

# ============================================
# ABA 1: RESULTADOS
# ============================================

with aba1:
    st.header("📊 Resultados da Pesquisa")
    
    # Resumo
    st.markdown(f"""
    <div class="highlight-box">
        <p style="margin: 0; font-size: 0.95rem;">
        <b>2025:</b> {DADOS_2025['usuarios']:,} usuários ({DADOS_2025['usuarios_novos']:,} novos) · 
        Busca Orgânica: {DADOS_2025['busca_organica']:.1f}% · 
        Público Feminino: {DADOS_2025['feminino']:.1f}%
        </p>
        <p style="margin: 5px 0 0 0; font-size: 0.95rem;">
        <b>2026 (jan-jul):</b> {DADOS_2026['usuarios']:,} usuários ({DADOS_2026['usuarios_novos']:,} novos) · 
        Busca Orgânica: {DADOS_2026['busca_organica']:.1f}% · 
        Público Feminino: {DADOS_2026['feminino']:.1f}%
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{DADOS_2025['usuarios']:,}</div>
            <div class="metric-label">👥 Usuários 2025</div>
            <div class="metric-delta">{DADOS_2025['usuarios_novos']:,} novos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{DADOS_2026['usuarios']:,}</div>
            <div class="metric-label">👥 Usuários 2026</div>
            <div class="metric-delta">{DADOS_2026['usuarios_novos']:,} novos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{DADOS_2026['busca_organica']:.1f}%</div>
            <div class="metric-label">🔍 Busca Orgânica</div>
            <div class="metric-delta">{DADOS_2025['busca_organica']:.1f}% em 2025</div>
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
    
    # Gráficos
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("📊 Canais de Acesso")
        df_canais = pd.DataFrame({
            'Canal': ['Busca Orgânica', 'Acesso Direto', 'Outros'],
            '2025': [DADOS_2025['busca_organica'], DADOS_2025['acesso_direto'], 
                    100 - DADOS_2025['busca_organica'] - DADOS_2025['acesso_direto']],
            '2026': [DADOS_2026['busca_organica'], DADOS_2026['acesso_direto'],
                    100 - DADOS_2026['busca_organica'] - DADOS_2026['acesso_direto']]
        }).melt(id_vars='Canal', var_name='Ano', value_name='%')
        
        fig = px.bar(df_canais, x='Canal', y='%', color='Ano', barmode='group',
                     text_auto='.1f', color_discrete_sequence=['#1E3D59', '#17B978'])
        fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
        fig.update_layout(yaxis_range=[0, 100], plot_bgcolor='rgba(0,0,0,0)',
                          height=350, showlegend=True)
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
        fig.update_layout(yaxis_range=[0, 85], plot_bgcolor='rgba(0,0,0,0)',
                          height=350, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Ranking de espécies
    st.subheader("🌿 Espécies Mais Acessadas (2026)")
    
    df_esp = pd.DataFrame({
        'Espécie': [
            'Folha-da-fortuna (Kalanchoe pinnata)',
            'Quebra-pedra (Phyllanthus spp.)',
            'Buchinha-do-norte (Luffa operculata)',
            'Alfavaca-cravo (Ocimum gratissimum)',
            'Aveloz (Euphorbia tirucalli)',
            'Melão-de-são-caetano (Momordica charantia)'
        ],
        'Sessões': [6460, 5599, 4334, 4127, 4092, 3500]
    }).sort_values('Sessões', ascending=True)
    
    fig = px.bar(df_esp, x='Sessões', y='Espécie', orientation='h',
                 text_auto=',d', color='Sessões', color_continuous_scale='Greens')
    fig.update_traces(textposition='outside', textfont_size=10)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', height=350,
                      xaxis_title="Sessões de Entrada", yaxis_title="",
                      showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Conclusão
    st.divider()
    st.markdown("""
    <div class="highlight-box">
        <h4>💡 Conclusão</h4>
        <p style="font-size: 0.95rem;">
        O site do Horto é um efetivo <b>lócus da Etnobiologia Digital</b>, ampliando o alcance do conhecimento etnobotânico.
        As métricas de <b>Web Analytics</b> permitem identificar canais de acesso, perfil dos usuários e conteúdos mais acessados.
        </p>
        <p style="font-size: 0.9rem; color: #555; margin-top: 5px;">
        Apoio: Universidade Federal de Santa Catarina (UFSC)
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# ABA 2: TEMPO REAL
# ============================================

with aba2:
    st.header("📈 Painel em Tempo Real")
    st.caption("Dados do Google Analytics 4 - Atualização automática")
    
    count = st_autorefresh(interval=30000, key="refresh")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        periodo = st.selectbox(
            "Período:",
            ["⚡ Tempo Real", "Últimos 7 dias", "Últimos 30 dias", "Ano de 2026"]
        )
    with col2:
        st.caption(f"🔄 Atualizado: {datetime.now().strftime('%H:%M:%S')}")
    
    st.divider()
    
    if "Tempo Real" in periodo:
        with st.spinner("Buscando dados..."):
            df_rt = get_realtime_data()
        
        if df_rt is not None and not df_rt.empty:
            col1, col2, col3 = st.columns(3)
            col1.metric("👤 Usuários Ativos", f"{df_rt['activeUsers'].sum():.0f}")
            col2.metric("📄 Páginas Vistas", f"{df_rt['screenPageViews'].sum():.0f}")
            if 'deviceCategory' in df_rt.columns:
                top = df_rt.groupby('deviceCategory')['activeUsers'].sum().idxmax()
                col3.metric("📱 Principal Dispositivo", top)
            
            st.divider()
            
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                st.write("**Páginas em Destaque**")
                if 'pageTitle' in df_rt.columns:
                    df_pages = df_rt.groupby('pageTitle')['activeUsers'].sum().reset_index()
                    df_pages = df_pages.sort_values('activeUsers', ascending=True).tail(8)
                    fig = px.bar(df_pages, x='activeUsers', y='pageTitle',
                                orientation='h', color='activeUsers',
                                color_continuous_scale='Greens', text_auto=True)
                    fig.update_layout(showlegend=False, height=300, plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col_g2:
                st.write("**Origem dos Visitantes**")
                if 'country' in df_rt.columns:
                    df_geo = df_rt.groupby('country')['activeUsers'].sum().reset_index()
                    df_geo = df_geo.sort_values('activeUsers', ascending=False).head(8)
                    fig = px.pie(df_geo, values='activeUsers', names='country',
                                color_discrete_sequence=px.colors.sequential.Greens_r)
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Dados em tempo real indisponíveis no momento")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("👤 Usuários Ativos", "18")
            col2.metric("📄 Páginas Vistas", "42")
            col3.metric("📱 Dispositivo", "Mobile (76%)")
            
            st.divider()
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.write("**Páginas em Destaque**")
                df_demo = pd.DataFrame({
                    'Página': ['Folha da Fortuna', 'Quebra-pedra', 'Home', 'Buchinha'],
                    'Usuários': [7, 5, 4, 2]
                })
                fig = px.bar(df_demo, x='Usuários', y='Página', orientation='h',
                            color='Usuários', color_continuous_scale='Greens', text_auto=True)
                fig.update_layout(showlegend=False, height=300, plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            
            with col_g2:
                st.write("**Origem dos Visitantes**")
                df_geo = pd.DataFrame({
                    'Local': ['São Paulo', 'Santa Catarina', 'Rio de Janeiro', 'Lisboa'],
                    'Usuários': [8, 5, 3, 2]
                })
                fig = px.pie(df_geo, values='Usuários', names='Local',
                            color_discrete_sequence=['#1E3D59', '#17B978', '#334E68', '#A7E9AF'])
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        st.caption(f"🔄 Atualização automática a cada 30 segundos | Ciclo: #{count}")
    
    else:
        st.info(f"📊 Dados históricos: **{periodo}**")
        
        end = datetime.now().strftime('%Y-%m-%d')
        if "7 dias" in periodo:
            start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        elif "30 dias" in periodo:
            start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        else:
            start = '2026-01-01'
        
        with st.spinner("Carregando dados..."):
            df_hist = get_ga4_data(start, end)
        
        if df_hist is not None and not df_hist.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Evolução Diária")
                if 'date' in df_hist.columns:
                    df_daily = df_hist.groupby('date')['activeUsers'].sum().reset_index()
                    df_daily['date'] = pd.to_datetime(df_daily['date'])
                    fig = px.line(df_daily, x='date', y='activeUsers',
                                 color_discrete_sequence=['#17B978'])
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📊 Canais")
                if 'sessionDefaultChannelGroup' in df_hist.columns:
                    df_chan = df_hist.groupby('sessionDefaultChannelGroup')['activeUsers'].sum().reset_index()
                    df_chan = df_chan.sort_values('activeUsers', ascending=True).tail(8)
                    fig = px.bar(df_chan, x='activeUsers', y='sessionDefaultChannelGroup',
                                orientation='h', color='activeUsers',
                                color_continuous_scale='Greens', text_auto=True)
                    fig.update_layout(showlegend=False, height=350, plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Dados históricos indisponíveis")

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
    st.markdown("🏛️ **Horto Didático UFSC**", unsafe_allow_html=True)
with col2:
    st.markdown(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}", unsafe_allow_html=True)
with col3:
    st.markdown("🎓 **XXVIII SPMB 2026**", unsafe_allow_html=True)

st.markdown(f"""
<div class="footer">
    🌿 Desenvolvido para apresentação no XXVIII SPMB 2026 | Apoio: UFSC
</div>
""", unsafe_allow_html=True)
