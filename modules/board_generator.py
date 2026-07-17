import json
from typing import Dict, Any, Optional
from pathlib import Path


class BoardGenerator:
    """Integración con MCP cwtwb para generar tableros en Looker Studio.

    https://github.com/imgwho/cwtwb
    """

    def __init__(self, model: str = "deepseek"):
        self.model = model
        self.mcp_config = self._default_mcp_config()

    def _default_mcp_config(self) -> Dict[str, Any]:
        return {
            "mcp_servers": {
                "cwtwb": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@imgwho/cwtwb"
                    ],
                    "env": {
                        "LOOKER_API_KEY": "",
                        "LOOKER_EMAIL": "",
                    }
                }
            }
        }

    def set_credentials(self, api_key: str, email: str = ""):
        self.mcp_config["mcp_servers"]["cwtwb"]["env"]["LOOKER_API_KEY"] = api_key
        if email:
            self.mcp_config["mcp_servers"]["cwtwb"]["env"]["LOOKER_EMAIL"] = email

    def build_spec(
        self,
        columns: list,
        prompt: str,
        design_config: Optional[Dict[str, Any]] = None,
        summary_stats: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Construye el spec JSON para cwtwb según datos + DESIGN.md + prompt."""
        spec = {
            "model": self.model,
            "layout": {
                "type": "bento_grid",
                "columns": 12,
                "gutter": 20,
            },
            "data_schema": {
                "columns": columns,
            },
            "visualizations": [],
            "styling": {
                "theme": "dark",
            },
        }

        if design_config:
            colors = design_config.get("colors", {})
            spec["styling"]["colors"] = colors

            typography = design_config.get("typography", {})
            spec["styling"]["typography"] = typography

            layout = design_config.get("layout", {})
            spec["layout"]["columns"] = layout.get("columns", 12)
            spec["layout"]["gutter"] = layout.get("gutter", "20px")

        viz_types = self._suggest_visualizations(columns, summary_stats, prompt)

        spec["visualizations"] = viz_types
        spec["prompt"] = prompt

        return spec

    def _suggest_visualizations(
        self,
        columns: list,
        summary_stats: Optional[Dict[str, Any]] = None,
        prompt: str = "",
    ) -> list:
        """Sugiere visualizaciones basadas en tipos de columna y prompt."""
        suggestions = []
        numeric = [c for c in columns if summary_stats and c in summary_stats] if summary_stats else []

        # Time series si hay fecha
        if any("date" in c.lower() or "time" in c.lower() or "timestamp" in c.lower() for c in columns):
            suggestions.append({
                "type": "timeseries",
                "title": "Tendencia Temporal",
                "config": {"show_legend": True, "smoothing": True},
            })

        # KPI cards para numéricas
        for col in numeric[:4]:
            suggestions.append({
                "type": "kpi_card",
                "title": col,
                "metric": col,
                "config": {"comparison": "period_over_period"},
            })

        # Tabla si hay pocas columnas
        if len(columns) <= 8:
            suggestions.append({
                "type": "data_table",
                "title": "Vista Detallada",
                "config": {"page_size": 10, "sortable": True},
            })

        if numeric:
            suggestions.append({
                "type": "bar_chart",
                "title": "Comparativa",
                "config": {"orientation": "vertical"},
            })

        return suggestions

    def generate_mcp_payload(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Genera el payload para enviar al MCP cwtwb."""
        return {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "create_dashboard",
                "arguments": {
                    "spec": json.dumps(spec),
                    "model": self.model,
                    "options": {
                        "use_design_md": True,
                        "auto_layout": True,
                    },
                },
            },
        }

    def get_mcp_config_file(self) -> str:
        """Genera el contenido para el archivo de configuración MCP."""
        return json.dumps(self.mcp_config, indent=2)
