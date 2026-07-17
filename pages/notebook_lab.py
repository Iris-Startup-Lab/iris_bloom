import streamlit as st
import json
from modules import NotebookGenerator

st.title("📓 Notebook Lab — Análisis Complejo")
st.caption("Genera notebooks de Colab para análisis avanzados vía colab-mcp")

design = st.session_state.design_config
PRIMARY = design["colors"]["primary"]
TERTIARY = design["colors"]["tertiary"]

df = st.session_state.df
report = st.session_state.validator_report
model_choice = st.session_state.model_choice
api_key = st.session_state.get(f"{model_choice.lower()}_api_key", "")

col_left, col_right = st.columns([5, 7])

with col_left:
    st.subheader("🎯 Tipo de Análisis")
    analysis_type = st.selectbox(
        "Selecciona el tipo",
        options=["exploratory", "predictive", "clustering", "timeseries", "nlp"],
        format_func=lambda x: {
            "exploratory": "🔍 Análisis Exploratorio (EDA)",
            "predictive": "🤖 Modelo Predictivo",
            "clustering": "🔗 Clustering",
            "timeseries": "📈 Series Temporales",
            "nlp": "💬 NLP / Texto",
        }.get(x, x),
    )

    st.subheader("🤖 Modelo")

    models = st.session_state.MODEL_VERSIONS[model_choice]
    model_ids = [m["id"] for m in models]
    current_ver = st.session_state.get("model_version", "")

    selected_idx = 0
    if current_ver in model_ids:
        selected_idx = model_ids.index(current_ver)

    model_version = st.selectbox(
        "Versión del modelo",
        options=model_ids,
        index=selected_idx,
        format_func=lambda x: next(
            (f"{m['label']} — {m['desc'][:60]}" for m in models if m["id"] == x),
            x,
        ),
    )
    st.session_state.model_version = model_version
    st.caption(f"{len(models)} modelos disponibles • Usa Refresh en sidebar para actualizar")

    st.subheader("📝 Prompt del Análisis")
    analysis_prompt = st.text_area(
        "Describe qué análisis necesitas",
        placeholder="Ej: Realiza un clustering de clientes por comportamiento de compra...",
        height=120,
    )

    can_generate = bool(api_key) and bool(analysis_prompt)
    if not api_key:
        st.warning(f"API Key de {model_choice} no configurada. Ve al sidebar.")

    generate_colab = st.button(
        "🚀 Generar Notebook",
        type="primary",
        disabled=not can_generate,
        use_container_width=True,
    )

with col_right:
    if df is not None:
        st.subheader("📋 Dataset Activo")
        st.markdown(f"""
        <div style="background:rgba(30,41,59,0.7);backdrop-filter:blur(12px);border:1px solid #334155;border-radius:0.5rem;padding:1rem;margin-bottom:1rem;">
            <span style="color:{TERTIARY};">✅ {st.session_state.data_file_name or 'Dataset cargado'}</span><br>
            <span style="color:#8c909f;">{df.shape[0]} filas × {df.shape[1]} columnas</span>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Columnas disponibles", expanded=False):
            for col in df.columns:
                dtype = str(df[col].dtype)
                st.markdown(f"- `{col}` → `{dtype}`")
    else:
        st.info("Carga un dataset en **Data Center** primero.")

    if generate_colab:
        with st.spinner(f"Generando notebook con {model_version}..."):
            columns = list(df.columns) if df is not None else []
            dataset_summary = None
            if df is not None:
                dataset_summary = {"rows": len(df), "columns": len(df.columns), "column_names": columns}

            notebook_gen = NotebookGenerator(model=model_version)
            spec = notebook_gen.build_notebook_spec(
                columns=columns, prompt=analysis_prompt,
                dataset_summary=dataset_summary, analysis_type=analysis_type,
            )
            colab_payload = notebook_gen.generate_mcp_payload(spec)
            st.session_state["last_notebook_spec"] = spec
            st.session_state["last_colab_payload"] = colab_payload

        st.success(f"✅ Notebook generado con {model_version}")

        tab1, tab2, tab3 = st.tabs(["📦 Spec", "🔌 Payload MCP", "📥 Descargar .ipynb"])
        with tab1:
            st.json(spec)
        with tab2:
            st.code(json.dumps(colab_payload, indent=2), language="json")
        with tab3:
            notebook_json = notebook_gen.render_notebook_json(spec)
            notebook_str = json.dumps(notebook_json, indent=2)
            st.code(notebook_str[:2000] + "...", language="json")
            file_name = f"analysis_{analysis_type}_{st.session_state.data_file_name or 'dataset'}.ipynb"
            st.download_button(
                label="⬇️ Descargar .ipynb", data=notebook_str,
                file_name=file_name, mime="application/json", use_container_width=True,
            )

st.markdown("---")
st.caption("Integración con [colab-mcp](https://github.com/googlecolab/colab-mcp) • Google Colab Notebook Generator")
