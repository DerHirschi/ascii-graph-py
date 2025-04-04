"""
by Grok3-beta (AI by x.com)
Ported from:
   TheNetNode
   File: src/graph.c
"""
from math import atan2, pi, cos, sin

def generate_ascii_pie_chart(data, titel, datasets, fill_pie=True, radius=15, outline_thickness=0.5):
    """
    Generates an ASCII pie chart from the given data.

    Parameters:
    - data (list): List of dictionaries with arbitrary datasets
    - titel (str): Title of the chart
    - datasets (dict): Dictionary mapping dataset keys to characters (e.g., {'min': '#', 'ave': '*', 'max': '+'})
    - fill_pie (bool): Whether to fill the pie segments (default: True)
    - radius (int): Radius of the circle (default: 15)
    - outline_thickness (float): Thickness of the outline (default: 0.5)

    Returns:
    - str: The pie chart as a string
    """
    totals = {key: sum(d.get(key, 0) for d in data if d.get(key) is not None) for key in datasets.keys()}
    total_sum = sum(totals.values())
    if total_sum == 0:
        raise ValueError("The sum of values cannot be 0")

    shares = {key: (value / total_sum) * 360 for key, value in totals.items()}
    output = f"{titel}\n  Total: {total_sum:.2f}\n"
    for key, value in totals.items():
        output += f"  {key.capitalize()}: {value:.2f} ({(value / total_sum * 100):.1f}%)\n"
    output += "\nLegende:\n"
    for key, symbol in datasets.items():
        output += f"  {symbol} = {key.capitalize()}\n"
    output += "\n"

    width_factor = 2
    chart = [[' ' for _ in range(2 * radius * width_factor + 1)] for _ in range(2 * radius + 1)]
    center_x, center_y = radius * width_factor, radius
    current_angle = 0
    segment_angles = [0]
    for key, angle in shares.items():
        symbol = datasets[key]
        end_angle = current_angle + angle
        segment_angles.append(end_angle % 360)
        if fill_pie:
            for y in range(2 * radius + 1):
                for x in range(2 * radius * width_factor + 1):
                    dx = (x - center_x) / width_factor
                    dy = y - center_y
                    distance = (dx ** 2 + dy ** 2) ** 0.5
                    if distance <= radius:
                        point_angle = atan2(dy, dx) * 180 / pi
                        if point_angle < 0:
                            point_angle += 360
                        if current_angle <= point_angle < end_angle or \
                           (end_angle > 360 and point_angle < (end_angle % 360)):
                            chart[y][x] = symbol
        else:
            for y in range(2 * radius + 1):
                for x in range(2 * radius * width_factor + 1):
                    dx = (x - center_x) / width_factor
                    dy = y - center_y
                    distance = (dx ** 2 + dy ** 2) ** 0.5
                    if abs(distance - radius) < outline_thickness:
                        point_angle = atan2(dy, dx) * 180 / pi
                        if point_angle < 0:
                            point_angle += 360
                        if current_angle <= point_angle < end_angle or \
                           (end_angle > 360 and point_angle < (end_angle % 360)):
                            chart[y][x] = symbol
        current_angle = end_angle % 360

    if not fill_pie:
        for i, angle in enumerate(segment_angles):
            rad = angle * pi / 180
            segment_idx = min(i, len(shares) - 1) if i > 0 else len(shares) - 1
            symbol = datasets[list(datasets.keys())[segment_idx]]
            for r in range(int(radius * 10)):
                x = int(center_x + r * cos(rad) * width_factor / 10)
                y = int(center_y - r * sin(rad) / 10)
                if 0 <= y < len(chart) and 0 <= x < len(chart[0]):
                    chart[y][x] = symbol

    for row in chart:
        output += ''.join(row) + '\n'
    return output

def generate_ascii_graph(data, titel, datasets, expand=False, x_scale=True, bar_mode=False, chart_type='line', fill_pie=True, radius=15, outline_thickness=0.5, graph_height=10, graph_width=None):
    """
    Generates an ASCII graph (line, bar, or pie) from the given data with scaling options for line charts.

    Parameters:
    - data (list): List of dictionaries with arbitrary datasets
    - titel (str): Title of the graph
    - datasets (dict): Dictionary mapping dataset keys to characters
    - expand (bool): Stretch line/bar graph between min and max (default: False)
    - x_scale (bool): Scale X-axis for line/bar (default: True)
    - bar_mode (bool): Render as bars for line/bar (default: False)
    - chart_type (str): 'line' for line/bar graph, 'pie' for pie chart (default: 'line')
    - fill_pie (bool): Fill pie chart segments (default: True)
    - radius (int): Radius of pie chart (default: 15)
    - outline_thickness (float): Thickness of pie chart outline (default: 0.5)
    - graph_height (int): Height of the graph in lines for line/bar (default: 10)
    - graph_width (int or None): Width of the graph for line/bar; if None, uses data length (default: None)

    Returns:
    - str: The graph as a string
    """
    if chart_type.lower() == 'pie':
        return generate_ascii_pie_chart(data, titel, datasets, fill_pie, radius, outline_thickness)

    # Line or Bar Graph
    elements = len(data)
    if elements == 0:
        raise ValueError("Data list cannot be empty")

    all_values = []
    for d in data:
        for key in datasets.keys():
            if key in d and d[key] is not None:
                all_values.append(d[key])

    if not all_values:
        raise ValueError("No valid data values found")

    maximum = max(all_values)
    minimum = min(all_values)
    valid_averages = [sum(d.get(key, 0) for key in datasets.keys() if d.get(key) is not None) /
                      len([k for k in datasets.keys() if d.get(k) is not None])
                      for d in data if any(k in d and d[k] is not None for k in datasets.keys())]
    average = sum(valid_averages) / len(valid_averages) if valid_averages else 0

    output = f"{titel}\n  Maximum: {maximum}\n  Average: {average:.2f}\n  Minimum: {minimum}\n\n"

    # Set graph dimensions
    lines = max(graph_height, 5)  # Minimum 5 lines for readability
    graph_width = graph_width if graph_width is not None else elements  # Default to number of data points
    graph_width = max(graph_width, 10)  # Minimum width for readability

    # Calculate range and raster
    if expand:
        range_value = maximum - minimum
    else:
        range_value = maximum

    raster = range_value / lines
    if raster == 0 or range_value % lines > 0:
        raster += range_value / lines / 10  # Slight adjustment for small ranges

    expandwert = minimum if expand else 0
    dataset_keys = list(datasets.keys())

    # Scale data to fit graph_width
    scaled_data = []
    if graph_width != elements:
        scale_factor = elements / graph_width
        for x in range(graph_width):
            orig_x = x * scale_factor
            lower_idx = int(orig_x)
            upper_idx = min(lower_idx + 1, elements - 1)
            frac = orig_x - lower_idx
            point = {}
            for key in dataset_keys:
                if lower_idx < elements and key in data[lower_idx]:
                    lower_val = data[lower_idx][key]
                    upper_val = data[upper_idx][key] if upper_idx < elements and key in data[upper_idx] else lower_val
                    point[key] = lower_val + (upper_val - lower_val) * frac if upper_val is not None else lower_val
            scaled_data.append(point)
    else:
        scaled_data = data

    # Generate the graph
    for line in range(lines, -1, -1):
        y_value = raster * line + expandwert
        output += f"{y_value:6.0f}|"
        for d in scaled_data:
            char = " "
            if bar_mode:
                for key in dataset_keys:
                    if key in d and d[key] is not None and d[key] >= y_value:
                        char = datasets[key]
                        break
            else:
                closest_key = None
                min_diff = float('inf')
                for key in dataset_keys:
                    if key in d and d[key] is not None:
                        diff = abs(d[key] - y_value)
                        if diff < min_diff and diff < raster / 2:
                            min_diff = diff
                            closest_key = key
                if closest_key:
                    char = datasets[closest_key]
            output += char
        output += "\n"

    output += "      +"
    if x_scale:
        scale_str = f"0{'-' * (graph_width - len(str(graph_width - 1)) - 1)}{graph_width - 1}"
        output += scale_str
    else:
        output += "-" * graph_width
    output += "\n"
    return output

# Example Usage
if __name__ == "__main__":
    custom_data = [{'low': i, 'high': i * i} for i in range(70)]
    datasets_custom = {'low': '#', 'high': '+'}
    test_data = [{'min': i, 'ave': i + 0.5, 'max': i + 1} for i in range(60)]
    datasets_test = {'min': '#', 'ave': '*', 'max': '+'}
    custom_data2 = [
        {'temp': 8}, {'temp': 9}, {'temp': 12}, {'temp': 14}, {'temp': 16}, {'temp': 21},
        {'temp': 23}, {'temp': 24}, {'temp': 24.5}, {'temp': 25}, {'temp': 23}, {'temp': 21},
        {'temp': 18}, {'temp': 17}, {'temp': 14}, {'temp': 12}, {'temp': 8}, {'temp': 5},
        {'temp': 6}, {'temp': 8}, {'temp': 10}, {'temp': 12}, {'temp': 13}, {'temp': 15},
        {'temp': 18}, {'temp': 20}, {'temp': 22}, {'temp': 24}, {'temp': 26}, {'temp': 27}
    ]
    datasets_custom2 = {'temp': '+'}

    # Line Graph with Default Scaling
    graph_test_line = generate_ascii_graph(test_data, "Test Graph (Line, Default)", datasets_test, chart_type='line')
    print(graph_test_line)

    # Line Graph with Custom Scaling (Height=15, Width=20)
    graph_test_line_scaled = generate_ascii_graph(test_data, "Test Graph (Line, Scaled H15 W20)", datasets_test, chart_type='line', graph_height=15, graph_width=20)
    print(graph_test_line_scaled)

    # Line Graph with Custom Scaling (Height=5, Width=10)
    graph_custom_line_scaled = generate_ascii_graph(custom_data, "Custom Graph (Line, Scaled H5 W10)", datasets_custom, chart_type='line', graph_height=5, graph_width=10)
    print(graph_custom_line_scaled)

    # Line Graph with Custom Scaling for custom_data2
    graph_custom2_line_scaled = generate_ascii_graph(custom_data2, "Custom Graph 2 (Line, Scaled H8 W15)", datasets_custom2, chart_type='line', graph_height=12, graph_width=70)
    print(graph_custom2_line_scaled)
