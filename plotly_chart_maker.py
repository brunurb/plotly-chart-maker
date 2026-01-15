import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import tempfile
from io import BytesIO, StringIO
import time

st.title('CSV to Chart Converter with Plotly')

# Create a temporary directory for output
output_dir = tempfile.mkdtemp()
st.write(f"Temporary output directory: {output_dir}")

# File uploader - modified for cloud environment
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

        # Color palette options
        color_palette_options = list(px.colors.qualitative.__dict__.keys())
        color_palette_options = [
            name for name in color_palette_options
            if not name.startswith('_') and isinstance(px.colors.qualitative.__dict__[name], list)
        ]

        # Create a dictionary to map palette names to their colors
        palette_colors = {name: px.colors.qualitative.__dict__[name] for name in color_palette_options}

        # Display palette previews in a vertical list
        st.write("### Color Palette Previews")

        # Use a selectbox for palette selection
        selected_palette_name = st.selectbox('Choose a color palette', options=color_palette_options)

        # Display the selected palette preview
        if selected_palette_name:
            colors = palette_colors[selected_palette_name]
            color_swatches = ''.join([
                f'<div style="display: inline-block; width: 12px; height: 12px; margin-right: 2px; '
                f'background-color: {color}; border: 1px solid #ddd;"></div>'
                for color in colors
            ])
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
                color_swatches = ''.join([
                    f'<div style="display: inline-block; width: 12px; height: 12px; margin-right: 2px; '
                    f'background-color: {color}; border: 1px solid #ddd;"></div>'
                    for color in colors
                ])
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <span style="margin-right: 10px; width: 150px;">{name}</span>
                    <div style="display: flex;">{color_swatches}</div>
                </div>
                """, unsafe_allow_html=True)

        # Legend positioning options
        legend_positions = ['top right', 'top left', 'bottom left', 'bottom right']
        selected_legend_position = st.selectbox('Choose legend position', options=legend_positions)

        # Text visibility options
        show_x_label = st.checkbox('Show X-axis label', value=True)
        show_y_label = st.checkbox('Show Y-axis label', value=True)
        show_title = st.checkbox('Show Title', value=True)

        # New options for bar values and background
        show_bar_values = st.checkbox('Show bar values', value=True)
        text_color = st.radio('Text color', ['Black', 'White'])
        bg_color = st.radio('Background color', ['White', 'Black', 'Transparent'])

        # Export options
        export_format = st.selectbox('Export format', ['PNG', 'JPEG', 'SVG', 'PDF'])

        def get_fig(data, chart_type, palette_name, filename=None):
            colors = px.colors.qualitative.__dict__[palette_name]

            # Determine text color based on background
            if bg_color == 'White':
                effective_text_color = 'black'
            elif bg_color == 'Black':
                effective_text_color = 'white'
            else:  # Transparent
                effective_text_color = text_color.lower()

            # Create figure with explicit height
            fig = go.Figure()

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
                        labels=data.columns[1:],
                        values=data.iloc[0, 1:],
                        marker=dict(colors=colors[:len(data.columns[1:])]),
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

            # Set background color and text color with soft gray grid lines
            if bg_color == 'White':
                fig.update_layout(
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    font=dict(color='black'),
                    xaxis=dict(
                        title=dict(font=dict(color='black')),
                        tickfont=dict(color='black'),
                        gridcolor='rgba(200, 200, 200, 0.3)',
                        showgrid=True,
                    ),
                    yaxis=dict(
                        title=dict(font=dict(color='black')),
                        tickfont=dict(color='black'),
                        gridcolor='rgba(200, 200, 200, 0.3)',
                        showgrid=True,
                        autorange=True
                    ),
                    legend=dict(font=dict(color='black')),
                    margin=dict(l=60, r=60, b=80, t=100, pad=10),
                    height=600,
                )
            elif bg_color == 'Black':
                fig.update_layout(
                    paper_bgcolor='black',
                    plot_bgcolor='black',
                    font=dict(color='white'),
                    xaxis=dict(
                        title=dict(font=dict(color='white')),
                        tickfont=dict(color='white'),
                        gridcolor='rgba(100, 100, 100, 0.5)',
                        showgrid=True,
                    ),
                    yaxis=dict(
                        title=dict(font=dict(color='white')),
                        tickfont=dict(color='white'),
                        gridcolor='rgba(100, 100, 100, 0.5)',
                        showgrid=True,
                        autorange=True
                    ),
                    legend=dict(font=dict(color='white')),
                    margin=dict(l=60, r=60, b=80, t=100, pad=10),
                    height=600,
                )
            else:  # Transparent
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=effective_text_color),
                    xaxis=dict(
                        title=dict(font=dict(color=effective_text_color)),
                        tickfont=dict(color=effective_text_color),
                        gridcolor='rgba(200, 200, 200, 0.3)',
                        showgrid=True,
                    ),
                    yaxis=dict(
                        title=dict(font=dict(color=effective_text_color)),
                        tickfont=dict(color=effective_text_color),
                        gridcolor='rgba(200, 200, 200, 0.3)',
                        showgrid=True,
                        autorange=True
                    ),
                    legend=dict(font=dict(color=effective_text_color)),
                    margin=dict(l=60, r=60, b=80, t=100, pad=10),
                    height=600,
                )

            fig.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="right", x=1),
                title_text=f'Responses by Concelhos - {os.path.splitext(filename)[0]}' if filename and show_title else ('Responses by Concelhos' if show_title else ''),
                xaxis_title='Concelhos' if show_x_label else '',
                yaxis_title='Percentage' if show_y_label else '',
                legend_title_text='',
                legend_traceorder="normal"
            )
            return fig

        if st.button('Preview Charts'):
            for uploaded_file in uploaded_files:
                try:
                    # Read CSV file
                    data = pd.read_csv(uploaded_file)
                    st.write(f"Data Preview for {uploaded_file.name}:", data.head())

                    fig = get_fig(data, selected_chart_type, selected_palette_name, uploaded_file.name)
                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{uploaded_file.name}")
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")

        if st.button('Export Current Chart'):
            for uploaded_file in uploaded_files:
                try:
                    data = pd.read_csv(uploaded_file)
                    fig = get_fig(data, selected_chart_type, selected_palette_name, uploaded_file.name)

                    img_data = fig.to_image(format=export_format.lower())

                    st.download_button(
                        label=f"Download Chart as {export_format}",
                        data=img_data,
                        file_name=f"chart_{os.path.splitext(uploaded_file.name)[0]}.{export_format.lower()}",
                        mime=f"image/{export_format.lower()}",
                        key=f"download_button_{uploaded_file.name}"
                    )
                except Exception as e:
                    st.error(f"Error exporting {uploaded_file.name}: {str(e)}")

        if st.button('Export All Charts to Folder'):
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                total_files = len(uploaded_files)
                for i, uploaded_file in enumerate(uploaded_files):
                    # Update progress
                    progress = (i + 1) / total_files
                    progress_bar.progress(progress)
                    status_text.text(f"Processing file {i+1} of {total_files}: {uploaded_file.name}")

                    try:
                        data = pd.read_csv(uploaded_file)
                        fig = get_fig(data, selected_chart_type, selected_palette_name, uploaded_file.name)

                        # Save the chart to temporary directory
                        output_path = os.path.join(output_dir, f"chart_{os.path.splitext(uploaded_file.name)[0]}.png")
                        fig.write_image(output_path, format="png")

                        # Small delay to allow the file to be written
                        time.sleep(0.1)
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {str(e)}")

                # Create a zip file of all exported charts
                zip_buffer = BytesIO()
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Copy all PNG files to temp directory
                    for file in os.listdir(output_dir):
                        if file.endswith(".png"):
                            src = os.path.join(output_dir, file)
                            dst = os.path.join(temp_dir, file)
                            with open(src, 'rb') as fsrc:
                                with open(dst, 'wb') as fdst:
                                    fdst.write(fsrc.read())

                    # Create zip file
                    import zipfile
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                zipf.write(os.path.join(root, file), file)

                status_text.text(f"All {total_files} charts have been processed.")
                st.success("Export completed successfully!")

                # Provide download link for the zip file
                zip_buffer.seek(0)
                st.download_button(
                    label="Download All Charts as ZIP",
                    data=zip_buffer,
                    file_name="charts.zip",
                    mime="application/zip"
                )

            except Exception as e:
                status_text.text(f"Error occurred: {str(e)}")
                st.error(f"Export failed: {str(e)}")

            finally:
                # Clean up temporary files
                for file in os.listdir(output_dir):
                    file_path = os.path.join(output_dir, file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        st.warning(f"Could not delete file {file_path}: {str(e)}")

                # Remove progress bar after completion
                time.sleep(2)
                progress_bar.empty()
                status_text.empty()

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

