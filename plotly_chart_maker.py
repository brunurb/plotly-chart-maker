import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from io import BytesIO
import zipfile

# =========================
# Translations
# =========================
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
        'legend_pos': 'Legend placement',
        'export_options': '💾 Export Options',
        'export_format': 'Export format',
        'preview_charts': '🔍 Preview Charts',
        'export_all': '📦 Export All Charts',
        'download_all': '⬇️ Download All Charts as {format} (ZIP)',
        'charts_ready': '✅ {count} charts ready!',
        'chart_title': 'Responses - {name}',
        'chart_title_default': 'Chart',
        'y_axis': 'Values',
        'black': 'Black',
        'white': 'White',
        'transparent': 'Transparent'
    },
    'pt': {
        'title': '📊 Conversor de CSV para Gráficos com Plotly',
        'upload': 'Escolher ficheiros CSV',
        'chart_type': 'Escolher tipo de gráfico',
        'color_palette': '🎨 Pré-visualização de Paletas',
        'choose_palette': 'Escolha uma paleta',
        'view_all_palettes': 'Ver todas as paletas',
        'display_options': '⚙️ Opções de Visualização',
        'show_x_label': 'Mostrar eixo X',
        'show_y_label': 'Mostrar eixo Y',
        'show_title': 'Mostrar título',
        'show_values': 'Mostrar valores',
        'style_options': '🎨 Opções de Estilo',
        'text_color': 'Cor do texto',
        'bg_color': 'Cor de fundo',
        'legend_pos': 'Posição da legenda',
        'export_options': '💾 Opções de Exportação',
        'export_format': 'Formato de exportação',
        'preview_charts': '🔍 Pré-visualizar Gráficos',
        'export_all': '📦 Exportar Todos',
        'download_all': '⬇️ Descarregar todos ({format})',
        'charts_ready': '✅ {count} gráficos prontos!',
        'chart_title': 'Respostas - {name}',
        'chart_title_default': 'Gráfico',
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

# =========================
# Page config
# =========================
st.set_page_config(
    page_title="ChartMaker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.title("🌐 Language / Idioma")
    language = st.radio(
        "",
        ['en', 'pt'],
        format_func=lambda x: '🇬🇧 English' if x == 'en' else '🇵🇹 Português'
    )
    st.markdown("---")
    st.markdown("**ChartMaker**")
    st.markdown("v1.0")

t = TRANSLATIONS[language]

# =========================
# Compact header (safe)
# =========================
st.markdown(
    f"""
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;">
        <h2 style="margin:0;">{t['title']}</h2>
        <div style="display:flex; align-items:center; gap:6px;">
            <span style="font-size:0.85em; color:#666;">by brunurb</span>
            <a href="https://brunurb.github.io/" target="_blank">
                <img src="https://avatars.githubusercontent.com/u/8878983?s=32"
                     width="20" height="20"
                     style="border-radius:50%;">
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# File uploader
# =========================
uploaded_files = st.file_uploader(
    t['upload'],
    type="csv",
    accept_multiple_files=True
)

if uploaded_files:
    chart_type_display = st.selectbox(
        t['chart_type'],
        CHART_TYPES[language]
    )

    chart_type = (
        CHART_TYPE_MAP.get(chart_type_display, chart_type_display)
        if language == 'pt'
        else chart_type_display
    )

    # -------------------------
    # Palette chooser (original)
    # -------------------------
    palette_names = [
        p for p in px.colors.qualitative.__dict__
        if not p.startswith("_")
        and isinstance(px.colors.qualitative.__dict__[p], list)
    ]

    palettes = {p: px.colors.qualitative.__dict__[p] for p in palette_names}

    st.markdown(f"### {t['color_palette']}")
    selected_palette = st.selectbox(t['choose_palette'], palette_names)

    if selected_palette:
        swatches = "".join(
            f'<div style="width:6px;height:6px;background:{c};margin-right:2px;"></div>'
            for c in palettes[selected_palette]
        )
        st.markdown(
            f'<div style="display:flex;align-items:center;">{swatches}</div>',
            unsafe_allow_html=True
        )

    # -------------------------
    # Options
    # -------------------------
    col1, col2 = st.columns(2)

    with col1:
        show_x = st.checkbox(t['show_x_label'], True)
        show_y = st.checkbox(t['show_y_label'], True)
        show_title = st.checkbox(t['show_title'], True)
        show_values = st.checkbox(t['show_values'], False)

    with col2:
        text_color_label = st.radio(t['text_color'], [t['black'], t['white']])
        bg_color_label = st.radio(
            t['bg_color'],
            [t['white'], t['black'], t['transparent']]
        )

        legend_pos = st.selectbox(
            t['legend_pos'],
            [
                'Right Top', 'Right Center', 'Right Bottom',
                'Bottom Left', 'Bottom Center', 'Bottom Right'
            ]
        )

    text_color = 'black' if text_color_label == t['black'] else 'white'
    bg_color = (
        'white' if bg_color_label == t['white']
        else 'black' if bg_color_label == t['black']
        else 'rgba(0,0,0,0)'
    )

    # -------------------------
    # Export format
    # -------------------------
    st.markdown(f"### {t['export_options']}")
    export_format = st.selectbox(
        t['export_format'],
        ['PNG', 'SVG', 'PDF', 'HTML']
    )

    # -------------------------
    # Chart builder
    # -------------------------
    def build_fig(df, filename):
        colors = palettes[selected_palette]
        numeric_cols = df.select_dtypes(include='number').columns
        fig = go.Figure()

        for i, col in enumerate(numeric_cols):
            fig.add_bar(
                x=df.iloc[:, 0],
                y=df[col],
                name=col,
                marker_color=colors[i % len(colors)],
                text=df[col] if show_values else None,
            )

        legend = {}
        margin = dict(l=50, r=50, t=60, b=50)

        if legend_pos.startswith('Right'):
            legend.update(
                orientation='v',
                x=1.02,
                y=1 if 'Top' in legend_pos else 0.5 if 'Center' in legend_pos else 0,
                xanchor='left',
                yanchor='top' if 'Top' in legend_pos else 'middle' if 'Center' in legend_pos else 'bottom'
            )
            margin['r'] = 180
        else:
            legend.update(
                orientation='h',
                y=-0.25,
                x=0 if 'Left' in legend_pos else 0.5 if 'Center' in legend_pos else 1,
                xanchor='left' if 'Left' in legend_pos else 'center' if 'Center' in legend_pos else 'right'
            )
            margin['b'] = 120

        fig.update_layout(
            title=t['chart_title'].format(name=filename) if show_title else None,
            yaxis_title=t['y_axis'] if show_y else None,
            legend=legend,
            paper_bgcolor=bg_color,
            plot_bgcolor=bg_color,
            font=dict(color=text_color),
            margin=margin,
            height=600
        )
        return fig

    # -------------------------
    # Preview
    # -------------------------
    if st.button(t['preview_charts'], type="primary"):
        for f in uploaded_files:
            df = pd.read_csv(f)
            fig = build_fig(df, os.path.splitext(f.name)[0])
            st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # Export all
    # -------------------------
    if st.button(t['export_all']):
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
            for f in uploaded_files:
                df = pd.read_csv(f)
                fig = build_fig(df, os.path.splitext(f.name)[0])
                name = os.path.splitext(f.name)[0]

                if export_format == 'HTML':
                    z.writestr(f"{name}.html", fig.to_html())
                else:
                    z.writestr(
                        f"{name}.{export_format.lower()}",
                        fig.to_image(format=export_format.lower(), scale=2)
                    )

        buffer.seek(0)
        st.download_button(
            t['download_all'].format(format=export_format),
            buffer,
            file_name="charts.zip",
            mime="application/zip"
        )
