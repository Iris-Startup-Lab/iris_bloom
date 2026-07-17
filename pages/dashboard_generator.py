import streamlit as st
import json
import os
from pathlib import Path
from modules import DesignParser, BoardGenerator, DataValidator
from modules.cwtwb_runner import CwtwbRunner

st.title("📈 Generador de Tableros MCP")
st.caption("Genera archivos .twb para Tableau Desktop vía cwtwb")

design = DesignParser()
design_config = design.parse()
PRIMARY = design_config["colors"]["primary"]
TERTIARY = design_config["colors"]["tertiary"]

data_validator = DataValidator()
df = st.session_state.df
report = st.session_state.validator_report
model_choice = st.session_state.model_choice
api_key = st.session_state.get(f"{model_choice.lower()}_api_key", "")

available, method = CwtwbRunner.check_available()

col_left, col_right = st.columns([5, 7])

with col_left:
    with st.container():
        st.subheader("📄 DESIGN.md")
        try:
            design_content = open("DESIGN.md", encoding="utf-8").read()
            with st.expander("Ver DESIGN.md", expanded=False):
                st.code(design_content, language="markdown")
        except FileNotFoundError:
            st.info("No se encontró DESIGN.md. Usando defaults.")

    with st.container():
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
                (f"{m['label']} — {m['desc'][:60]}" for m in models if m["id"] == x), x),
        )
        st.session_state.model_version = model_version

    with st.container():
        st.subheader("📄 Salida")
        output_dir = st.text_input("Directorio de salida", value="output", placeholder="output")
        output_file = st.text_input("Nombre del archivo", value="dashboard.twb", placeholder="dashboard.twb")
        output_path = os.path.join(output_dir, output_file)

    with st.container():
        st.subheader("✍️ Prompt")
        prompt = st.text_area(
            "Describe el tablero",
            placeholder="Ej: Crea una comparativa de ventas trimestrales por región con KPI de revenue...",
            height=150,
        )

        can_generate = bool(api_key) and bool(prompt) and df is not None and available
        if not api_key:
            st.warning(f"Ingresa la API Key de {model_choice} en el sidebar.")

        if st.button("🚀 Enviar Prompt y Generar .twb", type="primary", disabled=not can_generate, use_container_width=True):
            with st.spinner("Paso 1/2 — Generando spec con IA..."):
                columns = list(df.columns)
                stats = data_validator.get_summary_stats(df) if report else None
                board_gen = BoardGenerator(model=model_version)
                spec = board_gen.build_spec(
                    columns=columns,
                    prompt=prompt,
                    design_config=st.session_state.design_config,
                    summary_stats=stats,
                )
                ds = {"dtypes": report.get("dtypes", {})} if report else {}
                spec["data_schema"] = {**spec.get("data_schema", {}), **ds}
                st.session_state["last_board_spec"] = spec

            dataset_path = st.session_state.get("_dataset_temp_path", "")

            with st.spinner(f"Paso 2/2 — Ejecutando cwtwb..."):
                runner = CwtwbRunner()
                result = runner.generate_twb(spec, output_path, dataset_path=dataset_path)
                st.session_state["twb_result"] = result

            if result.get("success"):
                st.balloons()
            st.rerun()

with col_right:
    if not available:
        st.error("⚠️ cwtwb no instalado.")
        st.code("pip install cwtwb", language="bash")
    else:
        st.success(f"✅ cwtwb detectado: `{method}`")

    if df is not None:
        st.subheader("⚙️ Dataset")

        if report:
            st.markdown(f"""
            <div style="background:rgba(30,41,59,0.7);backdrop-filter:blur(12px);border:1px solid #334155;border-radius:0.5rem;padding:1rem;margin-bottom:1rem;">
                <span style="color:{TERTIARY};">✅ {st.session_state.data_file_name or 'N/A'}</span><br>
                <span style="color:#8c909f;">Calidad: {report['score']:.1f}% | {report['rows']} filas × {report['columns']} cols</span>
                <br><span style="color:#8c909f;font-size:0.75rem;">Fuente: {st.session_state.get('_dataset_temp_path', 'en memoria')}</span>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("📋 Schema", expanded=True):
            for col in df.columns:
                dtype = str(df[col].dtype)
                icon = "🔢" if "int" in dtype or "float" in dtype else "📝" if "object" in dtype else "📅"
                st.markdown(f"{icon} `{col}` → `{dtype}`")

        result = st.session_state.get("twb_result")
        if result:
            if result.get("success"):
                twb_path = result.get("output_path", "")
                st.success(f"✅ .twb generado")
                if os.path.exists(twb_path):
                    with open(twb_path, encoding="utf-8") as f:
                        twb_content = f.read()
                    st.download_button(
                        "⬇️ Descargar .twb",
                        data=twb_content,
                        file_name=os.path.basename(twb_path),
                        mime="application/xml",
                        use_container_width=True,
                    )
            else:
                st.error(f"Error: {result.get('error', 'desconocido')}")

            with st.expander("📋 Log de ejecución", expanded=True):
                for s in result.get("steps", []):
                    st.markdown(f"- {s}")

            with st.expander("📦 Spec generado", expanded=False):
                spec = st.session_state.get("last_board_spec", {})
                st.json(spec)
                st.download_button(
                    "⬇️ spec.json",
                    data=json.dumps(spec, indent=2),
                    file_name="dashboard_spec.json",
                    mime="application/json",
                )

    else:
        st.info("Ve a **Data Center** primero para cargar un dataset.")

st.markdown("---")
st.caption("Integración con [cwtwb MCP](https://github.com/imgwho/cwtwb) • Tableau .twb Generator")
