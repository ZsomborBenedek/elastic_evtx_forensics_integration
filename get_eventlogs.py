import zipfile
import os
import argparse
from evtx2es import evtx2es
import getpass


def extract_and_move(zip_path, target_folder=None):
    if target_folder is None:
        target_folder = os.path.splitext(zip_path)[0]

    with zipfile.ZipFile(zip_path) as zip:
        for zip_info in zip.infolist():
            if not zip_info.is_dir():
                zip_info.filename = os.path.basename(zip_info.filename)
                if zip_info.filename.endswith(".evtx"):
                    zip.extract(zip_info, target_folder)

    return target_folder


def send_to_es(source_folder, host, port, index, scheme, login, pwd):
    # evtx2es(source_folder, host, port, index, scheme, login, pwd)
    for filename in os.listdir(source_folder):
        file_path = os.path.join(source_folder, filename)

        # Check if the path is a file (not a directory)
        if os.path.isfile(file_path) and file_path.endswith('.evtx'):
            evtx2es(file_path, host, port, index, scheme, login=login, pwd=pwd, multiprocess=True)


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
        description='Extract a ZIP file and upload the evtx files to Elasticsearch.')
    parser.add_argument('-zp', '--zip_path', type=str,
                        help='Path to the ZIP file', required=True)
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

    args = parser.parse_args()

    user_password = get_secure_password()

    if user_password:
        # Call the function with the provided arguments
        target_folder = extract_and_move(args.zip_path)

        # subprocess.run(["evtx2es", target_folder, "--host", args.url, "--port",
        #                args.port, "--index", args.index, "--scheme", args.scheme, "--login", args.login, "--pwd", user_password])
        send_to_es(target_folder, host=args.url, port=args.port,
                   index=args.index, scheme=args.scheme, login=args.login, pwd=user_password)


if __name__ == "__main__":
    main()
