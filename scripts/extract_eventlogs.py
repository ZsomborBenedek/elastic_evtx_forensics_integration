import zipfile
import os
import argparse


def extract_and_move(zip_path):
    target_folder = os.path.splitext(zip_path)[0]

    with zipfile.ZipFile(zip_path) as zip:
        for zip_info in zip.infolist():
            if not zip_info.is_dir():
                zip_info.filename = os.path.basename(
                    zip_info.filename)
                if zip_info.filename.endswith(".evtx"):
                    zip.extract(zip_info, target_folder)

    return target_folder


def main(input_path):

    if os.path.isfile(input_path) and input_path.endswith('.zip'):
        extract_path = extract_and_move(input_path)
        print(f"Eventlog folder is {extract_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Extract a ZIP files and upload the evtx files to Elasticsearch.')
    parser.add_argument('-in', '--input_path', type=str,
                        help='Path of the directory of zips', required=True)

    args = parser.parse_args()

    main(input_path=args.input_path)
