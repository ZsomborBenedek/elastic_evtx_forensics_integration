import os
import json
import argparse
from evtx import PyEvtxParser

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, int):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

def evtx_to_ndjson(file_path):
    output_file = f"{os.path.splitext(file_path)[0]}.ndjson"
    parser = PyEvtxParser(file_path)

    with open(output_file, 'w', encoding='utf-8') as ndjson_file:
        for record in parser.records_json():
            # Convert each record to NDJSON format and write to the output file
            ndjson_data = json.loads(record["data"])
            ndjson_data = json.dumps(ndjson_data, cls=CustomEncoder)
            ndjson_file.write(f"{ndjson_data}\n")


def batch_convert(source_folder):
    # Iterate through each file in the input folder
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.endswith('.evtx'):
                evtx_file_path = os.path.join(root, file)
                evtx_to_ndjson(evtx_file_path)

    return source_folder


def main():
    parser = argparse.ArgumentParser(
        description='Parse all evtx files in a folder into ndjson.')
    parser.add_argument('source_folder', type=str,
                        help='Path to the evtx files')

    args = parser.parse_args()

    batch_convert(args.source_folder)


if __name__ == "__main__":
    main()
