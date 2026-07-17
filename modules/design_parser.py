import re
from pathlib import Path


class DesignParser:
    """Parsea el archivo DESIGN.md y extrae configuración de estilo y layout."""

    def __init__(self, design_path: str = "DESIGN.md"):
        self.design_path = Path(design_path)
        self.config = self._default_config()

    def _default_config(self):
        return {
            "brand": "Synthetic Precision",
            "colors": {
                "background": "#0b1326",
                "surface": "#1E293B",
                "primary": "#3B82F6",
                "secondary": "#8B5CF6",
                "tertiary": "#4edea3",
                "error": "#EF4444",
                "warning": "#F59E0B",
                "success": "#10B981",
                "on_surface": "#dae2fd",
                "on_surface_variant": "#c2c6d6",
                "outline": "#334155",
                "outline_variant": "#424754",
            },
            "typography": {
                "headings": "Inter",
                "mono": "JetBrains Mono",
            },
            "border_radius": "0.25rem",
            "layout": {
                "columns": 12,
                "gutter": "20px",
            },
        }

    def parse(self):
        """Lee DESIGN.md y extrae configuración. Retorna config actualizada."""
        if not self.design_path.exists():
            return self.config

        content = self.design_path.read_text(encoding="utf-8")

        # Extraer bloques YAML frontmatter
        yaml_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if yaml_match:
            yaml_text = yaml_match.group(1)
            self._parse_yaml_block(yaml_text)

        # Extraer colores del texto markdown
        self._parse_markdown_colors(content)

        return self.config

    def _parse_yaml_block(self, yaml_text: str):
        for line in yaml_text.strip().split("\n"):
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip("'").strip('"')

            if key == "name":
                self.config["brand"] = value
            elif key == "colors":
                continue  # se maneja en _parse_yaml_colors
            elif not key.startswith(" ") and key not in ("colors", "typography", "rounded", "spacing"):
                self.config[key] = value

        # Parsear colores del YAML
        colors_match = re.search(
            r"^colors:\s*$(.*?)^\w+:", yaml_text, re.MULTILINE | re.DOTALL
        )
        if colors_match:
            colors_text = colors_match.group(1)
            for line in colors_text.strip().split("\n"):
                line = line.strip()
                if ":" not in line:
                    continue
                ck, _, cv = line.partition(":")
                ck = ck.strip()
                cv = cv.strip().strip("'").strip('"')
                if cv.startswith("#"):
                    config_key = ck.replace("-", "_")
                    if config_key in self.config["colors"]:
                        self.config["colors"][config_key] = cv

    def _parse_markdown_colors(self, content: str):
        color_patterns = [
            (r"Primary\s*\([^)]+\):\s*`([^`]+)`", "primary"),
            (r"Secondary\s*\([^)]+\):\s*`([^`]+)`", "secondary"),
            (r"Success.*?:\s*`([^`]+)`", "success"),
            (r"Warning.*?:\s*`([^`]+)`", "warning"),
            (r"Error.*?:\s*`([^`]+)`", "error"),
        ]
        for pattern, key in color_patterns:
            match = re.search(pattern, content)
            if match:
                self.config["colors"][key] = match.group(1)

    def get_primary_color(self):
        return self.config["colors"]["primary"]

    def get_secondary_color(self):
        return self.config["colors"]["secondary"]

    def get_tertiary_color(self):
        return self.config["colors"]["tertiary"]

    def get_background_color(self):
        return self.config["colors"]["background"]

    def get_css(self) -> str:
        return f"""
        <style>
        .stApp {{
            background-color: {self.config['colors']['background']};
        }}
        .stTabs [data-baseweb="tab"] {{
            color: {self.config['colors']['on_surface']} !important;
        }}
        .stTabs [aria-selected="true"] {{
            border-bottom-color: {self.config['colors']['primary']} !important;
        }}
        h1, h2, h3 {{
            font-family: '{self.config['typography']['headings']}', sans-serif;
        }}
        code, pre {{
            font-family: '{self.config['typography']['mono']}', monospace;
        }}
        </style>
        """
