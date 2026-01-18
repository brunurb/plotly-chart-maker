import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import zipfile
from io import BytesIO

# --------------------------------------------------
# Translations
# --------------------------------------------------
TRANSLATIONS = {
    "en": {
        "title": "📊 CSV to Chart Converter with Plotly",
        "upload": "Choose CSV files",
        "chart_type": "Choose chart type",
        "palette": "🎨 Color Palette",
        "choose_palette": "Choose a palette",
        "preview_palettes": "Palette preview",
        "display": "⚙️ Display Options",
        "style": "🎨 Style Options",
        "show_x": "Show X-axis label",
        "show_y": "Show Y-axis label",
        "show_title": "Show title",
        "show_values": "Show values",
        "text_color": "Text color",
        "bg_color": "Background color",
        "legend": "Legend placement",
        "export": "💾 Export Options",
        "format": "Export format",
        "preview": "Preview charts",
        "export_all": "Export all charts",
        "black": "Black",
        "white": "White",
        "transparent": "Transparent",
        "y_axis": "Values",
    },
    "pt": {
        "title": "📊 Conversor CSV para Gráficos com Plotly",
        "upload": "Selecionar ficheiros CSV",
        "chart_type": "Tipo de gráfico",
        "palette": "🎨 Paleta de Cores",
        "choose_palette": "Escolher paleta",
        "preview_palettes": "Pré-visualização",
        "display": "⚙️ Opções de Visualização",
        "style": "🎨 Opções de Estilo",
        "show_x": "Mostrar eixo X",
        "show_y": "Mostrar eixo Y",
        "show_title": "Mostrar título",
        "show_values": "Mostrar valores",
        "text_color": "Cor do texto",
        "bg_color": "Cor de fundo",
        "legend": "Posição da legenda",
        "export": "💾 Opções de Exportação",
        "format": "Formato de exportação",
        "preview": "Pré-visualizar gráficos",
        "export_all": "Exportar todos",
        "black": "Preto",
        "white": "Branco",
        "transparent": "Transparente",
        "y_axis": "Valores",
    },
}

CHART_TYPES = {
    "en": ["Bar"],
    "pt": ["Barras"],
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
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.title("🌐 Language / Idioma")
    language = st.radio("", ["en", "pt"], index=0)
    st.markdown("---")
    st.markdown("**ChartMaker**")

t = TRANSLATIONS[language]

# --------------------------------------------------
# Compact header
# --------------------------------------------------
st.markdown(
    f"""
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
        <h2 style="margin:0; font-size:1.45em;">{t['title']}</h2>
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
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Upload
# --------------------------------------------------
files = st.file_uploader(t["upload"], type="csv", accept_multiple_files=True)

if not files:
    st.stop()

# --------------------------------------------------
# Palette chooser + preview (RESTORED)
# --------------------------------------------------
palettes = {
    name: px.colors.qualitative.__dict__[name]
    for name in px.colors.qualitative.__dict__
    if isinstance(px.colors.qualitative.__dict__[name], list)
}

st.markdown(f"### {t['palette']}")
palette_name = st.selectbox(t["choose_palette"], list(palettes.keys()))
palette = palettes[palette_name]

st.markdown(t["preview_palettes"])
st.plotly_chart(
    go.Figure(
        data=[
            go.Bar(x=[str(i)], y=[1], marker_color=c)
            for i, c in enumerate(palette)
        ]
    ).update_layout(height=120, showlegend=False),
    use_container_width=True,
)

# --------------------------------------------------
# Options
# --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### {t['display']}")
    show_x = st.checkbox(t["show_x"], True)
    show_y = st.checkbox(t["show_y"], True)
    show_title = st.checkbox(t["show_title"], True)
    show_values = st.checkbox(t["show_values"], False)

with col2:
    st.markdown(f"### {t['style']}")
    text_color_label = st.radio(t["text_color"], [t["black"], t["white"]])
    text_color = "black" if text_color_label == t["black"] else "white"

    bg_color_label = st.radio(t["bg_color"], [t["white"], t["black"], t["transparent"]])
    bg_color = (
        "white" if bg_color_label == t["white"]
        else "black" if bg_color_label == t["black"]
        else "rgba(0,0,0,0)"
    )

    legend_choice = st.selectbox(
        t["legend"],
        [
            "Right Top", "Right Center", "Right Bottom",
            "Bottom Left", "Bottom Center", "Bottom Right",
        ],
    )

# --------------------------------------------------
# Export options (RESTORED)
# --------------------------------------------------
st.markdown(f"### {t['export']}")
export_format = st.selectbox(t["format"], ["PNG", "SVG", "PDF", "HTML"])

# --------------------------------------------------
# Chart builder (TEXT COLOR FIXED)
# --------------------------------------------------
def build_fig(df, title):
    numeric = df.select_dtypes("number").columns
    fig = go.Figure()

    for i, col in enumerate(numeric):
        fig.add_bar(
            x=df.iloc[:, 0],
            y=df[col],
            name=col,
            marker_color=palette[i % len(palette)],
            text=df[col] if show_values else None,
        )

    legend = {}
    margin = dict(l=50, r=50, t=60, b=50)

    if legend_choice.startswith("Right"):
        legend.update(
            orientation="v",
            x=1.02,
            xanchor="left",
            y=1 if legend_choice.endswith("Top") else 0.5 if legend_choice.endswith("Center") else 0,
            yanchor="top" if legend_choice.endswith("Top") else "middle" if legend_choice.endswith("Center") else "bottom",
        )
        margin["r"] = 180
    else:
        legend.update(
            orientation="h",
            y=-0.3,
            yanchor="top",
            x=0 if legend_choice.endswith("Left") else 0.5 if legend_choice.endswith("Center") else 1,
            xanchor="left" if legend_choice.endswith("Left") else "center" if legend_choice.endswith("Center") else "right",
        )
        margin["b"] = 140

    fig.update_layout(
        title=dict(text=title if show_title else "", font=dict(color=text_color)),
        yaxis_title=t["y_axis"] if show_y else None,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color),
        legend=dict(font=dict(color=text_color), **legend),
        margin=margin,
        height=600,
    )

    fig.update_xaxes(showticklabels=show_x, tickfont=dict(color=text_color))
    fig.update_yaxes(showticklabels=show_y, tickfont=dict(color=text_color))

    return fig

# --------------------------------------------------
# Preview
# --------------------------------------------------
if st.button(t["preview"], type="primary"):
    for f in files:
        df = pd.read_csv(f)
        fig = build_fig(df, os.path.splitext(f.name)[0])
        st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# Export (RESTORED)
# --------------------------------------------------
if st.button(t["export_all"]):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for f in files:
            df = pd.read_csv(f)
            fig = build_fig(df, os.path.splitext(f.name)[0])

            filename = os.path.splitext(f.name)[0]
            if export_format == "HTML":
                html = fig.to_html()
                zipf.writestr(f"{filename}.html", html)
            else:
                img = fig.to_image(format=export_format.lower(), scale=2)
                zipf.writestr(f"{filename}.{export_format.lower()}", img)

    st.download_button(
        "⬇️ Download ZIP",
        zip_buffer.getvalue(),
        file_name=f"charts_{export_format.lower()}.zip",
        mime="application/zip",
    )
