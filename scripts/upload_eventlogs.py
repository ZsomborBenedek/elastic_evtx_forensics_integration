from fileinput import filename
import os
import argparse
from evtx2es import evtx2es
import getpass


def send_to_es(path, host, port, index, scheme, login, pwd):
    # Check if the path is a file (not a directory)
    if os.path.isfile(path) and path.endswith('.evtx'):
        print(f"{path} - sending to es...")
        try:
            evtx2es(path, host, port, index, scheme,
                    login=login, pwd=pwd, multiprocess=True, chunk_size=4000)
        except Exception as e:
            print(
                f"-- Could not upload the log at {path} due to error: {str(e)}")


def get_secure_password():
    try:
        # Use getpass to securely prompt for passwd
        password = getpass.getpass("Enter your password: ")
        return password
    except KeyboardInterrupt:
        # Handle Ctrl+C, if the user decides to interrupt the input
        print("\nPassword input interrupted.")
        return None


def main(input_path, password, elasticsearch, port, index, scheme, login):
    if password is None:
        user_password = get_secure_password()
    else:
        user_password = str(password)

    if user_password:

        if os.path.isfile(input_path) and input_path.endswith('.evtx'):
            send_to_es(input_path, host=elasticsearch, port=port,
                       index=index, scheme=scheme, login=login, pwd=user_password)


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

    args = parser.parse_args()

    main(input_path=args.input_path, password=args.password,
         elasticsearch=args.elasticsearch, port=args.port, index=args.index, scheme=args.scheme, login=args.login)
