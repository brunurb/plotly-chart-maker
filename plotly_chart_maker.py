import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from io import BytesIO
import zipfile

# ----------------------------
# Language translations
# ----------------------------
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
        'try_individual': '💡 Try using "Export Single Chart" below',
        'export_individual': '📥 Export Individual Charts',
        'download_single': '⬇️ Download {filename} as {format}',
        'data_preview': '📄 {filename}',
        'view_data': 'View data',
        'error_processing': 'Error processing {filename}: {error}',
        'error_exporting': 'Error exporting {filename}: {error}',
        'skipped': 'Skipped {filename}: {error}',
        'how_to_use': '📝 How to use:',
        'instructions': '''1. Upload CSV files
2. Choose chart type and palette
3. Customize display and style options
4. Preview or export charts''',
        'format_guide': '💡 Format Guide:',
        'format_info': '''PNG, SVG, PDF, HTML''',
        'chart_title': 'Responses by Concelhos - {name}',
        'chart_title_default': 'Chart',
        'y_axis': 'Values',
        'black': 'Black',
        'white': 'White',
        'transparent': 'Transparent'
    }
}

CHART_TYPES = {
    'en': ['Bar', 'Line', 'Scatter', 'Pie', 'Area']
}

st.set_page_config(page_title="ChartMaker", page_icon="📊", layout="wide")

# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:
    st.title("🌐 Language")
    language = st.radio("", ['en'], index=0)
    st.markdown("---")
    st.markdown("### ChartMaker")
    st.markdown("v1.0")

t = TRANSLATIONS[language]

# ----------------------------
# Compact header (NEW)
# ----------------------------
st.markdown(
    f"""
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;">
        <h2 style="margin:0; font-size:1.5em;">{t['title']}</h2>
        <div style="display:flex; align-items:center; gap:6px;">
            <span style="font-size:0.85em; color:#666;">by brunurb</span>
            <a href="https://brunurb.github.io/" target="_blank">
                <img src="https://avatars.githubusercontent.com/u/8878983?s=32"
                     width="20" height="20" style="border-radius:50%;">
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# File uploader
# ----------------------------
uploaded_files = st.file_uploader(t['upload'], type="csv", accept_multiple_files=True)

if uploaded_files:
    selected_chart_type = st.selectbox(t['chart_type'], CHART_TYPES['en'])

    palettes = {
        name: px.colors.qualitative.__dict__[name]
        for name in px.colors.qualitative.__dict__
        if isinstance(px.colors.qualitative.__dict__[name], list)
    }

    st.write(f"### {t['color_palette']}")
    selected_palette = st.selectbox(t['choose_palette'], list(palettes.keys()))

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"### {t['display_options']}")
        show_x_label = st.checkbox(t['show_x_label'], True)
        show_y_label = st.checkbox(t['show_y_label'], True)
        show_title = st.checkbox(t['show_title'], True)
        show_values = st.checkbox(t['show_values'], True)

    with col2:
        st.write(f"### {t['style_options']}")
        text_color_display = st.radio(t['text_color'], [t['black'], t['white']])
        text_color = 'black' if text_color_display == t['black'] else 'white'

        bg_color_display = st.radio(t['bg_color'], [t['white'], t['black'], t['transparent']])
        bg_color = bg_color_display

        legend_choice = st.selectbox(
            t['legend_placement'],
            [
                'Right Top', 'Right Center', 'Right Bottom',
                'Bottom Left', 'Bottom Center', 'Bottom Right'
            ]
        )

    st.write(f"### {t['export_options']}")
    export_format = st.selectbox(t['export_format'], ['PNG', 'SVG', 'PDF', 'HTML'])

    # ----------------------------
    # Chart builder
    # ----------------------------
    def get_fig(data, filename):
        colors = palettes[selected_palette]
        numeric_cols = data.select_dtypes(include='number').columns.tolist()
        fig = go.Figure()

        for i, col in enumerate(numeric_cols):
            fig.add_bar(
                x=data.iloc[:, 0],
                y=data[col],
                name=col,
                marker_color=colors[i % len(colors)],
                text=data[col] if show_values else None
            )

        legend = dict()

        if legend_choice.startswith("Right"):
            legend.update(
                orientation="v",
                x=1,
                xanchor="right",
                y=1 if legend_choice.endswith("Top") else 0.5 if legend_choice.endswith("Center") else 0,
                yanchor="top" if legend_choice.endswith("Top") else "middle" if legend_choice.endswith("Center") else "bottom"
            )
        else:
            legend.update(
                orientation="h",
                y=0,
                yanchor="bottom",
                x=0 if legend_choice.endswith("Left") else 0.5 if legend_choice.endswith("Center") else 1,
                xanchor="left" if legend_choice.endswith("Left") else "center" if legend_choice.endswith("Center") else "right"
            )

        fig.update_layout(
            title=t['chart_title'].format(name=os.path.splitext(filename)[0]) if show_title else None,
            legend=legend,
            yaxis_title=t['y_axis'] if show_y_label else None,
            paper_bgcolor='black' if bg_color == t['black'] else 'white' if bg_color == t['white'] else 'rgba(0,0,0,0)',
            font=dict(color=text_color),
            height=600
        )

        return fig

    # ----------------------------
    # Preview
    # ----------------------------
    if st.button(t['preview_charts'], type="primary"):
        for f in uploaded_files:
            df = pd.read_csv(f)
            fig = get_fig(df, f.name)
            st.plotly_chart(fig, use_container_width=True)

