import os
import argparse
import getpass
import shutil
from upload_eventlogs import send_to_es, send_to_es_3rdparty
from extract_eventlogs import extract_and_move
from evtx_to_json import batch_convert


def cleanup(file_path, extract_path, done_path):
    shutil.rmtree(extract_path)

    done_file_path = os.path.join(done_path, os.path.basename(file_path))
    print(f"deleted {extract_path}, moving {file_path} to {done_file_path}")
    shutil.move(file_path, done_file_path)


def main(input_path, done_path, elasticsearch, port, index, scheme, api_key):
    for filename in os.listdir(input_path):
        file_path = os.path.join(input_path, filename)

        if os.path.isfile(file_path) and file_path.endswith(".zip"):
            extract_path = extract_and_move(file_path)
            # print(f"Temporary folder is {extract_path}")

            files_path = batch_convert(extract_path)

            # send_to_es(
            #     files_path,
            #     host=elasticsearch,
            #     port=port,
            #     index=index,
            #     scheme=scheme,
            #     api_key=api_key,
            # )
            # # print("Docs sent to Elasticsearch, doing cleanup...")

            cleanup(file_path, extract_path, done_path)
            # print("Cleanup done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract a ZIP files and upload the evtx files to Elasticsearch."
    )
    parser.add_argument(
        "-in",
        "--input_path",
        type=str,
        help="Path of the directory of zips",
        required=True,
    )
    parser.add_argument(
        "-d", "--donepath", type=str, help="Path of the zip when done", required=True
    )
    parser.add_argument(
        "-e",
        "--elasticsearch",
        type=str,
        help="IP address or url of Elastic instance",
        required=False,
        default="127.0.0.1",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=str,
        help="Port to send, 9200 by default",
        required=False,
        default=9200,
    )
    parser.add_argument(
        "-i", "--index", type=str, help="Index to send the data to", required=True
    )
    parser.add_argument(
        "-s",
        "--scheme",
        type=str,
        help="http or https, https by default",
        required=False,
        default="https",
    )
    parser.add_argument(
        "-ak",
        "--api_key",
        type=str,
        help="Elasticsearch API key",
        required=False,
        default=None,
    )

    args = parser.parse_args()

    main(
        input_path=args.input_path,
        done_path=args.donepath,
        elasticsearch=args.elasticsearch,
        port=args.port,
        index=args.index,
        scheme=args.scheme,
        api_key=args.api_key,
    )
