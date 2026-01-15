import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import tempfile
import time
import io
import base64

# Set page config for better display
st.set_page_config(
    page_title="CSV to Chart Converter",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title('CSV to Chart Converter with Plotly')

# File uploader
uploaded_files = st.file_uploader(
    "Choose CSV files",
    type="csv",
    accept_multiple_files=True,
    help="Upload one or more CSV files to visualize"
)

if uploaded_files:
    try:
        # Chart type selection
        chart_types = ['Bar', 'Line', 'Scatter', 'Pie', 'Area']
        selected_chart_type = st.selectbox('Choose chart type', chart_types)

        # Color palette options - using a fixed set to avoid issues
        color_palette_options = [
            'Plotly', 'G10', 'T10', 'Alphabet', 'Dark24', 'Light24'
        ]

        # Use a selectbox for palette selection
        selected_palette_name = st.selectbox('Choose a color palette', options=color_palette_options)

        # Display options
        col1, col2 = st.columns(2)
        with col1:
            show_x_label = st.checkbox('Show X-axis label', value=True)
            show_bar_values = st.checkbox('Show bar values', value=True)
        with col2:
            show_y_label = st.checkbox('Show Y-axis label', value=True)
            show_title = st.checkbox('Show Title', value=True)

        # Background and text options
        text_color = st.radio('Text color', ['Black', 'White'])
        bg_color = st.radio('Background color', ['White', 'Black'])

        # Export options
        export_format = st.selectbox('Export format', ['PNG', 'JPEG'])

        def get_fig(data, chart_type, palette_name):
            # Get colors from the selected palette
            if palette_name == 'Plotly':
                colors = px.colors.qualitative.Plotly
            elif palette_name == 'G10':
                colors = px.colors.qualitative.G10
            elif palette_name == 'T10':
                colors = px.colors.qualitative.T10
            elif palette_name == 'Alphabet':
                colors = px.colors.qualitative.Alphabet
            elif palette_name == 'Dark24':
                colors = px.colors.qualitative.Dark24
            else:  # Light24
                colors = px.colors.qualitative.Light24

            # Determine text color based on background
            effective_text_color = 'white' if bg_color == 'Black' else 'black'

            # Create figure
            fig = go.Figure()

            # Check if required columns exist
            required_cols = ['concelhos', 'Sim', 'Não', 'Ns/Nr']
            for col in required_cols:
                if col not in data.columns:
                    st.warning(f"Column '{col}' not found in the CSV file. Using first 4 columns instead.")
                    # Use first 4 columns if required columns don't exist
                    if len(data.columns) >= 4:
                        data.columns = ['concelhos'] + list(data.columns[1:4])
                    else:
                        st.error("CSV file doesn't have enough columns (need at least 4)")
                        return None
                    break

            if chart_type == 'Bar':
                for i, col in enumerate(['Sim', 'Não', 'Ns/Nr']):
                    if col in data.columns:
                        fig.add_trace(go.Bar(
                            x=data['concelhos'],
                            y=data[col],
                            name=col,
                            marker_color=colors[i % len(colors)],
                            text=data[col] if show_bar_values else None,
                            textposition='outside' if show_bar_values else None,
                            textfont=dict(color=effective_text_color)
                        ))
                fig.update_layout(barmode='group')

            elif chart_type == 'Line':
                for i, col in enumerate(['Sim', 'Não', 'Ns/Nr']):
                    if col in data.columns:
                        fig.add_trace(go.Scatter(
                            x=data['concelhos'],
                            y=data[col],
                            name=col,
                            mode='lines+markers',
                            line=dict(color=colors[i % len(colors)]),
                            text=data[col] if show_bar_values else None,
                            textposition='top center' if show_bar_values else None,
                            textfont=dict(color=effective_text_color)
                        ))

            elif chart_type == 'Scatter':
                for i, col in enumerate(['Sim', 'Não', 'Ns/Nr']):
                    if col in data.columns:
                        fig.add_trace(go.Scatter(
                            x=data['concelhos'],
                            y=data[col],
                            name=col,
                            mode='markers',
                            marker=dict(color=colors[i % len(colors)]),
                            text=data[col] if show_bar_values else None,
                            textposition='top center' if show_bar_values else None,
                            textfont=dict(color=effective_text_color)
                        ))

            elif chart_type == 'Pie':
                if len(data.columns) > 1:
                    fig.add_trace(go.Pie(
                        labels=data.columns[1:4],  # Use first 3 data columns
                        values=data.iloc[0, 1:4],
                        marker=dict(colors=colors[:3]),
                        textinfo='label+percent' if show_bar_values else 'label',
                        textfont=dict(color=effective_text_color)
                    ))

            elif chart_type == 'Area':
                for i, col in enumerate(['Sim', 'Não', 'Ns/Nr']):
                    if col in data.columns:
                        fig.add_trace(go.Scatter(
                            x=data['concelhos'],
                            y=data[col],
                            name=col,
                            stackgroup='one',
                            fillcolor=colors[i % len(colors)],
                            line=dict(color=colors[i % len(colors)])
                        ))

            # Set background and layout
            fig.update_layout(
                paper_bgcolor='black' if bg_color == 'Black' else 'white',
                plot_bgcolor='black' if bg_color == 'Black' else 'white',
                font=dict(color=effective_text_color),
                xaxis=dict(
                    title=dict(font=dict(color=effective_text_color)) if show_x_label else None,
                    tickfont=dict(color=effective_text_color),
                    gridcolor='rgba(200, 200, 200, 0.3)' if bg_color == 'White' else 'rgba(100, 100, 100, 0.5)',
                    showgrid=True,
                ),
                yaxis=dict(
                    title=dict(font=dict(color=effective_text_color)) if show_y_label else None,
                    tickfont=dict(color=effective_text_color),
                    gridcolor='rgba(200, 200, 200, 0.3)' if bg_color == 'White' else 'rgba(100, 100, 100, 0.5)',
                    showgrid=True,
                ),
                legend=dict(
                    font=dict(color=effective_text_color),
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="right",
                    x=1
                ),
                margin=dict(l=50, r=50, b=80, t=100, pad=10),
                height=600,
                title_text=f'Responses by Concelhos' if show_title else '',
            )

            return fig

        if st.button('Preview Charts'):
            for uploaded_file in uploaded_files:
                try:
                    with st.spinner(f'Processing {uploaded_file.name}...'):
                        # Read CSV file
                        data = pd.read_csv(uploaded_file)

                        # Show data preview
                        with st.expander(f"Data Preview: {uploaded_file.name}"):
                            st.dataframe(data.head())

                        # Generate and display chart
                        fig = get_fig(data, selected_chart_type, selected_palette_name)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True, key=f"chart_{uploaded_file.name}")
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")

        if st.button('Export Current Chart'):
            for uploaded_file in uploaded_files:
                try:
                    with st.spinner(f'Exporting {uploaded_file.name}...'):
                        data = pd.read_csv(uploaded_file)
                        fig = get_fig(data, selected_chart_type, selected_palette_name)

                        if fig:
                            # Convert figure to image
                            img_bytes = fig.to_image(format=export_format.lower())

                            # Create download button
                            st.download_button(
                                label=f"Download {uploaded_file.name} as {export_format}",
                                data=img_bytes,
                                file_name=f"chart_{os.path.splitext(uploaded_file.name)[0]}.{export_format.lower()}",
                                mime=f"image/{export_format.lower()}",
                                key=f"download_{uploaded_file.name}"
                            )
                except Exception as e:
                    st.error(f"Error exporting {uploaded_file.name}: {str(e)}")

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

