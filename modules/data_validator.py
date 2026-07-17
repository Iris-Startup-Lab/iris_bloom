import pandas as pd
import numpy as np
from io import StringIO, BytesIO
from typing import Dict, Any, Optional


class DataValidator:
    """Valida la calidad de datasets CSV/Excel para generación de tableros."""

    REQUIRED_MIN_ROWS = 5
    MAX_MISSING_RATIO = 0.5
    MAX_DUPLICATE_RATIO = 0.3

    def __init__(self):
        self.report = {}

    def load_file(self, file_bytes: bytes, filename: str) -> Optional[pd.DataFrame]:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        try:
            if ext == "csv":
                return pd.read_csv(StringIO(file_bytes.decode("utf-8", errors="replace")))
            elif ext in ("xls", "xlsx"):
                return pd.read_excel(BytesIO(file_bytes))
            else:
                return None
        except Exception:
            return None

    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        report = {
            "passed": True,
            "score": 0.0,
            "rows": len(df),
            "columns": len(df.columns),
            "issues": [],
            "warnings": [],
            "suggestions": [],
            "dtypes": {},
            "missing_summary": {},
            "numeric_cols": [],
            "categorical_cols": [],
            "datetime_cols": [],
        }

        if df.empty:
            report["passed"] = False
            report["issues"].append("El dataset está vacío")
            report["score"] = 0.0
            self.report = report
            return report

        # Tipos de datos
        for col in df.columns:
            dtype = str(df[col].dtype)
            report["dtypes"][col] = dtype
            if "int" in dtype or "float" in dtype:
                report["numeric_cols"].append(col)
            elif "datetime" in dtype:
                report["datetime_cols"].append(col)
            else:
                report["categorical_cols"].append(col)

        # Missing values
        missing = df.isnull().sum()
        total_cells = len(df) * len(df.columns)
        total_missing = missing.sum()
        missing_ratio = total_missing / total_cells if total_cells > 0 else 0

        report["missing_summary"] = {
            col: int(missing[col])
            for col in df.columns
            if missing[col] > 0
        }

        if missing_ratio > self.MAX_MISSING_RATIO:
            report["passed"] = False
            report["issues"].append(
                f"Demasiados valores faltantes: {missing_ratio:.1%} del dataset"
            )
        elif missing_ratio > 0:
            cols_with_missing = [c for c in df.columns if missing[c] > 0]
            for col in cols_with_missing[:3]:
                pct = missing[col] / len(df)
                if df[col].dtype in ("int64", "float64"):
                    median_val = df[col].median()
                    report["suggestions"].append(
                        f"Columna '{col}': {missing[col]} ausentes ({pct:.1%}). Rellenar con mediana ({median_val:.2f})."
                    )
                else:
                    mode_val = df[col].mode().iloc[0] if not df[col].mode().empty else "N/A"
                    report["suggestions"].append(
                        f"Columna '{col}': {missing[col]} ausentes ({pct:.1%}). Rellenar con moda ('{mode_val}')."
                    )

        # Duplicados
        dups = df.duplicated().sum()
        dup_ratio = dups / len(df) if len(df) > 0 else 0
        if dup_ratio > self.MAX_DUPLICATE_RATIO:
            report["issues"].append(
                f"Alta tasa de duplicados: {dup_ratio:.1%} ({dups} filas)"
            )
        elif dups > 0:
            report["warnings"].append(f"{dups} filas duplicadas encontradas ({dup_ratio:.1%})")

        # Cardinalidad de categóricas
        for col in report["categorical_cols"]:
            unique_ratio = df[col].nunique() / len(df) if len(df) > 0 else 0
            if unique_ratio > 0.95 and len(df) > 10:
                report["warnings"].append(
                    f"Columna '{col}' tiene alta cardinalidad ({df[col].nunique()} valores únicos). "
                    "Podría ser un ID."
                )

        # Score
        penalties = 0.0
        penalties += missing_ratio * 30
        penalties += dup_ratio * 20
        penalties += len(report["issues"]) * 10

        report["score"] = max(0.0, min(100.0, 100.0 - penalties))

        if len(df) < self.REQUIRED_MIN_ROWS:
            report["issues"].append(
                f"Muy pocas filas ({len(df)}). Mínimo recomendado: {self.REQUIRED_MIN_ROWS}"
            )
            report["passed"] = False

        if report["score"] >= 70:
            report["passed"] = True

        self.report = report
        return report

    def suggest_fixes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica fixes sugeridos automáticamente."""
        df = df.copy()
        for col in df.columns:
            if df[col].isnull().sum() > 0:
                if df[col].dtype in ("int64", "float64"):
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else "")
        return df

    def get_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        stats = {}
        for col in df.select_dtypes(include=[np.number]).columns:
            stats[col] = {
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std()),
            }
        return stats
