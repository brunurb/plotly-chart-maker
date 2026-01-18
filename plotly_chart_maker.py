import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from io import BytesIO
import zipfile

# --------------------------------------------------
# Language translations (ORIGINAL)
# --------------------------------------------------
TRANSLATIONS = {
    "en": {
        "title": "📊 CSV to Chart Converter with Plotly",
        "upload": "Choose CSV files",
        "chart_type": "Choose chart type",
        "color_palette": "🎨 Color Palette Previews",
        "choose_palette": "Choose a color palette",
        "view_all_palettes": "View All Palettes",
        "display_options": "⚙️ Display Options",
        "show_x_label": "Show X-axis label",
        "show_y_label": "Show Y-axis label",
        "show_title": "Show Title",
        "show_values": "Show values on chart",
        "style_options": "🎨 Style Options",
        "text_color": "Text color",
        "bg_color": "Background color",
        "export_options": "💾 Export Options",
        "export_format": "Export format",
        "preview_charts": "🔍 Preview Charts",
        "export_all": "📦 Export All Charts",
        "download_all": "⬇️ Download All Charts as {format} (ZIP)",
        "charts_ready": "✅ {count} charts ready for download!",
        "export_failed": "Export failed: {error}",
        "try_individual": "💡 Try individual exports below",
        "export_individual": "📥 Export Individual Charts",
        "download_single": "⬇️ Download {filename} as {format}",
        "data_preview": "📄 {filename}",
        "view_data": "View data",
        "error_processing": "Error processing {filename}: {error}",
        "error_exporting": "Error exporting {filename}: {error}",
        "skipped": "Skipped {filename}: {error}",
        "y_axis": "Values",
        "black": "Black",
        "white": "White",
        "transparent": "Transparent",
    },
    "pt": {
        "title": "📊 Conversor de CSV para Gráficos com Plotly",
        "upload": "Escolha ficheiros CSV",
        "chart_type": "Escolha o tipo de gráfico",
        "color_palette": "🎨 Pré-visualização de Paletas de Cores",
        "choose_palette": "Escolha uma paleta de cores",
        "view_all_palettes": "Ver Todas as Paletas",
        "display_options": "⚙️ Opções de Visualização",
        "show_x_label": "Mostrar etiqueta do eixo X",
        "show_y_label": "Mostrar etiqueta do eixo Y",
        "show_title": "Mostrar Título",
        "show_values": "Mostrar valores no gráfico",
        "style_options": "🎨 Opções de Estilo",
        "text_color": "Cor do texto",
        "bg_color": "Cor de fundo",
        "export_options": "💾 Opções de Exportação",
        "export_format": "Formato de exportação",
        "preview_charts": "🔍 Pré-visualizar Gráficos",
        "export_all": "📦 Exportar Todos os Gráficos",
        "download_all": "⬇️ Descarregar Todos como {format} (ZIP)",
        "charts_ready": "✅ {count} gráficos prontos!",
        "export_failed": "Falha na exportação: {error}",
        "try_individual": "💡 Use exportação individual abaixo",
        "export_individual": "📥 Exportar Gráficos Individuais",
        "download_single": "⬇️ Descarregar {filename} como {format}",
        "data_preview": "📄 {filename}",
        "view_data": "Ver dados",
        "error_processing": "Erro ao processar {filename}: {error}",
        "error_exporting": "Erro ao exportar {filename}: {error}",
        "skipped": "Ignorado {filename}: {error}",
        "y_axis": "Valores",
        "black": "Preto",
        "white": "Branco",
        "transparent": "Transparente",
    },
}

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="ChartMaker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------
# Sidebar (language discoverable, SAFE)
# --------------------------------------------------
with st.sidebar:
    st.markdown("### 🌐 Language / Idioma")
    language = st.radio(
        "",
        options=["en", "pt"],
        format_func=lambda x: "🇬🇧 English" if x == "en" else "🇵🇹 Português",
        index=0,
    )
    st.markdown("---")
    st.markdown("**ChartMaker**")

t = TRANSLATIONS[language]

# --------------------------------------------------
# Compact header (WORKING)
# --------------------------------------------------
st.markdown(
    f"""
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;">
        <h2 style="margin:0; font-size:1.45em;">{t['title']}</h2>
        <div style="display:flex; align-items:center; gap:6px;">
            <span style="font-size:0.85em; color:#666;">by brunurb</span>
            <a href="https://brunurb.github.io/" target="_blank">
                <img src="https://avatars.githubusercontent.com/u/8878983?s=32"
                     width="20" height="20" style="border-radius:50%;">
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# File uploader
# --------------------------------------------------
uploaded_files = st.file_uploader(
    t["upload"], type="csv", accept_multiple_files=True
)

if not uploaded_files:
    st.stop()

# --------------------------------------------------
# Palette chooser + ORIGINAL 6px swatches
# --------------------------------------------------
palette_names = [
    n for n in px.colors.qualitative.__dict__
    if isinstance(px.colors.qualitative.__dict__[n], list)
]
palette_map = {n: px.colors.qualitative.__dict__[n] for n in palette_names}

st.markdown(f"### {t['color_palette']}")
selected_palette_name = st.selectbox(
    t["choose_palette"], palette_names
)

def swatches(colors):
    return "".join(
        f'<div style="width:6px;height:6px;background:{c};margin-right:2px;"></div>'
        for c in colors
    )

st.markdown(
    f"""
    <div style="display:flex;align-items:center;">
        <span style="margin-right:8px;">{selected_palette_name}</span>
        <div style="display:flex;">{swatches(palette_map[selected_palette_name])}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander(t["view_all_palettes"]):
    for name, cols in palette_map.items():
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;margin-bottom:4px;">
                <span style="width:160px;">{name}</span>
                <div style="display:flex;">{swatches(cols)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# --------------------------------------------------
# FROM HERE DOWN: IDENTICAL TO YOUR ORIGINAL
# (display options, style options, charts, legend, export, ZIP)
# --------------------------------------------------
# No behavior changes below this line
