#! python

'''
pyinstaller --clean --hidden-import flask --hidden-import requests --hidden-import rich --icon NONE --onefile ./FileServerClient.py
pyinstaller --hidden-import flask --hidden-import requests --hidden-import rich --icon NONE --onefile ./FileServerClient.py
pyinstaller  --icon NONE --onefile ./FileServerClient.py --name fsc

python FileServerClient.py -s [-t] [<ip>][:<port>] [<file>s...]
python FileServerClient.py -s -r [<ip>][:<port>] [-p <rx-path>]
python FileServerClient.py -c -t <ip>[:<port>] [<file>s...]
python FileServerClient.py [-c] [-r] <ip>[:<port>] [<file>s...] [-p <rx-path>]
'''


import os
import requests
import argparse
import time
import enum
from typing import Iterable
from flask import Flask, jsonify, send_file, request, Response
from urllib.parse import unquote
from pathlib import Path
from libpycom.Messager import Messager, LEVEL
from libpycom.message import message
from libpycom.networks.HeaderHandle import HeadersHandle
from libpycom.progress.io import new_progress, new_progress_track, FileProgressWrapper


class Config:
    IP = "0.0.0.0"
    Port = 8888
    RX_DirPath = "."
    NullDev = os.devnull
    Seq = '/'

    ChunkSize = 1 * (2**(10 * 2))  # 1 MiB

    @staticmethod
    def FILENAME():
        return f"fsc_file_{time.time()}"

    @classmethod
    def isDevnull(cls, path):
        return path == cls.NullDev


class FileServerClientFlag(enum.IntFlag):
    Off = 0
    Client = enum.auto()
    Server = enum.auto()
    Transimit = enum.auto()
    Receive = enum.auto()

    ChunkAuto = enum.auto()
    ChunkOff = enum.auto()
    ChunkOn = enum.auto()

    Fast = ChunkAuto
    Stardard = ChunkOff

    All = ~0


class FileServerClient:
    def __init__(self, ip=Config.IP, port=Config.Port,
                 files: Iterable[str] = None,
                 rx_dir: str = ".",
                 flag: FileServerClientFlag = FileServerClientFlag.Client | FileServerClientFlag.Receive | FileServerClientFlag.Fast,
                 level: LEVEL = LEVEL.INFO
                 ):

        # Args
        self.ip = ip
        self.port = port
        # self.chucked = chunked

        self.flag = flag

        self.files = files

        self.tx_files = {}
        self.rx_dir = rx_dir
        self.host = f"http://{ip}:{port}"

        # Objects
        self.messager = Messager(level, level, fn_new_progress=new_progress, fn_new_progress_track=new_progress_track)
        self.app = Flask(self.__class__.__name__)

        # --------------------------------------------------------- #
        # ----------------------- Server TX ----------------------- #
        # --------------------------------------------------------- #
        @self.app.route('/<path:path_or_filename>', methods=['GET'])
        @self.app.route('/', methods=['GET'])
        def server_tx_file(path_or_filename=None):
            self.messager.debug(f"Get Request: \t{path_or_filename}")
            path = None

            # route "/", get the one tx_file
            if len(self.tx_files) == 1 and path_or_filename is None:
                path_or_filename = next(iter(self.tx_files))

            # Get path
            filename = ""
            if path_or_filename is not None:
                path_or_filename = self.posixify_path(unquote(path_or_filename))

                if Config.Seq in path_or_filename:  # is path
                    filename = os.path.basename(path_or_filename)
                    path = path_or_filename
                else:  # is filename
                    filename = path_or_filename
                    if self.tx_files.get(filename) is not None:
                        if len(self.tx_files[filename]) == 0:
                            path = None
                        elif len(self.tx_files[filename]) == 1:
                            path = self.tx_files[filename][0]
                        else:
                            path = self.tx_files[filename]

            self.messager.debug(f"Locate file: \t{path_or_filename} to {path}")

            # Response
            if path is None or not os.path.isfile(path):  # Not Found
                return jsonify({"Error": f"File {path_or_filename} not found"}), 404
            elif isinstance(path, list):  # Multi files
                return jsonify({"Error": f"Multi files {path} exsit"}), 404
            else:
                if self.flag & FileServerClientFlag.ChunkOff:
                    self.messager.debug(f"Send unchunked: \t{path}")
                    return send_file(path, as_attachment=True, download_name=filename)
                else:
                    progress = self.messager.new_progress()
                    f = FileProgressWrapper(path, progress=progress, chunk_size=Config.ChunkSize)
                    filesize = f.total

                    headers = {}
                    headers = HeadersHandle.set_Filename(filename, headers)
                    headers = HeadersHandle.set_Size(filesize, headers)
                    self.messager.debug(f"Send chunked: \t{path} {headers}")

                    return Response(f.read_generator(), headers=headers)

        # --------------------------------------------------------- #
        # ----------------------- Server RX ----------------------- #
        # --------------------------------------------------------- #

        @self.app.route('/', methods=['POST'])
        def servers_rx_file():
            # Save the file
            filename = HeadersHandle.get_Filename(request.headers)
            filesize = HeadersHandle.get_Size(request.headers)

            filename = filename if filename else Config.FILENAME()

            self.messager.debug(request.headers)
            self.messager.debug(filename)

            rx_filepath = os.path.join(self.rx_dir, filename) if not Config.isDevnull(self.rx_dir) else self.rx_dir

            def content():
                while chunk := request.stream.read(Config.ChunkSize):
                    yield chunk

            with open(rx_filepath, 'wb') as f:
                for chunk in self.messager.message_progress(content(), total=filesize, description=""):
                    f.write(chunk)

            # Update files_to_send
            return jsonify({"success": f"File {filename} uploaded successfully."}), 200

    # --------------------------------------------------------- #
    # ----------------------- Client RX ----------------------- #
    # --------------------------------------------------------- #

    def start_client_rx(self, paths):
        # Default "/"
        if len(paths) == 0:
            paths = [""]

        for path in paths:
            filename = os.path.basename(path)

            url = f"{self.host}/{path}"
            self.messager.info(f"Download from: \t{url}")

            response = requests.get(url, stream=True)

            if response.status_code == 200:
                self.messager.debug(response.headers)

                if not filename:
                    if not (filename := HeadersHandle.get_Filename(response.headers)):
                        filename = Config.FILENAME()

                rx_filepath = os.path.join(self.rx_dir, filename) if not Config.isDevnull(self.rx_dir) else self.rx_dir
                self.messager.info(f"Download to: \t{rx_filepath}")

                file_size = HeadersHandle.get_ContentLength(response.headers)
                content = response.iter_content(chunk_size=Config.ChunkSize)
                with open(rx_filepath, 'wb') as f:
                    for chunk in self.messager.message_progress(content, total=file_size):
                        f.write(chunk)

                self.messager.info(f"Downloaded: \t{filename} @ {rx_filepath}")
            else:
                self.messager.info(
                    f"Error: \t{response.status_code} {response.json().get('Error')}")

    # --------------------------------------------------------- #
    # ----------------------- Client TX ----------------------- #
    # --------------------------------------------------------- #

    def start_client_tx(self, paths):
        for path in paths:
            filename = os.path.basename(path)
            url = f"{self.host}"

            filesize = os.path.getsize(path)
            headers = HeadersHandle.set_Filename(filename)
            headers = HeadersHandle.set_Size(filesize, headers)

            # FileProgressWrapper (Faster)
            progress = self.messager.new_progress()
            f = FileProgressWrapper(path, progress=progress, chunk_size=Config.ChunkSize)

            # Progress.wrap_file
            # f = open(path, 'rb')
            # if progress := self.messager.new_progress():
            #     progress: Progress
            #     f = progress.wrap_file(f, total=filesize)
            #     progress.start()

            if self.flag & FileServerClientFlag.ChunkOn:
                response = requests.post(url, headers=headers, data=f.read_generator(), stream=True)
            else:
                response = requests.post(url, headers=headers, data=f, stream=True)

            # progress.stop()
            f.close()

            if response.status_code == 200:
                self.messager.info(f"Uploaded: {filename}")
            else:
                self.messager.info(f"Error Uploaded {filename}: {response.json().get('Error')}")

    # --------------------------------------------------------- #
    # -------------------------- Run -------------------------- #
    # --------------------------------------------------------- #
    def run(self):
        if not Config.isDevnull(self.rx_dir):
            os.makedirs(self.rx_dir, exist_ok=True)

        if self.flag & FileServerClientFlag.Server:
            if self.flag & FileServerClientFlag.Transimit:
                self.add_tx_files(self.files)
                self.start_server()

            elif self.flag & FileServerClientFlag.Receive:
                self.start_server()
            else:
                self.messager.info("Invalid transmit/receive mode")

        elif self.flag & FileServerClientFlag.Client:
            if self.flag & FileServerClientFlag.Transimit:
                self.start_client_tx(self.files)

            elif self.flag & FileServerClientFlag.Receive:
                self.start_client_rx(self.files)
            else:
                self.messager.info("Invalid transmit/receive mode")

        else:
            self.messager.info("Invalid server/client mode")

    def start_server(self):
        self.messager.info(f"Server started: \t{self.host}")

        self.app.run(host=self.ip, port=self.port)

        self.messager.info(f"Server ended: \t{self.host}")

    def add_tx_files(self, paths):
        for path_or_filename in paths:
            path_or_filename = self.posixify_path(path_or_filename)
            if os.path.isdir(path_or_filename):
                path_or_filename = path_or_filename.rstrip(Config.Seq)

            basename = os.path.basename(path_or_filename)
            self.tx_files.setdefault(basename, [])
            self.tx_files[basename].append(path_or_filename)

        self.messager.info(self.tx_files)

    @staticmethod
    def posixify_path(path):
        return str(Path(path).as_posix())


# --------------------------------------------------------- #
# ------------------------ Parser ------------------------- #
# --------------------------------------------------------- #

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

    parser.add_argument("-d", "--rx_dir", metavar="<Dir>", type=str, default=Config.RX_DirPath,
                        help="Path of directory to save received files")

    # IP and port
    parser.add_argument(
        '[<IP>]:[<Port>]',
        help=f"Target IP address and optional port (default: {Config.IP}:{Config.Port})")

    # 解析接收路径或文件列表
    parser.add_argument('<File>', nargs='*', type=str, help="Files or paths to transmit or receive (default: .)")

    parser.add_argument("-v", "--verbose", action='store_true', help="Verbose output")

    chunk_group = parser.add_mutually_exclusive_group(required=False)
    chunk_group.add_argument("-n", "--unchunked", action='store_true', help="Unchunked transfer encoding")
    chunk_group.add_argument("-y", "--chunked", action='store_true', help="Chunked transfer encoding")
    chunk_group.add_argument("-a", "--auto", action='store_true',
                             help="Automatical transfer encoding (default: unchunked for client transmit; chunked for server transmit)")

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

    if not args.unchunked and not args.chunked and not args.auto:
        args.auto = True

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


if __name__ == "__main__":
    args = parse_args()
    message(args)
    flag = FileServerClientFlag.Off
    flag |= FileServerClientFlag.Server if args.server else FileServerClientFlag.Client
    flag |= FileServerClientFlag.Transimit if args.transmit else FileServerClientFlag.Receive
    if args.unchunked:
        flag |= FileServerClientFlag.ChunkOff
    elif args.chunked:
        flag |= FileServerClientFlag.ChunkOn
    else:
        flag |= FileServerClientFlag.ChunkAuto

    level = LEVEL.DEBUG if args.verbose else LEVEL.INFO

    server = FileServerClient(args.ip, args.port, args.paths, args.rx_dir, flag, level)
    server.run()
