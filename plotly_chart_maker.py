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
        'legend_position': 'Legend Position',
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
        'legend_position': 'Posição da Legenda',
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

CHART_TYPES = {'en':['Bar','Line','Scatter','Pie','Area'],'pt':['Barras','Linha','Dispersão','Circular','Área']}
CHART_TYPE_MAP = {'Barras':'Bar','Linha':'Line','Dispersão':'Scatter','Circular':'Pie','Área':'Area'}
LEGEND_OPTIONS = ['Right Top','Right Center','Right Bottom','Bottom Left','Bottom Center','Bottom Right']

st.set_page_config(page_title="ChartMaker", page_icon="📊", layout="wide")

# ----------------------------
# Sidebar language selector
# ----------------------------
with st.sidebar:
    st.title("🌐 Language / Idioma")
    language = st.radio("", ['en','pt'],
                        format_func=lambda x: '🇬🇧 English' if x=='en' else '🇵🇹 Português', index=0)
    st.markdown("---")
    st.markdown("### ChartMaker")
    st.markdown("v1.0")

t = TRANSLATIONS[language]

# ----------------------------
# Header with avatar
# ----------------------------
st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:center;">
    <h1 style="margin:0; font-size:32px;">{t['title']}</h1>
    <div style="display:flex; align-items:center; gap:5px;">
        <a href="https://brunurb.github.io/" target="_blank">
            <img src="https://avatars.githubusercontent.com/u/8878983?s=32" width="24" height="24" style="border-radius:50%;">
        </a>
        <span style="font-size:0.9em; color:#666;">by brunurb</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# File uploader
# ----------------------------
uploaded_files = st.file_uploader(t['upload'], type="csv", accept_multiple_files=True)

# ----------------------------
# Legend placement map
# ----------------------------
legend_map = {
    'Right Top': dict(orientation="v", x=1, y=1, xanchor="right", yanchor="top"),
    'Right Center': dict(orientation="v", x=1, y=0.5, xanchor="right", yanchor="middle"),
    'Right Bottom': dict(orientation="v", x=1, y=0, xanchor="right", yanchor="bottom"),
    'Bottom Left': dict(orientation="h", x=0, y=-0.2, xanchor="left", yanchor="bottom"),
    'Bottom Center': dict(orientation="h", x=0.5, y=-0.2, xanchor="center", yanchor="bottom"),
    'Bottom Right': dict(orientation="h", x=1, y=-0.2, xanchor="right", yanchor="bottom")
}

# ----------------------------
# Chart function
# ----------------------------
def get_fig(data, chart_type, palette_name, filename=None, x_label=None, y_label=None, legend_placement='Right Top'):
    colors = px.colors.qualitative.__dict__[palette_name]
    if x_label is None or x_label.strip()=='':
        x_label = data.columns[0] if len(data.columns)>0 else t['x_axis']
    if y_label is None or y_label.strip()=='':
        y_label = t['y_axis']
    effective_text_color = {'White':'black','Black':'white'}.get(bg_color,text_color.lower())
    fig = go.Figure()
    data_columns = [col for col in ['Sim','Não','Ns/Nr'] if col in data.columns]
    if not data_columns:
        data_columns = data.select_dtypes(include=['number']).columns.tolist()

    if chart_type=='Bar':
        for i,col in enumerate(data_columns):
            fig.add_trace(go.Bar(
                x=data.iloc[:,0] if len(data.columns)>0 else data.index,
                y=data[col],
                name=col,
                marker_color=colors[i%len(colors)],
                text=data[col] if show_bar_values else None,
                textposition='outside' if show_bar_values else None,
                textfont=dict(color=effective_text_color)
            ))
        fig.update_layout(barmode='group')
    elif chart_type=='Line':
        for i,col in enumerate(data_columns):
            fig.add_trace(go.Scatter(
                x=data.iloc[:,0] if len(data.columns)>0 else data.index,
                y=data[col],
                name=col,
                mode='lines+markers',
                line=dict(color=colors[i%len(colors)]),
                text=data[col] if show_bar_values else None,
                textposition='top center' if show_bar_values else None,
                textfont=dict(color=effective_text_color)
            ))
    elif chart_type=='Scatter':
        for i,col in enumerate(data_columns):
            fig.add_trace(go.Scatter(
                x=data.iloc[:,0] if len(data.columns)>0 else data.index,
                y=data[col],
                name=col,
                mode='markers',
                marker=dict(color=colors[i%len(colors)], size=10),
                text=data[col] if show_bar_values else None,
                textposition='top center' if show_bar_values else None,
                textfont=dict(color=effective_text_color)
            ))
    elif chart_type=='Pie':
        fig.add_trace(go.Pie(
            labels=data_columns,
            values=data[data_columns].iloc[0] if len(data)>0 else [],
            marker=dict(colors=colors[:len(data_columns)]),
            textinfo='label+percent' if show_bar_values else 'label',
            textfont=dict(color=effective_text_color)
        ))
    elif chart_type=='Area':
        for i,col in enumerate(data_columns):
            fig.add_trace(go.Scatter(
                x=data.iloc[:,0] if len(data.columns)>0 else data.index,
                y=data[col],
                name=col,
                stackgroup='one',
                fillcolor=colors[i%len(colors)],
                line=dict(color=colors[i%len(colors)])
            ))

    layout_config = dict(
        legend=legend_map[legend_placement],
        title_text=t['chart_title'].format(name=os.path.splitext(filename)[0]) if filename and show_title else (t['chart_title_default'] if show_title else ''),
        xaxis_title=x_label if show_x_label else '',
        yaxis_title=y_label if show_y_label else '',
        margin=dict(l=80,r=80,t=100,b=100,pad=10),
        height=600,width=1200,autosize=False
    )

    if bg_color=='White':
        layout_config.update({'paper_bgcolor':'white','plot_bgcolor':'white','font':dict(color='black')})
    elif bg_color=='Black':
        layout_config.update({'paper_bgcolor':'black','plot_bgcolor':'black','font':dict(color='white')})
    else:
        layout_config.update({'paper_bgcolor':'rgba(0,0,0,0)','plot_bgcolor':'rgba(0,0,0,0)','font':dict(color=effective_text_color)})

    fig.update_layout(**layout_config)
    return fig

# ----------------------------
# Main app logic
# ----------------------------
if uploaded_files:
    # Chart type
    selected_chart_type_display = st.selectbox(t['chart_type'], CHART_TYPES[language])
    selected_chart_type = CHART_TYPE_MAP.get(selected_chart_type_display, selected_chart_type_display)

    # Palette
    color_palette_options = [k for k in px.colors.qualitative.__dict__.keys() if not k.startswith('_') and isinstance(px.colors.qualitative.__dict__[k], list)]
    palette_colors = {name:px.colors.qualitative.__dict__[name] for name in color_palette_options}
    selected_palette_name = st.selectbox(t['choose_palette'], options=color_palette_options)
    colors = palette_colors[selected_palette_name]
    swatches = ''.join([f'<div style="width:12px;height:12px;margin-right:2px;background:{c};border:1px solid #ddd;"></div>' for c in colors])
    st.markdown(f'<div style="display:flex;align-items:center;margin-bottom:10px;">{swatches}</div>', unsafe_allow_html=True)

    # Legend placement
    legend_placement = st.selectbox(t['legend_position'], LEGEND_OPTIONS)

    # Display options
    show_x_label = st.checkbox(t['show_x_label'], value=True)
    show_y_label = st.checkbox(t['show_y_label'], value=True)
    show_title = st.checkbox(t['show_title'], value=True)
    show_bar_values = st.checkbox(t['show_values'], value=True)

    # Style
    text_color_options = [t['black'], t['white']]
    text_color_display = st.radio(t['text_color'], text_color_options)
    text_color = 'Black' if text_color_display==t['black'] else 'White'

    bg_color_options = [t['white'], t['black'], t['transparent']]
    bg_color_display = st.radio(t['bg_color'], bg_color_options)
    if bg_color_display == t['white']:
        bg_color = 'White'
    elif bg_color_display == t['black']:
        bg_color = 'Black'
    else:
        bg_color = 'Transparent'

    export_format = st.selectbox(t['export_format'], ['PNG','SVG','PDF','HTML'])

    # Custom X/Y labels
    try:
        df_temp = pd.read_csv(uploaded_files[0], nrows=1)
        default_x_label = df_temp.columns[0] if len(df_temp.columns)>0 else t['x_axis']
    except:
        default_x_label = t['x_axis']
    custom_x_label = st.text_input("X-axis label", value=default_x_label)
    custom_y_label = st.text_input("Y-axis label", value=t['y_axis'])

    # ----------------------------
    # Preview charts
    # ----------------------------
    if st.button(t['preview_charts'], type="primary"):
        for uploaded_file in uploaded_files:
            try:
                try:
                    data = pd.read_csv(uploaded_file, encoding='utf-8')
                except:
                    uploaded_file.seek(0)
                    data = pd.read_csv(uploaded_file, encoding='latin-1')
                st.write(f"### {t['data_preview'].format(filename=uploaded_file.name)}")
                with st.expander(t['view_data']):
                    st.dataframe(data.head())
                fig = get_fig(data, selected_chart_type, selected_palette_name,
                              uploaded_file.name, x_label=custom_x_label, y_label=custom_y_label,
                              legend_placement=legend_placement)
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{uploaded_file.name}")
            except Exception as e:
                st.error(t['error_processing'].format(filename=uploaded_file.name, error=str(e)))

    # ----------------------------
    # Export all charts
    # ----------------------------
    if st.button(t['export_all'], type="secondary"):
        try:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for uploaded_file in uploaded_files:
                    try:
                        try:
                            data = pd.read_csv(uploaded_file, encoding='utf-8')
                        except:
                            uploaded_file.seek(0)
                            data = pd.read_csv(uploaded_file, encoding='latin-1')
                        fig = get_fig(data, selected_chart_type, selected_palette_name,
                                      uploaded_file.name, x_label=custom_x_label, y_label=custom_y_label,
                                      legend_placement=legend_placement)
                        base_filename = os.path.splitext(uploaded_file.name)[0]
                        if export_format=='HTML':
                            html_str = fig.to_html(include_plotlyjs='cdn')
                            zip_file.writestr(f"{base_filename}.html", html_str.encode('utf-8'))
                        elif export_format=='SVG':
                            svg_bytes = fig.to_image(format='svg', width=1200, height=600, scale=2)
                            zip_file.writestr(f"{base_filename}.svg", svg_bytes)
                        elif export_format=='PDF':
                            pdf_bytes = fig.to_image(format='pdf', width=1200, height=600, scale=2)
                            zip_file.writestr(f"{base_filename}.pdf", pdf_bytes)
                        else:
                            png_bytes = fig.to_image(format='png', width=1200, height=600, scale=2)
                            zip_file.writestr(f"{base_filename}.png", png_bytes)
                    except Exception as e:
                        st.warning(t['skipped'].format(filename=uploaded_file.name,error=str(e)))
            zip_buffer.seek(0)
            st.download_button(
                t['download_all'].format(format=export_format),
                zip_buffer,
                file_name=f"charts_{export_format.lower()}.zip",
                mime="application/zip",
                type="primary"
            )
            st.success(t['charts_ready'].format(count=len(uploaded_files)))
        except Exception as e:
            st.error(t['export_failed'].format(error=str(e)))
        st.info(t['try_individual'])

    # ----------------------------
    # Export individual charts
    # ----------------------------
    st.write("---")
    st.write(f"### {t['export_individual']}")
    for uploaded_file in uploaded_files:
        try:
            try:
                data = pd.read_csv(uploaded_file, encoding='utf-8')
            except:
                uploaded_file.seek(0)
                data = pd.read_csv(uploaded_file, encoding='latin-1')
            fig = get_fig(data, selected_chart_type, selected_palette_name,
                          uploaded_file.name, x_label=custom_x_label, y_label=custom_y_label,
                          legend_placement=legend_placement)
            base_filename = os.path.splitext(uploaded_file.name)[0]
            if export_format=='HTML':
                file_data = fig.to_html(include_plotlyjs='cdn').encode('utf-8')
                mime_type = 'text/html'
                file_ext = 'html'
            elif export_format=='SVG':
                file_data = fig.to_image(format='svg', width=1200, height=600, scale=2)
                mime_type = 'image/svg+xml'
                file_ext = 'svg'
            elif export_format=='PDF':
                file_data = fig.to_image(format='pdf', width=1200, height=600, scale=2)
                mime_type = 'application/pdf'
                file_ext = 'pdf'
            else:
                file_data = fig.to_image(format='png', width=1200, height=600, scale=2)
                mime_type = 'image/png'
                file_ext = 'png'

            st.download_button(
                t['download_single'].format(filename=uploaded_file.name,format=export_format),
                file_data,
                file_name=f"{base_filename}.{file_ext}",
                mime=mime_type,
                key=f"download_{uploaded_file.name}_{export_format}"
            )
        except Exception as e:
            st.error(t['error_exporting'].format(filename=uploaded_file.name,error=str(e)))

    st.markdown("---")
    st.markdown(f"### {t['how_to_use']}")
    st.markdown(t['instructions'])
    st.markdown(f"### {t['format_guide']}")
    st.markdown(t['format_info'])
