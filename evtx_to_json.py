import os
import json
from python_evtx import PyEvtxParser
import argparse


def evtx_to_ndjson(file_path):

    output_file = f"{os.path.splitext(file_path)[0]}.ndjson"

    with open(output_file, 'w', encoding='utf-8') as ndjson_file:
        with PyEvtxParser(file_path) as parser:
            for record in parser.records():
                # Convert each record to NDJSON format and write to the output file
                ndjson_data = json.dumps(
                    record, ensure_ascii=False)
                ndjson_file.write(ndjson_data + '\n')


def batch_convert(source_folder):
    # Iterate through each file in the input folder
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.endswith('.evtx'):
                evtx_file_path = os.path.join(root, file)
                evtx_to_ndjson(evtx_file_path)


def main():
    parser = argparse.ArgumentParser(
        description='Parse all evtx files in a folder into ndjson.')
    parser.add_argument('source_folder', type=str,
                        help='Path to the evtx files')

    args = parser.parse_args()

    batch_convert(args.source_folder)


if __name__ == "__main__":
    main()
