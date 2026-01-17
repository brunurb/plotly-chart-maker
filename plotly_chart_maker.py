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
        '######': 'by brunurb',
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

# --- Compact header with avatar and link ---
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

if uploaded_files:
    # Chart type selection
    chart_types_display = CHART_TYPES[language]
    selected_chart_type_display = st.selectbox(t['chart_type'], chart_types_display)
    
    # Map back to English for internal use
    if language == 'pt':
        selected_chart_type = CHART_TYPE_MAP.get(selected_chart_type_display, selected_chart_type_display)
    else:
        selected_chart_type = selected_chart_type_display

    # Color palette options
    color_palette_options = list(px.colors.qualitative.__dict__.keys())
    color_palette_options = [name for name in color_palette_options if not name.startswith('_') and isinstance(px.colors.qualitative.__dict__[name], list)]
    palette_colors = {name: px.colors.qualitative.__dict__[name] for name in color_palette_options}

    # Display palette previews
    st.write(f"### {t['color_palette']}")
    selected_palette_name = st.selectbox(t['choose_palette'], options=color_palette_options)

    if selected_palette_name:
        colors = palette_colors[selected_palette_name]
        color_swatches = ''.join([f'<div style="display: inline-block; width: 12px; height: 12px; margin-right: 2px; background-color: {color}; border: 1px solid #ddd;"></div>' for color in colors])
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <span style="margin-right: 10px;">{selected_palette_name}</span>
            <div style="display: flex;">{color_swatches}</div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander(t['view_all_palettes'], expanded=False):
        for name in color_palette_options:
            colors = palette_colors[name]
            color_swatches = ''.join([f'<div style="display: inline-block; width: 12px; height: 12px; margin-right: 2px; background-color: {color}; border: 1px solid #ddd;"></div>' for color in colors])
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <span style="margin-right: 10px; width: 150px;">{name}</span>
                <div style="display: flex;">{color_swatches}</div>
            </div>
            """, unsafe_allow_html=True)

    # Options columns
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"### {t['display_options']}")
        show_x_label = st.checkbox(t['show_x_label'], value=True)
        show_y_label = st.checkbox(t['show_y_label'], value=True)
        show_title = st.checkbox(t['show_title'], value=True)
        show_bar_values = st.checkbox(t['show_values'], value=True)
    with col2:
        st.write(f"### {t['style_options']}")
        text_color_options = [t['black'], t['white']]
        text_color_display = st.radio(t['text_color'], text_color_options)
        text_color = 'Black' if text_color_display == t['black'] else 'White'
        bg_color_options = [t['white'], t['black'], t['transparent']]
        bg_color_display = st.radio(t['bg_color'], bg_color_options)
        if bg_color_display == t['white']:
            bg_color = 'White'
        elif bg_color_display == t['black']:
            bg_color = 'Black'
        else:
            bg_color = 'Transparent'

    # Export format
    st.write(f"### {t['export_options']}")
    export_format = st.selectbox(t['export_format'], ['PNG', 'SVG', 'PDF', 'HTML'])

    # Function to create chart
    def get_fig(data, chart_type, palette_name, filename=None):
        colors = px.colors.qualitative.__dict__[palette_name]
        effective_text_color = 'black' if bg_color == 'White' else 'white' if bg_color == 'Black' else text_color.lower()
        fig = go.Figure()
        data_columns = [col for col in ['Sim', 'Não', 'Ns/Nr'] if col in data.columns]
        if not data_columns:
            data_columns = data.select_dtypes(include=['number']).columns.tolist()

        if chart_type == 'Bar':
            for i, col in enumerate(data_columns):
                fig.add_trace(go.Bar(
                    x=data.iloc[:, 0] if len(data.columns) > 0 else data.index,
                    y=data[col],
                    name=col,
                    marker_color=colors[i % len(colors)],
                    text=data[col] if show_bar_values else None,
                    textposition='outside' if show_bar_values else None,
                    textfont=dict(color=effective_text_color)
                ))
            fig.update_layout(barmode='group')
        elif chart_type == 'Line':
            for i, col in enumerate(data_columns):
                fig.add_trace(go.Scatter(
                    x=data.iloc[:, 0] if len(data.columns) > 0 else data.index,
                    y=data[col],
                    name=col,
                    mode='lines+markers',
                    line=dict(color=colors[i % len(colors)]),
                    text=data[col] if show_bar_values else None,
                    textposition='top center' if show_bar_values else None,
                    textfont=dict(color=effective_text_color)
                ))
        elif chart_type == 'Scatter':
            for i, col in enumerate(data_columns):
                fig.add_trace(go.Scatter(
                    x=data.iloc[:, 0] if len(data.columns) > 0 else data.index,
                    y=data[col],
                    name=col,
                    mode='markers',
                    marker=dict(color=colors[i % len(colors)], size=10),
                    text=data[col] if show_bar_values else None,
                    textposition='top center' if show_bar_values else None,
                    textfont=dict(color=effective_text_color)
                ))
        elif chart_type == 'Pie':
            fig.add_trace(go.Pie(
                labels=data_columns,
                values=data[data_columns].iloc[0] if len(data) > 0 else [],
                marker=dict(colors=colors[:len(data_columns)]),
                textinfo='label+percent' if show_bar_values else 'label',
                textfont=dict(color=effective_text_color)
            ))
        elif chart_type == 'Area':
            for i, col in enumerate(data_columns):
                fig.add_trace(go.Scatter(
                    x=data.iloc[:, 0] if len(data.columns) > 0 else data.index,
                    y=data[col],
                    name=col,
                    stackgroup='one',
                    fillcolor=colors[i % len(colors)],
                    line=dict(color=colors[i % len(colors)])
                ))

        layout_config = {
            'legend': dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="right", x=1),
            'title_text': t['chart_title'].format(name=os.path.splitext(filename)[0]) if filename and show_title else (t['chart_title_default'] if show_title else ''),
            'xaxis_title': data.columns[0] if show_x_label and len(data.columns) > 0 else '',
            'yaxis_title': t['y_axis'] if show_y_label else '',
            'legend_title_text': '',
            'margin': dict(l=60, r=60, b=80, t=100, pad=10),
            'height': 600,
            'width': 1200,
            'autosize': False
        }

        if bg_color == 'White':
            layout_config.update({
                'paper_bgcolor': 'white',
                'plot_bgcolor': 'white',
                'font': dict(color='black'),
                'xaxis': dict(title=dict(font=dict(color='black')), tickfont=dict(color='black'), gridcolor='rgba(200,200,200,0.3)', showgrid=True),
                'yaxis': dict(title=dict(font=dict(color='black')), tickfont=dict(color='black'), gridcolor='rgba(200,200,200,0.3)', showgrid=True),
                'legend': dict(font=dict(color='black'))
            })
        elif bg_color == 'Black':
            layout_config.update({
                'paper_bgcolor': 'black',
                'plot_bgcolor': 'black',
                'font': dict(color='white'),
                'xaxis': dict(title=dict(font=dict(color='white')), tickfont=dict(color='white'), gridcolor='rgba(100,100,100,0.5)', showgrid=True),
                'yaxis': dict(title=dict(font=dict(color='white')), tickfont=dict(color='white'), gridcolor='rgba(100,100,100,0.5)', showgrid=True),
                'legend': dict(font=dict(color='white'))
            })
        else:
            layout_config.update({
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'font': dict(color=effective_text_color),
                'xaxis': dict(title=dict(font=dict(color=effective_text_color)), tickfont=dict(color=effective_text_color), gridcolor='rgba(200,200,200,0.3)', showgrid=True),
                'yaxis': dict(title=dict(font=dict(color=effective_text_color)), tickfont=dict(color=effective_text_color), gridcolor='rgba(200,200,200,0.3)', showgrid=True),
                'legend': dict(font=dict(color=effective_text_color))
            })

        fig.update_layout(**layout_config)
        return fig

# --- The rest of your code for preview, export, and single chart downloads stays exactly as before ---
# This keeps your original working logic intact.
# Just remove st.title(t['title']) line and replace with the above compact header.

# The remaining code (preview charts, export all, export single, instructions) goes here unchanged.
