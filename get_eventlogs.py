import zipfile
import os
import argparse


def extract_and_move(zip_path, target_folder=None):
    if target_folder is None:
        target_folder = os.path.splitext(zip_path)[0]

    with zipfile.ZipFile(zip_path) as zip:
        for zip_info in zip.infolist():
            if not zip_info.is_dir():
                zip_info.filename = os.path.basename(zip_info.filename)
                if zip_info.filename.endswith(".evtx"):
                    zip.extract(zip_info, target_folder)


def main():
    parser = argparse.ArgumentParser(
        description='Extract a ZIP file and move files with a specific extension into another folder.')
    parser.add_argument('-zp', '--zip_path', type=str,
                        help='Path to the ZIP file', required=True)
    parser.add_argument('-tf', '--target_folder', type=str,
                        help='Path to the target folder', required=False)

    args = parser.parse_args()

    # Call the function with the provided arguments
    extract_and_move(args.zip_path, args.target_folder)


if __name__ == "__main__":
    main()
