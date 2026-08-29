from pathlib import Path

import polars as pl
import json
import os


def create_3d_scatter_viewer(
    df: pl.DataFrame, file_path: str | Path = "3d_scatter_viewer.html"
):
    """
    Creates an interactive 3D scatter plot viewer as a single HTML file from a Polars DataFrame.

    The viewer includes controls to dynamically assign columns to the X, Y, Z,
    and color axes, as well as controls for opacity and colormap.

    Args:
        df (polars.DataFrame): The input Polars DataFrame.
        file_path (str): The path and filename for the output HTML file.
    """
    if not isinstance(df, pl.DataFrame):
        raise TypeError("Input must be a Polars DataFrame.")

    # Get the column names from the DataFrame
    columns = df.columns

    # Convert the DataFrame to a list of dictionaries (JSON serializable format)
    data = df.to_dicts()

    # Find the first three numerical columns to use as default axes
    numeric_cols = [col for col in columns if df[col].dtype.is_numeric()]
    x_col = numeric_cols[0] if len(numeric_cols) > 0 else columns[0]
    y_col = numeric_cols[1] if len(numeric_cols) > 1 else columns[0]
    z_col = numeric_cols[2] if len(numeric_cols) > 2 else columns[0]

    # List of available Plotly colormaps
    colormaps = [
        "Viridis",
        "Plasma",
        "Jet",
        "Cividis",
        "Greys",
        "YlGnBu",
        "RdBu",
        "Portland",
        "Blackbody",
        "Earth",
        "Electric",
        "Hot",
        "Greens",
        "Reds",
    ]

    # Create the HTML content as a single string
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Scatter Plot Viewer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            background-color: #f3f4f6;
        }}
        .rounded-xl {{ border-radius: 12px; }}
        .slider {{
            -webkit-appearance: none;
            width: 100%;
            height: 8px;
            background: #d1d5db;
            outline: none;
            -webkit-transition: .2s;
            transition: opacity .2s;
            border-radius: 4px;
        }}
        .slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 16px;
            height: 16px;
            background: #4f46e5;
            cursor: pointer;
            border-radius: 50%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body class="p-8 bg-gray-100 flex flex-col items-center justify-center min-h-screen">
    <div class="bg-white p-8 rounded-xl shadow-2xl w-full max-w-7xl flex flex-col h-[calc(100vh-4rem)]">
        <h1 class="text-3xl font-bold mb-6 text-center text-gray-800">3D Scatter Plot Viewer</h1>
        
        <div class="flex flex-col md:flex-row items-center justify-center gap-4 mb-8">
            <div class="w-full">
                <label for="x-select" class="block text-sm font-medium text-gray-700">X-Axis</label>
                <select id="x-select" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md shadow-sm">
                </select>
            </div>
            <div class="w-full">
                <label for="y-select" class="block text-sm font-medium text-gray-700">Y-Axis</label>
                <select id="y-select" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md shadow-sm">
                </select>
            </div>
            <div class="w-full">
                <label for="z-select" class="block text-sm font-medium text-gray-700">Z-Axis</label>
                <select id="z-select" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md shadow-sm">
                </select>
            </div>
            <div class="w-full">
                <label for="color-select" class="block text-sm font-medium text-gray-700">Color</label>
                <select id="color-select" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md shadow-sm">
                </select>
            </div>
            <div class="w-full">
                <label for="colormap-select" class="block text-sm font-medium text-gray-700">Colormap</label>
                <select id="colormap-select" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md shadow-sm">
                </select>
            </div>
            <div class="w-full">
                <label for="opacity-slider" class="block text-sm font-medium text-gray-700">Opacity</label>
                <input type="range" id="opacity-slider" min="0" max="1" step="0.1" value="0.8" class="slider mt-1">
            </div>
        </div>

        <div id="plot" class="w-full flex-grow bg-gray-200 rounded-xl shadow-inner"></div>

        <script>
            // Data and column names are passed from the Python script
            const data = {json.dumps(data)};
            const columns = {json.dumps(columns)};
            const colormaps = {json.dumps(colormaps)};
            const initialXCol = "{x_col}";
            const initialYCol = "{y_col}";
            const initialZCol = "{z_col}";
            const initialColorCol = "{columns[3]}";

            const plotDiv = document.getElementById('plot');
            const xSelect = document.getElementById('x-select');
            const ySelect = document.getElementById('y-select');
            const zSelect = document.getElementById('z-select');
            const colorSelect = document.getElementById('color-select');
            const colormapSelect = document.getElementById('colormap-select');
            const opacitySlider = document.getElementById('opacity-slider');

            // Function to populate the dropdown menus
            function populateSelects() {{
                const axisSelects = [xSelect, ySelect, zSelect, colorSelect];
                axisSelects.forEach(select => {{
                    columns.forEach(col => {{
                        const option = document.createElement('option');
                        option.value = col;
                        option.textContent = col;
                        select.appendChild(option);
                    }});
                }});

                colormaps.forEach(map => {{
                    const option = document.createElement('option');
                    option.value = map;
                    option.textContent = map;
                    colormapSelect.appendChild(option);
                }});

                xSelect.value = initialXCol;
                ySelect.value = initialYCol;
                zSelect.value = initialZCol;
                colorSelect.value = initialColorCol;
                colormapSelect.value = "Viridis";
            }}

            // Function to get values for a specific column
            function getValues(column) {{
                return data.map(row => row[column]);
            }}

            // Function to create and update the plot
            function updatePlot() {{
                const xCol = xSelect.value;
                const yCol = ySelect.value;
                const zCol = zSelect.value;
                const colorCol = colorSelect.value;
                const colormap = colormapSelect.value;
                const opacity = parseFloat(opacitySlider.value);

                // Create the trace for the scatter plot
                const trace = {{
                    x: getValues(xCol),
                    y: getValues(yCol),
                    z: getValues(zCol),
                    mode: 'markers',
                    type: 'scatter3d',
                    marker: {{
                        size: 5,
                        color: getValues(colorCol),
                        colorscale: colormap,
                        colorbar: {{ 
                            title: colorCol,
                            x: 0.0,
                        }},
                        line: {{
                            width: 0
                        }},
                        opacity: opacity
                    }},
                    hoverinfo: 'text',
                    text: data.map(row => `<b>${{xCol}}</b>: ${{row[xCol]}}<br><b>${{yCol}}</b>: ${{row[yCol]}}<br><b>${{zCol}}</b>: ${{row[zCol]}}<br><b>${{colorCol}}</b>: ${{row[colorCol]}}`)
                }};

                const layout = {{
                    scene: {{
                        xaxis: {{ title: xCol }},
                        yaxis: {{ title: yCol }},
                        zaxis: {{ title: zCol }}
                    }},
                    margin: {{ l: 0, r: 0, b: 0, t: 0 }},
                    height: plotDiv.offsetHeight, // Set height to container's height
                    width: plotDiv.offsetWidth, // Set width to container's width
                    hovermode: 'closest'
                }};

                Plotly.react(plotDiv, [trace], layout);
            }}

            // Initialize the viewer
            populateSelects();
            updatePlot();

            // Add event listeners to the dropdowns and slider to update the plot
            xSelect.addEventListener('change', updatePlot);
            ySelect.addEventListener('change', updatePlot);
            zSelect.addEventListener('change', updatePlot);
            colorSelect.addEventListener('change', updatePlot);
            colormapSelect.addEventListener('change', updatePlot);
            opacitySlider.addEventListener('input', updatePlot);
            
            // Add a resize event listener for the plot
            window.addEventListener('resize', () => {{
                Plotly.relayout(plotDiv, {{
                    height: plotDiv.offsetHeight,
                    width: plotDiv.offsetWidth,
                }});
            }});
        </script>
    </div>
</body>
</html>
    """

    # Write the HTML content to the specified file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(
            f"Successfully created 3D scatter plot viewer at: {os.path.abspath(file_path)}"
        )
    except IOError as e:
        print(f"Error writing file: {e}")
