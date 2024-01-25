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
                    zip.extract(zip_info, target_folder)

    return target_folder


def send_to_es(path, host, port, index, scheme, login, pwd):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)

        # Check if the path is a file (not a directory)
        if os.path.isfile(file_path) and file_path.endswith('.evtx'):
            # print(f"{file_path} - sending to es...")
            evtx2es(file_path, host, port, index, scheme,
                    login=login, pwd=pwd, multiprocess=True)


def cleanup(file_path, extract_path, done_path):
    shutil.rmtree(extract_path)

    done_file_path = os.path.join(done_path, os.path.basename(file_path))
    print(f"deleted {extract_path}, moving {file_path} to {done_file_path}")
    shutil.move(file_path, done_file_path)


def get_secure_password():
    try:
        # Use getpass to securely prompt for passwd
        password = getpass.getpass("Enter your password: ")
        return password
    except KeyboardInterrupt:
        # Handle Ctrl+C, if the user decides to interrupt the input
        print("\nPassword input interrupted.")
        return None


def main(input_path, done_path, password, elasticsearch, port, index, scheme, login):
    if password is None:
        user_password = get_secure_password()
    else:
        user_password = str(password)

    if user_password:
        for filename in os.listdir(input_path):
            file_path = os.path.join(input_path, filename)

            if os.path.isfile(file_path) and file_path.endswith('.zip'):
                extract_path = extract_and_move(file_path)
                # print(f"Temporary folder is {extract_folder}")

                send_to_es(extract_path, host=elasticsearch, port=port,
                           index=index, scheme=scheme, login=login, pwd=user_password)
                # print("Docs sent to Elasticsearch, doing cleanup...")

                cleanup(file_path, extract_path, done_path)
                # print("Cleanup done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Extract a ZIP files and upload the evtx files to Elasticsearch.')
    parser.add_argument('-in', '--input_path', type=str,
                        help='Path of the directory of zips', required=True)
    parser.add_argument('-d', '--donepath', type=str,
                        help='Path of the zip when done', required=True)
    parser.add_argument('-e', '--elasticsearch', type=str,
                        help='IP address or url of Elastic instance', required=False, default='127.0.0.1')
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

    main(input_path=args.input_path, done_path=args.donepath, password=args.password,
         elasticsearch=args.elasticsearch, port=args.port, index=args.index, scheme=args.scheme, login=args.login)
