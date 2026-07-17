import streamlit as st
import json
import httpx
from pathlib import Path
from modules import DesignParser, DataValidator, BoardGenerator, NotebookGenerator

st.set_page_config(
    page_title="Nexus AI Studio - Synthetic Precision",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

design = DesignParser()
design_config = design.parse()
st.markdown(design.get_css(), unsafe_allow_html=True)

PRIMARY = design_config["colors"]["primary"]
SECONDARY = design_config["colors"]["secondary"]
TERTIARY = design_config["colors"]["tertiary"]
BG = design_config["colors"]["background"]
ON_SURFACE = design_config["colors"]["on_surface"]

for key in ["df", "validator_report", "data_file_name", "last_board_spec", "last_mcp_payload",
            "last_notebook_spec", "last_colab_payload"]:
    if key not in st.session_state:
        st.session_state[key] = None

if "design_config" not in st.session_state:
    st.session_state.design_config = design_config
if "model_choice" not in st.session_state:
    st.session_state.model_choice = "DeepSeek"
if "deepseek_api_key" not in st.session_state:
    st.session_state.deepseek_api_key = ""
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""

FALLBACK_MODELS = {
    "DeepSeek": [
        {"id": "deepseek-chat", "label": "DeepSeek-V3", "desc": "Modelo conversacional", "tags": ["Chat"]},
    ],
    "Gemini": [
        {"id": "gemini-2.0-flash", "label": "Gemini 2.0 Flash", "desc": "Modelo rápido", "tags": ["Flash"]},
    ],
}

if "MODEL_VERSIONS" not in st.session_state:
    st.session_state.MODEL_VERSIONS = FALLBACK_MODELS
if "model_version" not in st.session_state:
    st.session_state.model_version = ""


def fetch_deepseek_models(api_key: str):
    try:
        resp = httpx.get(
            "https://api.deepseek.com/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        models = []
        for m in data.get("data", []):
            mid = m.get("id", "")
            if not mid:
                continue
            models.append({
                "id": mid,
                "label": m.get("id", mid),
                "desc": m.get("description", m.get("owned_by", "") or ""),
                "tags": [m.get("object", "model")],
            })
        return models if models else FALLBACK_MODELS["DeepSeek"]
    except Exception:
        return FALLBACK_MODELS["DeepSeek"]


def fetch_gemini_models(api_key: str):
    try:
        resp = httpx.get(
            "https://generativelanguage.googleapis.com/v1beta/models",
            params={"key": api_key},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        models = []
        for m in data.get("models", []):
            name = m.get("name", "").replace("models/", "")
            if not name or "generateContent" not in m.get("supportedGenerationMethods", []):
                continue
            desc = m.get("description", "") or ""
            models.append({
                "id": name,
                "label": m.get("displayName", name),
                "desc": desc[:120] if desc else "",
                "tags": [v for v in [m.get("version", "")] if v],
            })
        return models if models else FALLBACK_MODELS["Gemini"]
    except Exception:
        return FALLBACK_MODELS["Gemini"]


with st.sidebar:
    st.markdown("### 🤖 API Keys")
    st.caption("Las claves se guardan solo en la sesión actual.")

    selected_model = st.radio(
        "Modelo activo",
        options=["DeepSeek", "Gemini"],
        index=0,
        format_func=lambda x: {"DeepSeek": "🧠 DeepSeek", "Gemini": "🌟 Gemini"}.get(x, x),
        key="sidebar_model",
    )
    st.session_state.model_choice = selected_model

    key_field = f"{selected_model.lower()}_api_key"
    api_key_value = st.text_input(
        f"{selected_model} API Key",
        type="password",
        value=st.session_state.get(key_field, ""),
        placeholder="sk-..." if selected_model == "DeepSeek" else "AIza...",
        key=key_field,
    )

    refresh_disabled = not bool(api_key_value)

    col_btn, col_status = st.columns([1, 2])
    with col_btn:
        refresh_clicked = st.button(
            "🔄 Refresh", disabled=refresh_disabled,
            help="Obtener modelos disponibles con esta API key",
            use_container_width=True,
        )
    with col_status:
        st.caption("")

    if refresh_clicked:
        with st.spinner(f"Obteniendo modelos de {selected_model}..."):
            if selected_model == "DeepSeek":
                models = fetch_deepseek_models(api_key_value)
            else:
                models = fetch_gemini_models(api_key_value)

            st.session_state.MODEL_VERSIONS[selected_model] = models

            current = st.session_state.get("model_version", "")
            ids = [m["id"] for m in models]
            if current not in ids:
                st.session_state.model_version = ids[0] if ids else ""

    models = st.session_state.MODEL_VERSIONS[selected_model]
    with st.expander(f"📦 Modelos ({len(models)} disponibles)", expanded=False):
        if not models:
            st.caption("Presiona Refresh para cargar modelos.")
        else:
            model_ids = [m["id"] for m in models]
            selected_idx = 0
            current_ver = st.session_state.get("model_version", "")
            if current_ver in model_ids:
                selected_idx = model_ids.index(current_ver)

            sel = st.selectbox(
                "Versión", model_ids,
                index=selected_idx,
                label_visibility="collapsed",
                key="sidebar_model_version",
            )
            st.session_state.model_version = sel

            for m in models:
                st.markdown(f"""<div style="font-size:0.75rem;padding:0.25rem 0;border-bottom:1px solid #334155;">
                    <span style="color:#dae2fd;">{m['label']}</span>
                    <span style="color:#8c909f;margin-left:0.5rem;">{m['id']}</span>
                </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🧠 Nexus AI Studio")
    st.caption("v2.4.0-Alpha • Synthetic Precision")

st.markdown(f"""
<style>
    .stApp, .stApp > div {{
        background-color: {BG};
        color: {ON_SURFACE};
    }}
    .stSidebar, .stSidebar > div {{
        background-color: #131b2e;
    }}
    div[data-testid="stSidebarNav"] {{
        background-color: #131b2e;
    }}
    div[data-testid="stSidebarNav"] li {{
        padding: 0.5rem 1rem;
    }}
    div[data-testid="stSidebarNav"] li a {{
        color: #c2c6d6 !important;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
    }}
    div[data-testid="stSidebarNav"] li a:hover {{
        color: {PRIMARY} !important;
    }}
    div[data-testid="stSidebarNav"] li a[aria-current="page"] {{
        color: {PRIMARY} !important;
        font-weight: 600;
        border-right: 2px solid {PRIMARY};
    }}
    h1, h2, h3 {{
        font-family: 'Inter', sans-serif;
        color: {ON_SURFACE} !important;
    }}
    code, pre {{
        font-family: 'JetBrains Mono', monospace !important;
    }}
    .stButton button {{
        background-color: {PRIMARY};
        color: #002e6a;
        font-weight: 600;
        border: none;
        border-radius: 0.375rem;
        transition: all 0.2s;
    }}
    .stButton button:hover {{
        opacity: 0.9;
        transform: scale(1.02);
    }}
    .stButton button[kind="secondary"] {{
        background: transparent;
        border: 1px solid #334155;
        color: {ON_SURFACE};
    }}
    div[data-testid="stDataFrame"] {{
        background: #171f33;
        border: 1px solid #334155;
        border-radius: 0.5rem;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0;
        border-bottom: 1px solid #334155;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: #8c909f;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        padding: 0.75rem 1.5rem;
    }}
    .stTabs [aria-selected="true"] {{
        color: {PRIMARY} !important;
        border-bottom: 2px solid {PRIMARY} !important;
    }}
    .stAlert {{
        background: transparent;
        border: 1px solid #334155;
        border-radius: 0.5rem;
    }}
    .stTextInput input, .stTextArea textarea {{
        background-color: #060e20;
        color: {ON_SURFACE};
        border: 1px solid #334155;
        border-radius: 0.375rem;
    }}
    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: {PRIMARY};
    }}
    div[data-testid="stMetricValue"] {{
        color: {PRIMARY};
    }}
    div[role="radiogroup"] label {{
        background-color: #131b2e !important;
        border: 1px solid #334155 !important;
        border-radius: 0.5rem;
        padding: 1rem;
        color: {ON_SURFACE};
    }}
    div[role="radiogroup"] label:hover {{
        border-color: {PRIMARY} !important;
    }}
    .stProgress > div > div {{
        background-color: {TERTIARY};
    }}
</style>
""", unsafe_allow_html=True)

pg = st.navigation([
    st.Page("pages/data_center.py", title="Data Center", icon="📊"),
    st.Page("pages/dashboard_generator.py", title="Generador de Tableros", icon="📈"),
    st.Page("pages/notebook_lab.py", title="Notebook Lab", icon="📓"),
])

pg.run()
