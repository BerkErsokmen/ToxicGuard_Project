"""
ToxicGuard — Toksisite Tespit Sistemi
Ana Streamlit Uygulaması (V1/V2/V3/V4 Versiyon Desteği)
"""

import streamlit as st
import os
import sys
import json

# Proje kökünü path'e ekle
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Sayfa ayarları
st.set_page_config(
    page_title="ToxicGuard — Toksisite Tespit Sistemi",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- TEMA AYARLARI ---
if 'ui_theme' not in st.session_state:
    st.session_state.ui_theme = 'Karanlık'

# Tema Renk Tanımları
THEMES = {
    'Karanlık': {
        'bg_gradient': 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)',
        'card_bg': 'linear-gradient(145deg, #1a1a2e 0%, #16213e 100%)',
        'text_main': '#ffffff',
        'text_dim': '#b8b5ff',
        'text_card_label': '#a0a0c0',
        'border_color': 'rgba(255,255,255,0.05)',
        'metric_bg': 'linear-gradient(145deg, #1e1e3f 0%, #2d2d5e 100%)',
        'lime_bg': '#white', # LIME her zaman beyazda daha iyi ama karanlıkta kart içine alacağız
        'sidebar_bg': 'linear-gradient(180deg, #0f0c29 0%, #1a1a2e 100%)'
    },
    'Aydınlık': {
        'bg_gradient': '#ffffff',
        'card_bg': '#ffffff',
        'text_main': '#000000',
        'text_dim': '#555555',
        'text_card_label': '#333333',
        'border_color': 'rgba(0,0,0,0.05)',
        'metric_bg': '#ffffff',
        'lime_bg': '#ffffff',
        'sidebar_bg': '#ffffff'
    }
}

t = THEMES[st.session_state.ui_theme]

# Custom CSS Injection
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .stApp {{
        font-family: 'Inter', sans-serif;
    }}
    
    /* Header */
    .main-header {{
        background: {t['bg_gradient']};
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }}
    .main-header h1 {{
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }}
    .main-header p {{
        color: {t['text_dim']};
        font-size: 1.1rem;
    }}
    
    /* Prediction Cards */
    .score-card {{
        background: {t['card_bg']};
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.5rem 0;
        border: 1px solid {t['border_color']};
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    .score-card .label {{
        color: {t['text_card_label']};
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
    }}
    .score-card .value {{
        color: {t['text_main'] if st.session_state.ui_theme == 'Aydınlık' else 'inherit'};
        font-size: 1.8rem;
        font-weight: 700;
    }}
    
    /* Level Badge */
    .level-badge {{
        display: inline-block;
        padding: 0.6rem 1.5rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1.2rem;
        text-align: center;
        margin: 1rem 0;
    }}
    .level-safe {{ background: linear-gradient(135deg, #00b09b, #96c93d); color: white; }}
    .level-warning {{ background: linear-gradient(135deg, #f2994a, #f2c94c); color: #333; }}
    .level-danger {{ background: linear-gradient(135deg, #eb3349, #f45c43); color: white; }}
    
    /* Metric boxes */
    .metric-box {{
        background: {t['metric_bg']};
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid {t['border_color']};
    }}
    .metric-box .number {{
        color: {t['text_main']};
        font-size: 2rem;
        font-weight: 800;
    }}

    /* XAI Info */
    .xai-info {{
        background: {t['metric_bg']};
        padding: 1.2rem;
        border-left: 5px solid #3498db;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        color: {t['text_main']};
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    
    /* Version badges */
    .version-badge {{
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
    }}
    .version-v1 {{ background: linear-gradient(135deg, #667eea, #764ba2); }}
    .version-v2 {{ background: linear-gradient(135deg, #f093fb, #f5576c); }}
    .version-v3 {{ background: linear-gradient(135deg, #11998e, #38ef7d); }}
    .version-v4 {{ background: linear-gradient(135deg, #ff9966, #ff5e62); }}
    .version-v5 {{ background: linear-gradient(135deg, #1a1a2e, #e94560); }}
    .version-v5_2 {{ background: linear-gradient(135deg, #f7971e, #ffd200); color: #1a1a2e !important; }}
    .version-v5_02 {{ background: linear-gradient(135deg, #00c6ff, #0072ff); color: white !important; }}
    .version-v5_22 {{ background: linear-gradient(135deg, #f953c6, #b91d73); color: white !important; }}
    
    /* Custom Spinner — Streamlit default (koşan adam) yerine kalkan pulse animasyonu */
    .stSpinner > div > div {{
        border-color: #764ba2 !important;
    }}
    /* Spinner ikonunu gizle, yerine shield animasyonu koy */
    .stSpinner > div {{
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
    }}
    .stSpinner > div > i {{
        display: none !important;
    }}
    .stSpinner > div::before {{
        content: '🛡️';
        font-size: 1.5rem;
        display: inline-block;
        animation: shieldPulse 1.2s ease-in-out infinite;
    }}
    @keyframes shieldPulse {{
        0%, 100% {{ transform: scale(1); opacity: 1; }}
        50% {{ transform: scale(1.3); opacity: 0.6; }}
    }}

    /* All-models summary card */
    .all-models-card {{
        background: {t['card_bg']};
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        border: 1px solid {t['border_color']};
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .all-models-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.2);
    }}
    .all-models-card .model-title {{
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: {t['text_main']};
    }}
    .all-models-card .model-desc {{
        font-size: 0.78rem;
        color: {t['text_dim']};
        margin-bottom: 0.7rem;
    }}
    
    /* Utils */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)


def main():
    # Sidebar
    with st.sidebar:
        st.markdown("### 🛡️ ToxicGuard")
        
        # Tema seçimi
        st.session_state.ui_theme = st.selectbox(
            "🎨 Görünüm Teması",
            ['Karanlık', 'Aydınlık'],
            index=0 if st.session_state.ui_theme == 'Karanlık' else 1
        )
        
        st.markdown("---")
        page = st.radio(
            "Sayfa Seçin",
            ["🔍 Tahmin", "📋 Tüm Modeller", "🤖 Çoklu Model Analizi", "🔀 Versiyon Karşılaştırma", "⚖️ Baseline Karşılaştırma", "📊 EDA Görselleştirme", "🏆 Model Karşılaştırma"]
        )
        
        st.markdown("---")
        
        # Versiyon seçimi (Tahmin sayfası için)
        if page == "🔍 Tahmin":
            from src.predict import get_available_versions, VERSION_INFO
            versions = get_available_versions()
            if versions:
                version_labels = {v: VERSION_INFO[v]['name'] for v in versions}
                selected_version = st.selectbox(
                    "📦 Model Versiyonu",
                    versions,
                    format_func=lambda v: version_labels.get(v, v),
                    key="model_version"
                )
                
                # Seçilen versiyonun bilgilerini göster
                info = VERSION_INFO.get(selected_version, {})
                st.caption(info.get('description', ''))
            else:
                selected_version = 'v1'
                st.warning("Model bulunamadı!")
            
            st.session_state['selected_version'] = selected_version
        
        st.markdown("---")
        st.markdown(f"""
        <div style='text-align:center; color:#888; font-size:0.8rem;'>
            <p>ToxicGuard v5.2</p>
            <p>Tema: {st.session_state.ui_theme}</p>
        </div>
        """, unsafe_allow_html=True)
    
    if page == "🔍 Tahmin":
        show_prediction_page()
    elif page == "📋 Tüm Modeller":
        show_all_models_page()
    elif page == "🤖 Çoklu Model Analizi":
        show_multi_model_analysis_page()
    elif page == "🔀 Versiyon Karşılaştırma":
        show_comparison_page()
    elif page == "⚖️ Baseline Karşılaştırma":
        show_baseline_comparison_page()
    elif page == "📊 EDA Görselleştirme":
        show_eda_page()
    elif page == "🏆 Model Karşılaştırma":
        show_model_comparison_page()


@st.cache_resource
def get_cached_predictor(version):
    """Model yüklemeyi cache'le — her versiyon için bir kez yükle."""
    if version == 'v5_02':
        from src.predict import V502CascadePredictor
        return V502CascadePredictor()
    if version == 'v5_22':
        from src.predict import V522CascadePredictor
        return V522CascadePredictor()
    from src.predict import ToxicityPredictor
    return ToxicityPredictor(version=version)


def show_all_models_page():
    """Tüm modellerin çıktılarını yan yana gösteren sayfa."""
    st.markdown("""
    <div class="main-header">
        <h1>📋 Tüm Modeller — Toplu Analiz</h1>
        <p>Aynı metni mevcut tüm model versiyonları ile analiz edin ve sonuçları karşılaştırın</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        from src.predict import get_available_versions, VERSION_INFO
        from src.utils import LABEL_COLS, LABEL_NAMES_TR
        versions = get_available_versions()
        if not versions:
            st.warning("Hiçbir model versiyonu bulunamadı. Lütfen önce modelleri eğitin.")
            return
    except Exception as e:
        st.error(f"⚠️ Predict modülü yüklenemedi: {e}")
        return

    # Bulunan versiyonları göster
    ver_badges = " ".join(
        f'<span class="version-badge version-{v}">{v.upper()}</span>' for v in versions
    )
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:1.5rem;">
        <span style="color:#888; font-size:0.9rem;">Mevcut modeller:</span><br>
        <div style="margin-top:0.5rem; display:flex; gap:8px; justify-content:center;">
            {ver_badges}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Transformer uyarısı
    transformer_vers = [v for v in versions if v in ('v3', 'v4', 'v5', 'v5_2')]
    if transformer_vers:
        st.info(f"⚡ **Bilgi:** {', '.join(v.upper() for v in transformer_vers)} versiyonları Transformer tabanlıdır ve ilk çıkarım biraz daha uzun sürebilir.")

    # ===== İki modlu giriş: Tekli metin veya Dosya yükleme =====
    tab_text, tab_file = st.tabs(["✏️ Tekli Metin Girişi", "📁 Dosya Yükleme (Toplu Analiz)"])

    # === TAB 1: Tekli metin girişi ===
    with tab_text:
        user_text = st.text_area(
            "Analiz edilecek yorumu girin",
            height=130,
            placeholder="Örnek: You are such an idiot!  /  Sen gerçekten berbat birisin!",
            key="all_models_text"
        )

        analyze_btn = st.button(
            "🚀 Tüm Modelleri Çalıştır",
            type="primary",
            use_container_width=True,
            key="all_models_btn"
        )

        if analyze_btn and user_text.strip():
            _run_all_models_single(user_text, versions, LABEL_COLS, LABEL_NAMES_TR)
        elif analyze_btn:
            st.warning("Lütfen bir metin girin.")

    # === TAB 2: Dosya yükleme ===
    with tab_file:
        st.markdown("##### 📤 Dosya Yükleyin")
        st.markdown("`.txt` (her satır ayrı yorum, boş satırlar atlanır) veya `.csv` (yorum sütunu seçin) dosyası yükleyin.")

        uploaded_file = st.file_uploader(
            "Dosya seçin",
            type=['txt', 'csv'],
            help="Maksimum 10MB",
            key="all_models_file_upload"
        )

        column_name = None
        if uploaded_file is not None:
            file_type = uploaded_file.name.split('.')[-1].lower()
            file_content = uploaded_file.read()

            if len(file_content) > 10 * 1024 * 1024:
                st.error("Dosya boyutu 10MB'ı aşamaz!")
                return

            if file_type == 'csv':
                import io
                import pandas as pd
                temp_df = pd.read_csv(io.StringIO(file_content.decode('utf-8', errors='ignore')), sep=None, engine='python')
                text_cols = temp_df.select_dtypes(include='object').columns.tolist()
                if text_cols:
                    column_name = st.selectbox("Yorum sütununu seçin", text_cols, key="all_models_csv_col")
                else:
                    st.error("CSV dosyasında metin sütunu bulunamadı!")
                    return

            if st.button("🚀 Tüm Modeller ile Toplu Analiz Başlat", type="primary", use_container_width=True, key="all_models_file_btn"):
                _run_all_models_file(file_content, file_type, column_name, versions, LABEL_COLS, LABEL_NAMES_TR, uploaded_file.name)


def _run_all_models_single(user_text, versions, LABEL_COLS, LABEL_NAMES_TR):
    """Tek bir metni tüm modellerle analiz et ve göster."""
    from src.predict import VERSION_INFO

    results = {}
    progress_bar = st.progress(0, text="Modeller yükleniyor...")

    for idx, ver in enumerate(versions):
        progress_bar.progress(
            (idx) / len(versions),
            text=f"🛡️ {ver.upper()} modeli analiz ediyor..."
        )
        try:
            predictor = get_cached_predictor(ver)
            results[ver] = predictor.predict_text(user_text)
        except Exception as e:
            results[ver] = None
            st.warning(f"{ver.upper()} modeli çalıştırılamadı: {e}")

    progress_bar.progress(1.0, text="✅ Tüm modeller tamamlandı!")

    st.markdown("---")

    # === Özet: Genel skorlar yan yana ===
    st.subheader("🎯 Genel Sonuçlar")

    cols = st.columns(len(versions))
    for i, ver in enumerate(versions):
        res = results.get(ver)
        if not res:
            with cols[i]:
                st.warning(f"{ver.upper()} — Hata")
            continue

        emoji_v, color_v = VERSION_COLORS.get(ver, ('🔵', '#3498db'))
        level = res['level']
        level_cls = _level_class(level['label'])
        info = VERSION_INFO.get(ver, {})

        with cols[i]:
            st.markdown(f"""
            <div class="all-models-card">
                <div class="model-title">{emoji_v} {ver.upper()} — {info.get('name', '').split('—')[-1].strip()}</div>
                <div class="model-desc">{info.get('description', '')}</div>
                <div style="text-align:center;">
                    <div class="level-badge {level_cls}" style="font-size:1rem; padding:0.4rem 1rem;">
                        {level['emoji']} {level['label']} — {res['overall_score']:.1%}
                    </div>
                </div>
                <div style="margin-top:0.6rem; text-align:center; font-size:0.75rem; color:#888;">
                    Threshold: {res['threshold_used']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # === Tablo: Etiket bazlı karşılaştırma ===
    st.subheader("📊 Etiket Bazlı Karşılaştırma Tablosu")

    import pandas as pd
    table_rows = []
    for col_name in LABEL_COLS:
        row = {'Etiket': LABEL_NAMES_TR[col_name]}
        for ver in versions:
            res = results.get(ver)
            if res:
                score = res['scores'][col_name]
                pred = res['predictions'][col_name]
                icon = '⚠️' if pred else '✅'
                row[f'{ver.upper()} Skor'] = f"{score:.3f}"
                row[f'{ver.upper()} Tahmin'] = f'{icon} {"Evet" if pred else "Hayır"}'
            else:
                row[f'{ver.upper()} Skor'] = "—"
                row[f'{ver.upper()} Tahmin'] = "—"
        table_rows.append(row)

    df_all = pd.DataFrame(table_rows)
    st.dataframe(df_all, use_container_width=True, hide_index=True)

    # === Her model için detaylı kartlar ===
    st.subheader("🔍 Detaylı Model Çıktıları")

    for ver in versions:
        res = results.get(ver)
        if not res:
            continue

        emoji_v, color_v = VERSION_COLORS.get(ver, ('🔵', '#3498db'))
        info = VERSION_INFO.get(ver, {})

        with st.expander(f"{emoji_v} {ver.upper()} — {info.get('name', '')} — Detay", expanded=False):
            detail_cols = st.columns(3)
            for j, col_name in enumerate(LABEL_COLS):
                score = res['scores'][col_name]
                pred = res['predictions'][col_name]
                label_tr = LABEL_NAMES_TR[col_name]
                color = '#e74c3c' if pred else ('#f39c12' if score > 0.3 else '#2ecc71')
                icon = '⚠️' if pred else '✅'

                with detail_cols[j % 3]:
                    st.markdown(f"""
                    <div class="score-card">
                        <div class="label">{icon} {label_tr}</div>
                        <div class="value" style="color:{color}">{score:.1%}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(min(score, 1.0))

    # Temizlenmiş metin
    first_result = next((r for r in results.values() if r), None)
    if first_result:
        with st.expander("🔧 Temizlenmiş Metin"):
            st.code(first_result['cleaned_text'] or "(boş)", language=None)


def _run_all_models_file(file_content, file_type, column_name, versions, LABEL_COLS, LABEL_NAMES_TR, uploaded_filename='dosya'):
    """Dosyadan okunan metinleri tüm modellerle analiz et."""
    import pandas as pd
    import io
    from src.predict import VERSION_INFO

    # Dosyadan metinleri çıkar
    if file_type == 'txt':
        if isinstance(file_content, bytes):
            file_content_str = file_content.decode('utf-8', errors='ignore')
        else:
            file_content_str = file_content
        # Boş satırları ve === başlıkları ve "Beklenen Sonuç" satırlarını atla
        texts = []
        for line in file_content_str.split('\n'):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith('==='):
                continue
            if stripped.startswith('Beklenen Sonuç'):
                continue
            texts.append(stripped)
    elif file_type == 'csv':
        if isinstance(file_content, bytes):
            file_content_str = file_content.decode('utf-8', errors='ignore')
        else:
            file_content_str = file_content
        df_input = pd.read_csv(io.StringIO(file_content_str), sep=None, engine='python')
        if column_name and column_name in df_input.columns:
            texts = df_input[column_name].dropna().astype(str).tolist()
        else:
            text_cols = df_input.select_dtypes(include='object').columns
            if len(text_cols) == 0:
                st.error("CSV dosyasında metin sütunu bulunamadı.")
                return
            texts = df_input[text_cols[0]].dropna().astype(str).tolist()
    else:
        st.error(f"Desteklenmeyen dosya türü: {file_type}")
        return

    if not texts:
        st.warning("Dosyada analiz edilecek yorum bulunamadı.")
        return

    st.info(f"📄 Dosyadan **{len(texts)}** yorum bulundu. Tüm modeller ile analiz ediliyor...")

    # Her model için tüm metinleri analiz et
    all_results = {}  # ver -> list of result dicts
    progress_bar = st.progress(0, text="Modeller yükleniyor...")

    for v_idx, ver in enumerate(versions):
        progress_bar.progress(
            v_idx / len(versions),
            text=f"🛡️ {ver.upper()} modeli {len(texts)} yorumu analiz ediyor..."
        )
        try:
            predictor = get_cached_predictor(ver)
            ver_results = []
            for text in texts:
                ver_results.append(predictor.predict_text(text))
            all_results[ver] = ver_results
        except Exception as e:
            all_results[ver] = None
            st.warning(f"{ver.upper()} modeli çalıştırılamadı: {e}")

    progress_bar.progress(1.0, text="✅ Tüm modeller tamamlandı!")
    st.markdown("---")

    # === Özet istatistikler ===
    st.subheader("📊 Genel Özet")

    summary_cols = st.columns(len(versions))
    for i, ver in enumerate(versions):
        ver_res = all_results.get(ver)
        if not ver_res:
            with summary_cols[i]:
                st.warning(f"{ver.upper()} — Hata")
            continue

        safe_count = sum(1 for r in ver_res if r['level']['label'] == 'Güvenli')
        warn_count = sum(1 for r in ver_res if r['level']['label'] == 'Dikkat')
        toxic_count = sum(1 for r in ver_res if r['level']['label'] == 'Toksik')
        emoji_v, _ = VERSION_COLORS.get(ver, ('🔵', '#3498db'))
        info = VERSION_INFO.get(ver, {})

        with summary_cols[i]:
            st.markdown(f"""
            <div class="all-models-card">
                <div class="model-title">{emoji_v} {ver.upper()}</div>
                <div class="model-desc">{info.get('description', '')}</div>
                <div style="text-align:center; margin-top:0.5rem;">
                    <span style="color:#2ecc71; font-weight:bold;">🟢 {safe_count}</span> · 
                    <span style="color:#f39c12; font-weight:bold;">🟡 {warn_count}</span> · 
                    <span style="color:#e74c3c; font-weight:bold;">🔴 {toxic_count}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # === Detaylı sonuç tablosu ===
    st.subheader("📋 Tüm Yorumların Karşılaştırmalı Sonuçları")

    table_rows = []
    for t_idx, text in enumerate(texts):
        row = {'#': t_idx + 1, 'Yorum': text[:120] + ('...' if len(text) > 120 else '')}
        for ver in versions:
            ver_res = all_results.get(ver)
            if ver_res:
                r = ver_res[t_idx]
                level_label = r['level']['label']
                level_emoji = r['level']['emoji']
                row[f'{ver.upper()} Skor'] = f"{r['overall_score']:.3f}"
                row[f'{ver.upper()} Seviye'] = f"{level_emoji} {level_label}"
            else:
                row[f'{ver.upper()} Skor'] = "—"
                row[f'{ver.upper()} Seviye'] = "—"
        table_rows.append(row)

    df_results = pd.DataFrame(table_rows)
    st.dataframe(df_results, use_container_width=True, hide_index=True, height=500)

    # === CSV indirme ===
    csv_rows = []
    for t_idx, text in enumerate(texts):
        row = {'yorum': text}
        for ver in versions:
            ver_res = all_results.get(ver)
            if ver_res:
                r = ver_res[t_idx]
                row[f'{ver.upper()}_genel_skor'] = round(r['overall_score'], 4)
                row[f'{ver.upper()}_seviye'] = r['level']['label']
                for col in LABEL_COLS:
                    row[f'{ver.upper()}_{LABEL_NAMES_TR[col]}'] = round(r['scores'][col], 4)
        csv_rows.append(row)

    df_download = pd.DataFrame(csv_rows)
    csv_data = df_download.to_csv(index=False, sep=';').encode('utf-8-sig')
    # Yüklenen dosya adından uzantıyı çıkar
    import os as _os
    base_name = _os.path.splitext(uploaded_filename)[0]
    model_names = "_".join(v.upper() for v in versions)
    download_fname = f"{base_name}_analiz_{model_names}.csv"
    st.download_button(
        label="📥 Tüm Sonuçları CSV Olarak İndir",
        data=csv_data,
        file_name=download_fname,
        mime="text/csv",
        use_container_width=True
    )


def show_prediction_page():
    """Ana tahmin sayfası."""
    version = st.session_state.get('selected_version', 'v1')
    version_class = f"version-{version}"
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>🛡️ ToxicGuard</h1>
        <p>Yapay zeka destekli yorum toksiklik analiz sistemi</p>
        <div style="margin-top: 0.8rem;">
            <span class="version-badge {version_class}">{version.upper()} Modeli Aktif</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Model yükleme (cache'li)
    try:
        from src.utils import LABEL_COLS, LABEL_NAMES_TR
        predictor = get_cached_predictor(version)
        model_loaded = True
    except Exception as e:
        model_loaded = False
        st.error(f"⚠️ Model yüklenemedi ({version}): {e}")
        st.info("Lütfen önce modeli eğitin: `python -m src.train`")
        return
    
    # Threshold bilgisi
    st.info(f"🎯 Aktif threshold: **{predictor.threshold}** | Versiyon: **{version.upper()}**")
    
    # Analiz modu seçimi
    tab1, tab2 = st.tabs(["✏️ Tekli Yorum Analizi", "📁 Dosya Yükleme (Toplu Analiz)"])
    
    # === TAB 1: Tekli Yorum ===
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            user_text = st.text_area(
                "Analiz edilecek yorumu girin",
                height=150,
                placeholder="Örnek: Bu makale gerçekten faydalı, teşekkürler!",
                key="single_text"
            )
            analyze_btn = st.button("🔍 Analiz Et", type="primary", use_container_width=True, key="analyze_single")
        
        with col2:
            if version in ('v4', 'v5', 'v5_2', 'v5_02', 'v5_22'):
                lang_icon, lang_text = "🌍", "Evrensel (TR Dahil)"
            else:
                lang_icon, lang_text = "🇬🇧", "İngilizce"

            etiket_sayi = "6 + 🔬İroni" if version in ('v5_02', 'v5_22') else "6"
            etiket_acik = "Toksisite + Sarkazm cascade" if version in ('v5_02', 'v5_22') else "Toksisite kategorisi"
                
            st.markdown(f"""
            <div class="metric-box">
                <h3>Desteklenen Diller</h3>
                <div class="number">{lang_icon}</div>
                <p style="color:#888; font-size:0.8rem;">{lang_text}</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-box">
                <h3>Etiket Türleri</h3>
                <div class="number">{etiket_sayi}</div>
                <p style="color:#888; font-size:0.8rem;">{etiket_acik}</p>
            </div>
            """, unsafe_allow_html=True)
        
        show_xai = st.checkbox("🔮 Neden Toksik? (Açıklanabilir Yapay Zeka ile Analiz Et)", key="xai_check", help="LIME altyapısı kullanarak modelin hangi kelimeden dolayı toksik kararı verdiğini renklerle gösterir.")
        
        if analyze_btn and user_text.strip():
            with st.spinner("Analiz ediliyor..."):
                result = predictor.predict_text(user_text)

            # Context modifier aktifse bilgi notu göster
            if result.get('context_modified'):
                st.info(f"🧩 **Bağlam Düzeltmesi Uygulandı:** {result.get('context_note', '')}  \n"
                        f"Argo/küfür içeren ama arkadaşça/iltifat amaçlı ifade tespit edildi — "
                        f"ham skor düşürüldü.")

            # V5.02 cascade sonucu özel gösterim
            if result.get('cascade_label'):
                clr = result['cascade_color']
                lbl = result['cascade_label']
                emj = result['cascade_emoji']
                iry = result['irony_score']
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);
                            border-radius:14px; padding:1.2rem 1.6rem; margin-bottom:1rem;
                            border-left:5px solid {clr};">
                    <div style="font-size:0.8rem; color:#aaa; font-weight:600; letter-spacing:1px;
                                text-transform:uppercase; margin-bottom:4px;">CASCADE KARAR 🔬</div>
                    <div style="font-size:1.8rem; font-weight:800; color:{clr};">
                        {emj} {lbl}
                    </div>
                    <div style="margin-top:8px; font-size:0.85rem; color:#ccc;">
                        📌 Toksisite skoru: <b>{result['overall_score']:.1%}</b>  | 
                        🎭 İroni skoru: <b>{iry:.1%}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            display_single_result(result, LABEL_COLS, LABEL_NAMES_TR)
            
            if show_xai:
                is_transformer_model = version in ['v3', 'v4']
                lime_samples = 30 if is_transformer_model else 100  # Transformer modeller için azaltılmış örnek
                spinner_msg = (
                    "Modelin karar süreci analiz ediliyor (LIME XAI)... "
                    + ("Transformer modeli için 30 örnek kullanılıyor, ~15-30 sn sürebilir. ⏳" if is_transformer_model
                       else "Bu işlem birkaç saniye sürebilir.")
                )
                with st.spinner(spinner_msg):
                    try:
                        from lime.lime_text import LimeTextExplainer
                        import streamlit.components.v1 as components
                        
                        if is_transformer_model:
                            st.info("ℹ️ **Transformer Modu:** LIME, V3/V4 modellerinde her örnek için deep learning çıkarımı yapar. Hız için `num_samples=30` kullanılmaktadır.")
                        
                        explainer = LimeTextExplainer(class_names=['Zararsız', 'Toksik'])
                        exp = explainer.explain_instance(
                            user_text, 
                            predictor.predict_proba_for_lime, 
                            num_features=10, 
                            num_samples=lime_samples
                        )
                        html_exp = exp.as_html()
                        html_exp = f"<body style='background-color: white !important; color: black !important;'>{html_exp}</body>"
                        st.markdown("---")
                        st.markdown("### 🔮 Yapay Zeka Karar Raporu (LIME)")
                        st.markdown(f"""
                        <div class="xai-info">
                            <span style="color:#e74c3c; font-weight:bold;">Kırmızı</span>/Turuncu kelimeler mesajı <b>toksik</b> yaparken, 
                            <span style="color:#2ecc71; font-weight:bold;">Yeşil</span>/Mavi kelimeler <b>güvenli</b> (masum) algılanmıştır.
                        </div>
                        <div style="background-color:white; padding:15px; border-radius:12px; border: 1px solid #ddd; margin-top:10px;">
                        """, unsafe_allow_html=True)
                        components.html(html_exp, height=450, scrolling=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"XAI analizi sırasında hata oluştu: {e}. Modelin veya 'lime' paketinin yüklü olduğundan emin olun.")
        
        elif analyze_btn:
            st.warning("Lütfen bir metin girin.")
    
    # === TAB 2: Dosya Yükleme ===
    with tab2:
        st.markdown("##### 📤 Dosya Yükleyin")
        st.markdown("`.txt` (her satır ayrı yorum) veya `.csv` (yorum sütunu seçin) dosyası yükleyin.")
        
        uploaded_file = st.file_uploader(
            "Dosya seçin",
            type=['txt', 'csv'],
            help="Maksimum 10MB",
            key="file_upload"
        )
        
        if uploaded_file is not None:
            file_type = uploaded_file.name.split('.')[-1].lower()
            file_content = uploaded_file.read()
            
            # 10MB limit
            if len(file_content) > 10 * 1024 * 1024:
                st.error("Dosya boyutu 10MB'ı aşamaz!")
                return
            
            column_name = None
            if file_type == 'csv':
                import pandas as pd
                import io
                temp_df = pd.read_csv(io.StringIO(file_content.decode('utf-8', errors='ignore')), sep=None, engine='python')
                text_cols = temp_df.select_dtypes(include='object').columns.tolist()
                if text_cols:
                    column_name = st.selectbox("Yorum sütununu seçin", text_cols)
                else:
                    st.error("CSV dosyasında metin sütunu bulunamadı!")
                    return
            
            if st.button("📊 Toplu Analiz Başlat", type="primary", use_container_width=True, key="analyze_file"):
                with st.spinner("Dosya analiz ediliyor..."):
                    try:
                        results_df = predictor.predict_file(file_content, file_type, column_name)
                        
                        st.success(f"✅ {len(results_df)} yorum analiz edildi!")
                        
                        # Özet istatistikler
                        col1, col2, col3 = st.columns(3)
                        safe_count = (results_df['seviye'] == 'Güvenli').sum()
                        warn_count = (results_df['seviye'] == 'Dikkat').sum()
                        toxic_count = (results_df['seviye'] == 'Toksik').sum()
                        
                        col1.metric("🟢 Güvenli", safe_count)
                        col2.metric("🟡 Dikkat", warn_count)
                        col3.metric("🔴 Toksik", toxic_count)
                        
                        # Sonuç tablosu
                        st.dataframe(
                            results_df.style.apply(color_severity, subset=['seviye']),
                            use_container_width=True,
                            height=400
                        )
                        
                        # CSV indirme — dosya adı yüklenen dosya + model versiyonu
                        import os as _os
                        base_name = _os.path.splitext(uploaded_file.name)[0]
                        download_fname = f"{base_name}_analiz_{version.upper()}.csv"
                        csv = results_df.to_csv(index=False, sep=';').encode('utf-8-sig')
                        st.download_button(
                            label="📥 Sonuçları CSV Olarak İndir",
                            data=csv,
                            file_name=download_fname,
                            mime="text/csv",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Hata: {e}")


# Versiyon renkler / ikonlar
VERSION_COLORS = {
    'v1': ('🟣', '#764ba2'),
    'v2': ('🔴', '#f5576c'),
    'v3': ('🟢', '#38ef7d'),
    'v4': ('🟠', '#ff5e62'),
    'v5': ('⚡', '#e94560'),
    'v5_2': ('🏆', '#ffd200'),
    'v5_02': ('🔬', '#0072ff'),
    'v5_22': ('🎯', '#b91d73'),
}


def show_multi_model_analysis_page():
    """Çoklu model ile cümle analizi — checkbox seçimi, ironi/toksisite, XAI/LIME, genel kanı."""
    st.markdown("""
    <style>
    .multi-header {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        padding: 2rem 2rem 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .multi-header h1 { color: white; font-size: 2.2rem; font-weight: 800; margin-bottom: 0.3rem; }
    .multi-header p  { color: #b8b5ff; font-size: 1rem; }

    .model-result-card {
        border-radius: 16px;
        padding: 1.4rem 1.2rem;
        margin-bottom: 1.2rem;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 6px 24px rgba(0,0,0,0.18);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
    }
    .model-result-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.28);
    }
    .model-result-card .card-title {
        font-size: 1.05rem; font-weight: 700; margin-bottom: 0.6rem;
    }
    .score-pill {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 6px;
        margin-top: 4px;
    }
    .pill-toxic { background: rgba(231,76,60,0.18); border: 1px solid #e74c3c; color: #e74c3c; }
    .pill-irony { background: rgba(142,68,173,0.18); border: 1px solid #9b59b6; color: #9b59b6; }
    .pill-safe  { background: rgba(46,204,113,0.18); border: 1px solid #2ecc71; color: #2ecc71; }
    .pill-warn  { background: rgba(243,156,18,0.18);  border: 1px solid #f39c12; color: #f39c12; }

    .consensus-box {
        background: linear-gradient(135deg, #1a1a2e, #2d2d5e);
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        border: 1px solid rgba(116,75,162,0.4);
        box-shadow: 0 8px 32px rgba(116,75,162,0.15);
    }
    .consensus-box h3 { color: #b8b5ff; font-size: 1.1rem; margin-bottom: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="multi-header">
        <h1>🤖 Çoklu Model ile Analiz</h1>
        <p>İstediğin modelleri seçerek aynı cümleyi birlikte analiz et — ironi, toksisite, XAI açıklamaları ve genel kanı</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        from src.predict import get_available_versions, VERSION_INFO
        from src.utils import LABEL_COLS, LABEL_NAMES_TR
        versions = get_available_versions()
        if not versions:
            st.warning("Hiçbir model versiyonu bulunamadı.")
            return
    except Exception as e:
        st.error(f"⚠️ Predict modülü yüklenemedi: {e}")
        return

    # ── 1. Model Seçimi (Checkboxlar) ──────────────────────────────────
    st.markdown("### ✅ Analiz Edilecek Modelleri Seç")
    st.caption("En az bir model seçmelisin. İstediğin kadar ekleyebilirsin.")

    check_cols = st.columns(min(len(versions), 4))
    selected_versions = []
    for i, ver in enumerate(versions):
        emoji_v, _ = VERSION_COLORS.get(ver, ('🔵', '#3498db'))
        info = VERSION_INFO.get(ver, {})
        with check_cols[i % 4]:
            checked = st.checkbox(
                f"{emoji_v} **{ver.upper()}**\n{info.get('name', '').split('—')[-1].strip()}",
                value=(i < 2),  # İlk 2 model varsayılan seçili
                key=f"multi_check_{ver}"
            )
            if checked:
                selected_versions.append(ver)

    if not selected_versions:
        st.info("👆 Lütfen en az bir model seç.")
        return

    st.markdown("---")

    # === İki modlu giriş: Tekli metin veya Dosya yükleme ===
    tab_text, tab_file = st.tabs(["✏️ Tekli Metin Girişi", "📁 Dosya Yükleme (Toplu Analiz)"])

    # === TAB 1: Tekli metin girişi ===
    with tab_text:
        user_text = st.text_area(
            "📝 Analiz edilecek cümleyi girin",
            height=120,
            placeholder="Örnek: You are such an idiot!  /  Sen gerçekten harika birisin (ironik)!",
            key="multi_model_text"
        )

        col_btn1, col_btn2 = st.columns([4, 1])
        with col_btn1:
            analyze_btn = st.button(
                f"🚀 {len(selected_versions)} Model ile Analiz Et",
                type="primary",
                use_container_width=True,
                key="multi_model_btn"
            )
        with col_btn2:
            clear_btn = st.button(
                "🧹 Temizle",
                use_container_width=True,
                key="multi_model_clear_btn"
            )

        if clear_btn:
            st.session_state['multi_model_text'] = ""
            st.session_state['multi_model_results'] = None
            st.session_state['multi_model_analyzed_text'] = None
            st.session_state['multi_model_selected_versions'] = None
            st.session_state['active_lime_model'] = None
            st.session_state['active_lime_html'] = None
            st.rerun()

        # Check if we should perform the analysis
        run_analysis = False
        if analyze_btn and user_text.strip():
            run_analysis = True
        elif analyze_btn:
            st.warning("Lütfen analiz edilecek bir cümle girin.")

        # If the user clicked the button, run and save to session_state
        if run_analysis:
            results = {}
            progress = st.progress(0, text="Modeller yükleniyor...")

            for idx, ver in enumerate(selected_versions):
                progress.progress(
                    idx / len(selected_versions),
                    text=f"🛡️ {ver.upper()} analiz ediyor..."
                )
                try:
                    predictor = get_cached_predictor(ver)
                    results[ver] = predictor.predict_text(user_text)
                except Exception as e:
                    results[ver] = None
                    st.warning(f"{ver.upper()} modeli çalıştırılamadı: {e}")

            progress.progress(1.0, text="✅ Tüm modeller tamamlandı!")
            
            st.session_state['multi_model_results'] = results
            st.session_state['multi_model_analyzed_text'] = user_text
            st.session_state['multi_model_selected_versions'] = selected_versions
            
            # Clear previous LIME results from session state
            st.session_state['active_lime_model'] = None
            st.session_state['active_lime_html'] = None

    # === TAB 2: Dosya yükleme ===
    with tab_file:
        st.markdown("##### 📤 Dosya Yükleyin")
        st.markdown("`.txt` (her satır ayrı yorum, boş satırlar atlanır) veya `.csv` (yorum sütunu seçin) dosyası yükleyin.")

        uploaded_file = st.file_uploader(
            "Dosya seçin",
            type=['txt', 'csv'],
            help="Maksimum 10MB",
            key="multi_model_file_upload"
        )

        column_name = None
        if uploaded_file is not None:
            file_type = uploaded_file.name.split('.')[-1].lower()
            file_content = uploaded_file.read()

            if len(file_content) > 10 * 1024 * 1024:
                st.error("Dosya boyutu 10MB'ı aşamaz!")
            else:
                if file_type == 'csv':
                    import io
                    import pandas as pd
                    temp_df = pd.read_csv(io.StringIO(file_content.decode('utf-8', errors='ignore')), sep=None, engine='python')
                    text_cols = temp_df.select_dtypes(include='object').columns.tolist()
                    if text_cols:
                        column_name = st.selectbox("Yorum sütununu seçin", text_cols, key="multi_model_csv_col")
                    else:
                        st.error("CSV dosyasında metin sütunu bulunamadı!")
                        
                file_btn = st.button(
                    f"🚀 {len(selected_versions)} Model ile Toplu Analiz Başlat", 
                    type="primary", 
                    use_container_width=True, 
                    key="multi_model_file_btn"
                )
                if file_btn:
                    _run_all_models_file(file_content, file_type, column_name, selected_versions, LABEL_COLS, LABEL_NAMES_TR, uploaded_file.name)

    # Load from session state if available
    with tab_text:
        saved_results = st.session_state.get('multi_model_results')
        saved_text = st.session_state.get('multi_model_analyzed_text')
        saved_versions = st.session_state.get('multi_model_selected_versions')

        if saved_results is not None:
            results = saved_results
            selected_versions_to_show = saved_versions
            text_to_show = saved_text

            # ── 4. Genel Kanı (Consensus) ─────────────────────────────────────
            st.markdown("---")
            st.markdown("### 🗳️ Genel Kanı Özeti")

            valid_results = {v: r for v, r in results.items() if r is not None}
            if valid_results:
                total = len(valid_results)
                toxic_votes   = sum(1 for r in valid_results.values() if r['level']['label'] == 'Toksik')
                warning_votes = sum(1 for r in valid_results.values() if r['level']['label'] == 'Dikkat')
                safe_votes    = sum(1 for r in valid_results.values() if r['level']['label'] == 'Güvenli')
                avg_score     = sum(r['overall_score'] for r in valid_results.values()) / total

                # İroni bilgisi (sadece cascade modeller)
                irony_scores = [
                    r['irony_score'] for r in valid_results.values()
                    if r.get('irony_score') is not None
                ]
                avg_irony = sum(irony_scores) / len(irony_scores) if irony_scores else None

                # Çoğunluk kararı
                if toxic_votes > total / 2:
                    consensus_label = "Toksik"
                    consensus_emoji = "🔴"
                    consensus_cls   = "level-danger"
                    consensus_color = "#e74c3c"
                elif safe_votes > total / 2:
                    consensus_label = "Güvenli"
                    consensus_emoji = "🟢"
                    consensus_cls   = "level-safe"
                    consensus_color = "#2ecc71"
                elif warning_votes > 0:
                    consensus_label = "Dikkat"
                    consensus_emoji = "🟡"
                    consensus_cls   = "level-warning"
                    consensus_color = "#f39c12"
                else:
                    consensus_label = "Belirsiz"
                    consensus_emoji = "❓"
                    consensus_cls   = ""
                    consensus_color = "#95a5a6"

                cons_c1, cons_c2, cons_c3, cons_c4 = st.columns(4)
                with cons_c1:
                    st.markdown(f"""
                    <div class="metric-box" style="text-align:center;">
                        <div style="font-size:0.78rem;color:#888;">Genel Karar</div>
                        <div style="font-size:1.8rem; font-weight:800; color:{consensus_color};">
                            {consensus_emoji} {consensus_label}
                        </div>
                        <div style="font-size:0.72rem;color:#888;">{toxic_votes}/{total} Toksik oyu</div>
                    </div>
                    """, unsafe_allow_html=True)
                with cons_c2:
                    score_color = "#e74c3c" if avg_score > 0.5 else ("#f39c12" if avg_score > 0.25 else "#2ecc71")
                    st.markdown(f"""
                    <div class="metric-box" style="text-align:center;">
                        <div style="font-size:0.78rem;color:#888;">Ortalama Toksisite</div>
                        <div style="font-size:1.8rem; font-weight:800; color:{score_color};">
                            {avg_score:.1%}
                        </div>
                        <div style="font-size:0.72rem;color:#888;">{total} model ortalaması</div>
                    </div>
                    """, unsafe_allow_html=True)
                with cons_c3:
                    if avg_irony is not None:
                        irony_color = "#9b59b6" if avg_irony > 0.5 else ("#8e44ad" if avg_irony > 0.25 else "#888")
                        st.markdown(f"""
                        <div class="metric-box" style="text-align:center;">
                            <div style="font-size:0.78rem;color:#888;">Ortalama İroni</div>
                            <div style="font-size:1.8rem; font-weight:800; color:{irony_color};">
                                🎭 {avg_irony:.1%}
                            </div>
                            <div style="font-size:0.72rem;color:#888;">{len(irony_scores)} cascade model</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="metric-box" style="text-align:center;">
                            <div style="font-size:0.78rem;color:#888;">İroni Tespiti</div>
                            <div style="font-size:1.4rem; font-weight:600; color:#555;">—</div>
                            <div style="font-size:0.72rem;color:#888;">Cascade model seçilmedi</div>
                        </div>
                        """, unsafe_allow_html=True)
                with cons_c4:
                    oy_dagilimi = f"🔴{toxic_votes} 🟡{warning_votes} 🟢{safe_votes}"
                    st.markdown(f"""
                    <div class="metric-box" style="text-align:center;">
                        <div style="font-size:0.78rem;color:#888;">Oy Dağılımı</div>
                        <div style="font-size:1.3rem; font-weight:800; color:#b8b5ff;">{oy_dagilimi}</div>
                        <div style="font-size:0.72rem;color:#888;">Toksik · Dikkat · Güvenli</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Konsensüs genel yorum
                st.markdown("<br>", unsafe_allow_html=True)
                if consensus_label == "Toksik":
                    st.error(f"🔴 **{total} modelin {toxic_votes}'i** bu cümleyi **toksik** olarak değerlendirdi. Ortalama toksisite skoru: **{avg_score:.1%}**")
                elif consensus_label == "Güvenli":
                    st.success(f"🟢 **{total} modelin {safe_votes}'i** bu cümleyi **güvenli** olarak değerlendirdi. Ortalama toksisite skoru: **{avg_score:.1%}**")
                elif consensus_label == "Dikkat":
                    st.warning(f"🟡 Modeller arasında görüş birliği yok — **dikkat** eşiğinde. Ortalama skor: **{avg_score:.1%}**")
                else:
                    st.info(f"❓ Modeller bu cümle üzerinde birbirinden farklı kararlar verdi. Ortalama skor: **{avg_score:.1%}**")

            # ── 5. Etiket Bazlı Özet Tablo ─────────────────────────────────────
            import pandas as pd
            st.markdown("---")
            st.markdown("### 📊 Etiket Bazlı Skor Karşılaştırması")

            table_rows = []
            for col_name in LABEL_COLS:
                row = {'Etiket': LABEL_NAMES_TR[col_name]}
                for ver in selected_versions_to_show:
                    res = results.get(ver)
                    if res:
                        score = res['scores'][col_name]
                        pred  = res['predictions'][col_name]
                        icon  = '⚠️' if pred else '✅'
                        row[f'{ver.upper()} Skor']   = f"{score:.3f}"
                        row[f'{ver.upper()} Durum']  = f"{icon} {'Evet' if pred else 'Hayır'}"
                    else:
                        row[f'{ver.upper()} Skor']  = "—"
                        row[f'{ver.upper()} Durum'] = "—"
                table_rows.append(row)

            df_labels = pd.DataFrame(table_rows)
            st.dataframe(df_labels, use_container_width=True, hide_index=True)

            # ── 6. Model Kartları (detay + XAI) ──────────────────────────────
            st.markdown("---")
            st.markdown("### 🔍 Model Bazlı Detaylı Sonuçlar")

            for ver in selected_versions_to_show:
                res = results.get(ver)
                if not res:
                    continue

                emoji_v, color_v = VERSION_COLORS.get(ver, ('🔵', '#3498db'))
                info = VERSION_INFO.get(ver, {})
                level = res['level']
                level_cls = _level_class(level['label'])
                overall_score = res['overall_score']

                # İroni skoru
                irony_score = res.get('irony_score')
                cascade_label = res.get('cascade_label', '')

                # Model kart başlığı
                irony_pill = ""
                if irony_score is not None:
                    irony_pill = f'<span class="score-pill pill-irony">🎭 İroni: {irony_score:.1%}</span>'

                toxic_pill_cls  = "pill-toxic" if level['label'] == 'Toksik' else ("pill-warn" if level['label'] == 'Dikkat' else "pill-safe")
                toxic_pill      = f'<span class="score-pill {toxic_pill_cls}">{level["emoji"]} {level["label"]}: {overall_score:.1%}</span>'

                st.markdown(f"""
                <div class="model-result-card">
                    <div class="card-title" style="color:{color_v};">
                        {emoji_v} {ver.upper()} — {info.get('name', '').split('—')[-1].strip()}
                    </div>
                    {toxic_pill} {irony_pill}
                    {f'<span class="score-pill" style="background:rgba(0,114,255,0.12);border:1px solid #0072ff;color:#0072ff;">🔬 {cascade_label}</span>' if cascade_label else ''}
                </div>
                """, unsafe_allow_html=True)

                # Etiket skorları
                detail_cols = st.columns(3)
                for j, col_name in enumerate(LABEL_COLS):
                    score = res['scores'][col_name]
                    pred  = res['predictions'][col_name]
                    label_tr = LABEL_NAMES_TR[col_name]
                    color    = '#e74c3c' if pred else ('#f39c12' if score > 0.3 else '#2ecc71')
                    icon     = '⚠️' if pred else '✅'
                    with detail_cols[j % 3]:
                        st.markdown(f"""
                        <div class="score-card">
                            <div class="label">{icon} {label_tr}</div>
                            <div class="value" style="color:{color}">{score:.1%}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.progress(min(score, 1.0))

                # XAI / LIME Butonu ve Gösterim Alanı (Hemen model kartının altında)
                if st.session_state.get('active_lime_model') == ver and st.session_state.get('active_lime_html') is not None:
                    st.markdown(f"#### 🔮 {ver.upper()} Modeli Karar Raporu (LIME XAI)")
                    st.markdown(f"""
                    <div class="xai-info">
                        Modelin bu cümle için verdiği kararın sebepleri aşağıda gösterilmiştir.
                        <span style="color:#e74c3c; font-weight:bold;">Kırmızı</span>/Turuncu kelimeler metni <b>toksik</b> yaparken,
                        <span style="color:#2ecc71; font-weight:bold;">Yeşil</span>/Mavi kelimeler <b>güvenli</b> (masum) olarak algılanmıştır.
                    </div>
                    <div style="background-color:white; padding:15px; border-radius:12px; border:1px solid #ddd; margin-top:10px; margin-bottom: 10px;">
                    """, unsafe_allow_html=True)
                    
                    import streamlit.components.v1 as components
                    components.html(st.session_state['active_lime_html'], height=450, scrolling=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    if st.button("🗑️ XAI Açıklamasını Kapat", key=f"close_lime_{ver}"):
                        st.session_state['active_lime_model'] = None
                        st.session_state['active_lime_html'] = None
                        st.rerun()
                else:
                    is_transformer = ver in ['v3', 'v4', 'v5', 'v5_2', 'v5_02', 'v5_22']
                    btn_label = f"🔮 {ver.upper()} için LIME Açıklaması Hesapla"
                    if is_transformer:
                        btn_label += " (Transformer: ~15-30 sn)"
                        
                    if st.button(btn_label, key=f"calc_lime_{ver}"):
                        lime_samples = 30 if is_transformer else 100
                        with st.spinner(f"{ver.upper()} için LIME hesaplanıyor..."):
                            try:
                                from lime.lime_text import LimeTextExplainer
                                
                                predictor = get_cached_predictor(ver)
                                explainer = LimeTextExplainer(class_names=['Zararsız', 'Toksik'])
                                exp = explainer.explain_instance(
                                    text_to_show,
                                    predictor.predict_proba_for_lime,
                                    num_features=10,
                                    num_samples=lime_samples
                                )
                                html_exp = exp.as_html()
                                html_exp = f"<body style='background-color:white !important; color:black !important;'>{html_exp}</body>"
                                st.session_state['active_lime_model'] = ver
                                st.session_state['active_lime_html'] = html_exp
                                st.rerun()
                            except Exception as e:
                                st.error(f"{ver.upper()} XAI hatası: {e}")

                st.markdown("<br>", unsafe_allow_html=True)



def show_comparison_page():
    """Dinamik versiyon karşılaştırma sayfası — tüm versiyonları destekler."""
    st.markdown("""
    <div class="main-header">
        <h1>🔀 Versiyon Karşılaştırma</h1>
        <p>Aynı metni seçtiğiniz iki model versiyonu ile analiz edin</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        from src.predict import get_available_versions, VERSION_INFO
        from src.utils import LABEL_COLS, LABEL_NAMES_TR
        import pandas as pd
        
        versions = get_available_versions()
        if len(versions) < 2:
            st.warning("Karşılaştırma için en az **iki** model versiyonu gereklidir. Mevcut: " + ", ".join(versions))
            return
    except Exception as e:
        st.error(f"⚠️ Predict modülü yüklenemedi: {e}")
        return
    
    # Versiyon seçiciler
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        sel_a = st.selectbox(
            "Sol Versiyon",
            versions,
            index=0,
            format_func=lambda v: VERSION_INFO[v]['name'],
            key="cmp_ver_a"
        )
    with col_sel2:
        default_b_idx = min(1, len(versions) - 1)
        sel_b = st.selectbox(
            "Sağ Versiyon",
            versions,
            index=default_b_idx,
            format_func=lambda v: VERSION_INFO[v]['name'],
            key="cmp_ver_b"
        )
    
    if sel_a == sel_b:
        st.warning("Lütfen farklı iki versiyon seçin.")
        return
    
    # Model yükleme (cache'li)
    try:
        with st.spinner(f"{sel_a.upper()} ve {sel_b.upper()} modelleri yükleniyor..."):
            pred_a = get_cached_predictor(sel_a)
            pred_b = get_cached_predictor(sel_b)
    except Exception as e:
        st.error(f"⚠️ Model yüklenemedi: {e}")
        return
    
    # Versiyon bilgi kutular
    emoji_a, color_a = VERSION_COLORS.get(sel_a, ('🔵', '#3498db'))
    emoji_b, color_b = VERSION_COLORS.get(sel_b, ('🟡', '#f1c40f'))
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        info_a = VERSION_INFO[sel_a]
        st.markdown(f"""
        <div class="compare-header">
            <h3>{emoji_a} {sel_a.upper()} — {info_a['name'].split('—')[-1].strip()}</h3>
            <p style="font-size:0.8rem; color:#888;">{info_a['description']}</p>
            <p>Threshold: {pred_a.threshold:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_info2:
        info_b = VERSION_INFO[sel_b]
        st.markdown(f"""
        <div class="compare-header">
            <h3>{emoji_b} {sel_b.upper()} — {info_b['name'].split('—')[-1].strip()}</h3>
            <p style="font-size:0.8rem; color:#888;">{info_b['description']}</p>
            <p>Threshold: {pred_b.threshold:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Transformer uyarısı
    transformer_vers = [v for v in [sel_a, sel_b] if v in ('v3', 'v4')]
    if transformer_vers:
        st.info(f"⚡ **Transformer Modeli:** {', '.join(v.upper() for v in transformer_vers)} versiyonu derin öğrenme tabanlıdır. İlk çıkarım ~5-15 saniye sürebilir.")
    
    # Metin girişi
    user_text = st.text_area(
        "Karşılaştırılacak yorumu girin",
        height=120,
        placeholder="Örnek: You are such an idiot, go away!  /  Sen çok kötü birisin!",
        key="compare_text"
    )
    
    compare_btn = st.button("⚡ Karşılaştır", type="primary", use_container_width=True, key="compare_btn")
    
    if compare_btn and user_text.strip():
        with st.spinner(f"{sel_a.upper()} ve {sel_b.upper()} ile analiz ediliyor..."):
            result_a = pred_a.predict_text(user_text)
            result_b = pred_b.predict_text(user_text)
        
        st.markdown("---")
        
        # Genel skorlar yan yana
        col1, col2 = st.columns(2)
        
        with col1:
            level_a = result_a['level']
            level_class_a = _level_class(level_a['label'])
            st.markdown(f"""
            <div style='text-align:center;'>
                <span class="version-badge version-{sel_a}">{sel_a.upper()}</span>
                <div class="level-badge {level_class_a}" style="margin-top:0.5rem;">
                    {level_a['emoji']} {level_a['label']} — {result_a['overall_score']:.1%}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            level_b = result_b['level']
            level_class_b = _level_class(level_b['label'])
            st.markdown(f"""
            <div style='text-align:center;'>
                <span class="version-badge version-{sel_b}">{sel_b.upper()}</span>
                <div class="level-badge {level_class_b}" style="margin-top:0.5rem;">
                    {level_b['emoji']} {level_b['label']} — {result_b['overall_score']:.1%}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Etiket bazlı karşılaştırma tablosu
        st.subheader("📊 Etiket Bazlı Karşılaştırma")
        
        label_a = sel_a.upper()
        label_b = sel_b.upper()
        comparison_data = []
        for col in LABEL_COLS:
            s_a = result_a['scores'][col]
            s_b = result_b['scores'][col]
            delta = s_b - s_a
            comparison_data.append({
                'Etiket': LABEL_NAMES_TR[col],
                f'{label_a} Skor': f"{s_a:.3f}",
                f'{label_a} Tahmin': '⚠️ Evet' if result_a['predictions'][col] else '✅ Hayır',
                f'{label_b} Skor': f"{s_b:.3f}",
                f'{label_b} Tahmin': '⚠️ Evet' if result_b['predictions'][col] else '✅ Hayır',
                'Δ Fark': f"{delta:+.3f}",
            })
        
        df_comp = pd.DataFrame(comparison_data)
        st.dataframe(df_comp, use_container_width=True, hide_index=True)
        
        # Etiket bazlı detaylı görsel
        st.subheader("📈 Skor Karşılaştırma Grafikleri")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown(f'<div class="compare-header"><h3>{emoji_a} {label_a} Sonuçları</h3></div>', unsafe_allow_html=True)
            for col_name in LABEL_COLS:
                score = result_a['scores'][col_name]
                pred = result_a['predictions'][col_name]
                label_tr = LABEL_NAMES_TR[col_name]
                color = '#e74c3c' if pred == 1 else ('#f39c12' if score > 0.3 else '#2ecc71')
                icon = '⚠️' if pred == 1 else '✅'
                st.markdown(f"""
                <div class="score-card">
                    <div class="label">{icon} {label_tr}</div>
                    <div class="value" style="color:{color}">{score:.1%}</div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(min(score, 1.0))
        
        with col_right:
            st.markdown(f'<div class="compare-header"><h3>{emoji_b} {label_b} Sonuçları</h3></div>', unsafe_allow_html=True)
            for col_name in LABEL_COLS:
                score = result_b['scores'][col_name]
                pred = result_b['predictions'][col_name]
                label_tr = LABEL_NAMES_TR[col_name]
                color = '#e74c3c' if pred == 1 else ('#f39c12' if score > 0.3 else '#2ecc71')
                icon = '⚠️' if pred == 1 else '✅'
                st.markdown(f"""
                <div class="score-card">
                    <div class="label">{icon} {label_tr}</div>
                    <div class="value" style="color:{color}">{score:.1%}</div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(min(score, 1.0))
        
        # Temizlenmiş metin
        with st.expander("🔧 Temizlenmiş Metin"):
            st.code(result_a['cleaned_text'] or "(boş)", language=None)
    
    elif compare_btn:
        st.warning("Lütfen bir metin girin.")


def display_single_result(result, label_cols, label_names_tr):
    """Tekli tahmin sonucunu göster."""
    level = result['level']
    version = result.get('version', 'v1')
    
    # Seviye badge
    level_class = _level_class(level['label'])
    st.markdown(f"""
    <div style='text-align:center;'>
        <div class="level-badge {level_class}">
            {level['emoji']} {level['label']} — Genel Skor: {result['overall_score']:.1%}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Etiket bazlı skorlar
    cols = st.columns(3)
    for i, col_name in enumerate(label_cols):
        score = result['scores'][col_name]
        pred = result['predictions'][col_name]
        label_tr = label_names_tr[col_name]
        
        with cols[i % 3]:
            color = '#e74c3c' if pred == 1 else ('#f39c12' if score > 0.3 else '#2ecc71')
            icon = '⚠️' if pred == 1 else '✅'
            
            st.markdown(f"""
            <div class="score-card">
                <div class="label">{icon} {label_tr}</div>
                <div class="value" style="color:{color}">{score:.1%}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.progress(min(score, 1.0))
    
    # Temizlenmiş metin
    with st.expander("🔧 Temizlenmiş Metin"):
        st.code(result['cleaned_text'] or "(boş)", language=None)


def _level_class(label):
    """Seviye label'ına göre CSS class döndür."""
    if label == 'Güvenli':
        return 'level-safe'
    elif label == 'Dikkat':
        return 'level-warning'
    else:
        return 'level-danger'


def color_severity(col):
    """Seviye sütununu renklendir."""
    colors = []
    for val in col:
        if val == 'Güvenli':
            colors.append('background-color: #d4edda; color: #155724;')
        elif val == 'Dikkat':
            colors.append('background-color: #fff3cd; color: #856404;')
        elif val == 'Toksik':
            colors.append('background-color: #f8d7da; color: #721c24;')
        else:
            colors.append('')
    return colors


def show_eda_page():
    """EDA görselleştirme sayfası."""
    st.markdown("""
    <div class="main-header">
        <h1>📊 Keşifsel Veri Analizi</h1>
        <p>Veri setinin yapısını ve dağılımını keşfedin</p>
    </div>
    """, unsafe_allow_html=True)
    
    plots_dir = os.path.join(PROJECT_ROOT, 'reports', 'eda_plots')
    
    if not os.path.exists(plots_dir):
        st.warning("EDA grafikleri henüz oluşturulmamış. Lütfen önce EDA'yı çalıştırın: `python -m src.eda`")
        return
    
    plot_files = sorted([f for f in os.listdir(plots_dir) if f.endswith('.png')])
    
    if not plot_files:
        st.warning("EDA grafikleri bulunamadı.")
        return
    
    plot_titles = {
        '01_label_distribution.png': '📊 Etiket Dağılım Analizi',
        '02_class_imbalance.png': '⚖️ Sınıf Dengesizliği',
        '03_label_correlation.png': '🔗 Etiketler Arası Korelasyon',
        '04_text_statistics.png': '📝 Metin İstatistikleri',
        '05_wordclouds.png': '☁️ Kelime Bulutları',
        '06_data_summary.png': '📋 Veri Seti Özeti',
    }
    
    for plot_file in plot_files:
        title = plot_titles.get(plot_file, plot_file)
        st.subheader(title)
        st.image(os.path.join(plots_dir, plot_file), use_container_width=True)
        st.markdown("---")


def show_model_comparison_page():
    """Model karşılaştırma sayfası — V1/V2/V3/V4 destekli."""
    st.markdown("""
    <div class="main-header">
        <h1>🏆 Model Karşılaştırma</h1>
        <p>Eğitilmiş modellerin performans metrikleri</p>
    </div>
    """, unsafe_allow_html=True)
    
    import pandas as pd
    from src.utils import LABEL_NAMES_TR
    
    results_dir = os.path.join(PROJECT_ROOT, 'reports', 'model_results')
    
    # Her versiyonun JSON/CSV raporlarını bul
    VERSION_REPORT_KEYS = ['v1', 'v2', 'v3', 'v4']
    EMOJI_MAP = {'v1': '🟣', 'v2': '🔴', 'v3': '🟢', 'v4': '🟠'}
    
    found = {}  # v -> (json_path, csv_path)
    for ver in VERSION_REPORT_KEYS:
        j = os.path.join(results_dir, f'{ver}_model_comparison.json')
        c = os.path.join(results_dir, f'{ver}_model_comparison.csv')
        # V1 için eski format fallback
        if not os.path.exists(j) and ver == 'v1':
            j = os.path.join(results_dir, 'model_comparison.json')
            c = os.path.join(results_dir, 'model_comparison.csv')
        if os.path.exists(j):
            found[ver] = (j, c)
    
    if not found:
        st.warning("Model karşılaştırma sonuçları bulunamadı. Lütfen önce modelleri eğitin.")
        return
    
    # Tab oluştur
    tab_labels = []
    found_list = list(found.keys())  # sıralı liste
    
    # Özet tab — en az 2 klasik ML versiyonu varsa
    classic_ml = [v for v in found_list if v in ('v1', 'v2')]
    if len(classic_ml) >= 2:
        tab_labels.append("📊 V1 vs V2 Özet")
    
    for ver in found_list:
        emoji = EMOJI_MAP.get(ver, '🔵')
        tab_labels.append(f"{emoji} {ver.upper()} Detay")
    
    tabs = st.tabs(tab_labels)
    tab_idx = 0
    
    # Özet tab
    if len(classic_ml) >= 2:
        with tabs[tab_idx]:
            _show_version_summary(
                found['v1'][0], found['v2'][0],
                found['v1'][1], found['v2'][1],
                LABEL_NAMES_TR
            )
        tab_idx += 1
    
    # Her versiyon detay tab
    for ver in found_list:
        emoji = EMOJI_MAP.get(ver, '🔵')
        j_path, c_path = found[ver]
        with tabs[tab_idx]:
            _show_version_detail(f"{emoji} {ver.upper()}", j_path, c_path, LABEL_NAMES_TR)
        tab_idx += 1


def _load_results(json_path):
    """JSON sonuç dosyasını yükle, farklı formatları destekle."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # V2 formatı: { "metadata": {...}, "results": [...] }
    if isinstance(data, dict) and 'results' in data:
        return data['results'], data.get('metadata', {})
    
    # V1 formatı: [...]
    if isinstance(data, list):
        return data, {}
    
    return [], {}


def _show_version_summary(v1_json, v2_json, v1_csv, v2_csv, label_names_tr):
    """V1 vs V2 özet karşılaştırma göster."""
    import pandas as pd
    
    results_v1, meta_v1 = _load_results(v1_json)
    results_v2, meta_v2 = _load_results(v2_json)
    
    st.subheader("⚡ En İyi Model Karşılaştırması")
    
    best_v1 = max(results_v1, key=lambda x: x.get('f1_macro', 0))
    best_v2 = max(results_v2, key=lambda x: x.get('f1_macro', 0))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="compare-header">
            <h3>🟣 V1 En İyi</h3>
        </div>
        """, unsafe_allow_html=True)
        st.metric("Model", best_v1['model'])
        st.metric("F1 Macro", f"{best_v1['f1_macro']:.4f}")
        st.metric("ROC-AUC", f"{best_v1.get('roc_auc', 0):.4f}")
    
    with col2:
        f1_delta = best_v2['f1_macro'] - best_v1['f1_macro']
        auc_delta = best_v2.get('roc_auc', 0) - best_v1.get('roc_auc', 0)
        
        st.markdown("""
        <div class="compare-header">
            <h3>🔴 V2 En İyi</h3>
        </div>
        """, unsafe_allow_html=True)
        st.metric("Model", best_v2['model'])
        st.metric("F1 Macro", f"{best_v2['f1_macro']:.4f}", delta=f"{f1_delta:+.4f}")
        st.metric("ROC-AUC", f"{best_v2.get('roc_auc', 0):.4f}", delta=f"{auc_delta:+.4f}")
    
    # Tüm modellerin F1 karşılaştırma tablosu
    st.subheader("📋 Tüm Modellerin Karşılaştırması")
    
    # Ortak model isimlerini bul
    # V1 SVM = "SVM", V2 SVM = "Linear SVM" — normalize et
    def normalize_model_name(name):
        name = name.strip()
        if name in ('SVM', 'Linear SVM'):
            return 'SVM'
        return name
    
    v1_dict = {normalize_model_name(r['model']): r for r in results_v1}
    v2_dict = {normalize_model_name(r['model']): r for r in results_v2}
    all_models = sorted(set(list(v1_dict.keys()) + list(v2_dict.keys())))
    
    rows = []
    for m in all_models:
        r1 = v1_dict.get(m, {})
        r2 = v2_dict.get(m, {})
        f1_v1 = r1.get('f1_macro', None)
        f1_v2 = r2.get('f1_macro', None)
        
        row = {
            'Model': m,
            'V1 F1 Macro': f"{f1_v1:.4f}" if f1_v1 else "—",
            'V2 F1 Macro': f"{f1_v2:.4f}" if f1_v2 else "—",
            'V1 ROC-AUC': f"{r1.get('roc_auc', 0):.4f}" if f1_v1 else "—",
            'V2 ROC-AUC': f"{r2.get('roc_auc', 0):.4f}" if f1_v2 else "—",
        }
        
        if f1_v1 and f1_v2:
            delta = f1_v2 - f1_v1
            row['Δ F1'] = f"{delta:+.4f}"
        else:
            row['Δ F1'] = "—"
        
        rows.append(row)
    
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _show_version_detail(version_label, json_path, csv_path, label_names_tr):
    """Tekil versiyon detay göster."""
    import pandas as pd
    
    results, metadata = _load_results(json_path)
    
    if not results:
        st.warning(f"{version_label} sonuçları bulunamadı.")
        return
    
    # Performans tablosu
    st.subheader(f"📊 {version_label} Genel Performans Tablosu")
    
    if os.path.exists(csv_path):
        df_comp = pd.read_csv(csv_path)
        st.dataframe(df_comp, use_container_width=True, hide_index=True)
    
    # En iyi model
    best = max(results, key=lambda x: x.get('f1_macro', 0))
    st.success(f"🏆 En iyi model: **{best['model']}** (F1 Macro: {best['f1_macro']:.4f})")
    
    # Etiket bazlı performans
    st.subheader(f"🏷️ {version_label} Etiket Bazlı Performans")
    
    for r in results:
        with st.expander(f"📌 {r['model']}"):
            if 'per_label' in r:
                label_data = []
                for col, metrics in r['per_label'].items():
                    label_data.append({
                        'Etiket': label_names_tr.get(col, col),
                        'F1-Score': f"{metrics['f1']:.4f}",
                        'Precision': f"{metrics['precision']:.4f}",
                        'Recall': f"{metrics['recall']:.4f}",
                    })
                st.dataframe(pd.DataFrame(label_data), use_container_width=True, hide_index=True)


@st.cache_resource
def get_cached_baseline(model_key: str):
    """Baseline modeli cache'le — bir kez yükle, pipeline'ı hemen hazırla."""
    from src.baseline_predictor import BaselinePredictor
    predictor = BaselinePredictor(model_key=model_key)
    predictor._load_model()  # Pipeline'ı hemen oluştur (lazy bekleme yok)
    return predictor



def show_baseline_comparison_page():
    """
    Kendi modellerimizi unitary/toxic-bert gibi hazır endüstri
    modellerine karşı karşılaştıran sayfa.
    Hoca için: 'Sonucun doğruluğunu baseline ile ölçme' talebi.
    """
    st.markdown("""
    <div class="main-header">
        <h1>⚖️ Baseline Karşılaştırma</h1>
        <p>ToxicGuard modellerini <b>unitary/toxic-bert</b> endüstri baseline'ı ile bilimsel olarak ölçün</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        from src.predict import get_available_versions, VERSION_INFO
        from src.utils import LABEL_COLS, LABEL_NAMES_TR
        from src.baseline_predictor import BASELINE_MODELS, compare_with_baseline
        from src.api_baselines import API_BASELINES
        import pandas as pd
    except Exception as e:
        st.error(f"⚠️ Modül yüklenemedi: {e}")
        return

    # Tüm baseline seçenekleri: yerel modeller + API'ler
    ALL_BASELINES = {
        **{k: {**v, 'type': 'local'} for k, v in BASELINE_MODELS.items()},
        **{k: {**v, 'type': 'api'}  for k, v in API_BASELINES.items()},
    }

    # ── Bilgi kutuları ────────────────────────────────────────────────────
    st.info(
        "🎓 **Neden Baseline?** Akademik çalışmalarda kendi modelinin ne kadar iyi olduğunu "
        "kanıtlamak için yerleşik referans modeller kullanılır. "
        "`unitary/toxic-bert`, Kaggle Jigsaw veri setiyle eğitilmiş ve aynı 6 etiketi kullanan "
        "endüstri standardı modeldir — dolayısıyla 'apples-to-apples' karşılaştırma yapılabilir."
    )

    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown("""
        <div class="all-models-card">
            <div class="model-title">🤖 ToxicBERT (unitary/toxic-bert)</div>
            <div class="model-desc">
                BERT-base, Jigsaw Toxic Comment Challenge ile eğitilmiş.<br>
                <b>Etiketler:</b> toxic, severe_toxic, obscene, threat, insult, identity_hate<br>
                <b>Kullanım:</b> V1 / V2 / V3 ile karşılaştırma
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_info2:
        st.markdown("""
        <div class="all-models-card">
            <div class="model-title">🌍 Multilingual ToxicBERT (unitary/multilingual-toxic-xlm-roberta)</div>
            <div class="model-desc">
                XLM-RoBERTa tabanlı, çok dilli baseline.<br>
                <b>Desteklenen diller:</b> TR, EN, DE, FR, ES, IT, PT, RU<br>
                <b>Kullanım:</b> V4 (XLM-RoBERTa) ile birebir karşılaştırma
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Ayarlar ──────────────────────────────────────────────────────────
    col_s1, col_s2 = st.columns(2)

    versions = get_available_versions()
    with col_s1:
        our_version = st.selectbox(
            "📦 Bizim Modelimiz",
            versions,
            format_func=lambda v: VERSION_INFO[v]['name'],
            key="bl_our_ver"
        )
    with col_s2:
        baseline_key = st.selectbox(
            "🤖 Baseline Model",
            list(ALL_BASELINES.keys()),
            format_func=lambda k: f"{ALL_BASELINES[k]['emoji']} {ALL_BASELINES[k]['name']}",
            key="bl_baseline_key"
        )

    bl_info = ALL_BASELINES[baseline_key]

    # API seçildiyse key girişi göster
    api_key_value = ""
    if bl_info['type'] == 'api':
        import json
        import os
        
        # Daha önce kaydedilmiş key'leri oku
        key_file = "api_keys.json"
        saved_keys = {}
        if os.path.exists(key_file):
            try:
                with open(key_file, "r") as f:
                    saved_keys = json.load(f)
            except:
                pass
                
        saved_key = saved_keys.get(baseline_key, "")

        api_key_value = st.text_input(
            f"🔑 {bl_info['key_label']}",
            type="password",
            value=saved_key,
            placeholder="Buraya API key'inizi yapıştırın (Sadece ilk seferde istenir)",
            help=f"Nereden alınır: {bl_info['key_help']}",
            key=f"api_key_{baseline_key}"
        )
        
        # Eğer yeni bir key girildiyse (ve eskisinden farklıysa), kaydet
        if api_key_value and api_key_value != saved_key:
            saved_keys[baseline_key] = api_key_value
            with open(key_file, "w") as f:
                json.dump(saved_keys, f)

        if not api_key_value:
            st.warning(
                f"⚠️ **{bl_info['name']}** için API key gerekli.\n\n"
                f"**Nasıl alınır:** {bl_info['key_help']}\n\n"
                f"💡 Sadece bir kez girmeniz yeterlidir, sistem şifrenizi hatırlayacaktır."
            )

    # V4 dil uyarisi - eger baseline ingilizce ise goster
    if our_version == 'v4' and baseline_key == 'toxic-bert':
        st.warning(
            "⚠️ **V4 Çok Dilli — ToxicBERT Sadece İngilizce**\n\n"
            "💡 Çok dilli karşılaştırma için **Google Perspective API** veya **OpenAI Moderation API** seçin — Türkçe dahil tam destek."
        )
    elif our_version == 'v3' and baseline_key == 'toxic-bert':
        st.info("💡 **V3 DistilBERT** — İngilizce metinlerde ToxicBERT ile birebir karşılaştırılabilir. En anlamlı baseline sonuçlarını bu kombinasyon verir.")
    elif bl_info['type'] == 'api':
        st.success(
            f"✅ **{bl_info['emoji']} {bl_info['name']}** seçildi. "
            "Bu API Türkçe dahil çok dilli metinleri destekler — V4 için ideal karşılaştırma!"
        )

    # ── Sekme yapısı ─────────────────────────────────────────────────────
    tab_single, tab_batch = st.tabs(["✏️ Tekli Metin Analizi", "📁 Toplu Analiz (Dosya)"])

    # ═══════════════════════════════════════════════════════════════════
    # TAB 1 — Tekli metin
    # ═══════════════════════════════════════════════════════════════════
    with tab_single:
        user_text = st.text_area(
            "Analiz edilecek metni girin",
            height=130,
            placeholder="Örnek: You are such an idiot!  /  Sen gerçekten berbat birisin!",
            key="bl_single_text"
        )

        run_btn = st.button(
            "⚖️ Karşılaştır",
            type="primary",
            use_container_width=True,
            key="bl_single_btn"
        )

        if run_btn and user_text.strip():
            # API seçildiyse key kontrolü
            if bl_info['type'] == 'api' and not api_key_value:
                st.error("⛔ Lütfen önce API key'inizi girin.")
                return

            col_prog1, col_prog2 = st.columns(2)

            with st.spinner("Modellar çalışıyor…"):
                # Kendi modelimiz
                try:
                    our_pred = get_cached_predictor(our_version)
                    our_result = our_pred.predict_text(user_text)
                except Exception as e:
                    st.error(f"Kendi modelimiz hata verdi: {e}")
                    return

                # Baseline — yerel model veya API
                try:
                    if bl_info['type'] == 'api':
                        if baseline_key == 'perspective':
                            from src.api_baselines import PerspectiveAPIPredictor
                            bl_pred = PerspectiveAPIPredictor(api_key_value)
                        else:  # openai
                            from src.api_baselines import OpenAIModerationPredictor
                            bl_pred = OpenAIModerationPredictor(api_key_value)
                        bl_result = bl_pred.predict_text(user_text)
                    else:
                        bl_pred = get_cached_baseline(baseline_key)
                        bl_result = bl_pred.predict_text(user_text)
                except Exception as e:
                    st.error(f"Baseline hata verdi: {e}")
                    return

            from src.baseline_predictor import compare_with_baseline
            cmp = compare_with_baseline(our_result, bl_result)

            st.markdown("---")

            # ── Genel özet banner ────────────────────────────────────
            st.subheader("🎯 Genel Özet")
            c1, c2, c3, c4 = st.columns(4)

            our_lvl = our_result['level']
            bl_lvl = bl_result['level']
            our_lc = _level_class(our_lvl['label'])
            bl_lc = _level_class(bl_lvl['label'])

            with c1:
                st.markdown(f"""
                <div class="all-models-card" style="text-align:center;">
                    <div class="model-title">📦 {our_version.upper()} (Bizim)</div>
                    <div class="level-badge {our_lc}" style="font-size:0.9rem;padding:0.3rem 0.8rem;margin-top:0.4rem;">
                        {our_lvl['emoji']} {our_lvl['label']} — {our_result['overall_score']:.1%}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
                <div class="all-models-card" style="text-align:center;">
                    <div class="model-title">{bl_info['emoji']} Baseline</div>
                    <div class="level-badge {bl_lc}" style="font-size:0.9rem;padding:0.3rem 0.8rem;margin-top:0.4rem;">
                        {bl_lvl['emoji']} {bl_lvl['label']} — {bl_result['overall_score']:.1%}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with c3:
                agree_pct = cmp['agreement_rate'] * 100
                agree_color = "#2ecc71" if agree_pct >= 80 else ("#f39c12" if agree_pct >= 60 else "#e74c3c")
                st.markdown(f"""
                <div class="metric-box" style="text-align:center;">
                    <div style="font-size:0.8rem;color:#888;">Etiket Uyum Oranı</div>
                    <div class="number" style="color:{agree_color};">{agree_pct:.0f}%</div>
                    <div style="font-size:0.75rem;color:#888;">{int(agree_pct/100*len(LABEL_COLS))}/{len(LABEL_COLS)} etiket</div>
                </div>
                """, unsafe_allow_html=True)

            with c4:
                delta = cmp['overall_delta']
                delta_color = "#e74c3c" if delta > 0.1 else ("#2ecc71" if abs(delta) <= 0.05 else "#f39c12")
                delta_label = "Bizim Yüksek ↑" if delta > 0.05 else ("Baseline Yüksek ↓" if delta < -0.05 else "Uyumlu ≈")
                st.markdown(f"""
                <div class="metric-box" style="text-align:center;">
                    <div style="font-size:0.8rem;color:#888;">Genel Skor Farkı</div>
                    <div class="number" style="color:{delta_color};">{delta:+.3f}</div>
                    <div style="font-size:0.75rem;color:#888;">{delta_label}</div>
                </div>
                """, unsafe_allow_html=True)

            # ── Etiket bazlı karşılaştırma tablosu ──────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📊 Etiket Bazlı Karşılaştırma")

            rows = []
            for label in LABEL_COLS:
                lc = cmp['label_comparison'][label]
                agree_icon = "✅" if lc['agreement'] else "❌"
                delta_str = f"{lc['delta']:+.3f}"
                rows.append({
                    "Etiket": LABEL_NAMES_TR[label],
                    f"📦 {our_version.upper()} Skor": f"{lc['our_score']:.3f}",
                    f"📦 {our_version.upper()} Tahmin": "⚠️ Evet" if lc['our_pred'] else "✅ Hayır",
                    f"{bl_info['emoji']} Baseline Skor": f"{lc['baseline_score']:.3f}",
                    f"{bl_info['emoji']} Baseline Tahmin": "⚠️ Evet" if lc['baseline_pred'] else "✅ Hayır",
                    "Δ Fark": delta_str,
                    "Uyum": agree_icon,
                })

            df_cmp = pd.DataFrame(rows)
            st.dataframe(df_cmp, use_container_width=True, hide_index=True)

            # ── Etiket görsel karşılaştırma ──────────────────────────
            st.subheader("📈 Skor Karşılaştırma Grafikleri")
            gcol1, gcol2 = st.columns(2)

            with gcol1:
                st.markdown(f"**📦 {our_version.upper()} — {VERSION_INFO[our_version]['name'].split('—')[-1].strip()}**")
                for label in LABEL_COLS:
                    s = our_result['scores'][label]
                    p = our_result['predictions'][label]
                    color = '#e74c3c' if p else ('#f39c12' if s > 0.3 else '#2ecc71')
                    icon = '⚠️' if p else '✅'
                    st.markdown(f"""
                    <div class="score-card">
                        <div class="label">{icon} {LABEL_NAMES_TR[label]}</div>
                        <div class="value" style="color:{color}">{s:.1%}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(min(s, 1.0))

            with gcol2:
                st.markdown(f"**{bl_info['emoji']} {bl_info['name']}**")
                for label in LABEL_COLS:
                    s = bl_result['scores'][label]
                    p = bl_result['predictions'][label]
                    color = '#e74c3c' if p else ('#f39c12' if s > 0.3 else '#2ecc71')
                    icon = '⚠️' if p else '✅'
                    st.markdown(f"""
                    <div class="score-card">
                        <div class="label">{icon} {LABEL_NAMES_TR[label]}</div>
                        <div class="value" style="color:{color}">{s:.1%}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(min(s, 1.0))

            # ── Yorum / Analiz ───────────────────────────────────────
            with st.expander("💬 Otomatik Yorum — Modelin Durumu"):
                if cmp['agreement_rate'] >= 5/6:
                    st.success(
                        f"✅ **Yüksek Uyum ({cmp['agreement_rate']:.0%}):** "
                        f"{our_version.upper()} modelimiz, {bl_info['name']} baseline ile "
                        f"büyük ölçüde hemfikirdir. Bu, modelimizin genel toksisite kararlarında "
                        f"doğru çalıştığını gösterir."
                    )
                elif cmp['agreement_rate'] >= 3/6:
                    st.warning(
                        f"⚠️ **Orta Uyum ({cmp['agreement_rate']:.0%}):** "
                        f"Bazı etiketlerde görüş ayrılığı var. Bu, "
                        f"threshold optimizasyonu veya sınıf dengesizliği kaynaklı olabilir."
                    )
                else:
                    st.error(
                        f"❌ **Düşük Uyum ({cmp['agreement_rate']:.0%}):** "
                        f"Modelimiz baseline ile önemli ölçüde farklı kararlar veriyor. "
                        f"Bu bir hata değil — bağlam anlama (V3/V4) gibi üstün özelliklerden "
                        f"kaynaklanıyor olabilir. Detaylı analiz için dosya yükleme sekmesini kullanın."
                    )

                if not cmp['level_agreement']:
                    st.info(
                        f"ℹ️ **Risk Seviyesi Farklı:** "
                        f"Bizim modelimiz → **{cmp['our_level']}**, "
                        f"Baseline → **{cmp['baseline_level']}**. "
                        f"Bu, threshold farkından (V2: 0.25) veya bağlam yorumundan kaynaklanıyor olabilir."
                    )

        elif run_btn:
            st.warning("Lütfen bir metin girin.")

    # ═══════════════════════════════════════════════════════════════════
    # TAB 2 — Toplu analiz
    # ═══════════════════════════════════════════════════════════════════
    with tab_batch:
        st.markdown("##### 📤 Dosya Yükle — Toplu Baseline Karşılaştırma")
        st.markdown("`.txt` (her satır ayrı yorum) veya `.csv` dosyası yükleyin.")

        uploaded = st.file_uploader(
            "Dosya seçin",
            type=["txt", "csv"],
            key="bl_file_upload"
        )

        col_name = None
        if uploaded is not None:
            ft = uploaded.name.split(".")[-1].lower()
            fc = uploaded.read()
            if len(fc) > 5 * 1024 * 1024:
                st.error("Maksimum 5MB yükleyebilirsiniz.")
                return
            if ft == "csv":
                import io
                tmp_df = pd.read_csv(io.StringIO(fc.decode("utf-8", errors="ignore")))
                text_cols = tmp_df.select_dtypes(include="object").columns.tolist()
                if text_cols:
                    col_name = st.selectbox("Yorum sütununu seçin", text_cols, key="bl_csv_col")
                else:
                    st.error("CSV dosyasında metin sütunu bulunamadı.")
                    return

            if st.button("⚖️ Toplu Karşılaştırmayı Başlat", type="primary",
                         use_container_width=True, key="bl_batch_btn"):

                # Metinleri çıkar
                if ft == "txt":
                    texts = [l.strip() for l in fc.decode("utf-8", errors="ignore").split("\n")
                             if l.strip() and not l.strip().startswith("===")]
                else:
                    import io
                    df_in = pd.read_csv(io.StringIO(fc.decode("utf-8", errors="ignore")))
                    col = col_name or df_in.select_dtypes(include="object").columns[0]
                    texts = df_in[col].dropna().astype(str).tolist()

                if not texts:
                    st.warning("Dosyada analiz edilecek yorum bulunamadı.")
                    return

                st.info(f"📄 **{len(texts)}** yorum bulundu. Karşılaştırma başlıyor…")

                progress = st.progress(0, text="Yükleniyor…")
                our_pred = get_cached_predictor(our_version)
                bl_pred = get_cached_baseline(baseline_key)

                our_results, bl_results, cmp_results = [], [], []

                for i, text in enumerate(texts):
                    progress.progress((i + 1) / len(texts),
                                      text=f"Analiz ediliyor: {i+1}/{len(texts)}")
                    try:
                        or_ = our_pred.predict_text(text)
                        bl_ = bl_pred.predict_text(text)
                        cmp_ = compare_with_baseline(or_, bl_)
                    except Exception as e:
                        or_ = {"overall_score": 0, "level": {"label": "Hata", "emoji": "❓"},
                               "scores": {l: 0 for l in LABEL_COLS}, "predictions": {l: 0 for l in LABEL_COLS}}
                        bl_ = or_.copy()
                        cmp_ = {"agreement_rate": 0, "overall_delta": 0,
                                "our_level": "Hata", "baseline_level": "Hata",
                                "level_agreement": False, "mean_abs_delta": 0}
                    our_results.append(or_)
                    bl_results.append(bl_)
                    cmp_results.append(cmp_)

                progress.progress(1.0, text="✅ Tamamlandı!")
                st.markdown("---")

                # ── Özet istatistikler ───────────────────────────────
                st.subheader("📊 Toplu Özet")
                avg_agree = sum(c['agreement_rate'] for c in cmp_results) / len(cmp_results)
                level_agree_count = sum(1 for c in cmp_results if c['level_agreement'])
                our_toxic = sum(1 for r in our_results if r['level']['label'] == 'Toksik')
                bl_toxic = sum(1 for r in bl_results if r['level']['label'] == 'Toksik')

                mc1, mc2, mc3, mc4 = st.columns(4)
                mc1.metric("Toplam Yorum", len(texts))
                mc2.metric("Ort. Etiket Uyumu", f"{avg_agree:.0%}")
                mc3.metric(f"Toksik ({our_version.upper()})", our_toxic)
                mc4.metric(f"Toksik (Baseline)", bl_toxic,
                           delta=bl_toxic - our_toxic,
                           delta_color="inverse")

                # ── Detaylı sonuç tablosu ────────────────────────────
                st.subheader("📋 Yorum Bazlı Karşılaştırma")
                table_rows = []
                for i, text in enumerate(texts):
                    or_ = our_results[i]
                    bl_ = bl_results[i]
                    cmp_ = cmp_results[i]
                    table_rows.append({
                        "#": i + 1,
                        "Yorum": text[:100] + ("…" if len(text) > 100 else ""),
                        f"{our_version.upper()} Skor": f"{or_['overall_score']:.3f}",
                        f"{our_version.upper()} Seviye": f"{or_['level']['emoji']} {or_['level']['label']}",
                        "Baseline Skor": f"{bl_['overall_score']:.3f}",
                        "Baseline Seviye": f"{bl_['level']['emoji']} {bl_['level']['label']}",
                        "Etiket Uyumu": f"{cmp_['agreement_rate']:.0%}",
                        "Seviye Uyumu": "✅" if cmp_['level_agreement'] else "❌",
                    })

                df_batch = pd.DataFrame(table_rows)
                st.dataframe(df_batch, use_container_width=True, hide_index=True, height=500)

                # ── CSV indirme ───────────────────────────────────────
                csv_rows = []
                for i, text in enumerate(texts):
                    or_ = our_results[i]
                    bl_ = bl_results[i]
                    cmp_ = cmp_results[i]
                    row = {
                        "yorum": text,
                        f"{our_version}_genel_skor": round(or_['overall_score'], 4),
                        f"{our_version}_seviye": or_['level']['label'],
                        "baseline_genel_skor": round(bl_['overall_score'], 4),
                        "baseline_seviye": bl_['level']['label'],
                        "etiket_uyum_orani": round(cmp_['agreement_rate'], 4),
                        "seviye_uyumu": cmp_['level_agreement'],
                        "genel_skor_farki": round(cmp_['overall_delta'], 4),
                    }
                    for label in LABEL_COLS:
                        lc = cmp_['label_comparison'][label]
                        row[f"{label}_{our_version}_skor"] = round(lc['our_score'], 4)
                        row[f"{label}_baseline_skor"] = round(lc['baseline_score'], 4)
                        row[f"{label}_delta"] = round(lc['delta'], 4)
                        row[f"{label}_uyum"] = lc['agreement']
                    csv_rows.append(row)

                df_dl = pd.DataFrame(csv_rows)
                csv_bytes = df_dl.to_csv(index=False, sep=';').encode("utf-8-sig")
                st.download_button(
                    "📥 Tüm Karşılaştırma Sonuçlarını CSV İndir",
                    data=csv_bytes,
                    file_name=f"baseline_karsilastirma_{our_version}_vs_{baseline_key}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )


if __name__ == '__main__':
    main()
