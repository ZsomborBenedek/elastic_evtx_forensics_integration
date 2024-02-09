import os
import argparse
import getpass
import shutil
from upload_eventlogs import send_to_es
from extract_eventlogs import extract_and_move


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
