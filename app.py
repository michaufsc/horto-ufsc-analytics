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
# INFORMAÇÕES DO TRABALHO (DADOS DO SEU ARTIGO)
# ============================================

TITULO = "Etnobiologia digital no Horto Didático da UFSC: circulação do saber etnobotânico mensurada por web analytics"
AUTORES = "Lopes MAL¹, Biavatti MW², Ritter GD³, Tardim LS⁴"
AUTOR_PRINCIPAL = "Michael A. Lopes"  # VOCÊ!
INSTITUICAO = "¹UFSC - Graduando em Química Tecnológica | ²UFSC - Depto. Ciências Farmacêuticas | ³Farmacêutica | ⁴UFSC - Graduanda em Farmácia"
PALAVRAS_CHAVE = "Etnobiologia Digital; Web Analytics; Plantas Medicinais; Circulação do Conhecimento"

# Referências do seu artigo
REFERENCIAS = """
**Referências:**

BOELL, M. E. C. Espécies do Horto Didático de Plantas Medicinais do HU/CCS (UFSC): identificação botânica e uso terapêutico de plantas medicinais. 2023. Trabalho de Conclusão de Curso (Graduação) – Universidade Federal de Santa Catarina, Florianópolis, 2023.

CEUTERICK, M.; VANDEBROEK, I.; TORRY, B.; PIERONI, A. Cross-cultural adaptation in urban ethnobotany: the Colombian folk pharmacopoeia in London. Journal of Ethnopharmacology, v. 120, n. 3, p. 342-359, 2008.

DE MEYER, E.; CEUTERICK, M. Digital Ethnobiology: exploring the digisphere in search of traditional and indigenous knowledge and practices. Ethnobotany Research and Applications, v. 24, p. 1-8, 2022.

FOLKE, C.; BIGGS, R.; NORSTRÖM, A. V.; REYERS, B.; ROCKSTRÖM, J. Social-ecological resilience and biosphere-based sustainability science. Ecology and Society, v. 21, n. 3, p. 41, 2016.

RITTER, G. D. O site do Horto Didático de Plantas Medicinais (UFSC) como ferramenta de divulgação científica para o uso de plantas medicinais. 2025. Trabalho de Conclusão de Curso (Graduação) – Universidade Federal de Santa Catarina, Florianópolis, 2025.

SIMON, F. M.; CAMARGO, C. Q. Autopsy of a metaphor: the origins, use and blind spots of the 'infodemic'. New Media & Society, v. 25, n. 8, p. 2219-2240, 2023.

WELLMAN, B. Little Boxes, Glocalization, and Networked Individualism. In: TANABE, M.; BESSELAAR, P. van den; ISHIDA, T. (ed.). Digital Cities II: computational and sociological approaches. Berlin: Springer, 2002. p. 10-25.
"""

# Dados do artigo (valores exatos do seu trabalho)
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
    'brasil': 94.9
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
    'brasil': 92.4
}

# ============================================
# CARREGAR CREDENCIAIS DO GA4
# ============================================

GA4_PROPERTY_ID = "750410485227"

# Verifica se está no Streamlit Cloud ou local
if os.path.exists('ga4-credentials.json'):
    try:
        with open('ga4-credentials.json', 'r') as f:
            credentials_info = json.load(f)
        st.success("✅ Usando credenciais do arquivo local (ga4-credentials.json)")
    except:
        st.error("❌ Erro ao carregar ga4-credentials.json")
        credentials_info = None
else:
    try:
        credentials_json = st.secrets["google_analytics"]["credentials_json"]
        if isinstance(credentials_json, str):
            credentials_info = json.loads(credentials_json)
        else:
            credentials_info = credentials_json
        st.success("✅ Usando credenciais do Streamlit Secrets")
    except:
        st.warning("⚠️ Usando dados de demonstração (GA4 não configurado)")
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
    except Exception as e:
        st.error(f"❌ Erro ao conectar GA4: {str(e)}")
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
        
    except Exception as e:
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
        
    except Exception as e:
        return None

# ============================================
# ESTILOS VISUAIS
# ============================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3D59;
        font-weight: 700;
        text-align: center;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #17B978;
        font-weight: 600;
        margin-bottom: 20px;
        text-align: center;
    }
    .title-work {
        font-size: 1.3rem;
        color: #1E3D59;
        font-weight: 600;
        text-align: center;
        margin: 10px 0;
    }
    .authors {
        font-size: 1.0rem;
        color: #555;
        text-align: center;
        margin: 5px 0;
    }
    .institution {
        font-size: 0.9rem;
        color: #777;
        text-align: center;
        margin: 5px 0;
    }
    .keywords {
        font-size: 0.9rem;
        color: #17B978;
        text-align: center;
        font-weight: 500;
        margin: 10px 0;
    }
    .stMetric {
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #17B978;
    }
    .event-banner {
        background: linear-gradient(135deg, #1E3D59 0%, #17B978 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 20px 0;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .event-banner h2 {
        margin: 0;
        color: white;
        font-size: 1.5rem;
    }
    .event-banner p {
        margin: 5px 0 0 0;
        opacity: 0.9;
    }
    .event-banner .highlight {
        background: rgba(255,255,255,0.2);
        padding: 5px 15px;
        border-radius: 20px;
        display: inline-block;
        margin-top: 8px;
        font-weight: 600;
        font-size: 0.95rem;
    }
    .references-box {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #1E3D59;
        margin: 20px 0;
        font-size: 0.85rem;
        max-height: 400px;
        overflow-y: auto;
    }
    .references-box strong {
        color: #1E3D59;
    }
    .presenter-badge {
        background: #17B978;
        color: white;
        padding: 4px 15px;
        border-radius: 20px;
        display: inline-block;
        font-weight: 600;
        font-size: 0.85rem;
        margin-left: 10px;
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
    st.markdown('<p class="main-header">🌿 Etnobiologia Digital no Horto Didático UFSC</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Web Analytics & Circulação do Saber Etnobotânico</p>', unsafe_allow_html=True)

with col_logo2:
    st.image(
        "https://xxviiispmb.com.br/wp-content/uploads/2026/01/logo-spmb-2026.png",
        use_container_width=True
    )

# ============================================
# INFORMAÇÕES DO TRABALHO
# ============================================

st.markdown(f"""
<div style="text-align: center; margin: 15px 0;">
    <p class="title-work">{TITULO}</p>
    <p class="authors">{AUTORES} <span class="presenter-badge">🎤 Apresentador: Michael A. Lopes</span></p>
    <p class="institution">{INSTITUICAO}</p>
    <p class="keywords">🔑 {PALAVRAS_CHAVE}</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# BANNER SPMB 2026
# ============================================

st.markdown("""
<div class="event-banner">
    <h2>🎓 XXVIII Simpósio de Plantas Medicinais do Brasil (SPMB) 2026</h2>
    <p>📅 15 a 18 de setembro de 2026 | 📍 Univali - Campus Professor Edison Villela, Itajaí/SC</p>
    <p>🌿 Tema: <strong>Plantas medicinais como fonte de novos agentes medicinais</strong></p>
    <div class="highlight">🌟 Apresentação: Etnobiologia Digital no Horto UFSC - Michael A. Lopes</div>
</div>
""", unsafe_allow_html=True)

# ============================================
# NAVEGAÇÃO
# ============================================

aba_artigo, aba_ga4, aba_referencias = st.tabs([
    "📄 Resultados da Pesquisa",
    "📊 Analytics em Tempo Real",
    "📚 Referências"
])

# ============================================
# ABA 1: RESULTADOS DA PESQUISA
# ============================================

with aba_artigo:
    st.header("📈 Resultados e Discussão")
    
    st.markdown("""
    <div style="background: #f0f9f4; padding: 8px 15px; border-radius: 20px; border-left: 3px solid #17B978; font-size: 0.9rem; color: #1E3D59; display: inline-block; margin-bottom: 15px;">
        📄 Trabalho apresentado no XXVIII SPMB 2026 - Horto Didático UFSC
    </div>
    """, unsafe_allow_html=True)
    
    # Resumo com dados exatos do seu artigo
    st.markdown(f"""
    > **Resumo dos Resultados:** A análise combinada entre aquisição de usuários e aquisição de tráfego revela a sólida autoridade e o alcance do portal. Em **2025**, o site registrou **{DADOS_2025['usuarios']:,} usuários** ({DADOS_2025['usuarios_novos']:,} novos), com predomínio da busca orgânica ({DADOS_2025['busca_organica_usuarios']:,}; **{DADOS_2025['busca_organica_pct']:.2f}%**) e do acesso direto ({DADOS_2025['acesso_direto_usuarios']:,}; **{DADOS_2025['acesso_direto_pct']:.2f}%**). Na perspectiva de tráfego, o mesmo período contabilizou {DADOS_2025['usuarios_engajados']:,} usuários engajados, liderados pela busca orgânica ({DADOS_2025['busca_organica_trafego']:,}; **{DADOS_2025['busca_organica_trafego_pct']:.2f}%**) e acesso direto ({DADOS_2025['acesso_direto_trafego']:,}; **{DADOS_2025['acesso_direto_trafego_pct']:.2f}%**).
    > 
    > Em **2026 (jan–jul)**, foram **{DADOS_2026['usuarios']:,} usuários** ({DADOS_2026['usuarios_novos']:,} novos), mantendo a liderança da busca orgânica ({DADOS_2026['busca_organica_usuarios']:,}; **{DADOS_2026['busca_organica_pct']:.2f}%**) e acesso direto ({DADOS_2026['acesso_direto_usuarios']:,}; **{DADOS_2026['acesso_direto_pct']:.2f}%**), enquanto o tráfego total atingiu {DADOS_2026['usuarios_engajados']:,} usuários, com busca orgânica ({DADOS_2026['busca_organica_trafego']:,}; **{DADOS_2026['busca_organica_trafego_pct']:.2f}%**) e acesso direto ({DADOS_2026['acesso_direto_trafego']:,}; **{DADOS_2026['acesso_direto_trafego_pct']:.2f}%**).
    > 
    > Quanto ao perfil demográfico, observou-se predominância do público feminino (**{DADOS_2025['feminino']:.1f}% em 2025** e **{DADOS_2026['feminino']:.1f}% em 2026**) e de jovens adultos na faixa etária de 25 a 34 anos (**40,1%**). A imensa maioria dos acessos está concentrada no Brasil (**{DADOS_2025['brasil']:.1f}% em 2025** e **{DADOS_2026['brasil']:.1f}% em 2026**).
    """)
    
    st.divider()
    
    # KPIs
    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    
    with col_k1:
        st.metric("👥 Usuários (2025)", f"{DADOS_2025['usuarios']:,}", f"{DADOS_2025['usuarios_novos']:,} novos")
    
    with col_k2:
        st.metric("👥 Usuários (2026)", f"{DADOS_2026['usuarios']:,}", f"{DADOS_2026['usuarios_novos']:,} novos")
    
    with col_k3:
        st.metric("🔍 Busca Orgânica", f"{DADOS_2026['busca_organica_pct']:.1f}%", f"{DADOS_2025['busca_organica_pct']:.1f}% em 2025")
    
    with col_k4:
        st.metric("👩 Público Feminino", f"{DADOS_2026['feminino']:.1f}%", f"+{DADOS_2026['feminino'] - DADOS_2025['feminino']:.1f}% vs 2025")
    
    st.divider()
    
    # Gráficos
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("📊 Canais de Aquisição de Usuários")
        df_canais = pd.DataFrame({
            'Canal': ['Busca Orgânica', 'Acesso Direto', 'Outros (Referral/IA/Social)'],
            '2025 (%)': [DADOS_2025['busca_organica_pct'], DADOS_2025['acesso_direto_pct'], 100 - DADOS_2025['busca_organica_pct'] - DADOS_2025['acesso_direto_pct']],
            '2026 (%)': [DADOS_2026['busca_organica_pct'], DADOS_2026['acesso_direto_pct'], 100 - DADOS_2026['busca_organica_pct'] - DADOS_2026['acesso_direto_pct']]
        }).melt(id_vars='Canal', var_name='Ano', value_name='Porcentagem')
        
        fig_canais = px.bar(
            df_canais,
            x='Canal',
            y='Porcentagem',
            color='Ano',
            barmode='group',
            text_auto='.2f',
            color_discrete_sequence=['#1E3D59', '#17B978'],
            title="Distribuição por Canal de Aquisição"
        )
        fig_canais.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
        fig_canais.update_layout(
            yaxis_range=[0, 100],
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis_title="Percentual (%)",
            xaxis_title=""
        )
        st.plotly_chart(fig_canais, use_container_width=True)
    
    with col_g2:
        st.subheader("👥 Perfil Demográfico por Gênero")
        df_genero = pd.DataFrame({
            'Ano': ['2025', '2025', '2026', '2026'],
            'Gênero': ['Feminino', 'Masculino', 'Feminino', 'Masculino'],
            'Porcentagem': [DADOS_2025['feminino'], DADOS_2025['masculino'], DADOS_2026['feminino'], DADOS_2026['masculino']]
        })
        
        fig_genero = px.bar(
            df_genero,
            x='Ano',
            y='Porcentagem',
            color='Gênero',
            barmode='group',
            text_auto='.1f',
            color_discrete_sequence=['#17B978', '#1E3D59'],
            title="Distribuição por Gênero"
        )
        fig_genero.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
        fig_genero.update_layout(
            yaxis_range=[0, 85],
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis_title="Percentual (%)",
            xaxis_title=""
        )
        st.plotly_chart(fig_genero, use_container_width=True)
    
    st.divider()
    
    st.subheader("🌿 Ranking de Espécies Medicinais Mais Acessadas (2026)")
    
    df_especies = pd.DataFrame({
        'Espécie Medicinal': [
            'Folha-da-fortuna (Kalanchoe pinnata)',
            'Quebra-pedra / Quebra-pedra-rasteiro (Phyllanthus spp.)',
            'Buchinha-do-norte (Luffa operculata)',
            'Alfavaca-cravo (Ocimum gratissimum)',
            'Melão-de-são-caetano (Momordica charantia)',
            'Aveloz (Euphorbia tirucalli)',
            'Página Inicial (Home)'
        ],
        'Sessões de Entrada': [6460, 5599, 4334, 4127, 3500, 4092, 5622]
    }).sort_values(by='Sessões de Entrada', ascending=True)
    
    fig_especies = px.bar(
        df_especies,
        x='Sessões de Entrada',
        y='Espécie Medicinal',
        orientation='h',
        text_auto=',d',
        color='Sessões de Entrada',
        color_continuous_scale='Greens',
        title="Top 7 Espécies Mais Acessadas"
    )
    fig_especies.update_traces(textposition='outside', textfont_size=10)
    fig_especies.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Número de Sessões de Entrada",
        yaxis_title="",
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig_especies, use_container_width=True)
    
    st.divider()
    
    # Conclusão do artigo
    st.subheader("💡 Conclusão")
    st.markdown("""
    Os resultados confirmam o site do Horto como efetivo lócus empírico da **Etnobiologia Digital**, ampliando o alcance do conhecimento etnobotânico para além dos muros da universidade e alcançando públicos diversos em escala nacional e internacional.
    
    As métricas de **Web Analytics** mostraram-se ferramentas robustas para avaliar essa circulação, permitindo identificar:
    - Os principais canais de acesso (buscadores e assistentes de IA)
    - O perfil demográfico dos usuários
    - Os conteúdos mais acessados
    
    Essa análise evidencia a **tensão entre a capilaridade digital** (ampla disseminação do conhecimento) e o **risco de descontextualização** (perda do vínculo do saber com suas origens étnicas, ecológicas e culturais). Essa tensão reforça a necessidade de conciliar acessibilidade com a preservação da integridade dos saberes.
    
    > "garantindo que a divulgação científica não comprometa a riqueza e a segurança dos conhecimentos tradicionais" (De Meyer & Ceuterick, 2022; Simon & Camargo, 2021).
    """)
    
    st.divider()
    
    # Informações da apresentação
    st.markdown(f"""
    <div style="background: #f0f9f4; padding: 20px; border-radius: 10px; border-left: 5px solid #17B978; margin-top: 10px;">
        <h4 style="color: #1E3D59; margin-top: 0;">🎤 Informações da Apresentação - SPMB 2026</h4>
        <p><strong>Título:</strong> {TITULO}</p>
        <p><strong>Autores:</strong> {AUTORES}</p>
        <p><strong>Apresentador:</strong> Michael A. Lopes (Graduando em Química Tecnológica - UFSC)</p>
        <p><strong>Instituição:</strong> Universidade Federal de Santa Catarina (UFSC) - Horto Didático</p>
        <p><strong>Área:</strong> Etnobiologia Digital / Web Analytics</p>
        <p><strong>Palavras-chave:</strong> {PALAVRAS_CHAVE}</p>
        <p style="color: #17B978; font-weight: 600;">📅 Apresentação: 15 a 18 de setembro de 2026</p>
        <p style="color: #17B978; font-weight: 600;">🏛️ Local: Univali - Itajaí/SC</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# ABA 2: ANALYTICS EM TEMPO REAL
# ============================================

with aba_ga4:
    st.header("⚡ Painel Interativo Google Analytics 4")
    st.caption("Monitoramento dinâmico do portal Horto UFSC com dados do GA4")
    
    count = st_autorefresh(interval=30000, key="ga4_autorefresh")
    
    col_periodo, col_status = st.columns([3, 1])
    with col_periodo:
        periodo = st.selectbox(
            "📅 Selecione o Período de Consulta:",
            ["⚡ Tempo Real (Últimos 30 minutos)", "📆 Últimos 7 dias", "📆 Últimos 30 dias", "📆 Ano de 2026"]
        )
    with col_status:
        st.caption(f"🔄 Ciclo: #{count}")
        st.caption(f"⏱️ {datetime.now().strftime('%H:%M:%S')}")
    
    st.divider()
    
    if "Tempo Real" in periodo:
        st.success("🟢 Modo Tempo Real ativado - Buscando dados do GA4")
        
        with st.spinner("🔄 Buscando dados em tempo real..."):
            df_realtime = get_realtime_data()
        
        if df_realtime is not None and not df_realtime.empty:
            total_active = df_realtime['activeUsers'].sum() if 'activeUsers' in df_realtime.columns else 0
            
            rt_c1, rt_c2, rt_c3 = st.columns(3)
            rt_c1.metric("👤 Usuários Ativos", f"{total_active:.0f}", "Dados em tempo real")
            rt_c2.metric("📄 Páginas Vistas", df_realtime['screenPageViews'].sum() if 'screenPageViews' in df_realtime.columns else "N/A", "Últimos 30 min")
            
            if 'deviceCategory' in df_realtime.columns:
                device_counts = df_realtime.groupby('deviceCategory')['activeUsers'].sum()
                top_device = device_counts.idxmax() if not device_counts.empty else "N/A"
                rt_c3.metric("📱 Dispositivo Dominante", top_device, "Dados em tempo real")
            
            st.divider()
            
            c_rt1, c_rt2 = st.columns(2)
            
            with c_rt1:
                st.write("**📄 Páginas Sendo Acessadas**")
                if 'pageTitle' in df_realtime.columns:
                    df_rt_pages = df_realtime.groupby('pageTitle')['activeUsers'].sum().reset_index()
                    df_rt_pages = df_rt_pages.sort_values('activeUsers', ascending=True).tail(10)
                    
                    fig_rt_p = px.bar(
                        df_rt_pages,
                        x='activeUsers',
                        y='pageTitle',
                        orientation='h',
                        color='activeUsers',
                        color_continuous_scale='Greens',
                        text_auto=True
                    )
                    fig_rt_p.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=False,
                        height=350,
                        xaxis_title="Usuários Ativos",
                        yaxis_title=""
                    )
                    st.plotly_chart(fig_rt_p, use_container_width=True)
                else:
                    st.info("Dados de página não disponíveis")
            
            with c_rt2:
                st.write("**🌍 Origem Geográfica**")
                if 'country' in df_realtime.columns:
                    df_rt_geo = df_realtime.groupby('country')['activeUsers'].sum().reset_index()
                    df_rt_geo = df_rt_geo.sort_values('activeUsers', ascending=False).head(10)
                    
                    fig_rt_g = px.pie(
                        df_rt_geo,
                        values='activeUsers',
                        names='country',
                        color_discrete_sequence=px.colors.sequential.Greens_r,
                        hole=0.3
                    )
                    fig_rt_g.update_traces(textposition='inside', textinfo='percent+label')
                    fig_rt_g.update_layout(height=350)
                    st.plotly_chart(fig_rt_g, use_container_width=True)
                else:
                    st.info("Dados geográficos não disponíveis")
        else:
            # Dados de demonstração
            st.warning("⚠️ Dados em tempo real não disponíveis - usando dados de demonstração")
            
            rt_c1, rt_c2, rt_c3 = st.columns(3)
            rt_c1.metric("👤 Usuários Ativos Agora", "18", "+3 nos últimos 5 min")
            rt_c2.metric("📄 Páginas Vistas (30 min)", "42", "1.4 págs/minuto")
            rt_c3.metric("📱 Dispositivo Dominante", "Mobile (76%)", "Smartphone")
            
            c_rt1, c_rt2 = st.columns(2)
            with c_rt1:
                st.write("**📄 Páginas Sendo Acessadas**")
                df_rt_pages = pd.DataFrame({
                    'Página / Planta': ['Folha da Fortuna', 'Quebra-pedra', 'Home', 'Buchinha do Norte'],
                    'Usuários Ativos': [7, 5, 4, 2]
                })
                fig_rt_p = px.bar(
                    df_rt_pages,
                    x='Usuários Ativos',
                    y='Página / Planta',
                    orientation='h',
                    color='Usuários Ativos',
                    color_continuous_scale='Greens',
                    text_auto=True
                )
                fig_rt_p.update_layout(plot_bgcolor='rgba(0,0,0,0)', showlegend=False, height=350)
                st.plotly_chart(fig_rt_p, use_container_width=True)
            
            with c_rt2:
                st.write("**🌍 Origem Geográfica Instantânea**")
                df_rt_geo = pd.DataFrame({
                    'Localidade': ['São Paulo (BR)', 'Santa Catarina (BR)', 'Rio de Janeiro (BR)', 'Lisboa (PT)'],
                    'Usuários': [8, 5, 3, 2]
                })
                fig_rt_g = px.pie(
                    df_rt_geo,
                    values='Usuários',
                    names='Localidade',
                    color_discrete_sequence=['#1E3D59', '#17B978', '#334E68', '#A7E9AF'],
                    hole=0.3
                )
                fig_rt_g.update_traces(textposition='inside', textinfo='percent+label')
                fig_rt_g.update_layout(height=350)
                st.plotly_chart(fig_rt_g, use_container_width=True)
        
        st.caption(f"🔄 Atualizado automaticamente a cada 30 segundos | Ciclo atual: #{count} | {datetime.now().strftime('%H:%M:%S')}")
    
    else:
        st.info(f"📊 Exibindo dados históricos para: **{periodo}**")
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        if periodo == "📆 Últimos 7 dias":
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        elif periodo == "📆 Últimos 30 dias":
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        else:
            start_date = '2026-01-01'
        
        with st.spinner("🔄 Carregando dados históricos..."):
            df_historico = get_ga4_data(start_date, end_date)
        
        if df_historico is not None and not df_historico.empty:
            col_hist1, col_hist2 = st.columns(2)
            
            with col_hist1:
                st.subheader("📈 Evolução Diária")
                if 'date' in df_historico.columns:
                    df_daily = df_historico.groupby('date')['activeUsers'].sum().reset_index()
                    df_daily['date'] = pd.to_datetime(df_daily['date'])
                    fig_hist = px.line(
                        df_daily,
                        x='date',
                        y='activeUsers',
                        title=f"Tráfego Diário - {periodo}",
                        color_discrete_sequence=['#17B978']
                    )
                    fig_hist.update_layout(plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_hist, use_container_width=True)
            
            with col_hist2:
                st.subheader("📊 Top Fontes de Tráfego")
                if 'sessionDefaultChannelGroup' in df_historico.columns:
                    df_fontes = df_historico.groupby('sessionDefaultChannelGroup')['activeUsers'].sum().reset_index()
                    df_fontes = df_fontes.sort_values('activeUsers', ascending=True).tail(10)
                    fig_fontes = px.bar(
                        df_fontes,
                        x='activeUsers',
                        y='sessionDefaultChannelGroup',
                        orientation='h',
                        color='activeUsers',
                        color_continuous_scale='Greens',
                        text_auto=True
                    )
                    fig_fontes.update_layout(plot_bgcolor='rgba(0,0,0,0)', showlegend=False, height=350)
                    st.plotly_chart(fig_fontes, use_container_width=True)
        else:
            # Dados de demonstração
            st.warning("⚠️ Dados históricos não disponíveis - usando dados de demonstração")
            
            col_hist1, col_hist2 = st.columns(2)
            with col_hist1:
                st.subheader("📈 Evolução Diária (Simulação)")
                dates = pd.date_range(start='2026-01-01', periods=30, freq='D')
                data_hist = pd.DataFrame({
                    'Data': dates,
                    'Usuários': [150, 180, 200, 190, 220, 250, 230, 260, 280, 300,
                                290, 310, 320, 305, 330, 350, 340, 360, 370, 355,
                                380, 390, 385, 400, 420, 410, 430, 440, 450, 435]
                })
                fig_hist = px.line(data_hist, x='Data', y='Usuários', color_discrete_sequence=['#17B978'])
                fig_hist.update_layout(plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col_hist2:
                st.subheader("📊 Top Fontes de Tráfego")
                df_fontes = pd.DataFrame({
                    'Fonte': ['Google', 'Direct', 'Bing', 'Social', 'Outros'],
                    'Sessões': [2500, 800, 300, 150, 100]
                })
                fig_fontes = px.pie(
                    df_fontes,
                    values='Sessões',
                    names='Fonte',
                    color_discrete_sequence=px.colors.sequential.Greens_r
                )
                fig_fontes.update_traces(textposition='inside', textinfo='percent+label')
                fig_fontes.update_layout(height=350)
                st.plotly_chart(fig_fontes, use_container_width=True)

# ============================================
# ABA 3: REFERÊNCIAS
# ============================================

with aba_referencias:
    st.header("📚 Referências Bibliográficas")
    
    st.markdown("""
    <div class="references-box">
        <p><strong>BOELL, M. E. C.</strong> Espécies do Horto Didático de Plantas Medicinais do HU/CCS (UFSC): identificação botânica e uso terapêutico de plantas medicinais. 2023. Trabalho de Conclusão de Curso (Graduação) – Universidade Federal de Santa Catarina, Florianópolis, 2023. Disponível em: https://repositorio.ufsc.br/handle/123456789/266030. Acesso em: 4 ago. 2026.</p>
        
        <p><strong>CEUTERICK, M.; VANDEBROEK, I.; TORRY, B.; PIERONI, A.</strong> Cross-cultural adaptation in urban ethnobotany: the Colombian folk pharmacopoeia in London. Journal of Ethnopharmacology, v. 120, n. 3, p. 342-359, 2008. DOI: 10.1016/j.jep.2008.09.004.</p>
        
        <p><strong>DE MEYER, E.; CEUTERICK, M.</strong> Digital Ethnobiology: exploring the digisphere in search of traditional and indigenous knowledge and practices. Ethnobotany Research and Applications, v. 24, p. 1-8, 2022. DOI: 10.32859/era.24.37.1-8.</p>
        
        <p><strong>FOLKE, C.; BIGGS, R.; NORSTRÖM, A. V.; REYERS, B.; ROCKSTRÖM, J.</strong> Social-ecological resilience and biosphere-based sustainability science. Ecology and Society, v. 21, n. 3, p. 41, 2016. DOI: 10.5751/ES-08748-210341.</p>
        
        <p><strong>RITTER, G. D.</strong> O site do Horto Didático de Plantas Medicinais (UFSC) como ferramenta de divulgação científica para o uso de plantas medicinais. 2025. Trabalho de Conclusão de Curso (Graduação) – Universidade Federal de Santa Catarina, Florianópolis, 2025. Disponível em: https://repositorio.ufsc.br/xmlui/handle/123456789/252686. Acesso em: 4 ago. 2026.</p>
        
        <p><strong>SIMON, F. M.; CAMARGO, C. Q.</strong> Autopsy of a metaphor: the origins, use and blind spots of the 'infodemic'. New Media & Society, v. 25, n. 8, p. 2219-2240, 2023. DOI: 10.1177/14614448211031908.</p>
        
        <p><strong>WELLMAN, B.</strong> Little Boxes, Glocalization, and Networked Individualism. In: TANABE, M.; BESSELAAR, P. van den; ISHIDA, T. (ed.). Digital Cities II: computational and sociological approaches. Berlin: Springer, 2002. p. 10-25.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("📄 Referências completas do trabalho 'Etnobiologia digital no Horto Didático da UFSC'")

# ============================================
# RODAPÉ
# ============================================

st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.markdown("""
    <div style="text-align: center;">
        <p style="font-size: 0.85rem; color: #666;">
            🏛️ <strong>Horto Didático UFSC</strong><br>
            Universidade Federal de Santa Catarina
        </p>
    </div>
    """, unsafe_allow_html=True)
    
with col_footer2:
    st.markdown(f"""
    <div style="text-align: center;">
        <p style="font-size: 0.85rem; color: #666;">
            📅 Atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
with col_footer3:
    st.markdown("""
    <div style="text-align: center;">
        <p style="font-size: 0.85rem; color: #666;">
            🎓 <strong>XXVIII SPMB 2026</strong><br>
            Apresentação: Michael A. Lopes
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; padding: 10px; margin-top: 10px; background: #f8f9fa; border-radius: 10px;">
    <p style="font-size: 0.8rem; color: #999; margin: 0;">
        🌿 Desenvolvido para apresentação no XXVIII Simpósio de Plantas Medicinais do Brasil (SPMB) 2026
        <br>
        <span style="font-size: 0.75rem;">Apoio Financeiro: Universidade Federal de Santa Catarina (UFSC)</span>
    </p>
</div>
""", unsafe_allow_html=True)