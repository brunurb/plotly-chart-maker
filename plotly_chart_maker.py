import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ----------------------------
# Translations
# ----------------------------
TRANSLATIONS = {
    "en": {
        "title": "📊 CSV to Chart Converter with Plotly",
        "upload": "Choose CSV files",
        "chart_type": "Choose chart type",
        "display_options": "⚙️ Display Options",
        "style_options": "🎨 Style Options",
        "show_x": "Show X-axis label",
        "show_y": "Show Y-axis label",
        "show_title": "Show title",
        "show_values": "Show values",
        "text_color": "Text color",
        "bg_color": "Background color",
        "legend": "Legend placement",
        "preview": "Preview charts",
        "black": "Black",
        "white": "White",
        "transparent": "Transparent",
        "y_axis": "Values",
    },
    "pt": {
        "title": "📊 Conversor CSV para Gráficos com Plotly",
        "upload": "Selecionar ficheiros CSV",
        "chart_type": "Tipo de gráfico",
        "display_options": "⚙️ Opções de Visualização",
        "style_options": "🎨 Opções de Estilo",
        "show_x": "Mostrar eixo X",
        "show_y": "Mostrar eixo Y",
        "show_title": "Mostrar título",
        "show_values": "Mostrar valores",
        "text_color": "Cor do texto",
        "bg_color": "Cor de fundo",
        "legend": "Posição da legenda",
        "preview": "Pré-visualizar gráficos",
        "black": "Preto",
        "white": "Branco",
        "transparent": "Transparente",
        "y_axis": "Valores",
    },
}

CHART_TYPES = {
    "en": ["Bar", "Line", "Scatter", "Pie", "Area"],
    "pt": ["Barras", "Linha", "Dispersão", "Circular", "Área"],
}

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="ChartMaker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------
# Sidebar (language restored)
# ----------------------------
with st.sidebar:
    st.title("🌐 Language / Idioma")
    language = st.radio("", ["en", "pt"], index=0)
    st.markdown("---")
    st.markdown("**ChartMaker**")

t = TRANSLATIONS[language]

# ----------------------------
# Compact header (correct)
# ----------------------------
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

# ----------------------------
# File upload
# ----------------------------
files = st.file_uploader(t["upload"], type="csv", accept_multiple_files=True)

if files:
    chart_type = st.selectbox(t["chart_type"], CHART_TYPES[language])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### {t['display_options']}")
        show_x = st.checkbox(t["show_x"], True)
        show_y = st.checkbox(t["show_y"], True)
        show_title = st.checkbox(t["show_title"], True)
        show_values = st.checkbox(t["show_values"], False)

    with col2:
        st.markdown(f"### {t['style_options']}")
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

    # ----------------------------
    # Chart builder (fully corrected)
    # ----------------------------
    def build_fig(df, name):
        numeric = df.select_dtypes("number").columns
        fig = go.Figure()

        for col in numeric:
            fig.add_bar(
                x=df.iloc[:, 0],
                y=df[col],
                name=col,
                text=df[col] if show_values else None,
            )

        legend = {}
        margin = dict(l=40, r=40, t=50, b=40)

        if legend_choice.startswith("Right"):
            legend.update(
                orientation="v",
                x=1.02,
                xanchor="left",
                y=1 if legend_choice.endswith("Top") else 0.5 if legend_choice.endswith("Center") else 0,
                yanchor="top" if legend_choice.endswith("Top") else "middle" if legend_choice.endswith("Center") else "bottom",
            )
            margin["r"] = 160

        else:
            legend.update(
                orientation="h",
                y=-0.25,
                yanchor="top",
                x=0 if legend_choice.endswith("Left") else 0.5 if legend_choice.endswith("Center") else 1,
                xanchor="left" if legend_choice.endswith("Left") else "center" if legend_choice.endswith("Center") else "right",
            )
            margin["b"] = 120

        fig.update_layout(
            title=name if show_title else None,
            yaxis_title=t["y_axis"] if show_y else None,
            legend=legend,
            margin=margin,
            paper_bgcolor=bg_color,
            plot_bgcolor=bg_color,
            font=dict(color=text_color),
            height=600,
        )

        return fig

    # ----------------------------
    # Preview
    # ----------------------------
    if st.button(t["preview"], type="primary"):
        for f in files:
            df = pd.read_csv(f)
            fig = build_fig(df, os.path.splitext(f.name)[0])
            st.plotly_chart(fig, use_container_width=True)
