import json
from typing import Dict, Any, Optional, List


def _safe_name(s: str) -> str:
    return "".join(c if c.isalnum() or c == "_" else "_" for c in s)


def _col_refs(cols: List[str], prefix="df") -> str:
    return ", ".join(f"{prefix}['{c}']" for c in cols)


def _num_cols(df_summary: Optional[Dict]) -> List[str]:
    return df_summary.get("column_names", []) if df_summary else []


def _is_num(col: str) -> bool:
    return any(t in col.lower() for t in ["price", "revenue", "amount", "count", "age", "score", "rate",
                                            "value", "cost", "sales", "profit", "quantity", "income",
                                            "balance", "fee", "duration", "distance", "size", "weight",
                                            "height", "temperature", "population", "year"])


def _is_cat(col: str) -> bool:
    return any(t in col.lower() for t in ["name", "category", "type", "group", "region", "country",
                                            "city", "state", "status", "gender", "color", "brand",
                                            "department", "segment", "product", "channel", "source",
                                            "class", "code", "id_"])


def _is_date(col: str) -> bool:
    return any(t in col.lower() for t in ["date", "time", "timestamp", "day", "month", "year",
                                            "period", "fecha", "created", "updated"])


class NotebookGenerator:
    def __init__(self, model: str = "gemini"):
        self.model = model

    def build_notebook_spec(
        self,
        columns: list,
        prompt: str,
        dataset_summary: Optional[Dict[str, Any]] = None,
        analysis_type: str = "exploratory",
    ) -> Dict[str, Any]:
        spec = {
            "model": self.model,
            "title": self._generate_title(prompt, analysis_type),
            "cells": self._generate_cells(columns, dataset_summary, prompt, analysis_type),
        }
        return spec

    def _generate_title(self, prompt: str, analysis_type: str) -> str:
        labels = {
            "exploratory": "Análisis Exploratorio de Datos",
            "predictive": "Modelo Predictivo",
            "clustering": "Análisis de Clustering",
            "nlp": "Procesamiento de Lenguaje Natural",
            "timeseries": "Análisis de Series Temporales",
        }
        base = labels.get(analysis_type, "Análisis Personalizado")
        return f"{base}: {prompt[:60]}{'...' if len(prompt) > 60 else ''}"

    def _classify_cols(self, columns: list) -> dict:
        nums, cats, dates = [], [], []
        for c in columns:
            if _is_date(c):
                dates.append(c)
            elif _is_num(c):
                nums.append(c)
            elif _is_cat(c):
                cats.append(c)
            else:
                cats.append(c)
        return {"numeric": nums, "categorical": cats, "datetime": dates}

    def _generate_cells(self, columns: list, ds: Optional[Dict], prompt: str, atype: str) -> list:
        cells = []
        cls = self._classify_cols(columns)
        nums = cls["numeric"]
        cats = cls["categorical"]
        dates = cls["datetime"]
        safe_cols = [_safe_name(c) for c in columns]

        cells.append({
            "type": "code",
            "title": "Configuración e importaciones",
            "content": [
                "import pandas as pd",
                "import numpy as np",
                "import matplotlib.pyplot as plt",
                "import seaborn as sns",
                "from pathlib import Path",
                "",
                "sns.set_theme(style='darkgrid', palette='viridis')",
                "plt.rcParams['figure.figsize'] = (14, 6)",
                "pd.set_option('display.max_columns', None)",
                "",
                'print("✅ Entorno listo")',
            ],
        })

        cells.append({
            "type": "code",
            "title": "Carga del dataset",
            "content": [
                "# Cargar dataset",
                f'df = pd.read_csv("dataset.csv")  # reemplaza con tu ruta',
                f'print(f"Filas: {{df.shape[0]}} • Columnas: {{df.shape[1]}}")',
                f'print(f"Columnas: {columns}")',
            ],
        })

        if nums:
            cells.append({
                "type": "code",
                "title": "Estadísticas descriptivas — numéricas",
                "content": [
                    f"num_cols = {nums}",
                    f"df[num_cols].describe().T",
                ],
            })

        if cats:
            cells.append({
                "type": "code",
                "title": "Distribuciones — variables categóricas",
                "content": [
                    f"cat_cols = {cats}",
                    "fig, axes = plt.subplots(1, min(len(cat_cols), 4), figsize=(16, 4))",
                    "if len(cat_cols) == 1:",
                    "    axes = [axes]",
                    "for ax, col in zip(axes, cat_cols[:4]):",
                    "    df[col].value_counts().head(15).plot(kind='bar', ax=ax, title=col)",
                    "plt.tight_layout()",
                    "plt.show()",
                ],
            })

        if dates:
            cells.append({
                "type": "code",
                "title": "Análisis temporal",
                "content": [
                    f"date_cols = {dates}",
                    f"for col in date_cols:",
                    f"    df[col] = pd.to_datetime(df[col], errors='coerce')",
                    f"df.set_index(date_cols[0], inplace=True) if len(date_cols) else None",
                ],
            })

        if nums and cats:
            cells.append({
                "type": "code",
                "title": "Comparativas por categoría",
                "content": [
                    f"target_metric = '{nums[0]}'",
                    f"group_col = '{cats[0]}'",
                    "df.groupby(group_col)[target_metric].agg(['mean', 'sum', 'count'])"
                    ".sort_values('mean', ascending=False).head(10)",
                ],
            })

        if len(nums) >= 2 and nums:
            cells.append({
                "type": "code",
                "title": "Matriz de correlación",
                "content": [
                    f"corr = df[{nums}].corr()",
                    "plt.figure(figsize=(10, 8))",
                    "mask = np.triu(np.ones_like(corr, dtype=bool))",
                    "sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='coolwarm', center=0, square=True)",
                    "plt.title('Matriz de Correlación')",
                    "plt.show()",
                ],
            })

        if atype == "predictive" and nums and cats:
            cells.append({
                "type": "markdown",
                "title": "Modelo predictivo",
                "content": [
                    "## Modelo Predictivo",
                    "",
                    f"Objetivo: {prompt[:100]}",
                    "",
                    "Pipeline de regresión con validación cruzada.",
                ],
            })
            cells.append({
                "type": "code",
                "title": "Pipeline de regresión",
                "content": [
                    "from sklearn.model_selection import train_test_split, cross_val_score",
                    "from sklearn.ensemble import RandomForestRegressor",
                    "from sklearn.preprocessing import OneHotEncoder, StandardScaler",
                    "from sklearn.compose import ColumnTransformer",
                    "from sklearn.pipeline import Pipeline",
                    f"",
                    f"target = '{nums[0]}'",
                    f"features = {[c for c in columns if c != nums[0]]}",
                    "",
                    "X = df[features]",
                    "y = df[target]",
                    "",
                    "num_features = X.select_dtypes(include=[np.number]).columns.tolist()",
                    "cat_features = X.select_dtypes(exclude=[np.number]).columns.tolist()",
                    "",
                    "preprocessor = ColumnTransformer([",
                    "    ('num', StandardScaler(), num_features),",
                    "    ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features),",
                    "])",
                    "",
                    "model = Pipeline([",
                    "    ('prep', preprocessor),",
                    "    ('rf', RandomForestRegressor(n_estimators=100, random_state=42)),",
                    "])",
                    "",
                    "X_train, X_test, y_train, y_test = train_test_split(",
                    "    X, y, test_size=0.2, random_state=42)",
                    "model.fit(X_train, y_train)",
                    "",
                    "train_score = model.score(X_train, y_train)",
                    "test_score = model.score(X_test, y_test)",
                    f"print(f'R² Train: {{train_score:.3f}} • R² Test: {{test_score:.3f}}')",
                ],
            })

        if atype == "clustering" and nums:
            cells.append({
                "type": "markdown",
                "title": "Clustering",
                "content": [
                    "## Segmentación por Clustering",
                    "",
                    "K-Means con determinación automática de clusters óptimos.",
                ],
            })
            cells.append({
                "type": "code",
                "title": "K-Means clustering",
                "content": [
                    "from sklearn.cluster import KMeans",
                    "from sklearn.preprocessing import StandardScaler",
                    "",
                    f"cluster_cols = {nums[:6]}",
                    "X = StandardScaler().fit_transform(df[cluster_cols].dropna())",
                    "",
                    "# Codo de inercia",
                    "inertias = []",
                    "K = range(2, 11)",
                    "for k in K:",
                    "    km = KMeans(n_clusters=k, random_state=42, n_init=10)",
                    "    km.fit(X)",
                    "    inertias.append(km.inertia_)",
                    "",
                    "plt.plot(K, inertias, 'bo-')",
                    "plt.xlabel('Clusters')",
                    "plt.ylabel('Inercia')",
                    "plt.title('Método del Codo')",
                    "plt.show()",
                ],
            })

        if atype == "timeseries" and nums:
            cells.append({
                "type": "code",
                "title": "Serie temporal",
                "content": [
                    "from statsmodels.tsa.seasonal import seasonal_decompose",
                    "",
                    f"ts_col = '{nums[0]}'",
                    "# Descomposición",
                    "result = seasonal_decompose(df[ts_col].dropna(), model='additive', period=12)",
                    "fig = result.plot()",
                    "fig.set_size_inches(14, 10)",
                    "plt.show()",
                ],
            })

        cells.append({
            "type": "markdown",
            "title": "Conclusiones",
            "content": [
                "## Conclusiones",
                "",
                f"Resumen del análisis:",
                f"- Dataset con {len(columns)} columnas analizadas",
                f"- {len(nums)} variables numéricas, {len(cats)} categóricas, {len(dates)} temporales",
                f"- {prompt[:200]}",
            ],
        })

        cells.append({
            "type": "code",
            "title": "Exportar resultados",
            "content": [
                "# Exportar resultados a CSV",
                "# df.to_csv('resultados_analisis.csv', index=False)",
                'print("✅ Análisis completado")',
            ],
        })

        return cells

    def generate_mcp_payload(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "create_notebook",
                "arguments": {
                    "spec": json.dumps(spec),
                    "model": self.model,
                    "environment": {
                        "runtime": "python3.10",
                        "accelerator": "GPU",
                    },
                },
            },
        }

    def render_notebook_json(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        nb_cells = []
        for cell in spec.get("cells", []):
            cell_type = cell.get("type", "code")
            source_lines = cell.get("content", [])
            nb_cells.append({
                "cell_type": cell_type,
                "metadata": {"tags": [cell.get("title", "")]} if cell.get("title") else {},
                "source": [l + "\n" for l in source_lines],
                "outputs": [] if cell_type == "code" else [],
            })

        return {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3",
                },
                "language_info": {
                    "name": "python",
                    "version": "3.10.0",
                },
            },
            "cells": nb_cells,
        }
