import os
import tempfile
import traceback
from typing import Optional

try:
    from cwtwb.twb_editor import TWBEditor
    HAS_CWTWB = True
except ImportError:
    HAS_CWTWB = False


_MARK_MAP = {
    "kpi_card": "Automatic",
    "bar_chart": "Bar",
    "timeseries": "Line",
    "line_chart": "Line",
    "pie_chart": "Pie",
    "data_table": "Automatic",
    "heatmap": "Square",
    "scatter": "Circle",
}


def _classify(columns: list, dtypes: dict) -> tuple:
    nums, cats, dates = [], [], []
    for c in columns:
        dt = str(dtypes.get(c, "")).lower()
        if any(t in dt for t in ["int", "float"]):
            nums.append(c)
        elif any(t in dt for t in ["datetime"]):
            dates.append(c)
        else:
            cats.append(c)
    if not nums:
        nums = columns[:1]
    return nums, cats, dates


def _ext(path: str) -> str:
    return os.path.splitext(path)[1].lstrip(".").lower()


class CwtwbRunner:
    def __init__(self):
        pass

    def generate_twb(
        self,
        spec: dict,
        output_path: str = "output/dashboard.twb",
        dataset_path: str = "",
    ) -> dict:
        if not HAS_CWTWB:
            return {"success": False, "error": "cwtwb no instalado. pip install cwtwb", "steps": []}

        steps = []
        try:
            # 1. Crear workbook desde template default
            editor = TWBEditor("")
            steps.append("create_workbook OK")
            steps.append(editor.list_fields()[:200])

            columns = spec.get("data_schema", {}).get("columns", [])
            dtypes = spec.get("data_schema", {}).get("dtypes", {})

            # 2. Conectar dataset
            if dataset_path and os.path.exists(dataset_path):
                ext = _ext(dataset_path)
                if ext in ("csv",):
                    editor.set_csv_connection(filepath=dataset_path)
                    steps.append(f"set_csv_connection({os.path.basename(dataset_path)}) OK")
                elif ext in ("xls", "xlsx"):
                    editor.set_excel_connection(filepath=dataset_path)
                    steps.append(f"set_excel_connection({os.path.basename(dataset_path)}) OK")
                else:
                    steps.append(f"extensión .{ext} no soportada para conexión")
            else:
                steps.append("Sin dataset local — se mantiene la fuente default")

            nums, cats, dates = _classify(columns, dtypes)

            # 3. Worksheets + charts
            vizzes = spec.get("visualizations", [])
            existing = set(editor.list_worksheets())
            sheet_names = []
            for i, viz in enumerate(vizzes):
                vtype = viz.get("type", "bar_chart")
                base = viz.get("title", "").strip() or f"Viz_{i+1}"
                # asegurar nombre único
                name = base
                suffix = 1
                while name in existing:
                    name = f"{base}_{suffix}"
                    suffix += 1
                existing.add(name)
                mark = _MARK_MAP.get(vtype, "Automatic")
                sheet_names.append(name)

                editor.add_worksheet(name)
                steps.append(f"add_worksheet({name}) OK")

                chart_args = {"worksheet_name": name, "mark_type": mark}
                if nums or cats:
                    if nums:
                        chart_args["rows"] = [nums[0]]
                    if cats:
                        chart_args["columns"] = [cats[0]]
                    elif len(nums) > 1:
                        chart_args["columns"] = [nums[1]]

                try:
                    editor.configure_chart(**chart_args)
                    steps.append(f"configure_chart({name}, {mark}) OK")
                except Exception as e:
                    steps.append(f"configure_chart({name}): {e}")

            # 4. Dashboard
            if sheet_names:
                try:
                    editor.add_dashboard(
                        dashboard_name=(spec.get("prompt", "Dashboard") or "Dashboard")[:60],
                        worksheet_names=sheet_names,
                        width=1200,
                        height=800,
                    )
                    steps.append("add_dashboard OK")
                except Exception as e:
                    steps.append(f"add_dashboard: {e}")

            # 5. Guardar a temp, sanitizar XML, y copiar a salida
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            tmp_final = os.path.join(tempfile.mkdtemp(prefix="cwtwb_final_"), "tmp.twb")
            try:
                editor.save(tmp_final, validate=False)
                steps.append("save (validate=False) OK")
            except TypeError:
                editor.save(tmp_final)
                steps.append("save OK")

            # Sanitizar: si hay ventanas duplicadas, renombrar las repetidas
            import lxml.etree as ET
            tree = ET.parse(tmp_final)
            root = tree.getroot()
            counts = {}
            windows = []
            for el in root.iter():
                if not isinstance(el.tag, str):
                    continue
                tag = el.tag.split("}")[-1]
                if tag == "window" and el.get("name"):
                    name = el.get("name")
                    counts[name] = counts.get(name, 0) + 1
                    windows.append(el)

            if any(v > 1 for v in counts.values()):
                seen = {}
                for el in windows:
                    name = el.get("name")
                    seen[name] = seen.get(name, 0) + 1
                    if seen[name] > 1:
                        new_name = f"{name}_{seen[name]}"
                        el.set("name", new_name)
                        steps.append(f"dedup window: '{name}' → '{new_name}'")
                tree.write(output_path, encoding="utf-8", xml_declaration=True)
                steps.append("dedup applied")
            else:
                # sin duplicados, copiar directamente
                import shutil
                shutil.copy2(tmp_final, output_path)
                steps.append("no duplicates found")

            steps.append(f"sanitized → {output_path}")

            success = os.path.exists(output_path)
            if success:
                steps.append(f"✅ .twb generado: {output_path}")
            else:
                steps.append("❌ No se encontró el archivo después de save")

            return {"success": success, "output_path": output_path, "steps": steps, "error": None}

        except Exception as e:
            tb = traceback.format_exc()
            steps.append(f"❌ Error: {e}")
            return {"success": False, "output_path": output_path, "steps": steps, "error": f"{e}\n{tb}"}

    @staticmethod
    def check_available() -> tuple[bool, str]:
        if HAS_CWTWB:
            return True, "cwtwb (Python API)"
        try:
            import cwtwb  # noqa
            return True, "cwtwb"
        except ImportError:
            pass
        return False, "pip install cwtwb"
