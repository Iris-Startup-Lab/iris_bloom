# Plan de Mejoras — Iris Bloom

> **Producto:** Iris Bloom — plataforma de agentes de análisis de datos.
> **Organización:** Iris Startup Lab · Área de Innovación.
> Documento de trabajo para retomar el proyecto posteriormente.
> Fecha de evaluación: 2026-07-17 · Autor de la revisión: Claude Code
>
> *Nota de marca: el producto se llamaba "Nexus AI Studio" en el prototipo; el nombre oficial es ahora **Iris Bloom**. El nombre evoca el icónico Iris dataset de ciencia de datos ("bloom" = insights que florecen).*

---

## 1. Visión objetivo

Construir un **agente** que use los MCP de **Tableau** (offline, vía `cwtwb`) y **Colab** para generar:

- **Análisis descriptivos** → dashboards / tableros (`.twb` de Tableau).
- **Análisis inferenciales / prescriptivos** → notebooks de Colab ejecutados con resultados reales.

Con la capacidad (segunda iteración) de que el usuario **inserte su diseño de tablero** (imagen o `.fig`) para condicionar el estilo/layout, aprovechando un modelo de visión local sobre **HF Spaces Zero GPU**.

---

## 2. Diagnóstico del estado actual

### 2.1 Hallazgo principal

**Hoy NO hay agente ni inferencia de IA real.** La app es un **generador determinista de plantillas** con una UI que aparenta ser "AI-powered".

- `board_generator.py` → `_suggest_visualizations()` usa **heurísticas fijas**; el prompt del usuario solo se guarda como string, nunca llega a un modelo.
- `notebook_generator.py` → celdas de **plantilla estática**; clasifica columnas por **palabras en el nombre** (`_is_num`, `_is_cat`), no por dtypes reales.
- `generate_mcp_payload()` (ambos módulos) → construye JSON-RPC que **nunca se envía**. No existe cliente MCP.
- El sidebar hace HTTP real **solo para listar modelos** de DeepSeek/Gemini. La API key nunca se usa para generar.

Conclusión: es un **prototipo de UI pulido** con andamiaje MCP simulado; el motor (agente + MCP + IA) está vacío. La visión es esencialmente **greenfield sobre esta UI**.

### 2.2 Lo que vale la pena conservar

- **Sistema de diseño** (`DESIGN.md`, tema "Synthetic Precision"): coherente y reutilizable como **tokens de tema**. ⚠️ El código de UI actual es **Streamlit** y **se reimplementará en Gradio** (ver §3); se conservan paleta/tipografía/tokens, no el layout Streamlit.
- **`cwtwb_runner.py`**: lo único que hace trabajo real; genera `.twb` válido con `TWBEditor`, incluye saneamiento del XML (dedup de `window`).
- **`data_validator.py`**: sólido (health scan, score, fixes). Base natural del contexto para el agente.
- **`data_formulator/`** (Docker + LiteLLM en HF Spaces): patrón proxy multi-modelo reutilizable.

### 2.3 Correcciones conceptuales (verificadas 2026-07-17)

1. **"MCP de Tableau" ≠ generar `.twb`.** El [MCP oficial de Tableau](https://github.com/tableau/tableau-mcp) sirve para **leer/consultar** datos publicados (VizQL Data Service), metadatos y Pulse en Tableau Cloud/Server — *no* crea workbooks. Generar el tablero como archivo lo hace `cwtwb` (offline). El comentario "Looker Studio" en `board_generator.py` es incorrecto: `cwtwb` edita `.twb` de **Tableau**.
2. **El [Colab MCP](https://github.com/googlecolab/colab-mcp) ya existe y es oficial** (lanzado marzo 2026). Expone `create_cell`, `execute_cell`, `get_cell_output`, etc. Permite **crear Y ejecutar** celdas en un notebook real → reemplaza el `render_notebook_json` estático.
3. **[Zero GPU](https://huggingface.co/docs/hub/spaces-zerogpu)** exige: plan **PRO**, **SDK Gradio exclusivamente**, decorar con `@spaces.GPU` (H200). **Solo acelera cargas que usan GPU** (modelos locales). Con APIs remotas + pandas NO aporta nada, salvo que se muevan modelos (p. ej. visión) a GPU local.

### 2.4 Bugs y deuda técnica

| Sev. | Dónde | Problema |
|---|---|---|
| Alta | Todo el flujo | No hay cliente MCP ni llamada a LLM; los payloads se descartan. |
| Alta | `board_generator.py:16` | `mcp_config` apunta a `npx @imgwho/cwtwb` como MCP npm — pero `cwtwb` es librería **Python**. Config inválida. |
| Media | `notebook_generator.py` | Clasifica columnas por nombre, no por dtypes reales del validador → falla con nombres en español/ambiguos. |
| Media | `design_parser.py:74` | Parser YAML a mano con regex (`^colors:\s*$(.*?)^\w+:`). Frágil. `PyYAML` no está en `requirements.txt`. |
| Media | `dashboard_generator.py:30`, `design_parser.py:8` | `DESIGN.md` con ruta relativa → depende del CWD; cae silenciosamente a defaults. |
| Baja | `data_center.py:67` | `file_bytes if ext in (...) else file_bytes` — ramas idénticas, código muerto. |
| Baja | `notebook_generator.py:333` | Celdas markdown con `outputs: []`, inválido en nbformat. |
| Baja | `_is_num`/`_is_date` | "year" está en ambas listas; el orden hace que siempre gane fecha. |
| — | Global | Sin tests, sin manejo de errores de LLM, sin repo git, secrets solo en sesión. |

---

## 3. Decisiones tomadas

| Tema | Decisión | Consecuencia |
|---|---|---|
| **Tableau** | Tableau Desktop / `.twb` offline | Se conserva `cwtwb` como herramienta del agente. |
| **Cómputo/IA** | **Híbrido** | Agente con APIs remotas (CPU) + modelo de visión local en GPU para ingesta de diseño. |
| **Prioridad** | Los 3 frentes son prioritarios | Se construye un núcleo compartido y luego 3 tracks en paralelo. |

### Decisión de despliegue: stack unificado en Gradio

**ZeroGPU exige SDK Gradio.** Streamlit en HF solo puede correr en (a) **CPU básico gratis** (sin GPU) o (b) **GPU dedicada de pago** (facturada por hora, ociosa o no) — nunca ZeroGPU. Para evitar esa limitación y mantener un solo stack, **toda la plataforma se construye en Gradio** y la UI Streamlit actual se reimplementa.

Dos Spaces, ambos Gradio:

1. **`iris-bloom`** (agente + Tableau + Colab): Gradio en **HF Spaces CPU (gratis)**. Usa APIs remotas; no necesita GPU.
2. **`iris-vision`** (ingesta de diseño): Gradio + `@spaces.GPU` en **Space ZeroGPU (cuenta PRO)**. Recibe imagen/`.fig`, devuelve tokens de diseño (JSON). `iris-bloom` lo llama por HTTP; la GPU solo se enciende **on-demand**.

Ventaja: un solo SDK (Gradio) simplifica el stack y deja ZeroGPU disponible de forma nativa. Costo de GPU = solo la suscripción PRO (sin GPU dedicada siempre encendida).

---

## 4. Arquitectura objetivo

```
iris-bloom  (Gradio · HF Spaces CPU gratis)
  Usuario → UI Gradio (dataset + diseño + prompt)
        → Agente (LLM con tool-use, APIs remotas + MCP)
            ├─ [descriptivo]  cwtwb → dashboard .twb (Tableau, oficial)
            │                 └ o Stitch MCP → shell HTML + agente inyecta charts (simples)
            ├─ [inferencial]  Colab MCP → notebook ejecutado + resultados
            ├─ [diseño·gen]   Stitch MCP → maqueta UI + código (usuario SIN diseño)
            └─ contexto: DataValidator + tokens de diseño
                                                   ▲ HTTP
iris-vision (Gradio + @spaces.GPU · ZeroGPU/PRO)
  .fig/imagen del usuario → modelo de visión → JSON de tokens (extracción fiel) ┘
```

---

## 5. Plan por fases

### Fase 0 — Saneamiento (bloqueante ligero, ~1 sesión)
- [ ] Añadir `PyYAML`; reemplazar parser regex de `DESIGN.md`.
- [ ] Rutas absolutas para `DESIGN.md` (independiente del CWD).
- [ ] Unificar clasificación de columnas usando dtypes reales del `DataValidator` (eliminar heurística por nombre en `notebook_generator.py`).
- [ ] `git init` + `.gitignore`; limpiar código muerto (`data_center.py:67`); corregir comentario "Looker Studio".
- [ ] **Rebranding a "Iris Bloom"**: definir identidad/logo de Iris Startup Lab y aplicar el nombre en la nueva UI Gradio (ver Fase 1). Nota: no se reetiqueta la UI Streamlit actual porque se reemplaza por Gradio.

### Fase 1 — Núcleo del agente + UI Gradio (BLOQUEANTE para los 3 tracks)
- [ ] Cliente LLM real con **tool-use** (recomendado: API de Claude; alternativa: LiteLLM multiplexando DeepSeek/Gemini como en `data_formulator/`).
- [ ] **Cliente MCP funcional** (hoy inexistente): lanza servidores MCP (**Colab MCP** + **Stitch MCP**, ambos `npx`/`uvx`) y despacha `tools/call` de verdad. Reemplaza los `generate_mcp_payload` que se descartan.
- [ ] Bucle de agente: recibe `{schema + stats del validador + tokens de diseño + prompt}` y decide qué herramientas invocar.
- [ ] **Reimplementar la UI en Gradio** (reemplaza `streamlit_app/`): vistas Data Center / Tableros / Notebook Lab como `gr.Blocks`, aplicando los tokens de `DESIGN.md` como tema. Reutiliza `data_validator.py` y `cwtwb_runner.py` (no dependen de Streamlit).

### Track A — Tableau descriptivo (~60% ya hecho)
- [ ] Envolver `cwtwb` como **tool del agente** (crear worksheet, configurar chart, dashboard).
- [ ] El LLM decide el spec de visualizaciones (sustituye `_suggest_visualizations`); `cwtwb_runner` ejecuta.

**Dos niveles de salida descriptiva:**
- **Tableros simples** → **HTML autocontenido**. El shell/maqueta lo puede generar **Stitch MCP** (`build_site`/`get_screen_code`) y el agente inyecta los charts con datos (Plotly/Altair). Sin depender de Tableau; compartible por link/Artifact, ideal para vistas ligeras o prototipos.
- **Tablero "oficial"** → **Tableau (`.twb` vía `cwtwb`) es la herramienta recomendada/oficial** del proyecto. La UI debe **sugerir Tableau por defecto** y ofrecer HTML como alternativa ligera, no al revés.

### Track B — Colab inferencial/prescriptivo
- [ ] Conectar [Colab MCP](https://github.com/googlecolab/colab-mcp) (`uvx googlecolab/colab-mcp`) al cliente MCP de Fase 1.
- [ ] El agente **crea y ejecuta** celdas y lee `get_cell_output` → resultados reales.
- [ ] Eliminar `render_notebook_json` (JSON estático sin ejecución).

**Nota sobre "Visualization Mode" (verificado 2026-07-17):**
- El **Visualization Mode** y el **Fullscreen Output Sharing** de Colab son features **exclusivas de UI**, acopladas al asistente **Gemini** (dropdown). **No** hay API, metadata de celda ni magic command para activarlos → **NO son invocables vía el Colab MCP ni el CLI**. El feature request [colabtools #991](https://github.com/googlecolab/colabtools/issues/991) confirma que el fullscreen aún no es programable.
- **No dependemos de Visualization Mode: el agente lo reemplaza.** Su valor ("lenguaje natural → generar y ejecutar código de gráfico") lo cubre nuestro propio agente escribiendo el código y ejecutándolo con `execute_cell` + `get_cell_output`. Así evitamos acoplarnos a una feature de UI no automatizable.
- Lo único no replicable vía MCP es la **URL de output a pantalla completa para compartir**. Alternativa: renderizar el gráfico a **HTML autocontenido** (Plotly/Altair) y publicarlo como **Artifact / Space propio**, en vez de depender del fullscreen de Colab.

### Track C — Capa de diseño (dos vías complementarias)
- [ ] Definir **contrato JSON de tokens de diseño** (paleta, layout, tipos de gráfico) — común a ambas vías.
- [ ] **Vía A — Generar (Stitch MCP):** conectar al cliente de Fase 1. Para usuarios **SIN** diseño: prompt/sketch → maqueta UI + código; parsear su HTML a tokens. ⚠️ Requiere Google Cloud OAuth por usuario y tiene cuota (~350 gen/mes); servicio externo (Google Labs).
- [ ] **Vía B — Extraer (visión local, ZeroGPU):** Space Gradio + `@spaces.GPU` con modelo de visión open-source. Para el `.fig`/imagen que el usuario **YA** tiene → extracción **fiel** de tokens. Entrada **imagen** (MVP); `.fig` en 2ª iteración (requiere API/plugin de Figma).
- [ ] Integrar el JSON de tokens (de cualquier vía) como contexto del agente.

### Fase final — Despliegue
- [ ] `iris-bloom` → Space **Gradio, CPU gratis**.
- [ ] `iris-vision` → Space **Gradio + ZeroGPU (cuenta PRO)**.
- [ ] Contrato HTTP entre ambos + manejo de errores/timeouts.

---

## 6. Próximo paso recomendado

**Empezar por Fase 0 + Fase 1** (núcleo agente + cliente MCP), porque sin el cliente MCP y el bucle de agente los tres tracks no tienen dónde conectarse.

Alternativa: definir primero el **contrato JSON de tokens de diseño** (Track C) para arrancar los tres tracks en paralelo.

---

## 7. Referencias verificadas

- Tableau MCP oficial: https://github.com/tableau/tableau-mcp
- Colab MCP oficial: https://github.com/googlecolab/colab-mcp
- Google Stitch: https://stitch.withgoogle.com · MCP: https://github.com/davideast/stitch-mcp · docs https://stitch.withgoogle.com/docs/mcp/setup
- HF Spaces Zero GPU: https://huggingface.co/docs/hub/spaces-zerogpu
- cwtwb (editor `.twb`): https://github.com/imgwho/cwtwb
- Microsoft Data Formulator: https://github.com/microsoft/data-formulator

---

## 8. Inventario de archivos actuales (referencia)

> ⚠️ `streamlit_app/` se **migra a Gradio** (ver §3 y Fase 1). Se reutiliza la lógica de `data_validator.py`, `cwtwb_runner.py` y los tokens de `DESIGN.md`; el layout Streamlit se descarta.

```
DESIGN.md                              Sistema de diseño (frontmatter YAML + guía)
streamlit_app/
  streamlit_app.py                     Entrada; sidebar de modelos (solo lista, no infiere)
  modules/
    design_parser.py                   Parser regex de DESIGN.md (frágil)
    data_validator.py                  Validación de datasets (SÓLIDO, conservar)
    board_generator.py                 Heurísticas de viz + payload MCP no usado
    notebook_generator.py              Plantillas estáticas + payload MCP no usado
    cwtwb_runner.py                    Genera .twb real con TWBEditor (conservar)
  pages/
    data_center.py                     Upload + health scan
    dashboard_generator.py             UI generación de tableros
    notebook_lab.py                    UI generación de notebooks
data_formulator/                       Experimento Docker + LiteLLM en HF Spaces
output/dashboard.twb                   Salida de ejemplo
*/code.html + screen.png               Mockups de diseño (Figma exports)
```
