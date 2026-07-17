# Design System — Catálogo de Agentes de IA (Iris StartUp Lab)

Documento de referencia para migrar el diseño visual e interacciones de `Catalogo_Agentes_IA_Iris_1.html` a otro sitio/stack. No incluye el contenido de negocio (los 31 prompts/agentes), solo el **sistema de diseño y comportamiento de UI**.

---

## 1. Fundamentos

### 1.1 Tipografía
- **Fuente de display / títulos:** `Sora` (weights 400, 600, 700, 800) — usada en `h1, h2, h3, .font-display`, números de stats, badges, nombres de nivel.
- **Fuente de cuerpo:** `Inter` (weights 400, 500, 600, 700) — resto de la UI.
- Importadas vía Google Fonts:
  ```html
  <link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  ```
- Tamaño base: `font-size: 16px` en `:root`. `line-height: 1.55` en body.
- Escalas usadas: `.66rem, .68rem, .7rem, .72rem, .74rem, .76rem, .78rem, .8rem, .82rem, .83rem, .85rem, .86rem, .88rem, .9rem, .92rem, .95rem, 1rem, 1.15rem, 1.25rem, 1.3rem`, y responsivas con `clamp()` para H1 (`clamp(1.5rem,3.2vw,2.35rem)`).

### 1.2 Paleta de color (variables CSS)
```css
:root{
  /* Morados (marca / fondo oscuro) */
  --purple-900:#241B33;
  --purple-800:#2A2433;
  --purple-700:#3D2766;
  --purple-600:#5A3A8C;
  --purple-500:#7A4E96;
  --purple-200:#D9CCEF;
  --purple-100:#EDE6F7;
  --purple-050:#F7F3FC;

  /* Dorado (acento) */
  --gold-600:#B8862F;
  --gold-500:#D4A73E;
  --gold-400:#E8B93E;

  /* Texto / neutros */
  --ink:#2A2433;
  --ink-soft:#5C5468;
  --line:#E4DCEF;
  --white:#FFFFFF;

  /* Escala de riesgo (semáforo 1–5) */
  --risk1:#3E8E5A; /* bajo */
  --risk2:#7FA84C;
  --risk3:#C99A2E;
  --risk4:#C97133;
  --risk5:#B84A3D; /* alto */

  --radius:14px;
  --shadow-sm:0 1px 3px rgba(42,36,51,.08);
  --shadow-md:0 6px 20px rgba(61,39,102,.12);
  --shadow-lg:0 16px 44px rgba(36,27,51,.22);
}
```

**Uso semántico:**
| Rol | Variable |
|---|---|
| Fondo general de página | `--purple-050` |
| Fondo header/footer (oscuro, marca) | gradiente `--purple-900 → --purple-700 → #4A2F7A` |
| Texto principal | `--ink` |
| Texto secundario/soft | `--ink-soft` |
| Bordes/divisores | `--line` |
| Acento dorado (CTAs destacados, "top", nivel 5) | `--gold-400/500/600` |
| Botones activos / seleccionados | `--purple-700` o `--purple-600` |

### 1.3 Radios, sombras, espaciado
- Radio estándar de tarjetas/paneles: `14px` (`--radius`); pills/chips/botones: `999px` (full pill).
- 3 niveles de sombra (`sm`, `md`, `lg`) reutilizados en cards, paneles, modal.
- Padding lateral responsivo global: `clamp(20px, 4vw, 56px)`.
- Grid de tarjetas: `grid-template-columns: repeat(auto-fill, minmax(295px, 1fr)); gap: 14px`.

### 1.4 Accesibilidad / motion
- Foco visible: `outline: 3px solid var(--gold-400); outline-offset:2px; border-radius:6px`.
- Respeta `prefers-reduced-motion: reduce` (desactiva animaciones/transiciones).
- Botones táctiles con `min-height: 44px` (header) / `38–46px` (chips, inputs).

---

## 2. Layout general (secciones de la página)

1. **Header (hero)** — fondo oscuro con degradado + mancha radial decorativa, logo, botones "ghost", eyebrow, H1, subtítulo, fila de stats.
2. **Panel de niveles** (acordeón) — se superpone al header (`margin-top:-16px`), tarjetas de nivel 1–5 con flechas de progresión.
3. **Toolbar** — buscador, select de orden, switch de vista (por etapa / por nivel), chips de filtro por etapa y por nivel, línea de resultados.
4. **Catálogo (main)** — secciones agrupadas (por etapa o por nivel), cada una con header de sección + grid de tarjetas; al hacer click, la tarjeta expande un panel de detalle inline dentro del grid.
5. **Modal de "Mitigación de riesgos"** — overlay + tarjetas explicativas.
6. **Footer** — fondo morado oscuro, 4 columnas de info operativa + nota final.

---

## 3. Componentes

### 3.1 Header
```css
header.site{
  background:linear-gradient(135deg,var(--purple-900) 0%,var(--purple-700) 62%,#4A2F7A 100%);
  color:#fff; padding:28px clamp(20px,4vw,56px) 34px; position:relative; overflow:hidden;
}
```
- Decoración: círculo radial dorado semitransparente en la esquina superior derecha (`::after`, 420×420px, `radial-gradient(circle, rgba(232,185,62,.16), transparent 65%)`).
- `.logo-chip`: contenedor blanco redondeado (12px) con sombra `--shadow-md`, contiene el logo (imagen, `height:52px`).
- `.header-actions`: botones "ghost" alineados a la derecha (`margin-left:auto`), pill translúcido con borde blanco tenue, hover que aclara fondo/borde.
- `.eyebrow`: etiqueta pequeña dorada, mayúsculas, `letter-spacing:.14em`, con un guion decorativo (`::before`, línea de 26×2px) antes del texto.
- `h1`: `clamp(1.5rem,3.2vw,2.35rem)`, peso 800, fuente Sora.
- `.hero-stats`: fila de "stat cards" translúcidas (`rgba(255,255,255,.07)`, borde `rgba(255,255,255,.16)`), número grande en Sora con el valor destacado en dorado (`<em>`) y label pequeño gris claro debajo.

### 3.2 Panel de niveles (acordeón)
- Contenedor blanco flotante sobre el header (`.levels-panel`, radius 18px, shadow-md).
- Header clickeable (`.levels-head`) con título, hint y chevron que rota 180° al abrir (clase `.open`).
- Cuerpo oculto por defecto (`display:none` → `block` con `.open .levels-body`).
- Grid responsivo de 5 tarjetas de nivel (`repeat(auto-fit, minmax(210px,1fr))`).
- Cada `.level-card`: badge numerado circular/redondeado (34×34px) con color progresivo por nivel (de morado claro a dorado en nivel 5), nombre del nivel, lista de requisitos con bullets dorados custom, y una flecha circular (`.level-arrow`) entre tarjetas indicando progresión (oculta en `<1150px`).
- La tarjeta de **nivel 5** tiene tratamiento especial: fondo oscuro degradado (`#2A2433 → #3D2766`) con texto claro, en lugar del fondo lila claro del resto.
- Nota informativa final con icono, fondo `--purple-100`.

### 3.3 Toolbar de filtros
- `.search-box`: pill blanco con icono de lupa + input sin bordes.
- `select.sort`: pill con flecha custom en SVG inline como `background-image` (data URI), sin apariencia nativa (`appearance:none`).
- `.view-switch`: grupo de 2 botones tipo toggle dentro de un contenedor pill; el activo tiene fondo `--purple-700` y texto blanco.
- `.chips`: filtros tipo pill (`border:1.5px solid var(--line)`); estado activo (`.on`) cambia fondo según el grupo:
  - Chip de etapa activo → `--purple-700`
  - Chip de nivel activo (`.lvl.on`) → `--purple-600`
  - Chip "Top" activo (`.top-chip.on`) → `--gold-600`
  - Chip de automatización activo (`.auto-chip.on`) → `--purple-900`
- `.results-line`: texto pequeño con conteo de resultados y botón "Limpiar filtros" (link subrayado en `--purple-600`).

### 3.4 Secciones del catálogo
- `.section-head`: título con icono cuadrado de color (según etapa/nivel) + texto meta a la derecha; separador inferior (`border-bottom:2px solid var(--purple-200)`).
- `.grid`: CSS grid autoajustable (`minmax(295px,1fr)`).

### 3.5 Tarjeta (`.card`)
- Fondo blanco, borde `--line`, radius 14px, padding ~18px, layout en columna con `gap:9px`.
- Hover: `translateY(-3px)` + sombra media + borde lila claro.
- Estado expandido (`.expanded`): borde `--purple-600` + sombra media.
- Variante **"automatización"** (`.is-auto`): fondo degradado oscuro (`#2A2433 → #3D2766`), texto claro, acentos dorados en vez de morados; al hover el borde se vuelve dorado.
- Estructura interna:
  - `.card-top`: tag superior (ej. "AUTO") + badge "Top" alineado a la derecha (fondo crema/dorado translúcido).
  - `h3` (nombre), `.tool` (herramienta, en color acento).
  - `p.desc` (descripción corta, `flex:1` para empujar el footer abajo).
  - `.card-foot`: separador punteado superior, contiene pill de nivel (`.lvl-pill`, fondo `--purple-100`), pill de tiempo, y puntos de riesgo (`.risk-dots`) alineados a la derecha.
  - `.expand-hint`: texto + chevron centrado abajo, el chevron rota 180° cuando la tarjeta está expandida.

### 3.6 Panel de detalle (expandido dentro del grid)
- Ocupa todo el ancho del grid (`grid-column:1/-1`), aparece con animación `reveal` (fade + slide desde arriba, 0.28s).
- Borde de color según variante (`--purple-600` normal / `--gold-600` automatización).
- `.detail-head`: fondo degradado suave, título, herramienta, descripción larga, botón circular de cierre (`.close-detail`), y fila de badges (`.dbadge`) con info clave (tiempo, nivel, etc.); badge dorado especial (`.dbadge.gold`) para destacar.
- `.detail-body`: grid de bloques (`.dblock`, `minmax(250px,1fr)`), cada uno con:
  - Etiqueta superior en mayúsculas con icono cuadrado de fondo morado (`.db-ico`).
  - Contenido en texto normal.
  - Bloque especial de **riesgo**: barra de progreso (`.risk-track` / `.risk-fill`) coloreada dinámicamente según nivel de riesgo (usa `--risk1..5`), + valor numérico + leyenda.
  - Bloque **"próximos pasos"** (`.dblock.next`) resaltado en tono crema/dorado (`#FDF8EC`, borde `#EDD592`), ocupa todo el ancho (`grid-column:1/-1`).

### 3.7 Slider de ejemplos (dentro del detalle, solo agentes de automatización)
- Contenedor oscuro (`#241B33` con borde `#3D2766`).
- Carrusel simple: `.slides` (flex row) que se desplaza con `translateX(-N*100%)`.
- Placeholder con icono + texto cuando no hay imagen cargada.
- Controles: botones circulares prev/next semitransparentes sobre la imagen, y dots de paginación abajo (dot activo en dorado).

### 3.8 Estado vacío (sin resultados)
- `.empty-state`: tarjeta punteada centrada, icono grande, texto en dos líneas (título en negrita + sugerencia).

### 3.9 Modal (Mitigación de riesgos)
- Overlay fijo full-screen (`rgba(36,27,51,.62)` + `backdrop-filter: blur(3px)`), oculto por defecto, visible con `.open` (`display:flex`).
- Caja modal centrada, blanca, radius 20px, ancho máx. 960px, animación `reveal`.
- Header con degradado morado oscuro, icono en chip dorado translúcido, título + descripción, botón de cierre circular.
- Body en grid de "risk-cards" (número circular + título + lista con bullets dorados).
- Footer con nota legal/aclaratoria pequeña.
- Cierra con click en overlay, botón de cierre, o tecla `Escape`.

### 3.10 Footer
- Fondo `--purple-900`, texto lila claro (`#C9BCE0`).
- Grid de 4 columnas (`repeat(auto-fit, minmax(210px,1fr))`), cada una con encabezado dorado + icono, y listas/párrafos con términos en negrita blanca.
- Línea final (`.foot-note`) separada por borde superior tenue, con dos textos distribuidos (`justify-content:space-between`).

---

## 4. Iconografía
- Todos los iconos son **SVG inline** (stroke-based, `stroke-width:2`, `fill:none`), estilo *outline* minimalista (tipo Feather/Lucide).
- Tamaños típicos: 12–22px según contexto (chip, botón, badge, header de sección).
- Color heredado vía `currentColor` o `color` del contenedor — permite reutilizar el mismo SVG en fondo claro u oscuro.

---

## 5. Responsive
Breakpoint principal: `max-width: 1150px` → oculta flechas de progresión entre niveles (`.level-arrow`).
Breakpoint móvil: `max-width: 640px`:
```css
.header-actions{margin-left:0;width:100%}
.detail-body{grid-template-columns:1fr}
```
El resto de la grilla usa `auto-fit`/`auto-fill` con `minmax()`, por lo que es fluida sin más breakpoints explícitos.

---

## 6. Patrones de interacción (JS) a replicar
No es necesario copiar el código, pero el comportamiento a reproducir es:

1. **Filtrado en vivo**: buscador de texto libre + chips multi-selección (etapa, nivel, "top", "automatización") + botón "limpiar filtros"; todo combinado con lógica AND/OR sobre el dataset.
2. **Orden**: select con opciones (orden original, A–Z, nivel asc/desc, riesgo asc/desc, "top primero").
3. **Vista conmutable**: agrupar el catálogo por **etapa** o por **nivel** (toggle de 2 botones).
4. **Expansión de tarjeta**: click en tarjeta → inserta/quita un panel de detalle justo debajo dentro del grid (no es un modal), con scroll suave hacia la tarjeta. Solo una tarjeta expandida a la vez.
5. **Acordeón de niveles**: abre/cierra, controlado también por un botón del header que hace scroll + fuerza apertura.
6. **Modal de riesgos**: abre/cierra con botón del header, click fuera, o `Escape` (que también cierra cualquier detalle expandido).
7. **Carrusel** dentro del detalle (solo si el ítem tiene imágenes de ejemplo): botones prev/next + dots, sin librerías externas.
8. **Accesibilidad de estado**: uso de `aria-expanded`, `aria-pressed`, `aria-label`, `aria-modal`, `role="dialog"`, `role="group"`.

---

## 7. Checklist de migración
- [ ] Importar fuentes Sora + Inter.
- [ ] Definir variables de color/sombra/radio como custom properties (o tokens equivalentes en el nuevo stack: Tailwind config, CSS Modules, styled-components, etc.).
- [ ] Reconstruir header con degradado + mancha decorativa + stats.
- [ ] Reconstruir acordeón de niveles con las 5 tarjetas y flechas de progresión.
- [ ] Reconstruir toolbar (buscador, sort, view-switch, chips) y su lógica de filtrado/orden.
- [ ] Reconstruir card + detail panel expandible inline (no modal) con sus bloques de información y barra de riesgo dinámica.
- [ ] Reconstruir slider simple de imágenes de ejemplo.
- [ ] Reconstruir modal de "Mitigación de riesgos".
- [ ] Reconstruir footer de 4 columnas.
- [ ] Portar breakpoints (`1150px`, `640px`) y comportamiento `prefers-reduced-motion`.
- [ ] Sustituir el logo embebido en base64 por el asset real del nuevo sitio.

---

*Nota: este documento describe el diseño y comportamiento de UI. El contenido de negocio (los 31 prompts/agentes, textos de niveles, textos de riesgos, etc.) vive en el arreglo `DATA` del archivo original y debe migrarse por separado como datos, no como parte del sistema de diseño.*
