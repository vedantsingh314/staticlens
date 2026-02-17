import json


def generate_json_report(results: dict, output_path: str = None):
    

    json_data = json.dumps(results, indent=4)

    if output_path:
        with open(output_path, "w") as f:
            f.write(json_data)

    return json_data
