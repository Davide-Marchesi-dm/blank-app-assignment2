import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time
import pydeck as pdk

# 1. Configurazione della pagina
st.set_page_config(layout="wide", page_title="App Tour de France")


# ==========================================
# FUNZIONE PER CARICARE I DATI 
# ==========================================
@st.cache_data
def load_all_datasets():
    # Link ai dataset esistenti
    url_storico = "https://docs.google.com/spreadsheets/d/1hI6y5tDpw176v0DhJN-P5hzsmXrtRSB0/export?format=xlsx"
    url_stage_h = "https://docs.google.com/spreadsheets/d/1bYnt9BfbKk-HMYR8bekqQfaKH02eZBWq/export?format=xlsx" 
    url_tour_w = "https://docs.google.com/spreadsheets/d/1GrXwBG2Cda93AvOsWa-oDT19gwWCaF-2/export?format=xlsx"
    
    # 1. NUOVO LINK GOOGLE DRIVE PER LE COORDINATE
    url_coords = "https://docs.google.com/spreadsheets/d/1NoKnm0M5WCKIwTvu2wwGEWRgG3EKBoeJ/export?format=xlsx"
    # Caricamento file esistenti
    try:
        df_storico = pd.read_excel(url_storico, engine="openpyxl")
    except Exception as e:
        st.error(f"Errore file Storico: {e}")
        df_storico = pd.DataFrame()

    try:
        df_stage_h = pd.read_excel(url_stage_h, engine="openpyxl")
    except Exception as e:
        st.error(f"Errore file Stage_h: {e}")
        df_stage_h = pd.DataFrame()

    try:
        df_tour_w = pd.read_excel(url_tour_w, engine="openpyxl")
    except Exception as e:
        st.error(f"Errore file Tour_w: {e}")
        df_tour_w = pd.DataFrame()

    # 2. CARICAMENTO NUOVO FILE COORDINATE
    try:
        df_coords = pd.read_excel(url_coords, engine="openpyxl")
    except Exception as e:
        st.error(f"Errore file Coordinate: {e}")
        df_coords = pd.DataFrame()
    
    # Filtro Anno: dal 1913 in poi
    if not df_storico.empty and 'Year' in df_storico.columns:
        df_storico = df_storico[df_storico['Year'] >= 1913]
        
    if not df_stage_h.empty and 'Year' in df_stage_h.columns:
        df_stage_h = df_stage_h[df_stage_h['Year'] >= 1913]
        
    if not df_tour_w.empty and 'Year' in df_tour_w.columns:
        df_tour_w = df_tour_w[df_tour_w['Year'] >= 1913]

    # Applichiamo il filtro anche al nuovo dataframe se necessario
    if not df_coords.empty and 'Year' in df_coords.columns:
        df_coords = df_coords[df_coords['Year'] >= 1913]

    return df_storico, df_stage_h, df_tour_w, df_coords

# 3. CHIAMATA 
df_storico, df_stage_h, df_tour_w, df_coords = load_all_datasets()

# 1. Configurazione della pagina
st.set_page_config(layout="wide", page_title="App Tour de France")

# ==========================================
# 2. GESTIONE DELLA NAVIGAZIONE (CORE LOGIC)
# ==========================================

# A. Se l'utente clicca sul logo, l'URL conterrà "?nav=home". Lo intercettiamo:
if "nav" in st.query_params and st.query_params["nav"] == "home":
    st.session_state.pagina_corrente = "home"
    del st.query_params["nav"] # Puliamo l'URL dopo averlo letto

# B. Inizializziamo lo stato se è la prima volta che si apre l'app
if "pagina_corrente" not in st.session_state:
    st.session_state.pagina_corrente = "home"


# ==========================================
# 3. CSS E STILE DELLA BARRA NERA E SFONDO
# ==========================================
st.markdown("""
    <style>
    /* ---> 1. IMPORTIAMO IL FONT GIORNALISTICO DA GOOGLE FONTS <--- */
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;0,900;1,400&display=swap');

    /* ---> 2. APPLICHIAMO IL FONT A TUTTI I TESTI DELL'APP <--- */
    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Merriweather', Georgia, 'Times New Roman', serif !important;
        color: #FFFFFF !important;
    }

    /* ---> 3. SFONDO GIALLO GIORNALE <--- */
    .stApp {
        background-color: #F4F1EA; /* Un giallo carta antico/giornale molto elegante */
    }

    /* Nasconde la barra spaziatrice superiore di default di Streamlit */
    [data-testid="stHeader"] { 
        display: none; 
    }
    
    .block-container {
        padding-top: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }
    
    /* Sfondo nero per l'intera riga della navigazione */
    [data-testid="stHorizontalBlock"] {
        background-color: #000000;
        align-items: center;
        padding: 10px 20px;
        margin-bottom: 20px;
    }
    
    /* Stile base dei bottoni (i bottoni manterranno il font scelto sopra!) */
    div.stButton > button {
        background-color: transparent !important;
        color: #FFFFFF !important;
        border: none !important;
        border-bottom: 4px solid transparent !important; 
        border-radius: 0px !important;
        box-shadow: none !important;
        font-weight: bold;
        font-size: 16px;
        letter-spacing: 1px;
        padding-bottom: 8px;
        transition: border-color 0.2s ease-in-out;
    }
    
    /* Effetto hover (quando passi il cursore) */
    div.stButton > button:hover, 
    div.stButton > button:focus, 
    div.stButton > button:active {
        color: #FFFFFF !important;
        border-bottom: 4px solid #FFCC00 !important;
        background-color: transparent !important;
    }
    
    [data-testid="column"] {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    [data-testid="stMarkdownContainer"] p {
        margin-bottom: 0 !important;
    }
    
    /* Margini per il contenuto delle pagine sotto la barra */
    .contenuto-pagina {
        padding: 2rem 4rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. COSTRUZIONE DELLA BARRA DI NAVIGAZIONE
# ==========================================
col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 2, 1.5, 1.5], vertical_alignment="center")

with col1:
    # Se clicchi, lo stato cambia in "2025"
    if st.button("CLASSIFICA", use_container_width=True):
        st.session_state.pagina_corrente = "classifica"
with col2:
    if st.button("CORRIDORI", use_container_width=True):
        st.session_state.pagina_corrente = "corridori"

with col3:
    url_logo = "https://www.brandforum.it/wp-content/uploads/2019/03/38020191021104459.png"
    
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; margin: 0; padding: 0; transform: translateY(-8px);">
            <a href="?nav=home" target="_self" title="Torna alla Home">
                <img src="{url_logo}" 
                     style="width: 100%; max-width: 140px; background-color: white; padding: 2px 8px; border-radius: 8px; cursor: pointer;">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    if st.button("TAPPE", use_container_width=True):
        st.session_state.pagina_corrente = "tappe"

with col5:
    if st.button("TEAMS", use_container_width=True):
        st.session_state.pagina_corrente = "teams"


# ==========================================
# 5. CONTENUTO DELLE PAGINE
# ==========================================
st.markdown('<div class="contenuto-pagina">', unsafe_allow_html=True)


if st.session_state.pagina_corrente == "home":
    
    # 1. IL "TITOLONE" DA PRIMA PAGINA
    st.markdown("""
        <h1 style='text-align: center; font-size: 3.5rem; text-transform: uppercase; border-bottom: 3px solid black; padding-bottom: 10px; margin-bottom: 10px; color: #000000;'>
            Le Tour de France
        </h1>
        <h3 style='text-align: center; font-style: italic; color: #000000; margin-bottom: 40px;'>
            Tutti i numeri, i segreti e i protagonisti della Grande Boucle
        </h3>
    """, unsafe_allow_html=True)

    # 2. LAYOUT A COLONNE (Stile articolo)
    col_sx, col_dx = st.columns([1.5, 1], gap="large")
    
    with col_sx:
        # Testo dell'articolo introduttivo
        st.markdown("""
        **PARIGI** — Il Tour de France non è semplicemente una corsa ciclistica; è un monumento nazionale itinerante, una prova di resistenza sovrumana e il palcoscenico dove, da oltre un secolo, si forgiano le leggende dello sport. 
        
        Sulle strade di Francia, i giganti del pedale si sfidano attraverso pianure spazzate dal vento, colline insidiose e le vette massacranti di Alpi e Pirenei. Questo portale nasce per dissezionare ogni singolo aspetto della corsa a tappe più famosa del mondo.
        
        **Esplora i dati:** Usa la barra di navigazione superiore per immergerti nelle statistiche. Dalle planimetrie dettagliate di ogni singola tappa, fino ai profili biometrici dei ciclisti e alle squadre World Tour.
        """)
        
        # Una linea di separazione
        st.markdown("<hr style='border: 1px solid #555; margin-top: 30px; margin-bottom: 30px;'>", unsafe_allow_html=True)
        
        # ---> LE STATISTICHE
        st.markdown("<h3 style='margin-top: 20px; margin-bottom: 15px; color: #FFFFFF;'>I Numeri della Corsa</h3>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Edizioni", "111")
        c2.metric("Chilometri", "~3.500")
        c3.metric("Tappe", "21")
        
        # Un po' di spazio
        st.markdown("<br>", unsafe_allow_html=True)

        # ---> BOX CURIOSITÀ SPOSTATO SOTTO <---
        st.markdown("""
            <div style='background-color: #E6E1CF; color: #000000; padding: 15px; border-left: 5px solid #FFCC00; margin-top: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);'>
            <h4 style='margin-top: 0; margin-bottom: 10px; font-style: italic; border-bottom: 1px solid #999; padding-bottom: 5px; color: #000000;'>📰 Dietro le quinte del Tour</h4>
                
            <p style='font-size: 0.95rem; margin-top: 10px;'><strong>Le origini commerciali:</strong> Il Tour fu fondato nel 1903 da Henri Desgrange, direttore del giornale sportivo francese <em>L'Auto</em> (il predecessore de L'Équipe), con un obiettivo molto pratico: sbaragliare la concorrenza e vendere più copie del suo quotidiano.</p>
                
            <p style='font-size: 0.95rem; margin-bottom: 0;'><strong>Il segreto del Giallo:</strong> La celebre maglia gialla, introdotta nel 1919 per rendere il leader della corsa facilmente riconoscibile in gruppo, deve il suo colore proprio alla carta su cui veniva stampato il giornale <em>L'Auto</em>.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col_dx:
        # Foto "in prima pagina" (Senza icona espandi schermo)
        foto_hero = "https://cdn.artphotolimited.com/images/5c2e191bd96b2e012e7a7fc5/1000x1000/tour-de-france-1937.jpg"
        st.markdown(f"<img src='{foto_hero}' style='width: 100%; border-radius: 3px;'>", unsafe_allow_html=True)
        
        # Didascalia della foto in piccolo (Margine sistemato per l'HTML)
        st.markdown("""
            <p style='font-size: 0.85rem; text-align: right; font-style: italic; color: #FFFFFF; margin-top: 5px;'>
                Guy Lapébie il vincitore dell'edizione del 1937. (Foto: Archivi Storici)
            </p>
        """, unsafe_allow_html=True)
    
    # ---> SEZIONE CITAZIONI CELEBRI (3 Colonne) <---
    # Una linea per separare la parte alta della pagina
    st.markdown("<hr style='border: 1px solid #555; margin-top: 50px; margin-bottom: 30px;'>", unsafe_allow_html=True)
    
    # Titolo della sezione citazioni
    st.markdown("<h3 style='text-align: center; font-style: italic; color: #333; margin-bottom: 40px;'> Voci dalla Grande Boucle</h3>", unsafe_allow_html=True)

    # Creiamo tre colonne per affiancare le tue tre citazioni
    cit1, cit2, cit3 = st.columns(3, gap="large")

    with cit1:
        # Henri Desgrange
        st.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTBrNDQ34YGwB6cNLr1TaGGmkzQtqPAjpaB8g&s" 
                 style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 2px solid #333; margin-bottom: 15px; filter: grayscale(100%);">
            <p style='font-size: 1.05rem; font-style: italic; margin-bottom: 15px; line-height: 1.4; color: #FFFFFF;'>
                «Il Tour de France ideale sarebbe quello in cui un solo corridore riuscisse ad arrivare a Parigi.»
            </p>
            <p style='font-size: 0.9rem; margin: 0;'><strong>— Henri Desgrange</strong></p>
            <p style='font-size: 0.8rem; color: #FFFFFF; line-height: 1.3; margin-top: 5px;'>Fondatore del Tour.</p>
        </div>
        """, unsafe_allow_html=True)

    with cit2:
        # Lance Armstrong
        st.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <img src="https://cdn.mos.cms.futurecdn.net/WAu4qwBuYVmi4qtQ6W8F4K.jpg" 
                 style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 2px solid #333; margin-bottom: 15px; filter: grayscale(100%);">
            <p style='font-size: 1.05rem; font-style: italic; margin-bottom: 15px; line-height: 1.4; color: #FFFFFF;'>
                «Il Tour non è solo una gara di ciclismo, nient'affatto. È una prova. Ti prova fisicamente, ti prova mentalmente e ti prova persino moralmente.»
            </p>
            <p style='font-size: 0.9rem; margin: 0;'><strong>— Lance Armstrong</strong></p>
            </div>
            """, unsafe_allow_html=True)

    with cit3:
        # Mark Cavendish
        st.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <img src="https://imgresizer.eurosport.com/unsafe/1200x0/filters:format(jpeg)/origin-imgresizer.eurosport.com/2021/06/29/3163795-64831628-2560-1440.jpg" 
                 style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 2px solid #333; margin-bottom: 15px; filter: grayscale(100%);">
            <p style='font-size: 1.05rem; font-style: italic; margin-bottom: 15px; line-height: 1.4; color: #FFFFFF;'>
                «Il ciclismo non è un gioco, è uno sport in cui si soffre. Ma il Tour de France è un livello di sofferenza completamente diverso.»
            </p>
            <p style='font-size: 0.9rem; margin: 0;'><strong>— Mark Cavendish</strong></p>
        </div>
        """, unsafe_allow_html=True)

        
elif st.session_state.pagina_corrente == "classifica":
    
    st.markdown("<h2 style='text-align: center; color: #000000; margin-bottom: 30px;'>🏆 Classifica e Albo d'Oro</h2>", unsafe_allow_html=True)
    
    if not df_storico.empty:
        
        # ==========================================
        # 1. CSS PER LA TENDINA NERA
        # ==========================================
        st.markdown("""
            <style>
            div[data-baseweb="select"] > div {
                background-color: #111111 !important; 
                color: #FFFFFF !important; 
                border-radius: 5px !important;
            }
            div[data-baseweb="popover"],
            div[data-baseweb="popover"] > div,
            div[data-baseweb="popover"] > div > div,
            div[data-baseweb="popover"] ul,
            ul[data-baseweb="menu"],
            ul[role="listbox"] {
                background-color: #111111 !important;
            }
            div[data-baseweb="popover"] li,
            div[data-baseweb="popover"] li span,
            ul[data-baseweb="menu"] li {
                color: #FFFFFF !important;
                background-color: transparent !important;
            }
            div[data-baseweb="popover"] li:hover,
            ul[data-baseweb="menu"] li:hover {
                background-color: #333333 !important;
            }
            .stSelectbox label {
                color: #000000 !important;
                font-weight: bold !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # ==========================================
        # 2. FILTRO ANNO E DATI
        # ==========================================
        anni_disponibili = sorted(df_storico['Year'].dropna().unique(), reverse=True)
        
        col_filtro, _ = st.columns([1, 3])
        with col_filtro:
            anno_selezionato = st.selectbox("Seleziona l'edizione:", anni_disponibili)
            
        st.markdown("<hr style='border: 1px solid #ccc; margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)

        df_anno = df_storico[df_storico['Year'] == anno_selezionato].reset_index(drop=True)
        
       # ==========================================
        # 3. IL PODIO
        # ==========================================
        st.markdown(f"<h3 style='color: #000000; margin-bottom: 20px; font-family: Georgia, serif;'>Il Podio dell'edizione {int(anno_selezionato)}</h3>", unsafe_allow_html=True)
        
        try:
            # Estrazione sicura dei dati
            rider_1 = df_anno.iloc[0].get("Rider", "N/D")
            tempo_1 = df_anno.iloc[0].get("Time", "N/D")
            
            rider_2 = df_anno.iloc[1].get("Rider", "N/D")
            gap_2 = df_anno.iloc[1].get("Gap", "N/D")
            
            rider_3 = df_anno.iloc[2].get("Rider", "N/D")
            gap_3 = df_anno.iloc[2].get("Gap", "N/D")

            # Stringa HTML/CSS appiattita a sinistra: crea i cilindri 3D SENZA riflesso
            html_podio = f"""
<style>
.podium-stage {{ display: flex; justify-content: center; align-items: flex-end; gap: 0px; margin-top: 60px; margin-bottom: 40px; }}
.podium-col {{ display: flex; flex-direction: column; align-items: center; width: 140px; }}
.rider-info {{ text-align: center; margin-bottom: 40px; color: #000000; font-family: 'Georgia', serif; z-index: 10; }}
.rider-name {{ font-size: 17px; font-weight: bold; line-height: 1.2; text-transform: uppercase; }}
.rider-time {{ font-size: 14px; color: #555; font-style: italic; margin-top: 5px; }}

/* Il corpo del cilindro nero lucido (senza riflesso) */
.cylinder {{
    position: relative;
    width: 140px;
    /* Gradiente per dare l'effetto di luce/cilindro curvo */
    background: linear-gradient(to right, #1a1a1a 0%, #666666 25%, #1a1a1a 60%, #000000 100%);
    /* Arrotonda la base inferiore */
    border-radius: 0 0 50% 50% / 0 0 25px 25px;
    display: flex;
    justify-content: center;
    align-items: center;
}}

/* La cima del cilindro (l'ovale colorato) */
.cylinder::before {{
    content: ""; 
    position: absolute; 
    top: -25px; 
    left: 0; 
    width: 100%; 
    height: 50px; 
    border-radius: 50%; 
    z-index: 2;
}}

/* Altezze dei gradini */
.c-1 {{ height: 200px; z-index: 3; box-shadow: 0px 10px 15px -5px rgba(0,0,0,0.5); }}
.c-2 {{ height: 140px; z-index: 2; box-shadow: 0px 10px 15px -5px rgba(0,0,0,0.5); }}
.c-3 {{ height: 110px; z-index: 1; box-shadow: 0px 10px 15px -5px rgba(0,0,0,0.5); }}

/* Colori delle cime: Oro, Argento, Bronzo */
.c-1::before {{ background: radial-gradient(ellipse at top left, #ffdf00, #b8860b); }}
.c-2::before {{ background: radial-gradient(ellipse at top left, #f0f0f0, #999999); }}
.c-3::before {{ background: radial-gradient(ellipse at top left, #ffa07a, #8b4513); }}

/* I numeri sul fronte del cilindro */
.pos-number {{ font-size: 55px; font-weight: bold; font-family: 'Arial', sans-serif; z-index: 4; margin-top: 15px; opacity: 0.9; }}
.n-1 {{ color: #ffd700; text-shadow: 2px 2px 4px #000; }}
.n-2 {{ color: #e0e0e0; text-shadow: 2px 2px 4px #000; }}
.n-3 {{ color: #cd7f32; text-shadow: 2px 2px 4px #000; }}
</style>

<div class="podium-stage">
<div class="podium-col">
<div class="rider-info">
<div class="rider-name">{rider_2}</div>
<div class="rider-time">{gap_2}</div>
</div>
<div class="cylinder c-2"><div class="pos-number n-2">2</div></div>
</div>

<div class="podium-col" style="margin-top: -30px;">
<div class="rider-info">
<div class="rider-name" style="font-size: 21px;">{rider_1}</div>
<div class="rider-time">{tempo_1}</div>
</div>
<div class="cylinder c-1"><div class="pos-number n-1">1</div></div>
</div>

<div class="podium-col">
<div class="rider-info">
<div class="rider-name">{rider_3}</div>
<div class="rider-time">{gap_3}</div>
</div>
<div class="cylinder c-3"><div class="pos-number n-3">3</div></div>
</div>
</div>
"""
            st.markdown(html_podio, unsafe_allow_html=True)

        except Exception as e:
            st.warning("Dati del podio incompleti per questa edizione.")

        st.markdown("<br><hr style='border: 1px dashed #ccc; margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        # ==========================================
        # 4. GRAFICI E METRICHE
        # ==========================================
        st.markdown("<h4 style='color: #000000;'>Dinamiche e Performance</h4>", unsafe_allow_html=True)
        col_stat1, col_stat2 = st.columns(2, gap="large")
        
        vincitore_anno = df_anno.iloc[0]
        # Check di sicurezza sui tempi
        tempi_validi = pd.notna(vincitore_anno.get('TotalSeconds')) and vincitore_anno.get('TotalSeconds', 0) > 0
        
        with col_stat1:
            # Titolo impostato su bianco (#FFFFFF)
            st.markdown("<p style='font-weight: bold; color: #FFFFFF;'>I distacchi della Top 10 (in minuti)</p>", unsafe_allow_html=True)
            
            if tempi_validi:
                df_top10 = df_anno.head(10).copy()
                
                # --- CONVERSIONE IN MINUTI ---
                df_top10['Gap (Minuti)'] = df_top10['GapSeconds'] / 60
                
                # --- TRUCCO PER L'ORDINAMENTO ---
                # 1. Ci assicuriamo che il Rank sia un numero intero pulito
                df_top10['Rank_Int'] = pd.to_numeric(df_top10['Rank'], errors='coerce').fillna(0).astype(int)
                
                # 2. Creiamo una nuova etichetta combinando Posizione (con zfill a 2 cifre) e Nome
                df_top10['Rider_Label'] = df_top10['Rank_Int'].astype(str).str.zfill(2) + "° " + df_top10['Rider']
                
                # 3. Impostiamo questa nuova colonna come indice per il grafico
                df_top10.set_index('Rider_Label', inplace=True)
                
                # Convertiamo in Altair per forzare lo sfondo nero e i testi bianchi
                df_bar_chart = df_top10.reset_index()
                grafico_barre = alt.Chart(df_bar_chart).mark_bar(color="#FFCC00").encode(
                    x=alt.X('Rider_Label:N', sort=None, title='', axis=alt.Axis(labelAngle=-45)),
                    y=alt.Y('Gap (Minuti):Q', title='Gap (Minuti)')
                ).configure(
                    background='black',
                    view=alt.ViewConfig(stroke='transparent'),
                    axis=alt.AxisConfig(
                        labelColor='white', 
                        titleColor='white', 
                        gridColor='#333333', 
                        domainColor='#333333', 
                        tickColor='white'
                    )
                )
                st.altair_chart(grafico_barre, use_container_width=True, theme=None)
            else:
                st.info("ℹ️ I dati sui distacchi cronometrici non sono disponibili per questa edizione.")
        with col_stat2:
            # 1. Titolo bianco (#FFFFFF)
            st.markdown("<p style='font-weight: bold; color: #FFFFFF;'>Storico del distacco tra 1° e 10° Classificato</p>", unsafe_allow_html=True)
            
            # --- CSS PER LO SLIDER GIALLO ---
            # Andiamo a "colorare" la barra e i pallini dello slider
            st.markdown("""
                <style>
                /* Colore del pallino dello slider */
                .stSlider [data-baseweb="slider"] [role="slider"] {
                    background-color: #FFCC00 !important;
                }
                /* Colore della barra riempita */
                .stSlider [data-baseweb="slider"] div[data-testid="stTickBar"] > div > div > div {
                    background-color: #FFCC00 !important;
                }
                </style>
            """, unsafe_allow_html=True)

            # Preparazione dei dati base
            df_gap_storico = df_storico.copy()
            df_gap_storico['Rank_Int'] = pd.to_numeric(df_gap_storico['Rank'], errors='coerce')
            df_decimi = df_gap_storico[df_gap_storico['Rank_Int'] == 10].copy()
            
            df_decimi = df_decimi[df_decimi['GapSeconds'].notna()]
            df_decimi = df_decimi[df_decimi['GapSeconds'] > 0]
            df_decimi['Gap (Minuti)'] = df_decimi['GapSeconds'] / 60
            
            df_chart = df_decimi[['Year', 'Gap (Minuti)']].dropna()
            
            # SLIDER PER IL RANGE DI ANNI
            min_year_disp = int(df_chart['Year'].min())
            max_year_disp = int(df_chart['Year'].max())
            
            range_anni = st.slider(
                "Seleziona il periodo storico da visualizzare:",
                min_value=min_year_disp,
                max_value=max_year_disp,
                value=(min_year_disp, max_year_disp) 
            )
            
            # Filtriamo il dataframe in base agli anni scelti con lo slider
            df_chart_filtered = df_chart[(df_chart['Year'] >= range_anni[0]) & (df_chart['Year'] <= range_anni[1])]
            
            # 4. Creiamo il grafico base con Altair (Linea GIALLA: #FFCC00)
            linea_storico = alt.Chart(df_chart_filtered).mark_line(color='#FFCC00', strokeWidth=2).encode(
                x=alt.X('Year:Q', 
                        title='Anno', 
                        axis=alt.Axis(format='d'), 
                        scale=alt.Scale(domain=[range_anni[0], range_anni[1]])),
                y=alt.Y('Gap (Minuti):Q', title='Gap (Minuti)')
            )
            
            # 4.1 Punti interattivi su tutta la linea (Punti GIALLI: #FFCC00)
            punti_storico = alt.Chart(df_chart_filtered).mark_circle(color='#FFCC00', size=50).encode(
                x=alt.X('Year:Q', scale=alt.Scale(domain=[range_anni[0], range_anni[1]])),
                y=alt.Y('Gap (Minuti):Q'),
                tooltip=[
                    alt.Tooltip('Year:Q', title='Anno', format='d'),
                    alt.Tooltip('Gap (Minuti):Q', title='Distacco (min)', format='.1f')
                ]
            )
            
            # 5. Punto rosso e linea tratteggiata per l'anno selezionato
            df_anno_sel = df_chart[df_chart['Year'] == int(anno_selezionato)]
            
            punto_rosso = alt.Chart(df_anno_sel).mark_circle(color='red', size=120, opacity=1).encode(
                x='Year:Q',
                y='Gap (Minuti):Q',
                tooltip=[
                    alt.Tooltip('Year:Q', title='Anno Selezionato', format='d'),
                    alt.Tooltip('Gap (Minuti):Q', title='Distacco (min)', format='.1f')
                ]
            )
            
            linea_vert_rossa = alt.Chart(df_anno_sel).mark_rule(color='red', strokeDash=[5, 5]).encode(
                x='Year:Q'
            )
            
            # 6. Sovrapposizione finale con aggiunta del tema nero
            grafico_completo = alt.layer(linea_storico, punti_storico, linea_vert_rossa, punto_rosso).configure(
                background='black', 
                view=alt.ViewConfig(stroke='transparent'), 
                axis=alt.AxisConfig(
                    labelColor='white', 
                    titleColor='white', 
                    gridColor='#333333', 
                    domainColor='#333333', 
                    tickColor='white' 
                )
            )
            
            # Mostriamo il grafico usando theme=None per bloccare il tema chiaro di Streamlit
            st.altair_chart(grafico_completo, use_container_width=True, theme=None)
        st.markdown("<hr style='border: 1px dashed #ccc; margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        
        c_met1, c_met2, c_met3 = st.columns(3)
        c_met1.metric("Distanza Totale", f"{vincitore_anno.get('Distance (km)', 'N/D')} km")
        c_met2.metric("Numero di Tappe", vincitore_anno.get('Number of stages', 'N/D'))
        
        if tempi_validi:
            ore_totali = vincitore_anno['TotalSeconds'] / 3600
            vel_media = vincitore_anno['Distance (km)'] / ore_totali
            c_met3.metric("Velocità Media Vincitore", f"{vel_media:.1f} km/h")
        else:
            c_met3.metric("Velocità Media Vincitore", "N/D")
        # ==========================================
        # 5. TABELLA DATI COMPLETI
        # ==========================================
        st.markdown("<h4 style='color: #000000; margin-top: 30px;'>Dati Completi dell'Edizione</h4>", unsafe_allow_html=True)
        st.dataframe(df_anno, use_container_width=True, hide_index=True)

    else:
        st.warning("Impossibile caricare i dati. Assicurati che il link sia corretto e il file accessibile.")


elif st.session_state.pagina_corrente == "corridori":
    # ==========================================
    # 1. CSS PER LA TENDINA NERA (COERENZA UI)
    # ==========================================
    st.markdown("""
        <style>
        div[data-baseweb="select"] > div {
            background-color: #111111 !important; 
            color: #FFFFFF !important; 
            border-radius: 5px !important;
        }
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] > div,
        div[data-baseweb="popover"] > div > div,
        div[data-baseweb="popover"] ul,
        ul[data-baseweb="menu"],
        ul[role="listbox"] {
            background-color: #111111 !important;
        }
        div[data-baseweb="popover"] li,
        div[data-baseweb="popover"] li span,
        ul[data-baseweb="menu"] li {
            color: #FFFFFF !important;
            background-color: transparent !important;
        }
        div[data-baseweb="popover"] li:hover,
        ul[data-baseweb="menu"] li:hover {
            background-color: #333333 !important;
        }
        .stSelectbox label {
            color: #000000 !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: center; color: #000000; margin-bottom: 30px;'>🏆 I Campioni della Grande Boucle</h2>", unsafe_allow_html=True)

    # ==========================================
    # 2. SELEZIONE ATLETA DA DF_TOUR_W
    # ==========================================
    if not df_tour_w.empty:
        # Creiamo la lista dalla colonna Winner
        lista_campioni = sorted(df_tour_w['Winner'].dropna().unique())
        
        col_sel, _ = st.columns([1.5, 2])
        with col_sel:
            vincitore_scelto = st.selectbox("Seleziona un vincitore:", lista_campioni)
        
        st.markdown("<hr style='border: 1px solid #ccc; margin-top: 10px; margin-bottom: 30px;'>", unsafe_allow_html=True)

        # ==========================================
        # 3. FILTRAGGIO DATI VITTORIE
        # ==========================================
        # Filtriamo TUTTE le righe del vincitore per contare gli anni
        storico_vittorie = df_tour_w[df_tour_w['Winner'] == vincitore_scelto].sort_values('Year')
        
        numero_vittorie = len(storico_vittorie)
        anni_vittoria = ", ".join(storico_vittorie['Year'].astype(str).tolist())
        
        # Per i dati biometrici prendiamo l'ultima riga (la vittoria più recente)
        dati_vincitore = storico_vittorie.iloc[-1]

        # ==========================================
        # 4. VISUALIZZAZIONE DATI TECNICI (COLONNE)
        # ==========================================
        col_bio, col_pps = st.columns([1.2, 2], gap="large")

        with col_bio:
            # Box Carta d'Identità (ora include il numero di vittorie e gli anni)
            st.markdown(f"""
                <div style="background-color: #000000; padding: 20px; border-radius: 10px; border-left: 8px solid #FFCC00;">
                    <h3 style="color: #FFCC00; margin-bottom: 5px;">{vincitore_scelto}</h3>
                    <p style="color: #ffffff; font-size: 1.1rem; margin-bottom: 2px;"><b>Paese:</b> {dati_vincitore.get('Country', 'N/D')}</p>
                    <p style="color: #ffffff; font-size: 0.9rem; font-style: italic;">{dati_vincitore.get('Team', 'Team N/D')}</p>
                    
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- PARAMETRI BIOMETRICI ---
            st.markdown("<h4 style='color: #000;'>Dati Antropometrici</h4>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)

            # 1. Gestione Altezza (Correzione virgola e precisione a 2 decimali)
            raw_h = str(dati_vincitore.get('height_(m)', '0')).replace(',', '.')

            try:
                val_h = float(raw_h)
                
                if val_h > 10: 
                    s_h = str(int(val_h))
                    txt_altezza = f"{s_h[0]}.{s_h[1:3]} m" 
                else:
                    txt_altezza = f"{val_h:.2f} m"
            except:
                txt_altezza = "N/D"

            # 2. Gestione Peso
            try:
                val_peso = float(str(dati_vincitore.get('weight_(Kg)', '0')).replace(',', '.'))
                txt_peso = f"{val_peso:.1f} kg" 
            except:
                txt_peso = "N/D"

            # Visualizzazione nelle colonne
            c1.metric("Altezza", txt_altezza)
            c1.metric("Peso", txt_peso)

            # 3. Età e BMI
            try:
                eta = int(dati_vincitore.get('age', 0))
                c2.metric("Età", f"{eta} anni")
            except:
                c2.metric("Età", "N/D")

            try:
                bmi_val = float(str(dati_vincitore.get('BMI', 0)).replace(',', '.'))
                c2.metric("BMI", f"{bmi_val:.1f}")
            except:
                c2.metric("BMI", "N/D")
                    
        with col_pps:
            # --- PROFILO DI POTENZA (PPS) ---
            st.markdown("<h4 style='color: #000;'>Analisi Tecnica (PPS)</h4>", unsafe_allow_html=True)
            tipo_pps = dati_vincitore.get('rider_type_(PPS)', 'N/D')
            simile_pps = dati_vincitore.get('close_rider_type_(PPS)', 'N/D')

            st.markdown(f"""
                <div style="background-color: #E6E1CF; padding: 20px; border-radius: 5px; color: #000; border: 1px solid #999;">
                    <p style="margin-bottom: 10px;"><b> Rider Type:</b><br><span style="font-size: 1.3rem; font-weight: bold; color: #d4af37;">{tipo_pps}</span></p>
                    <p style="margin-bottom: 0;"><b>Close Rider Type:</b><br><span>{simile_pps}</span></p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
        
        # ==========================================
        # 5. CARRIERA COMPLETA E CONFRONTO (Grafico Interattivo)
        # ==========================================
        st.markdown("<hr style='border: 1px dashed #ccc; margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #000; font-weight: bold;'>Analisi Comparativa della Carriera</h4>", unsafe_allow_html=True)
        
        # 1. Normalizziamo il nome del ciclista principale
        nome_principale = str(vincitore_scelto).strip().upper()
        
        # 2. Creiamo una lista pulita di tutti i corridori per il menu a tendina
        df_storico['Rider_Norm'] = df_storico['Rider'].astype(str).str.strip().str.upper()
        tutti_i_corridori = sorted(df_storico['Rider'].astype(str).str.strip().unique())
        
        # 3. Selezione sfidanti (Multi-selezione)
        st.markdown("""
            <style>
            div[data-testid="stMultiSelect"] label p {
                color: #000000 !important;
                font-weight: bold !important;
                font-size: 1.1rem !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        sfidanti = st.multiselect(
            "Aggiungi altri ciclisti al grafico per un confronto testa a testa:", 
            options=[c for c in tutti_i_corridori if str(c).strip().upper() != nome_principale],
            help="Seleziona uno o più nomi dall'archivio storico"
        )
        
        # 4. Prepariamo la lista di tutti i nomi da cercare (Principale + Sfidanti)
        nomi_da_cercare = [nome_principale] + [str(s).strip().upper() for s in sfidanti]
        
        # 5. Funzione di ricerca elastica per più nomi contemporaneamente
        def match_multiplo(nome_db):
            for nome in nomi_da_cercare:
                if nome in nome_db or nome_db in nome:
                    return True
            return False
            
        # Filtriamo il database storico
        maschera_ricerca = df_storico['Rider_Norm'].apply(match_multiplo)
        df_plot = df_storico[maschera_ricerca].copy()
        
        if not df_plot.empty:
            # Convertiamo il Rank in formato numerico (fondamentale per l'asse Y)
            # errors='coerce' trasforma eventuali testi come "DNF" (Ritirato) in NaN
            df_plot['Rank_Num'] = pd.to_numeric(df_plot['Rank'], errors='coerce')
            
            # Filtriamo le righe valide per il grafico
            df_grafico = df_plot.dropna(subset=['Rank_Num'])
            
            # --- CREAZIONE GRAFICO ALTAIR NERO ---
            grafico_carriera = alt.Chart(df_grafico).mark_line(
                point=alt.OverlayMarkDef(size=80, opacity=1, filled=True), 
                strokeWidth=3
            ).encode(
                x=alt.X('Year:O', title='Anno', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Rank_Num:Q', title='Posizione Finale', scale=alt.Scale(reverse=True, domainMin=1)),
                color=alt.Color('Rider:N', title='Atleta', scale=alt.Scale(scheme='set1')),
                # Il Tooltip genera la finestra riassuntiva al passaggio del mouse
                tooltip=[
                    alt.Tooltip('Rider:N', title='Ciclista'),
                    alt.Tooltip('Year:O', title='Anno'),
                    alt.Tooltip('Rank:N', title='Classifica Generale'),
                    alt.Tooltip('Team:N', title='Squadra'),
                    alt.Tooltip('Times:N', title='Tempo') # Se la tua colonna si chiama 'Times', correggi qui
                ]
            ).properties(
                height=450
            ).interactive().configure(
                background='black', # Sfondo generale nero
                view=alt.ViewConfig(stroke='transparent'), # Rimuove il bordo quadrato grigio
                axis=alt.AxisConfig(
                    labelColor='white', # Testo dei numeri (es. anni e posizioni) in bianco
                    titleColor='white', # Titolo degli assi in bianco
                    gridColor='#333333', # Griglia grigio scuro
                    domainColor='#333333', # Linea base degli assi grigio scuro
                    tickColor='white' # Tacchette bianche
                ),
                legend=alt.LegendConfig(
                    labelColor='white', # Nomi degli atleti in legenda bianchi
                    titleColor='white' # Titolo della legenda bianco
                )
            )
            
            # Mostriamo il grafico usando theme=None per bloccare il tema chiaro di Streamlit
            st.altair_chart(grafico_carriera, use_container_width=True, theme=None)
            
            
    else:
        st.warning("Caricamento del dataset vincitori non riuscito.")


elif st.session_state.pagina_corrente == "tappe":
    
    # ==========================================
    # INIEZIONE CSS PER DESIGN UNIFORMATO
    # ==========================================
    st.markdown("""
        <style>
        /* 1. Forza il testo dei Radio Button e delle loro opzioni al NERO */
        div[data-testid="stRadio"] label, 
        div[data-testid="stRadio"] p,
        div[data-testid="stRadio"] span {
            color: #000000 !important;
        }        
        div[data-baseweb="select"] > div {
            background-color: #111111 !important; 
            color: #FFFFFF !important; 
            border-radius: 5px !important;
        }
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] > div,
        div[data-baseweb="popover"] > div > div,
        div[data-baseweb="popover"] ul,
        ul[data-baseweb="menu"],
        ul[role="listbox"] {
            background-color: #111111 !important;
        }
        div[data-baseweb="popover"] li,
        div[data-baseweb="popover"] li span,
        ul[data-baseweb="menu"] li {
            color: #FFFFFF !important;
            background-color: transparent !important;
        }
        div[data-baseweb="popover"] li:hover,
        ul[data-baseweb="menu"] li:hover {
            background-color: #333333 !important;
        }
        .stSelectbox label {
            color: #000000 !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)
    # --- PREPARAZIONE DATI ---
    df_stage_h['Year'] = df_stage_h['Year'].fillna(0).astype(int)

    # ==========================================
    # 0. INTRODUZIONE: LA MAPPA STORICA
    # ==========================================

    url_mappa = "https://preview.redd.it/map-of-all-the-stages-in-the-history-of-the-tour-de-france-v0-v1t2yrg7zzyf1.jpeg?width=1080&crop=smart&auto=webp&s=16442894182572aebe679320c02811e74f233f67"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(url_mappa, width=650)
        
        st.markdown(
            """
            <p style='color: white; text-align: center; font-size: 0.9rem; margin-top: -10px; font-family: sans-serif;'>
                La fitta rete di tutte le tappe corse nella storia del Tour de France: un viaggio attraverso oltre un secolo di ciclismo.
            </p>
            """, 
            unsafe_allow_html=True
        )
    
    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 🎛️ CONTROLLO GLOBALE: SLIDER ANNI
    # ==========================================
    
   # 1. Aggiungiamo il CSS per lo sfondo nero e il testo dello slider bianco
    st.markdown(
        """
        <style>
        [data-testid="stSlider"] {
            background-color: #000000;
            padding: 15px 20px;
            border-radius: 8px;
        }
        [data-testid="stWidgetLabel"] p {
            color: #ffffff !important;
        }
        [data-testid="stSliderTickBarMin"], 
        [data-testid="stSliderTickBarMax"], 
        div[data-testid="stSlider"] div {
            color: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 2. Il tuo markdown: ho cambiato 'color: black' in 'color: white'
    st.markdown("<p style='font-weight: bold; color: black; font-family: sans-serif; font-size: 1.2rem;'>Esplora i Dati Storici</p>", unsafe_allow_html=True)

    # 3. La tua logica per i dati storici (invariata)
    anno_min_assoluto = int(df_stage_h[df_stage_h['Year'] > 0]['Year'].min())
    anno_max_assoluto = int(df_stage_h['Year'].max())

    anno_min, anno_max = st.slider(
        "Seleziona il periodo storico da visualizzare nei grafici sottostanti:",
        min_value=anno_min_assoluto,
        max_value=anno_max_assoluto,
        value=(anno_min_assoluto, anno_max_assoluto), 
        step=1
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 1. STORICO: DISTANZA TOTALE E MEDIA NEL TEMPO
    # ==========================================
    col_dist1, col_dist2 = st.columns(2)

    with col_dist1:
        df_dist_filtered = df_stage_h[(df_stage_h['Year'] >= anno_min) & (df_stage_h['Year'] <= anno_max)]
        df_distanza = df_dist_filtered.groupby('Year')['TotalTDFDistance'].max().reset_index()
        df_distanza = df_distanza.set_index('Year').reindex(range(anno_min, anno_max + 1)).reset_index()
        
        fig_dist = px.line(df_distanza, x='Year', y='TotalTDFDistance', 
                           labels={'TotalTDFDistance': '', 'Year': 'Anno'}, markers=True)
        fig_dist.update_traces(line_color='#FFCC00', line_width=3, marker=dict(size=4, color='white'), connectgaps=False)
        
        fig_dist.add_vrect(x0=1914.5, x1=1918.5, fillcolor="#888888", opacity=0.2, layer="below", line_width=0,
                           annotation_text="I Guerra Mondiale", annotation_position="inside bottom left",
                           annotation_font=dict(color="#AAAAAA", size=11, family="sans-serif"), annotation_textangle=-90)
        fig_dist.add_vrect(x0=1939.5, x1=1946.5, fillcolor="#888888", opacity=0.2, layer="below", line_width=0,
                           annotation_text="II Guerra Mondiale", annotation_position="inside bottom left",
                           annotation_font=dict(color="#AAAAAA", size=11, family="sans-serif"), annotation_textangle=-90)

        fig_dist.update_layout(
            title=dict(text="<b>Distanza Totale (km)</b>", font=dict(color="white", size=18, family="sans-serif")),
            plot_bgcolor="black", 
            paper_bgcolor="black", 
            font=dict(color="white", family="sans-serif"),
            height=380, margin=dict(l=0, r=0, t=50, b=0), 
            xaxis=dict(range=[anno_min, anno_max])
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_dist2:
        df_dist_avg = df_dist_filtered.groupby('Year').agg({'TotalTDFDistance': 'max', 'Stages': 'count'}).reset_index()
        df_dist_avg['Distanza_Media_Tappa'] = df_dist_avg['TotalTDFDistance'] / df_dist_avg['Stages']
        df_dist_avg = df_dist_avg.set_index('Year').reindex(range(anno_min, anno_max + 1)).reset_index()
        
        fig_avg_dist = px.area(df_dist_avg, x='Year', y='Distanza_Media_Tappa',
                               labels={'Distanza_Media_Tappa': '', 'Year': 'Anno'})
        fig_avg_dist.update_traces(line_color='#FF6666', fillcolor='rgba(255, 102, 102, 0.3)', connectgaps=False)
        
        fig_avg_dist.add_vrect(x0=1914.5, x1=1918.5, fillcolor="#888888", opacity=0.2, layer="below", line_width=0,
                               annotation_text="I Guerra Mondiale", annotation_position="inside bottom left",
                               annotation_font=dict(color="#AAAAAA", size=11, family="sans-serif"), annotation_textangle=-90)
        fig_avg_dist.add_vrect(x0=1939.5, x1=1946.5, fillcolor="#888888", opacity=0.2, layer="below", line_width=0,
                               annotation_text="II Guerra Mondiale", annotation_position="inside bottom left",
                               annotation_font=dict(color="#AAAAAA", size=11, family="sans-serif"), annotation_textangle=-90)

        fig_avg_dist.update_layout(
            title=dict(text="<b>Intensità: Km Medi per Tappa</b>", font=dict(color="white", size=18, family="sans-serif")),
            plot_bgcolor="black", 
            paper_bgcolor="black", 
            font=dict(color="white", family="sans-serif"),
            height=380, margin=dict(l=0, r=0, t=50, b=0),
            xaxis=dict(range=[anno_min, anno_max])
        )
        st.plotly_chart(fig_avg_dist, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 2. STORICO: VELOCITÀ MEDIA 
    # ==========================================
    
    df_vincitori = df_storico[(df_storico['Rank'] == 1) | (df_storico['Rank'] == '1')].copy()
    df_vincitori = df_vincitori[df_vincitori['TotalSeconds'].notna() & (df_vincitori['TotalSeconds'] > 0)]
    df_vincitori['Velocità Media (km/h)'] = df_vincitori['Distance (km)'] / (df_vincitori['TotalSeconds'] / 3600)
    
    df_vincitori_filtered = df_vincitori[(df_vincitori['Year'] >= anno_min) & (df_vincitori['Year'] <= anno_max)]
    df_vincitori_chart = df_vincitori_filtered[['Year', 'Velocità Media (km/h)']].set_index('Year').reindex(range(anno_min, anno_max + 1)).reset_index()

    fig_vel = px.line(df_vincitori_chart, x='Year', y='Velocità Media (km/h)', 
                      labels={'Velocità Media (km/h)': 'Velocità Media (km/h)', 'Year': 'Anno'}, markers=True)
    fig_vel.update_traces(line_color='#FFCC00', line_width=3, marker=dict(size=5, color='white'), connectgaps=False)
    
    fig_vel.add_vrect(x0=1914.5, x1=1918.5, fillcolor="#888888", opacity=0.2, layer="below", line_width=0,
                      annotation_text="I Guerra Mondiale", annotation_position="inside bottom left",
                      annotation_font=dict(color="#AAAAAA", size=11, family="sans-serif"), annotation_textangle=-90)
    fig_vel.add_vrect(x0=1939.5, x1=1946.5, fillcolor="#888888", opacity=0.2, layer="below", line_width=0,
                      annotation_text="II Guerra Mondiale", annotation_position="inside bottom left",
                      annotation_font=dict(color="#AAAAAA", size=11, family="sans-serif"), annotation_textangle=-90)

    try:
        y_1998 = df_vincitori[df_vincitori['Year'] == 1998]['Velocità Media (km/h)'].iloc[0]
        y_2006 = df_vincitori[df_vincitori['Year'] == 2006]['Velocità Media (km/h)'].iloc[0]

        fig_vel.add_scatter(x=[1998, 2006], y=[y_1998, y_2006], mode='lines', line=dict(color='#FF3333', width=2, dash='dash'), hoverinfo='skip', showlegend=False)

        anni_buco = list(range(1999, 2006))
        step = (y_2006 - y_1998) / (2006 - 1998)
        y_buco = [y_1998 + step * (anno - 1998) for anno in anni_buco]
        testo_hover = ["<b>Squalifiche per Doping</b><br>I titoli di L. Armstrong (1999-2005) e F. Landis (2006)<br>stati cancellati e mai riassegnati."] * len(anni_buco)

        fig_vel.add_scatter(x=anni_buco, y=y_buco, mode='markers', marker=dict(size=7, color='#FF3333', symbol='x', line=dict(width=2)),
                            hoverinfo='text', hovertext=testo_hover, showlegend=False)
        
        fig_vel.add_vrect(x0=1998.5, x1=2006, fillcolor="#888888", opacity=0.2, layer="below", line_width=0,
                          annotation_text="Titoli Revocati", annotation_position="inside bottom left",
                          annotation_font=dict(color="#AAAAAA", size=11, family="sans-serif"), annotation_textangle=-90)
    except Exception as e:
        pass 

    fig_vel.update_layout(
        title=dict(text="<b>L'evoluzione della Velocità Media</b>", font=dict(color="white", size=20, family="sans-serif")),
        plot_bgcolor="black", 
        paper_bgcolor="black", 
        font=dict(color="white", family="sans-serif"),
        height=450, margin=dict(l=0, r=0, t=60, b=0), 
        xaxis=dict(range=[anno_min, anno_max])
    )
    st.plotly_chart(fig_vel, use_container_width=True)
    
    # Sostituita la linea gialla con una linea grigia neutra per staccare le sezioni
    st.markdown("<hr style='border: 1px solid #CCCCCC; margin-top: 30px; margin-bottom: 30px;'>", unsafe_allow_html=True)
    # ==========================================
    # FINE SEZIONE STORICA 
    # ==========================================
    
    st.markdown("<hr style='border: 1px solid #FFCC00; margin-top: 30px; margin-bottom: 30px;'>", unsafe_allow_html=True)
    
    # I titoletti da qui in giù sono NERI per risaltare sullo sfondo chiaro generale
    st.markdown("<p style='font-weight: bold; color: black; font-family: sans-serif; font-size: 1.2rem;'>Dettaglio Percorso e Leaderboard</p>", unsafe_allow_html=True)

    lista_anni = sorted(df_stage_h['Year'].unique(), reverse=True)
    lista_anni = [anno for anno in lista_anni if anno > 0]
    anno_scelto = st.selectbox("Seleziona un'edizione per vedere i dettagli:", lista_anni)

    df_anno = df_stage_h[df_stage_h['Year'] == anno_scelto].sort_values('Stages').copy()

    if not df_anno.empty:
        distanza_tot = df_anno['TotalTDFDistance'].iloc[0] if 'TotalTDFDistance' in df_anno.columns else "N/D"
        num_tappe = len(df_anno)
        
        df_anno['Vincitore_Clean'] = df_anno['Winner of stage'].apply(
            lambda x: str(x).split('(')[0].strip() if pd.notnull(x) else "N/D"
        )
        df_anno['Team'] = df_anno['Winner of stage'].str.extract(r'\((.*?)\)')
        df_anno['Team'] = df_anno['Team'].fillna('Indipendente/Sconosciuto')

        vittorie_count = df_anno['Vincitore_Clean'].value_counts()
        top_rider = vittorie_count.index[0] if not vittorie_count.empty and vittorie_count.index[0] != "N/D" else "N/D"
        n_vittorie = vittorie_count.iloc[0] if not vittorie_count.empty else 0

        vincitore_finale = "N/D"
        cambi_maglia = "N/D"
        colonna_leader = 'Yellow Jersey' 
        
        if colonna_leader in df_anno.columns:
            leader_validi = df_anno[colonna_leader].dropna()
            if not leader_validi.empty:
                vincitore_finale = leader_validi.iloc[-1]
                cambi_maglia = (df_anno[colonna_leader] != df_anno[colonna_leader].shift()).sum() - 1
                cambi_maglia = max(0, cambi_maglia)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Distanza Totale", f"{distanza_tot} km")
        m2.metric("Vincitore Finale", vincitore_finale)
        m3.metric("Cannibale (Vittorie)", top_rider, f"{n_vittorie} tappe")
        m4.metric("Cambi Maglia Gialla", cambi_maglia)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"<h3 style='color: black;'>Evoluzione della Leadership nel {anno_scelto}</h3>", unsafe_allow_html=True)
        
        maglie_config = {
            "Gialla": {
                "col": "Yellow Jersey", 
                "color": "#FFCC00", 
                "img": "https://www.bobshop.com/media/92/7a/02/1776411535/11346-1_1.png?ts=1776411535",
                "anno_intro": 1919,
                "storia": "La Maglia Gialla è stata introdotta nel 1919. Prima di allora, il leader veniva identificato solo da un bracciale verde."
            },
            "Verde": {
                "col": "Green jersey", 
                "color": "#009900", 
                "img": "https://lh3.googleusercontent.com/d/1d1GLPgO6NHqt4bguSBdXjs8NowirbXAu",
                "anno_intro": 1953,
                "storia": "La Maglia Verde (classifica a punti) è stata creata nel 1953 per celebrare il 50º anniversario del Tour de France."
            },
            "A Pois": {
                "col": "Polka-dot jersey", 
                "color": "#FF0000", 
                "img": "https://lh3.googleusercontent.com/d/1sOEebeyDAuhP0Mt6I5L4poKbahfv3xky",
                "anno_intro": 1975,
                "storia": "Sebbene il Gran Premio della Montagna esista dal 1933, la celebre Maglia a Pois bianchi e rossi è nata ufficialmente solo nel 1975!"
            },
            "Bianca": {
                "col": "White jersey", 
                "color": "#CCCCCC", 
                "img": "https://lh3.googleusercontent.com/d/1DAYUL8bk7eYxd83opOKJCkYT_afuKWdp",
                "anno_intro": 1975,
                "storia": "La Maglia Bianca, riservata al miglior giovane (attualmente Under-25), è stata istituita a partire dal 1975."
            }
        }

        scelta_maglia = st.radio(
            "Seleziona la maglia:", 
            list(maglie_config.keys()), 
            horizontal=True
        )

        col_selezionata = maglie_config[scelta_maglia]["col"]
        colore_linea = maglie_config[scelta_maglia]["color"]
        url_immagine = maglie_config[scelta_maglia]["img"]
        anno_introduzione = maglie_config[scelta_maglia]["anno_intro"]

        if anno_scelto < anno_introduzione:
            # Creiamo il testo del messaggio
            testo_storia = f"🕰️ <b>Un po' di storia:</b> Nel {anno_scelto} questa maglia non esisteva ancora. {maglie_config[scelta_maglia]['storia']}"
            
            # Lo inseriamo in un div HTML personalizzato tramite st.markdown
            st.markdown(
                f"""
                <div style="background-color: #f5f0e6; border-left: 5px solid #FFCC00; padding: 15px; border-radius: 5px; color: black; font-family: sans-serif;">
                    {testo_storia}
                </div>
                """, 
                unsafe_allow_html=True
            )
        elif col_selezionata in df_anno.columns and not df_anno[col_selezionata].dropna().empty:
            df_leader = df_anno.dropna(subset=[col_selezionata]).copy()
            ordine_cronologico = df_leader[col_selezionata].drop_duplicates().tolist()
            
            fig_leader = px.line(df_leader, x='Stages', y=col_selezionata)
            fig_leader.update_traces(line=dict(color=colore_linea, width=3))
            
            for index, row in df_leader.iterrows():
                fig_leader.add_layout_image(
                    dict(
                        source=url_immagine, xref="x", yref="y",
                        x=row['Stages'], y=row[col_selezionata],
                        sizex=1.2, sizey=0.9,
                        xanchor="center", yanchor="middle", layer="above"
                    )
                )
            
            min_tappa = df_leader['Stages'].min() - 1
            max_tappa = df_leader['Stages'].max() + 1
            num_corridori = len(ordine_cronologico)
            
            fig_leader.update_layout(
                yaxis=dict(
                    title="", categoryorder='array', categoryarray=ordine_cronologico[::-1],
                    range=[-0.5, max(0.5, num_corridori - 0.5)],
                    showgrid=True, gridwidth=1, gridcolor='#333333'
                ), 
                xaxis=dict(
                    title="Tappa", tickmode='linear', dtick=1,
                    range=[min_tappa, max_tappa],
                    showgrid=True, gridwidth=1, gridcolor='#333333'
                ),
                height=max(300, num_corridori * 60), 
                showlegend=False, 
                paper_bgcolor="black",   
                plot_bgcolor="black",    
                font=dict(color="white"), 
                margin=dict(l=0, r=0, t=20, b=0)
            )
            st.plotly_chart(fig_leader, use_container_width=True)
            
        else:
            st.warning(f"Dati non disponibili per la {scelta_maglia} nell'edizione {anno_scelto}.")
            
        # ==========================================
        # 4. DASHBOARD MULTI-LEADER E STATISTICHE
        # ==========================================
        col_gialla = 'Yellow Jersey'
        col_verde = 'Green' 
        col_pois = 'Polka'  
        col_bianca = 'White'

        maglie_presenti = [col for col in [col_gialla, col_verde, col_pois, col_bianca] if col in df_anno.columns]
        
        if len(maglie_presenti) > 1:
            st.markdown("<h3 style='color: black;'>👕 I detentori delle Maglie tappa per tappa</h3>", unsafe_allow_html=True)
            df_maglie = df_anno[['Stages'] + maglie_presenti].copy()
            st.dataframe(df_maglie, use_container_width=True, hide_index=True)
            
        st.markdown("<br>", unsafe_allow_html=True)

        col_chart1, col_chart2, col_table = st.columns([1, 1, 1.5], gap="medium")

        with col_chart1:
            st.markdown("<b style='color: black;'>Plurivincitori</b>", unsafe_allow_html=True)
            df_top10 = vittorie_count.reset_index()
            df_top10.columns = ['Atleta', 'Vittorie']
            df_top10 = df_top10[df_top10['Atleta'] != 'N/D'].head(8) 
            
            fig_vittorie = px.bar(df_top10, y='Atleta', x='Vittorie', orientation='h', color_discrete_sequence=['#FFCC00'])
            fig_vittorie.update_layout(yaxis={'categoryorder':'total ascending', 'title':''}, xaxis={'title': 'Vittorie'},
                                       height=350, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_vittorie, use_container_width=True)

        with col_chart2:
            st.markdown("<b style='color: black;'>Dominanza Squadre</b>", unsafe_allow_html=True)
            team_counts = df_anno['Team'].value_counts().reset_index()
            team_counts.columns = ['Team', 'Vittorie']
            team_counts = team_counts[team_counts['Team'] != 'Indipendente/Sconosciuto'].head(8) 
            
            fig_team = px.pie(
                team_counts, 
                values='Vittorie', 
                names='Team', 
                hole=0.6, 
                color_discrete_sequence=px.colors.sequential.YlOrBr[::-1] 
            )
            
            fig_team.update_traces(
                textposition='inside', 
                textinfo='label+value',
                hovertemplate='<b>%{label}</b><br>Vittorie: %{value}<extra></extra>',
                marker=dict(line=dict(color='#000000', width=2)) 
            )
            fig_team.update_layout(
                showlegend=False, 
                height=350, 
                margin=dict(l=10, r=10, t=20, b=10), 
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_team, use_container_width=True)
        
        # ==========================================
        # MAPPA INTERATTIVA
        # ==========================================
        st.markdown("<hr style='border: 1px solid #FFCC00; margin-top: 30px; margin-bottom: 30px;'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: black;'>Mappa del Percorso: {anno_scelto}</h3>", unsafe_allow_html=True)

        if not df_coords.empty:
            df_coords_anno = df_coords[df_coords['Year'] == anno_scelto].copy()
            df_map_plot = df_coords_anno.dropna(subset=['start_lat', 'start_lon', 'end_lat', 'end_lon'])

            if not df_map_plot.empty:
                view_state = pdk.ViewState(
                    latitude=46.2276, 
                    longitude=2.2137, 
                    zoom=5, 
                    pitch=0
                )

                line_layer = pdk.Layer(
                    "LineLayer",
                    df_map_plot,
                    get_source_position="[start_lon, start_lat]",
                    get_target_position="[end_lon, end_lat]",
                    get_color="[255, 204, 0, 200]",
                    get_width=5,
                    pickable=True,
                )

                start_point_layer = pdk.Layer(
                    "ScatterplotLayer",
                    df_map_plot,
                    get_position="[start_lon, start_lat]",
                    get_color="[0, 0, 0, 255]",
                    get_radius=8000,
                    pickable=True,
                )

                end_point_layer = pdk.Layer(
                    "ScatterplotLayer",
                    df_map_plot,
                    get_position="[end_lon, end_lat]",
                    get_color="[0, 0, 0, 255]",
                    get_radius=8000,
                    pickable=True,
                )

                st.pydeck_chart(pdk.Deck(
                    map_style="light", 
                    initial_view_state=view_state,
                    layers=[line_layer, start_point_layer, end_point_layer], 
                    tooltip={
                        "html": "<b>Tappa {Stages}</b><br/>Da: {Start}<br/>A: {End}",
                        "style": {"color": "white", "backgroundColor": "black"}
                    }
                ))
            else:
                st.info(f"Nessun dato geografico trovato per l'anno {anno_scelto}.")
        
        with col_table:
            st.markdown("<b style='color: black;'>Dettaglio Percorso</b>", unsafe_allow_html=True)
            cols_to_show = ['Stages', 'Start', 'End', 'Vincitore_Clean']
            df_display = df_anno[cols_to_show].copy()
            st.dataframe(df_display, use_container_width=True, hide_index=True, height=350)

    
    
elif st.session_state.pagina_corrente == "teams":
        
        # --- 1. INIEZIONE CSS PER SELECTBOX SCURI E LABEL NERA ---
        css_selectbox_scuro = """
        <style>
            div[data-testid="stSelectbox"] label p {
                color: #000000 !important;
                font-family: 'Georgia', serif !important;
            }
            div[data-baseweb="select"] > div {
                background-color: #111111 !important;
                border: 1px solid #ff0000 !important;
                border-radius: 4px !important;
            }
            div[data-baseweb="select"] span {
                color: #ffffff !important;
                font-family: 'Georgia', serif !important;
                font-size: 16px !important;
            }
            div[data-baseweb="select"] div[data-testid="stSelectbox"] svg,
            div[data-baseweb="select"] svg {
                color: #ffffff !important;
            }
            div[data-baseweb="popover"] div[role="listbox"],
            div[data-baseweb="popover"] ul {
                background-color: #111111 !important;
                border: 1px solid #333333 !important;
            }
            div[data-baseweb="popover"] ul li {
                color: #ffffff !important;
                font-family: 'Georgia', serif !important;
                background-color: #111111 !important;
                padding-top: 10px !important;
                padding-bottom: 10px !important;
            }
            div[data-baseweb="popover"] ul li:hover, 
            div[data-baseweb="popover"] ul li[aria-selected="true"],
            div[data-baseweb="popover"] ul li[aria-selected="true"]:hover {
                background-color: #2b2d30 !important;
                color: #ffffff !important;
            }
        </style>
        """
        st.markdown(css_selectbox_scuro, unsafe_allow_html=True)

        # --- 2. HEADER DELLA PAGINA (Testo Nero) ---
        st.markdown('<h1 class="vintage-title" style="color: #000000;">Analisi Team</h1>', unsafe_allow_html=True)
        st.markdown('<p class="journal-subtitle" style="color: #000000;">Esplora le performance storiche, la composizione e il palmarès delle squadre.</p>', unsafe_allow_html=True)

        # --- 3. GESTIONE DATI STORICI E FILTRI ANOMALIE ---
        anni_revocati = [1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006]
        
        teams_disponibili = sorted(df_storico['Team'].dropna().unique())
        team_selezionato = st.selectbox("Seleziona una squadra dal menu:", teams_disponibili)
        
        st.markdown('<hr class="vintage-divider">', unsafe_allow_html=True)

        # Filtraggio dataset principale
        df_team_storico = df_storico[df_storico['Team'] == team_selezionato].copy()
        df_team_storico['Rank_Num'] = pd.to_numeric(df_team_storico['Rank'], errors='coerce')

        
        import unicodedata
        import re

        def pulisci_e_ordina_nome(nome):
            if pd.isna(nome): return ""
            s = str(nome)
            s = re.sub(r'\(.*?\)', '', s) # Rimuove tutto tra parentesi es. (SLO)
            s = re.sub(r'[^a-zA-Z\s]', '', s) # Rimuove asterischi, numeri, punteggiatura
            s = s.lower().strip()
            s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
            parole = sorted(s.split())
            return " ".join(parole)

        # Puliamo i dataset per il merge
        df_stage_h_clean = df_stage_h.copy()
        df_stage_h_clean['Winner_Clean'] = df_stage_h_clean['Winner of stage'].apply(pulisci_e_ordina_nome)
        df_stage_h_clean['Yellow_Clean'] = df_stage_h_clean['Yellow Jersey'].apply(pulisci_e_ordina_nome)
        df_stage_h_clean['Green_Clean'] = df_stage_h_clean['Green jersey'].apply(pulisci_e_ordina_nome)
        df_stage_h_clean['Pois_Clean'] = df_stage_h_clean['Polka-dot jersey'].apply(pulisci_e_ordina_nome)

        df_storico_clean_all = df_storico[['Year', 'Rider', 'Team']].drop_duplicates().copy()
        df_storico_clean_all['Rider_Clean'] = df_storico_clean_all['Rider'].apply(pulisci_e_ordina_nome)
        
        df_team_storico['Rider_Clean'] = df_team_storico['Rider'].apply(pulisci_e_ordina_nome)

        # Merge tappe vinte individualmente dai corridori
        df_merge_tappe_individuali = pd.merge(
            df_stage_h_clean, 
            df_storico_clean_all, 
            left_on=['Year', 'Winner_Clean'], right_on=['Year', 'Rider_Clean'], how='inner'
        )
        df_tappe_team_individuali = df_merge_tappe_individuali[df_merge_tappe_individuali['Team'] == team_selezionato]

        # Recuperiamo anche le Cronosquadre (TTT) vinte direttamente dal Team
        df_tappe_ttt = df_stage_h_clean[df_stage_h_clean['Winner of stage'].str.contains(str(team_selezionato), case=False, na=False)].copy()
        df_tappe_ttt['Team'] = team_selezionato
        
        # Uniamo le vittorie individuali con quelle di squadra
        df_tappe_team = pd.concat([df_tappe_team_individuali, df_tappe_ttt], ignore_index=True)

        # --- 4. FUNZIONE HELP PER GRAFICI PLOTLY (Testo Bianco Puro) ---
        def applica_tema_vintage(fig):
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Georgia, serif", color="#FFFFFF"), 
                title_font_color="#FFFFFF",
                title_font_size=18,
                margin=dict(l=40, r=40, t=60, b=40)
            )
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.15)', title_font=dict(color="#FFFFFF"), tickfont=dict(color="#FFFFFF"))
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.15)', title_font=dict(color="#FFFFFF"), tickfont=dict(color="#FFFFFF"))
            return fig

        # --- 5. SEZIONE 1: KPI GENERALI DEL TEAM (Versione Sfondo Nero) ---
        vittorie_df = df_team_storico[(df_team_storico['Rank_Num'] == 1) & (~df_team_storico['Year'].isin(anni_revocati))]
        vittorie_totali = len(vittorie_df)
        
        miglior_piazzamento = int(df_team_storico['Rank_Num'].min()) if not df_team_storico['Rank_Num'].isna().all() else "N/A"
        partecipazioni = df_team_storico['Year'].nunique()

        # Nuova iniezione CSS specifica per i KPI Neri
        css_vintage_kpis = """
        <style>
            .vintage-kpi-block-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 15px;
                margin-bottom: 25px;
            }
            .vintage-kpi-block-title {
                color: #FFFFFF; 
                font-family: 'Georgia', serif !important;
                font-size: 22px;
                font-weight: bold;
                text-align: center;
                text-transform: uppercase;
                margin: 0;
            }
            .vintage-card-container-uniform {
                display: flex;
                gap: 15px;
                justify-content: center;
                width: 100%;
            }
            .vintage-card-uniform {
                flex: 1;
                padding: 15px;
                text-align: center;
                /* Background Nero Puro */
                background-color: #000000 !important; 
                /* Bordo Nero */
                border: 2px solid #000000 !important; 
                border-radius: 4px !important;
                /* Ombra leggera per staccarlo dallo sfondo generale (se non è nero) */
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            }
            .vintage-card-uniform h4 {
                margin: 0;
                /* Testo Bianco per i titoli interni */
                color: #FFFFFF !important;
                font-family: 'Georgia', serif !important;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .vintage-card-uniform h2 {
                margin: 10px 0 0 0;
                /* Testo Bianco Puro per i numeri */
                color: #FFFFFF !important;
                font-family: 'Georgia', serif !important;
                font-size: 34px;
                font-weight: bold;
            }
        </style>
        """
        st.markdown(css_vintage_kpis, unsafe_allow_html=True)

        # Nuovo HTML dei KPI strutturato e uniformato
        html_kpi_uniformed = f"""
        <div class="vintage-kpi-block-container">
            <h3 class="vintage-kpi-block-title">Panoramica Squadra</h3>
            <div class="vintage-card-container-uniform">
                <div class="vintage-card-uniform">
                    <h4>Vittorie Classifica Generale</h4>
                    <h2>{vittorie_totali}</h2>
                </div>
                <div class="vintage-card-uniform">
                    <h4>Miglior Piazzamento</h4>
                    <h2>{miglior_piazzamento}</h2>
                </div>
                <div class="vintage-card-uniform">
                    <h4>Edizioni Partecipate</h4>
                    <h2>{partecipazioni}</h2>
                </div>
            </div>
        </div>
        """
        st.markdown(html_kpi_uniformed, unsafe_allow_html=True)
        st.markdown('<hr class="vintage-divider">', unsafe_allow_html=True)
        # --- 6. SEZIONE 2: COMPOSIZIONE E STRUTTURA DEL TEAM CORRIDORI ---
        st.markdown('<h3 class="vintage-section-title" style="color: #000000; font-family: Georgia, serif;">I Protagonisti del Team</h3>', unsafe_allow_html=True)
        
        if not df_team_storico.empty:
            col_comp1, col_comp2 = st.columns(2)

            with col_comp1:
                # Grafico dei plurivincitori di tappe 
                if not df_tappe_team.empty:
                    vincitori_tappe = df_tappe_team.groupby('Winner of stage').size().reset_index(name='Tappe Vinte')
                    vincitori_tappe = vincitori_tappe.rename(columns={'Winner of stage': 'Corridore'})
                    vincitori_tappe = vincitori_tappe.sort_values(by='Tappe Vinte', ascending=False).head(5)
                    
                    fig_vincitori = px.bar(
                        vincitori_tappe, x='Tappe Vinte', y='Corridore', orientation='h',
                        title="I plurivincitori di tappe nel Team",
                        labels={'Corridore': '', 'Tappe Vinte': 'Numero di tappe'}
                    )
                    fig_vincitori.update_traces(marker_color='#ff6666') 
                    fig_vincitori.update_layout(yaxis={'categoryorder':'total ascending'})
                    fig_vincitori = applica_tema_vintage(fig_vincitori)
                    st.plotly_chart(fig_vincitori, use_container_width=True)
                else:
                    st.markdown('<p style="color:white ; font-style: italic; text-align: center; padding-top: 30px;">Nessun corridore di questa formazione ha mai conquistato una vittoria di tappa al Tour.</p>', unsafe_allow_html=True)
            with col_comp2:
                # Grafico delle presenze storiche del team (I Fedelissimi)
                fedelissimi = df_team_storico['Rider'].value_counts().head(5).reset_index()
                fedelissimi.columns = ['Corridore', 'Partecipazioni']
                
                fig_fedeli = px.bar(
                    fedelissimi, x='Partecipazioni', y='Corridore', orientation='h',
                    title="I 'Fedelissimi' del Team (Presenze)",
                    labels={'Corridore': '', 'Partecipazioni': 'Tour disputati'}
                )
                fig_fedeli.update_traces(marker_color='#d2b48c') 
                fig_fedeli.update_layout(yaxis={'categoryorder':'total ascending'})
                fig_fedeli = applica_tema_vintage(fig_fedeli)
                st.plotly_chart(fig_fedeli, use_container_width=True)

        st.markdown('<hr class="vintage-divider">', unsafe_allow_html=True)

        # --- 7. SEZIONE 3: PERFORMANCE STORICHE, SELEZIONE ANNO UNICA E STRIP PLOT ---
        st.markdown('<h3 class="vintage-section-title" style="color: #000000; font-family: Georgia, serif;">Performance Storiche</h3>', unsafe_allow_html=True)
        if not df_team_storico.empty:
            col_grafico1, col_grafico2 = st.columns(2)
            
            with col_grafico1:
                anni_disponibili_team = sorted(df_team_storico['Year'].unique(), reverse=True)
                anno_selezionato = st.selectbox("Seleziona l'edizione del Tour:", anni_disponibili_team)
                
                roster_anno = df_team_storico[df_team_storico['Year'] == anno_selezionato][['Rider', 'Rank_Num']].sort_values(by='Rank_Num')
                roster_anno['Rank_Num'] = roster_anno['Rank_Num'].apply(lambda x: int(x) if pd.notna(x) else "Ritirato")
                roster_anno.columns = ['Corridore', 'Piazzamento Finale']
                
                st.markdown(f'<p style="color: #000000; font-family: Georgia, serif; margin-top: 10px;"><strong>Formazione e Risultati nel {anno_selezionato}:</strong></p>', unsafe_allow_html=True)
                st.dataframe(roster_anno, use_container_width=True, hide_index=True)
                
            with col_grafico2:
                df_scatter = df_team_storico.dropna(subset=['Rank_Num']).copy()
                df_scatter['Evidenziato'] = df_scatter['Year'] == anno_selezionato
                
                fig_roster = px.strip(
                    df_scatter, x='Year', y='Rank_Num',
                    hover_name='Rider',
                    color='Evidenziato', 
                    color_discrete_map={True: '#ff4b4b', False: 'rgba(143, 188, 143, 0.25)'},
                    title="Piazzamenti dell'intero Roster nella Storia",
                    labels={'Rank_Num': 'Posizione in Classifica', 'Year': 'Anno'}
                )
                fig_roster.update_yaxes(autorange="reversed")
                fig_roster.update_traces(
                    marker=dict(size=10, line=dict(width=1, color='rgba(255,255,255,0.8)')),
                    jitter=0.2
                )
                fig_roster.update_layout(showlegend=False)
                fig_roster = applica_tema_vintage(fig_roster)
                st.plotly_chart(fig_roster, use_container_width=True)

        # --- 8. SEZIONE 4: PALMARÈS MAGLIE E VITTORIE TAPPE ---
        st.markdown('<h3 class="vintage-section-title" style="color: #000000; font-family: Georgia, serif;">Palmarès: Tappe e Maglie</h3>', unsafe_allow_html=True)
        
        # Calcolo maglie protetto
        corridori_team_clean = df_team_storico[['Year', 'Rider_Clean']].drop_duplicates()
        maglia_gialla = pd.merge(df_stage_h_clean, corridori_team_clean, left_on=['Year', 'Yellow_Clean'], right_on=['Year', 'Rider_Clean'], how='inner')
        maglia_verde = pd.merge(df_stage_h_clean, corridori_team_clean, left_on=['Year', 'Green_Clean'], right_on=['Year', 'Rider_Clean'], how='inner')
        maglia_pois = pd.merge(df_stage_h_clean, corridori_team_clean, left_on=['Year', 'Pois_Clean'], right_on=['Year', 'Rider_Clean'], how='inner')
        
        html_maglie = f"""
        <div class="vintage-card-container" style="display: flex; gap: 20px; justify-content: center; margin-bottom: 20px;">
            <div class="vintage-card" style="flex: 1; padding: 15px; text-align: center; border: 2px solid #FFD700; background-color: #fffacd;">
                <h4 style="margin: 0; color: #000000; font-family: Georgia, serif; font-size: 14px;">Giorni in Giallo</h4>
                <h2 style="margin: 10px 0 0 0; color: #000000; font-size: 24px; font-weight: bold;">{len(maglia_gialla)}</h2>
            </div>
            <div class="vintage-card" style="flex: 1; padding: 15px; text-align: center; border: 2px solid #228B22; background-color: #f0fff0;">
                <h4 style="margin: 0; color: #000000; font-family: Georgia, serif; font-size: 14px;">Giorni in Verde</h4>
                <h2 style="margin: 10px 0 0 0; color: #000000; font-size: 24px; font-weight: bold;">{len(maglia_verde)}</h2>
            </div>
            <div class="vintage-card" style="flex: 1; padding: 15px; text-align: center; border: 2px solid #ff0000; background-image: radial-gradient(#ff0000 15%, transparent 16%), radial-gradient(#ff0000 15%, transparent 16%); background-size: 20px 20px; background-position: 0 0, 10px 10px; background-color: white;">
                <h4 style="margin: 0; color: #000000; font-family: Georgia, serif; background-color: rgba(255,255,255,0.85); padding: 5px; font-size: 14px;">Giorni a Pois</h4>
                <h2 style="margin: 10px 0 0 0; color: #000000; background-color: rgba(255,255,255,0.85); padding: 5px; display: inline-block; font-size: 24px; font-weight: bold;">{len(maglia_pois)}</h2>
            </div>
        </div>
        """
        st.markdown(html_maglie, unsafe_allow_html=True)
        
        if not df_tappe_team.empty:
            vittorie_per_anno = df_tappe_team.groupby('Year').size().reset_index(name='Vittorie')
            fig_tappe = px.bar(
                vittorie_per_anno, x='Year', y='Vittorie',
                title="Numero di tappe vinte per edizione",
                labels={'Vittorie': 'Tappe Vinte', 'Year': 'Anno'}
            )
             
            # 1. Applichiamo il Giallo Tour de France alle barre
            fig_tappe.update_traces(marker_color='#FFCC00')
            
            # 2. Applichiamo il font di base vintage
            fig_tappe = applica_tema_vintage(fig_tappe)
            
            # 3. Sovrascriviamo lo sfondo trasparente forzando il Nero assoluto per questo specifico grafico
            fig_tappe.update_layout(
                paper_bgcolor='#000000', 
                plot_bgcolor='#000000',
                title_font_color="#FFFFFF",
                font=dict(color="#FFFFFF")
            )
            
            # 4. Assicuriamoci che anche griglie, assi e numerini siano perfettamente bianchi e visibili sul nero
            fig_tappe.update_xaxes(gridcolor='rgba(255,255,255,0.2)', title_font=dict(color="#FFFFFF"), tickfont=dict(color="#FFFFFF"))
            fig_tappe.update_yaxes(gridcolor='rgba(255,255,255,0.2)', title_font=dict(color="#FFFFFF"), tickfont=dict(color="#FFFFFF"))
            
            st.plotly_chart(fig_tappe, use_container_width=True)
        else:
            st.markdown('<p class="journal-text" style="color: #000000; font-style: italic; text-align: center;">Nessuna vittoria di tappa trovata per questa squadra nei dati a disposizione.</p>', unsafe_allow_html=True)
#============================================
# 6. MENU LATERALE (SIDEBAR)
# ==========================================
#with st.sidebar:
#    st.title("≡ Filtri globali")
#   st.selectbox("Seleziona Nazionalità:", ["Tutte", "Italia", "Francia", "Spagna"])
#    st.checkbox("Mostra solo i team World Tour")





TEAMS

