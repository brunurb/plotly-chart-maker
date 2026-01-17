import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from io import BytesIO

st.set_page_config(page_title="ChartMaker", page_icon="📊", layout="wide")

st.title('📊 CSV to Chart Converter with Plotly')

# File uploader
uploaded_files = st.file_uploader("Choose CSV files", type="csv", accept_multiple_files=True)

if uploaded_files:
    # Chart type selection
    chart_types = ['Bar', 'Line', 'Scatter', 'Pie', 'Area']
    selected_chart_type = st.selectbox('Choose chart type', chart_types)

    # Color palette options
    color_palette_options = list(px.colors.qualitative.__dict__.keys())
    color_palette_options = [name for name in color_palette_options if not name.startswith('_') and isinstance(px.colors.qualitative.__dict__[name], list)]

    # Create a dictionary to map palette names to their colors
    palette_colors = {name: px.colors.qualitative.__dict__[name] for name in color_palette_options}

    # Display palette previews
    st.write("### 🎨 Color Palette Previews")

    # Use a selectbox for palette selection
    selected_palette_name = st.selectbox('Choose a color palette', options=color_palette_options)

    # Display the selected palette preview
    if selected_palette_name:
        colors = palette_colors[selected_palette_name]
        color_swatches = ''.join([f'<div style="display: inline-block; width: 12px; height: 12px; margin-right: 2px; background-color: {color}; border: 1px solid #ddd;"></div>' for color in colors])
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <span style="margin-right: 10px;">{selected_palette_name}</span>
            <div style="display: flex;">{color_swatches}</div>
        </div>
        """, unsafe_allow_html=True)

    # Show all palettes in an expander
    with st.expander("View All Palettes", expanded=False):
        for name in color_palette_options:
            colors = palette_colors[name]
            color_swatches = ''.join([f'<div style="display: inline-block; width: 12px; height: 12px; margin-right: 2px; background-color: {color}; border: 1px solid #ddd;"></div>' for color in colors])
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <span style="margin-right: 10px; width: 150px;">{name}</span>
                <div style="display: flex;">{color_swatches}</div>
            </div>
            """, unsafe_allow_html=True)

    # Options in columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### ⚙️ Display Options")
        show_x_label = st.checkbox('Show X-axis label', value=True)
        show_y_label = st.checkbox('Show Y-axis label', value=True)
        show_title = st.checkbox('Show Title', value=True)
        show_bar_values = st.checkbox('Show values on chart', value=True)
    
    with col2:
        st.write("### 🎨 Style Options")
        text_color = st.radio('Text color', ['Black', 'White'])
        bg_color = st.radio('Background color', ['White', 'Black', 'Transparent'])

    def get_fig(data, chart_type, palette_name, filename=None):
        colors = px.colors.qualitative.__dict__[palette_name]

        # Determine text color based on background
        if bg_color == 'White':
            effective_text_color = 'black'
        elif bg_color == 'Black':
            effective_text_color = 'white'
        else:  # Transparent
            effective_text_color = text_color.lower()

        # Create figure
        fig = go.Figure()

        # Check if data has the expected columns
        data_columns = [col for col in ['Sim', 'Não', 'Ns/Nr'] if col in data.columns]
        
        # If specific columns not found, use all numeric columns except first
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

        # Set background color and text color
        layout_config = {
            'legend': dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="right", x=1),
            'title_text': f'Responses by Concelhos - {os.path.splitext(filename)[0]}' if filename and show_title else ('Chart' if show_title else ''),
            'xaxis_title': data.columns[0] if show_x_label and len(data.columns) > 0 else '',
            'yaxis_title': 'Values' if show_y_label else '',
            'legend_title_text': '',
            'margin': dict(l=60, r=60, b=80, t=100, pad=10),
            'height': 600,
            'autosize': False
        }

        if bg_color == 'White':
            layout_config.update({
                'paper_bgcolor': 'white',
                'plot_bgcolor': 'white',
                'font': dict(color='black'),
                'xaxis': dict(
                    title=dict(font=dict(color='black')),
                    tickfont=dict(color='black'),
                    gridcolor='rgba(200, 200, 200, 0.3)',
                    showgrid=True
                ),
                'yaxis': dict(
                    title=dict(font=dict(color='black')),
                    tickfont=dict(color='black'),
                    gridcolor='rgba(200, 200, 200, 0.3)',
                    showgrid=True
                ),
                'legend': dict(font=dict(color='black'))
            })
        elif bg_color == 'Black':
            layout_config.update({
                'paper_bgcolor': 'black',
                'plot_bgcolor': 'black',
                'font': dict(color='white'),
                'xaxis': dict(
                    title=dict(font=dict(color='white')),
                    tickfont=dict(color='white'),
                    gridcolor='rgba(100, 100, 100, 0.5)',
                    showgrid=True
                ),
                'yaxis': dict(
                    title=dict(font=dict(color='white')),
                    tickfont=dict(color='white'),
                    gridcolor='rgba(100, 100, 100, 0.5)',
                    showgrid=True
                ),
                'legend': dict(font=dict(color='white'))
            })
        else:  # Transparent
            layout_config.update({
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'font': dict(color=effective_text_color),
                'xaxis': dict(
                    title=dict(font=dict(color=effective_text_color)),
                    tickfont=dict(color=effective_text_color),
                    gridcolor='rgba(200, 200, 200, 0.3)',
                    showgrid=True
                ),
                'yaxis': dict(
                    title=dict(font=dict(color=effective_text_color)),
                    tickfont=dict(color=effective_text_color),
                    gridcolor='rgba(200, 200, 200, 0.3)',
                    showgrid=True
                ),
                'legend': dict(font=dict(color=effective_text_color))
            })

        fig.update_layout(**layout_config)
        return fig

    # Preview button
    if st.button('🔍 Preview Charts', type="primary"):
        for uploaded_file in uploaded_files:
            try:
                # Try different encodings
                try:
                    data = pd.read_csv(uploaded_file, encoding='utf-8')
                except:
                    uploaded_file.seek(0)
                    data = pd.read_csv(uploaded_file, encoding='latin-1')
                
                st.write(f"### 📄 {uploaded_file.name}")
                with st.expander("View data"):
                    st.dataframe(data.head())

                fig = get_fig(data, selected_chart_type, selected_palette_name, uploaded_file.name)
                
                # Display chart with config for download
                st.plotly_chart(
                    fig, 
                    use_container_width=True, 
                    key=f"chart_{uploaded_file.name}",
                    config={
                        'toImageButtonOptions': {
                            'format': 'png',
                            'filename': f'chart_{os.path.splitext(uploaded_file.name)[0]}',
                            'height': 600,
                            'width': 1200,
                            'scale': 2
                        },
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['pan2d', 'lasso2d']
                    }
                )
                
                st.info("💡 Use the 📷 camera icon in the chart toolbar above to download as PNG")
                
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")

    # Add a helpful note
    st.markdown("---")
    st.markdown("""
    ### 📝 How to use:
    1. Upload one or more CSV files
    2. Choose your chart type and color palette
    3. Customize display and style options
    4. Click **Preview Charts** to see your visualizations
    5. Use the 📷 **camera icon** in each chart's toolbar to download
    
    ### 💡 Tips:
    - Your CSV should have column headers
    - First column will be used as X-axis labels
    - Numeric columns will be plotted
    - Hover over charts for interactive details
    """)
