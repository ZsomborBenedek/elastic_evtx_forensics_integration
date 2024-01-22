import zipfile
import os
import argparse
from evtx2es import evtx2es
import getpass
import shutil


def extract_and_move(zip_path):
    target_folder = os.path.splitext(zip_path)[0]

    with zipfile.ZipFile(zip_path) as zip:
        for zip_info in zip.infolist():
            if not zip_info.is_dir():
                zip_info.filename = os.path.basename(
                    zip_info.filename)
                if zip_info.filename.endswith(".evtx"):
                    zip.extract(zip_info, os.path.join('./tmp', target_folder))

    return target_folder


def send_to_es(folder, host, port, index, scheme, login, pwd):
    source_folder = os.path.join('./tmp', folder)
    for filename in os.listdir(source_folder):
        file_path = os.path.join(source_folder, filename)

        # Check if the path is a file (not a directory)
        if os.path.isfile(file_path) and file_path.endswith('.evtx'):
            evtx2es(file_path, host, port, index, scheme,
                    login=login, pwd=pwd, multiprocess=True)


def cleanup(folder):
    tmp_path = os.path.join('./tmp', folder)
    zip_path = f"{folder}.zip"
    new_zip_path = os.path.join('./done', zip_path)
    shutil.rmtree(tmp_path)
    shutil.move(zip_path, new_zip_path)
    # print(f"deleted {tmp_path}, moved {zip_path} to {new_zip_path}")


def get_secure_password():
    try:
        # Use getpass to securely prompt for passwd
        password = getpass.getpass("Enter your password: ")
        return password
    except KeyboardInterrupt:
        # Handle Ctrl+C, if the user decides to interrupt the input
        print("\nPassword input interrupted.")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Extract a ZIP files and upload the evtx files to Elasticsearch.')
    parser.add_argument('-u', '--url', type=str,
                        help='IP address or url of Elastic instance', required=True)
    parser.add_argument('-p', '--port', type=str,
                        help='Port to send, 9200 by default', required=False, default=9200)
    parser.add_argument('-i', '--index', type=str,
                        help='Index to send the data to', required=True)
    parser.add_argument('-s', '--scheme', type=str,
                        help='http or https, https by default', required=False, default='https')
    parser.add_argument('-l', '--login', type=str,
                        help='User to use for input', required=True)
    parser.add_argument('-pw', '--password', type=str,
                        help='Password of the uploader', required=False, default=None)

    args = parser.parse_args()

    if args.password is None:
        user_password = get_secure_password()
    else:
        user_password = str(args.password)

    if user_password:
        for filename in os.listdir():
            file_path = os.path.join(filename)

            if os.path.isfile(file_path) and file_path.endswith('.zip'):
                target_folder = extract_and_move(file_path)
                # print(f"Temporary folder is {target_folder}")

                send_to_es(target_folder, host=args.url, port=args.port,
                           index=args.index, scheme=args.scheme, login=args.login, pwd=user_password)
                # print("Docs sent to Elasticsearch, doing cleanup...")

                cleanup(target_folder)
                # print("Cleanup done")


if __name__ == "__main__":
    main()
