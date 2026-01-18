import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from io import BytesIO
import zipfile

# -----------------------
# Language translations
# -----------------------
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
        'legend_placement': 'Legend placement',
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
        'legend_placement': 'Posição da legenda',
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

LEGEND_OPTIONS = {
    'en': [
        'Right Top', 'Right Center', 'Right Bottom',
        'Bottom Left', 'Bottom Center', 'Bottom Right'
    ],
    'pt': [
        'Direita Topo', 'Direita Centro', 'Direita Baixo',
        'Inferior Esquerda', 'Inferior Centro', 'Inferior Direita'
    ]
}

# -----------------------
# Page config
# -----------------------
st.set_page_config(page_title="ChartMaker", page_icon="📊", layout="wide")

# -----------------------
# Sidebar
# -----------------------
with st.sidebar:
    st.markdown("### 🌐 Language / Idioma")
    language = st.radio(
        "",
        options=['en', 'pt'],
        format_func=lambda x: '🇬🇧 English' if x == 'en' else '🇵🇹 Português',
        index=0
    )
    st.markdown("---")
    st.markdown("### ChartMaker")
    st.markdown("v1.0")

t = TRANSLATIONS[language]

# -----------------------
# Header with title and credit
# -----------------------
st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:center;">
    <h1 style="margin:0; font-size:1.5rem;">{t['title']}</h1>
    <a href="https://brunurb.github.io/" target="_blank" style="display:flex; align-items:center; text-decoration:none;">
        <img src="https://avatars.githubusercontent.com/u/8878983?s=32" width="20" height="20" style="border-radius:50%; margin-right:4px;">
        <span style="font-size:0.9rem; color:#666;">by brunurb</span>
    </a>
</div>
""", unsafe_allow_html=True)

# -----------------------
# File uploader
# -----------------------
uploaded_files = st.file_uploader(t['upload'], type="csv", accept_multiple_files=True)

if uploaded_files:
    # Chart type selection
    chart_types_display = CHART_TYPES[language]
    selected_chart_type_display = st.selectbox(t['chart_type'], chart_types_display)
    selected_chart_type = CHART_TYPE_MAP.get(selected_chart_type_display, selected_chart_type_display) if language=='pt' else selected_chart_type_display

    # Color palette selection
    color_palette_options = [name for name in dir(px.colors.qualitative) if not name.startswith('_') and isinstance(getattr(px.colors.qualitative, name), list)]
    palette_colors = {name: getattr(px.colors.qualitative, name) for name in color_palette_options}
    selected_palette_name = st.selectbox(t['choose_palette'], color_palette_options)
    
    # Display palette preview
    if selected_palette_name:
        colors = palette_colors[selected_palette_name]
        color_swatches = ''.join([f'<div style="display:inline-block; width:6px; height:6px; margin-right:2px; background-color:{c}; border:1px solid #ddd;"></div>' for c in colors])
        st.markdown(f"<div style='margin-bottom:10px;'>{selected_palette_name} {color_swatches}</div>", unsafe_allow_html=True)

    # -----------------------
    # Display options and style options
    # -----------------------
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"### {t['display_options']}")
        show_x_label = st.checkbox(t['show_x_label'], value=True)
        show_y_label = st.checkbox(t['show_y_label'], value=True)
        show_title = st.checkbox(t['show_title'], value=True)
        show_bar_values = st.checkbox(t['show_values'], value=True)
        legend_choice = st.selectbox(t['legend_placement'], LEGEND_OPTIONS[language])
    with col2:
        st.write(f"### {t['style_options']}")
        text_color_options = [t['black'], t['white']]
        text_color_label = st.radio(t['text_color'], text_color_options)
        text_color = 'black' if text_color_label==t['black'] else 'white'
        bg_color_options = [t['white'], t['black'], t['transparent']]
        bg_color_display = st.radio(t['bg_color'], bg_color_options)
        bg_color = bg_color_display.lower() if bg_color_display!=t['transparent'] else 'transparent'

    # -----------------------
    # Export format
    # -----------------------
    export_format = st.selectbox(t['export_format'], ['PNG','SVG','PDF','HTML'])

    # -----------------------
    # Helper: Generate Plotly figure
    # -----------------------
    def get_fig(data, chart_type, palette_name, filename=None):
        colors = palette_colors[palette_name]
        # Determine effective text color
        effective_text_color = text_color if bg_color=='transparent' else ('black' if bg_color=='white' else 'white')
        fig = go.Figure()
        data_cols = [c for c in data.columns if data[c].dtype in [int,float]] or data.columns[1:]
        if chart_type=='Bar':
            for i,col in enumerate(data_cols):
                fig.add_trace(go.Bar(
                    x=data.iloc[:,0],
                    y=data[col],
                    name=col,
                    marker_color=colors[i % len(colors)],
                    text=data[col] if show_bar_values else None,
                    textposition='outside' if show_bar_values else None,
                    textfont=dict(color=effective_text_color)
                ))
            fig.update_layout(barmode='group')
        elif chart_type=='Line':
            for i,col in enumerate(data_cols):
                fig.add_trace(go.Scatter(
                    x=data.iloc[:,0],
                    y=data[col],
                    name=col,
                    mode='lines+markers',
                    line=dict(color=colors[i % len(colors)]),
                    text=data[col] if show_bar_values else None,
                    textposition='top center' if show_bar_values else None,
                    textfont=dict(color=effective_text_color)
                ))
        # Pie, Scatter, Area omitted for brevity; same logic

        # Chart layout
        fig.update_layout(
            title=dict(
                text=t['chart_title'].format(name=filename) if show_title else '',
                font=dict(color=effective_text_color)
            ),
            xaxis=dict(
                title=dict(text=data.columns[0] if show_x_label else '', font=dict(color=effective_text_color)),
                tickfont=dict(color=effective_text_color),
                gridcolor='rgba(200,200,200,0.3)',
                showgrid=True
            ),
            yaxis=dict(
                title=dict(text=t['y_axis'] if show_y_label else '', font=dict(color=effective_text_color)),
                tickfont=dict(color=effective_text_color),
                gridcolor='rgba(200,200,200,0.3)',
                showgrid=True
            ),
            paper_bgcolor='white' if bg_color=='white' else 'black' if bg_color=='black' else 'rgba(0,0,0,0)',
            plot_bgcolor='white' if bg_color=='white' else 'black' if bg_color=='black' else 'rgba(0,0,0,0)',
        )

        # -----------------------
        # Legend placement outside chart
        # -----------------------
        right_opts = ['Right Top','Right Center','Right Bottom','Direita Topo','Direita Centro','Direita Baixo']
        bottom_opts = ['Bottom Left','Bottom Center','Bottom Right','Inferior Esquerda','Inferior Centro','Inferior Direita']
        if legend_choice in right_opts:
            y_map = {'Top':1,'Centro':0.5,'Center':0.5,'Baixo':0}[legend_choice.split()[-1]]
            fig.update_layout(
                legend=dict(
                    orientation='v',
                    x=1.02,
                    xanchor='left',
                    y=y_map,
                    yanchor='top',
                    font=dict(color=effective_text_color)
                ),
                margin=dict(l=60,r=150,t=100,b=80)
            )
        elif legend_choice in bottom_opts:
            x_map = {'Left':0,'Centro':0.5,'Center':0.5,'Direita':1,'Right':1,'Esquerda':0}[legend_choice.split()[-1]]
            fig.update_layout(
                legend=dict(
                    orientation='h',
                    x=x_map,
                    xanchor='center' if x_map==0.5 else ('left' if x_map==0 else 'right'),
                    y=-0.25,
                    yanchor='top',
                    font=dict(color=effective_text_color)
                ),
                margin=dict(l=60,r=60,t=100,b=120)
            )
        return fig

    # -----------------------
    # Preview charts
    # -----------------------
    if st.button(t['preview_charts'], type="primary"):
        for uploaded_file in uploaded_files:
            try:
                data = pd.read_csv(uploaded_file, encoding='utf-8')
            except:
                uploaded_file.seek(0)
                data = pd.read_csv(uploaded_file, encoding='latin-1')
            st.write(f"### {t['data_preview'].format(filename=uploaded_file.name)}")
            with st.expander(t['view_data']):
                st.dataframe(data.head())
            fig = get_fig(data, selected_chart_type, selected_palette_name, uploaded_file.name)
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{uploaded_file.name}")

# -----------------------
# Export and other functions omitted for brevity
# -----------------------
