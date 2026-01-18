import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from io import BytesIO
import zipfile

# ---------------------
# Language translations
# ---------------------
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

st.set_page_config(page_title="ChartMaker", page_icon="📊", layout="wide")

# Sidebar language
with st.sidebar:
    st.markdown("## 🌐 Language / Idioma")
    language = st.radio("", options=['en','pt'],
                        format_func=lambda x: '🇬🇧 English' if x=='en' else '🇵🇹 Português', index=0)
    st.markdown("---")
    st.markdown("### ChartMaker")
    st.markdown("v1.0")

t = TRANSLATIONS[language]

# Header
st.markdown(
f"""
<div style="display:flex; align-items:center; justify-content:space-between;">
<h1 style="margin:0; font-size:28px;">{t['title']}</h1>
<a href="https://brunurb.github.io/" target="_blank" style="display:flex; align-items:center; text-decoration:none;">
<img src="https://avatars.githubusercontent.com/u/8878983?s=32" width="24" height="24" style="border-radius:50%; margin-right:4px;">
<span style="font-size:0.9em; color:#666;">by brunurb</span>
</a>
</div>
""", unsafe_allow_html=True)

# File uploader
uploaded_files = st.file_uploader(t['upload'], type="csv", accept_multiple_files=True)

if uploaded_files:
    # Chart type selection
    chart_types_display = CHART_TYPES[language]
    selected_chart_type_display = st.selectbox(t['chart_type'], chart_types_display)
    selected_chart_type = CHART_TYPE_MAP.get(selected_chart_type_display, selected_chart_type_display) if language=='pt' else selected_chart_type_display

    # Palette selection
    color_palette_options = [name for name in px.colors.qualitative.__dict__.keys() 
                             if not name.startswith('_') and isinstance(px.colors.qualitative.__dict__[name], list)]
    palette_colors = {name:px.colors.qualitative.__dict__[name] for name in color_palette_options}
    st.write(f"### {t['color_palette']}")
    selected_palette_name = st.selectbox(t['choose_palette'], options=color_palette_options)

    if selected_palette_name:
        colors = palette_colors[selected_palette_name]
        color_swatches = ''.join([f'<div style="display:inline-block;width:12px;height:12px;margin-right:2px;background-color:{c};border:1px solid #ddd;"></div>' for c in colors])
        st.markdown(f"<div style='display:flex; align-items:center; margin-bottom:10px;'><span style='margin-right:10px;'>{selected_palette_name}</span><div style='display:flex;'>{color_swatches}</div></div>", unsafe_allow_html=True)

    # All palettes in expander
    with st.expander(t['view_all_palettes'], expanded=False):
        for name in color_palette_options:
            colors = palette_colors[name]
            color_swatches = ''.join([f'<div style="display:inline-block;width:12px;height:12px;margin-right:2px;background-color:{c};border:1px solid #ddd;"></div>' for c in colors])
            st.markdown(f"<div style='display:flex; align-items:center; margin-bottom:5px;'><span style='margin-right:10px; width:150px;'>{name}</span><div style='display:flex;'>{color_swatches}</div></div>", unsafe_allow_html=True)

    # Display and style options
    col1,col2 = st.columns(2)
    with col1:
        st.write(f"### {t['display_options']}")
        show_x_label = st.checkbox(t['show_x_label'], value=True)
        show_y_label = st.checkbox(t['show_y_label'], value=True)
        show_title = st.checkbox(t['show_title'], value=True)
        show_bar_values = st.checkbox(t['show_values'], value=True)
        legend_choice = st.selectbox(t['legend_position'],
                                     ['Right Top','Right Center','Right Bottom','Bottom Left','Bottom Center','Bottom Right'])
    with col2:
        st.write(f"### {t['style_options']}")
        text_color_display = st.radio(t['text_color'], [t['black'], t['white']])
        text_color = 'Black' if text_color_display==t['black'] else 'White'
        bg_color_display = st.radio(t['bg_color'], [t['white'], t['black'], t['transparent']])
        bg_color = 'White' if bg_color_display=='White' else 'Black' if bg_color_display=='Black' else 'Transparent'

    # Export format
    st.write(f"### {t['export_options']}")
    export_format = st.selectbox(t['export_format'], ['PNG','SVG','PDF','HTML'])

    # ---------------------
    # get_fig function
    # ---------------------
    def get_fig(data, chart_type, palette_name, filename=None):
        colors = px.colors.qualitative.__dict__[palette_name]
        effective_text_color = 'black' if text_color=='Black' else 'white'
        fig = go.Figure()
        data_columns = [col for col in ['Sim','Não','Ns/Nr'] if col in data.columns]
        if not data_columns:
            data_columns = data.select_dtypes(include=['number']).columns.tolist()
        # --- add traces ---
        if chart_type=='Bar':
            for i,col in enumerate(data_columns):
                fig.add_trace(go.Bar(
                    x=data.iloc[:,0] if len(data.columns)>0 else data.index,
                    y=data[col],
                    name=col,
                    marker_color=colors[i % len(colors)],
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
                    line=dict(color=colors[i % len(colors)]),
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
                    marker=dict(color=colors[i % len(colors)], size=10),
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
                    fillcolor=colors[i % len(colors)],
                    line=dict(color=colors[i % len(colors)])
                ))
        # --- layout ---
        layout_config = dict(
            title=dict(text=t['chart_title'].format(name=os.path.splitext(filename)[0]) if filename and show_title else (t['chart_title_default'] if show_title else ''),
                       font=dict(color=effective_text_color)),
            xaxis=dict(title=dict(text=data.columns[0] if show_x_label else '', font=dict(color=effective_text_color)),
                       tickfont=dict(color=effective_text_color),
                       gridcolor='rgba(200,200,200,0.3)', showgrid=True),
            yaxis=dict(title=dict(text=t['y_axis'] if show_y_label else '', font=dict(color=effective_text_color)),
                       tickfont=dict(color=effective_text_color),
                       gridcolor='rgba(200,200,200,0.3)', showgrid=True),
            legend=dict(font=dict(color=effective_text_color)),
            paper_bgcolor='white' if bg_color=='White' else 'black' if bg_color=='Black' else 'rgba(0,0,0,0)',
            plot_bgcolor='white' if bg_color=='White' else 'black' if bg_color=='Black' else 'rgba(0,0,0,0)',
            margin=dict(l=60,r=60,t=100,b=80),
            height=600,
            width=1200,
            autosize=False
        )

        # --- Legend placement outside ---
        if legend_choice in ['Right Top','Right Center','Right Bottom']:
            y_pos = 1 if legend_choice.endswith('Top') else 0.5 if legend_choice.endswith('Center') else 0
            layout_config['legend'].update(
                orientation='v', x=1.02, xanchor='left',
                y=y_pos,
                yanchor='top' if legend_choice.endswith('Top') else 'middle' if legend_choice.endswith('Center') else 'bottom',
                font=dict(color=effective_text_color)
            )
            layout_config['margin']['r']=150
        elif legend_choice in ['Bottom Left','Bottom Center','Bottom Right']:
            x_pos = 0 if legend_choice.endswith('Left') else 0.5 if legend_choice.endswith('Center') else 1
            layout_config['legend'].update(
                orientation='h', x=x_pos,
                xanchor='left' if legend_choice.endswith('Left') else 'center' if legend_choice.endswith('Center') else 'right',
                y=-0.25, yanchor='top',
                font=dict(color=effective_text_color)
            )
            layout_config['margin']['b']=120
            layout_config['height']+=50

        fig.update_layout(**layout_config)
        return fig

    # ---------------------
    # Preview Charts
    # ---------------------
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

                fig = get_fig(data, selected_chart_type, selected_palette_name, uploaded_file.name)
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{uploaded_file.name}")
            except Exception as e:
                st.error(t['error_processing'].format(filename=uploaded_file.name,error=str(e)))

    # ---------------------
    # Export All Charts
    # ---------------------
    if st.button(t['export_all'], type="secondary"):
        try:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer,'w',zipfile.ZIP_DEFLATED) as zip_file:
                for uploaded_file in uploaded_files:
                    try:
                        try:
                            data = pd.read_csv(uploaded_file, encoding='utf-8')
                        except:
                            uploaded_file.seek(0)
                            data = pd.read_csv(uploaded_file, encoding='latin-1')
                        fig = get_fig(data, selected_chart_type, selected_palette_name, uploaded_file.name)
                        base_filename = os.path.splitext(uploaded_file.name)[0]
                        if export_format=='HTML':
                            html_str = fig.to_html(include_plotlyjs='cdn')
                            zip_file.writestr(f"{base_filename}.html", html_str.encode('utf-8'))
                        else:
                            img_bytes = fig.to_image(format=export_format.lower(), width=1200, height=600, scale=2)
                            zip_file.writestr(f"{base_filename}.{export_format.lower()}", img_bytes)
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

    # ---------------------
    # Export Single Chart
    # ---------------------
    st.write("---")
    st.write(f"### {t['export_individual']}")
    for uploaded_file in uploaded_files:
        try:
            try:
                data = pd.read_csv(uploaded_file, encoding='utf-8')
            except:
                uploaded_file.seek(0)
                data = pd.read_csv(uploaded_file, encoding='latin-1')

            fig = get_fig(data, selected_chart_type, selected_palette_name, uploaded_file.name)
            base_filename = os.path.splitext(uploaded_file.name)[0]
            if export_format=='HTML':
                file_data = fig.to_html(include_plotlyjs='cdn').encode('utf-8')
                mime_type = 'text/html'
                file_ext='html'
            elif export_format=='SVG':
                file_data = fig.to_image(format='svg', width=1200, height=600, scale=2)
                mime_type='image/svg+xml'
                file_ext='svg'
            elif export_format=='PDF':
                file_data = fig.to_image(format='pdf', width=1200, height=600, scale=2)
                mime_type='application/pdf'
                file_ext='pdf'
            else:
                file_data = fig.to_image(format='png', width=1200, height=600, scale=2)
                mime_type='image/png'
                file_ext='png'

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
