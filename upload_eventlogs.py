from fileinput import filename
import os
import argparse
from evtx2es import evtx2es
import getpass
from elasticsearch import Elasticsearch
import json


def send_to_es_3rdparty(folder_path, host, port, index, scheme, login, pwd):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Check if the path is a file (not a directory)
        if os.path.isfile(file_path) and file_path.endswith('.evtx'):
            print(f"{file_path} - sending to es...")
            try:
                evtx2es(file_path, host, port, index, scheme,
                        login=login, pwd=pwd, multiprocess=True, chunk_size=4000)
            except Exception as e:
                print(
                    f"-- Could not upload the log at {file_path} due to error: {str(e)}")


def send_to_es(folder_path, host, port, index, scheme, api_key):
    es = Elasticsearch([f"{scheme}://{host}:{port}"], ssl_show_warn=False,
                       verify_certs=False, api_key=api_key)
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Check if the path is a file (not a directory)
        if os.path.isfile(file_path) and file_path.endswith('.ndjson'):
            print(f"{file_path} - sending to es...")
            with open(file_path, 'r', encoding='utf-8') as ndjson_file:
                for line in ndjson_file.readlines():
                    try:
                        es.index(index=index, document=json.loads(line))
                    except Exception as e:
                        print(
                            f"-- Could not upload the log at {file_path} due to error: {str(e)}")


def get_secure_password():
    try:
        # Use getpass to securely prompt for passwd
        password = getpass.getpass("Enter your password: ")
        return password
    except KeyboardInterrupt:
        # Handle Ctrl+C, if the user decides to interrupt the input
        print("\nPassword input interrupted.")
        return None


def main(input_path, password, elasticsearch, port, index, scheme, login, api_key):
    if password is None:
        user_password = get_secure_password()
    else:
        user_password = str(password)

    if user_password:

        if os.path.isfile(input_path) and input_path.endswith('.evtx'):
            send_to_es_3rdparty(input_path, host=elasticsearch, port=port,
                       index=index, scheme=scheme, login=login, pwd=user_password)
            send_to_es(input_path, host=elasticsearch, port=port,
                       index=index, scheme=scheme, api_key=api_key)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Extract a ZIP files and upload the evtx files to Elasticsearch.')
    parser.add_argument('-in', '--input_path', type=str,
                        help='Path of the of evtx file', required=True)
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
    parser.add_argument('-ak', '--api_key', type=str,
                        help='Elasticsearch API key', required=False, default=None)

    args = parser.parse_args()

    main(input_path=args.input_path, password=args.password,
         elasticsearch=args.elasticsearch, port=args.port, index=args.index, scheme=args.scheme, login=args.login, api_key=args.api_key)
