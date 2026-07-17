import streamlit as st
import os
import tempfile
from modules import DesignParser, DataValidator
import pandas as pd
import time

st.title("📊 Data Center")
st.caption("Sube y valida tus datasets para la orquestación de tableros.")

design = DesignParser()
design_config = design.parse()
PRIMARY = design_config["colors"]["primary"]
TERTIARY = design_config["colors"]["tertiary"]
ERROR = design_config["colors"]["error"]
WARNING = design_config["colors"]["warning"]

data_validator = DataValidator()
df = st.session_state.df
report = st.session_state.validator_report
file_name = st.session_state.data_file_name

col_left, col_right = st.columns([5, 7])

with col_left:
    with st.container():
        st.markdown(f"""
        <div style="
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            border: 2px dashed #334155;
            border-radius: 0.75rem;
            padding: 2rem;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
        " onmouseover="this.style.borderColor='{PRIMARY}'" onmouseout="this.style.borderColor='#334155'">
            <div style="font-size: 48px; color: {PRIMARY};">📄</div>
            <h3 style="margin-top: 0.5rem;">Ingestar Nuevo Dataset</h3>
            <p style="color: #8c909f;">CSV, XLSX — Max 200MB</p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Seleccionar archivo",
            type=["csv", "xls", "xlsx"],
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            with st.spinner("Analizando archivo..."):
                file_bytes = uploaded_file.getvalue()
                df = data_validator.load_file(file_bytes, uploaded_file.name)

                if df is None:
                    st.error("Formato no soportado o archivo corrupto.")
                else:
                    report = data_validator.validate(df)
                    st.session_state.df = df
                    st.session_state.validator_report = report
                    st.session_state.data_file_name = uploaded_file.name

                    tmp_dir = tempfile.mkdtemp(prefix="nexus_dataset_")
                    ext = uploaded_file.name.rsplit(".", 1)[-1] if "." in uploaded_file.name else "csv"
                    tmp_path = os.path.join(tmp_dir, f"dataset.{ext}")
                    with open(tmp_path, "wb") as f:
                        f.write(file_bytes if ext in ("xls", "xlsx") else file_bytes)
                    st.session_state._dataset_temp_path = tmp_path

                    progress = report["score"] / 100
                    st.progress(progress)

                    if report["passed"]:
                        st.success(f"Dataset validado: {report['score']:.1f}% de calidad")
                    else:
                        st.error(f"Dataset con problemas: {report['score']:.1f}% de calidad")

    if df is not None and report:
        st.markdown("---")
        st.subheader("📋 Resumen del Dataset")

        m1, m2, m3 = st.columns(3)
        m1.metric("Filas", report["rows"])
        m2.metric("Columnas", report["columns"])
        m3.metric("Score", f"{report['score']:.1f}%")

        st.markdown("##### Tipos de Datos")
        for col, dtype in report["dtypes"].items():
            st.markdown(f"- `{col}` → `{dtype}`")

with col_right:
    if df is not None and report:
        st.subheader("🩺 AI Health Scan")

        if report["issues"]:
            with st.expander("🔴 Issues Críticos", expanded=True):
                for issue in report["issues"]:
                    st.error(issue)

        if report["warnings"]:
            with st.expander("🟡 Advertencias", expanded=True):
                for warn in report["warnings"]:
                    st.warning(warn)

        if report["suggestions"]:
            with st.expander("🔵 Sugerencias de Limpieza", expanded=True):
                for sug in report["suggestions"]:
                    st.markdown(f"- {sug}")

                if st.button("🛠️ Aplicar Fixes Sugeridos", type="primary"):
                    with st.spinner("Aplicando correcciones..."):
                        time.sleep(1)
                        fixed_df = data_validator.suggest_fixes(df)
                        st.session_state.df = fixed_df
                        new_report = data_validator.validate(fixed_df)
                        st.session_state.validator_report = new_report
                        st.success(f"Fixes aplicados. Nueva calidad: {new_report['score']:.1f}%")
                        st.rerun()

        with st.expander("Estadísticas Descriptivas", expanded=False):
            if report["numeric_cols"]:
                stats = data_validator.get_summary_stats(df)
                stats_df = pd.DataFrame(stats).T
                st.dataframe(stats_df, use_container_width=True)
            else:
                st.info("No hay columnas numéricas para estadísticas.")

        st.markdown("---")
        st.subheader("Vista Previa del Dataset")
        st.dataframe(df.head(10), use_container_width=True)

    elif not uploaded_file:
        st.info("Sube un archivo CSV o Excel para comenzar.")
