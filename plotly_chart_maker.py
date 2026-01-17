import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from io import BytesIO
import zipfile

# Language translations
TRANSLATIONS = {
    'en': {
        'title': '📊 CSV to Chart Converter with Plotly',
        'upload': 'Choose CSV files',
        'chart_type': 'Choose chart type',
        'color_palette': '🎨 Color Palette Previews',
        'choose_palette': 'Choose a color palette',
        'view_all_palettes': 'View All Palettes',
        'display_options': '⚙️ Display Options',
        'show_x_label': 'Show X-axis label',
        'show_y_label': 'Show Y-axis label',
        'show_title': 'Show Title',
        'show_values': 'Show values on chart',
        'style_options': '🎨 Style Options',
        'text_color': 'Text color',
        'bg_color': 'Background color',
        'export_options': '💾 Export Options',
        'export_format': 'Export format',
        'preview_charts': '🔍 Preview Charts',
        'export_all': '📦 Export All Charts',
        'download_all': '⬇️ Download All Charts as {format} (ZIP)',
        'charts_ready': '✅ {count} charts ready for download!',
        'export_failed': 'Export failed: {error}',
        'try_individual': '💡 Try using "Export Single Chart" below for individual downloads',
        'export_individual': '📥 Export Individual Charts',
        'download_single': '⬇️ Download {filename} as {format}',
        'data_preview': '📄 {filename}',
        'view_data': 'View data',
        'error_processing': 'Error processing {filename}: {error}',
        'error_exporting': 'Error exporting {filename}: {error}',
        'skipped': 'Skipped {filename}: {error}',
        'how_to_use': '📝 How to use:',
        'instructions': '''1. Upload one or more CSV files
2. Choose your chart type and color palette
3. Customize display and style options
4. Select export format (PNG, SVG, PDF, or HTML)
5. Click **Preview Charts** to see visualizations
6. Click **Export All Charts** to download everything as a ZIP
7. Or use individual download buttons for single charts''',
        'format_guide': '💡 Format Guide:',
        'format_info': '''- **PNG**: Best for presentations and documents (raster image)
- **SVG**: Best for scaling and editing (vector image)
- **PDF**: Best for printing and reports
- **HTML**: Interactive chart that opens in browser''',
        'chart_title': 'Responses by Concelhos - {name}',
        'chart_title_default': 'Chart',
        'x_axis': 'Concelhos',
        'y_axis': 'Values',
        'black': 'Black',
        'white': 'White',
        'transparent': 'Transparent'
    },
    'pt': {
        'title': '📊 Conversor de CSV para Gráficos com Plotly',
        'upload': 'Escolha ficheiros CSV',
        'chart_type': 'Escolha o tipo de gráfico',
        'color_palette': '🎨 Pré-visualização de Paletas de Cores',
        'choose_palette': 'Escolha uma paleta de cores',
        'view_all_palettes': 'Ver Todas as Paletas',
        'display_options': '⚙️ Opções de Visualização',
        'show_x_label': 'Mostrar etiqueta do eixo X',
        'show_y_label': 'Mostrar etiqueta do eixo Y',
        'show_title': 'Mostrar Título',
        'show_values': 'Mostrar valores no gráfico',
        'style_options': '🎨 Opções de Estilo',
        'text_color': 'Cor do texto',
        'bg_color': 'Cor de fundo',
        'export_options': '💾 Opções de Exportação',
        'export_format': 'Formato de exportação',
        'preview_charts': '🔍 Pré-visualizar Gráficos',
        'export_all': '📦 Exportar Todos os Gráficos',
        'download_all': '⬇️ Descarregar Todos os Gráficos como {format} (ZIP)',
        'charts_ready': '✅ {count} gráficos prontos para descarregar!',
        'export_failed': 'Falha na exportação: {error}',
        'try_individual': '💡 Tente usar "Exportar Gráficos Individuais" abaixo para descargas individuais',
        'export_individual': '📥 Exportar Gráficos Individuais',
        'download_single': '⬇️ Descarregar {filename} como {format}',
        'data_preview': '📄 {filename}',
        'view_data': 'Ver dados',
        'error_processing': 'Erro ao processar {filename}: {error}',
        'error_exporting': 'Erro ao exportar {filename}: {error}',
        'skipped': 'Ignorado {filename}: {error}',
        'how_to_use': '📝 Como usar:',
        'instructions': '''1. Carregue um ou mais ficheiros CSV
2. Escolha o tipo de gráfico e a paleta de cores
3. Personalize as opções de visualização e estilo
4. Selecione o formato de exportação (PNG, SVG, PDF ou HTML)
5. Clique em **Pré-visualizar Gráficos** para ver as visualizações
6. Clique em **Exportar Todos os Gráficos** para descarregar tudo num ZIP
7. Ou use os botões de descarga individuais para gráficos únicos''',
        'format_guide': '💡 Guia de Formatos:',
        'format_info': '''- **PNG**: Melhor para apresentações e documentos (imagem raster)
- **SVG**: Melhor para dimensionamento e edição (imagem vetorial)
- **PDF**: Melhor para impressão e relatórios
- **HTML**: Gráfico interativo que abre no navegador''',
        'chart_title': 'Respostas por Concelhos - {name}',
        'chart_title_default': 'Gráfico',
        'x_axis': 'Concelhos',
        'y_axis': 'Valores',
        'black': 'Preto',
        'white': 'Branco',
        'transparent': 'Transparente'
    }
}

# Chart type translations
CHART_TYPES = {
    'en': ['Bar', 'Line', 'Scatter', 'Pie', 'Area'],
    'pt': ['Barras', 'Linha', 'Dispersão', 'Circular', 'Área']
}

CHART_TYPE_MAP = {
    'Barras': 'Bar',
    'Linha': 'Line',
    'Dispersão': 'Scatter',
    'Circular': 'Pie',
    'Área': 'Area'
}

st.set_page_config(page_title="ChartMaker", page_icon="📊", layout="wide")

# Language selector in sidebar
with st.sidebar:
    st.title("🌐 Language / Idioma")
    language = st.radio(
        "",
        options=['en', 'pt'],
        format_func=lambda x: '🇬🇧 English' if x == 'en' else '🇵🇹 Português',
        index=0
    )
    st.markdown("---")
    st.markdown("### ChartMaker")
    st.markdown("v1.0")

# Get translations
t = TRANSLATIONS[language]

# --- Title with avatar/credit below and right ---
st.markdown(
    f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
        <h2 style="margin: 0; font-size: 1.5em;">{t['title']}</h2>
        <div style="display: flex; align-items: center; gap: 6px;">
            <span style="font-size: 0.85em; color: #666;">by brunurb</span>
            <a href="https://brunurb.github.io/" target="_blank">
                <img src="https://avatars.githubusercontent.com/u/8878983?s=32" width="20" height="20" style="border-radius:50%;">
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)



# --- File uploader ---
uploaded_files = st.file_uploader(t['upload'], type="csv", accept_multiple_files=True)

# --- Main app logic continues exactly as your previous code ---
# From here, the rest of your code (chart type selection, palette previews, get_fig(), previews, exports) remains the same.
# Make sure to remove any other st.title(t['title']) calls further down.

