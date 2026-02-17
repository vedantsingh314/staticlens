def generate_html_report(results, output_path: str = None):

    html_content = """
    <html>
    <head>
        <title>Code Analysis Report</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            h1 { color: #2c3e50; }
            .section { margin-bottom: 30px; }
            table { border-collapse: collapse; width: 60%; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background-color: #f4f4f4; }
        </style>
    </head>
    <body>
    <h1>Static Code Analysis Report</h1>
    """

    # If multiple files
    if isinstance(results, list):

        for file_result in results:

            html_content += f"""
            <div class="section">
                <h2>File: {file_result.get("file")}</h2>
                <p><strong>Language:</strong> {file_result.get("language")}</p>
            """

            metrics = file_result.get("metrics", {})

            for metric_name, metric_values in metrics.items():

                html_content += f"""
                <h3>{metric_name.replace('_', ' ').title()}</h3>
                <table>
                """

                if isinstance(metric_values, dict):
                    for key, value in metric_values.items():
                        html_content += f"""
                        <tr>
                            <th>{key}</th>
                            <td>{value}</td>
                        </tr>
                        """
                else:
                    html_content += f"""
                    <tr>
                        <th>{metric_name}</th>
                        <td>{metric_values}</td>
                    </tr>
                    """

                html_content += "</table>"

            html_content += "</div>"

    # If single file
    else:

        html_content += f"""
        <div class="section">
            <h2>File: {results.get("file")}</h2>
            <p><strong>Language:</strong> {results.get("language")}</p>
        """

        metrics = results.get("metrics", {})

        for metric_name, metric_values in metrics.items():

            html_content += f"""
            <h3>{metric_name.replace('_', ' ').title()}</h3>
            <table>
            """

            if isinstance(metric_values, dict):
                for key, value in metric_values.items():
                    html_content += f"""
                    <tr>
                        <th>{key}</th>
                        <td>{value}</td>
                    </tr>
                    """
            else:
                html_content += f"""
                <tr>
                    <th>{metric_name}</th>
                    <td>{metric_values}</td>
                </tr>
                """

            html_content += "</table>"

        html_content += "</div>"

    html_content += "</body></html>"

    if output_path:
        with open(output_path, "w") as f:
            f.write(html_content)

    return html_content
