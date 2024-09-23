#! python

import os
from flask import Flask, send_from_directory, jsonify, send_file, request
from threading import Thread
import requests
from urllib.parse import unquote
import argparse


seq = '/'
POST_FILE_KEY = 'file'


class Config:
    IP = "0.0.0.0"
    Port = 6666
    RX_DIRPATH = "."
    NULL_DEV = "/dev/null" if os.name != 'nt' else 'nul'

    @classmethod
    def is_NULL_DEV(cls, path):
        return path == cls.NULL_DEV


class FileServerClient:
    def __init__(self, ip=Config.IP, port=Config.Port):
        self.app = Flask(self.__class__.__name__)
        self.ip = ip
        self.port = port
        self.tx_files = {}
        self.rx_dir = None
        self.tx_files = None
        self.host = f"http://{ip}:{port}"

        @self.app.route('/<path:path_or_filename>', methods=['GET'])
        @self.app.route('/', methods=['GET'])
        def server_tx_file(path_or_filename=None):
            print(path_or_filename)
            path = None

            # "/"
            if len(self.tx_files) == 1 and path_or_filename is None:
                path_or_filename = next(iter(self.tx_files))

            path_or_filename = unquote(path_or_filename)
            print("post", path_or_filename)

            if seq in path_or_filename:  # is path
                filename = os.path.basename(path_or_filename)
                path = path_or_filename
            else:  # is File
                filename = path_or_filename
                if self.tx_files.get(filename) is not None:
                    if len(self.tx_files[filename]) == 0:
                        path = None
                    elif len(self.tx_files[filename]) == 1:
                        path = self.tx_files[filename][0]
                    else:
                        path = self.tx_files[filename]
                else:
                    path = None

            if path is None or not os.path.isfile(path):
                return jsonify({"Error": f"File {path_or_filename} not found"}), 404
            elif isinstance(path, list):
                return jsonify({"Error": f"Multi files {path} exsit"}), 404
            else:
                return send_file(path, download_name=filename)

        @self.app.route('/', methods=['POST'])
        def servers_rx_file():
            if 'file' not in request.files:
                return jsonify({"Error": "No file part"}), 400

            file = request.files[POST_FILE_KEY]
            if file.filename == '':
                return jsonify({"Error": "No selected file"}), 400

            # Save the file
            rx_filepath = os.path.join(self.rx_dir, file.filename) if not Config.is_NULL_DEV(self.rx_dir) else self.rx_dir

            file.save(rx_filepath)

            # Update files_to_send
            return jsonify({"success": f"File {file.filename} uploaded successfully."}), 200

    def start_server(self):

        print(f"Server started at {self.host}")

        self.app.run(host=self.ip, port=self.port)

        print(f"Server ended at{self.host}")

    def add_tx_files(self, paths):
        for path_or_filename in paths:
            if os.path.isdir(path_or_filename):
                path_or_filename = path_or_filename.rstrip(seq)

            basename = os.path.basename(path_or_filename)
            self.tx_files.setdefault(basename, [])
            self.tx_files[basename].append(path_or_filename)

        print(self.tx_files)

    def start_client_rx(self, paths):

        for path in paths:
            filename = os.path.basename(path)
            url = f"{self.host}/{path}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    rx_filepath = os.path.join(self.rx_dir, filename) if not Config.is_NULL_DEV(self.rx_dir) else self.rx_dir

                    with open(rx_filepath, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded: {filename}")
                else:
                    print(f"Error downloading {filename}: {response.status_code} {response.json().get('Error')}")
            except Exception as e:
                print(f"Failed to download {filename}: {str(e)}")

    def start_client_tx(self, paths):
        for path in paths:
            filename = os.path.basename(path)
            url = f"{self.host}"
            try:
                f = open(path, 'rb')
                files = {POST_FILE_KEY: (filename, f)}
                response = requests.post(url, files=files)
                f.close()
                if response.status_code == 200:
                    print(f"Uploaded: {filename}")
                else:
                    print(f"Error Uploaded {filename}: {response.json().get('error')}")
            except Exception as e:
                print(f"Failed to Uploaded {filename}: {str(e)}")

    def run(self, args):
        self.rx_dir = args.rx_dir
        if not Config.is_NULL_DEV(self.rx_dir):
            os.makedirs(self.rx_dir, exist_ok=True)

        if args.server:
            if args.transmit:
                self.add_tx_files(args.paths)
                self.start_server()

            elif args.receive:
                self.start_server()
            else:
                print("Invalid mode. Use -t/--transmit for transmit or -r/--receive for receive.")

        elif args.client:
            if args.transmit:

                self.start_client_tx(args.paths)

            elif args.receive:

                self.start_client_rx(args.paths)
            else:
                print("Invalid mode. Use -t/--transmit for transmit or -r/--receive for receive.")

        else:
            print("Invalid mode. Use -s for server or -c for client.")


def parse_args():
    parser = argparse.ArgumentParser(description="Script to handle server/client to transmit/receive files.")

    # mux
    mode_group = parser.add_mutually_exclusive_group(required=False)
    mode_group.add_argument('-s', '--server', action='store_true', help="Run in server mode")
    mode_group.add_argument('-c', '--client', action='store_true', help="Run in client mode (default)")

    # mux
    action_group = parser.add_mutually_exclusive_group(required=False)
    action_group.add_argument('-t', '--transmit', action='store_true', help="Enable transmit mode (default for server)")
    action_group.add_argument('-r', '--receive', action='store_true', help="Enable receive mode (default for client)")

    parser.add_argument("-d", "--rx_dir", metavar="<Dir>", type=str, default=Config.RX_DIRPATH, help="Path of directory to save received files")

    # IP and port
    parser.add_argument('[<IP>]:[<Port>]', help="Target IP address and optional port (default: 0.0.0.0:6666)")

    # 解析接收路径或文件列表
    parser.add_argument('<File>', nargs='*', type=str, help="Files or paths to transmit or receive (default: .)")

    # 解析参数
    args = parser.parse_args()

    # 推导默认值
    if not args.server and not args.client:
        if args.receive:
            args.client = True  # 如果传输模式被指定，默认为客户端模式
        elif args.transmit:
            args.server = True  # 如果接收模式被指定，默认为服务器模式
        else:
            args.client = True
            args.receive = True
    if not args.transmit and not args.receive:
        if args.server:
            args.transmit = True  # 如果服务器模式被指定，默认为接收模式
        elif args.client:
            args.receive = True  # 如果客户端模式被指定，默认为传输模式

    ip_port = getattr(args, '[<IP>]:[<Port>]')
    if getattr(args, '[<IP>]:[<Port>]'):
        ip_port = ip_port.rsplit(":", 1)
        assert len(ip_port) == 1 or len(ip_port) == 2
        args.ip = ip_port[0] if ip_port[0] != "" else Config.IP
        args.port = int(ip_port[1]) if len(ip_port) == 2 and ip_port[1] != "" else Config.Port
    else:
        args.ip = Config.IP
        args.port = Config.Port
    args.paths = getattr(args, "<File>")

    return args


def main():
    args = parse_args()
    print(args)

    server = FileServerClient(args.ip, args.port)
    server.run(args)


if __name__ == "__main__":
    main()
'''
python script.py -s [-t] [<ip>][:<port>] [<file>s...]
python script.py -s -r [<ip>][:<port>] [-p <rx-path>]
python script.py -c -t <ip>[:<port>] [<file>s...]
python script.py [-c] [-r] <ip>[:<port>] [<file>s...] [-p <rx-path>]
'''
