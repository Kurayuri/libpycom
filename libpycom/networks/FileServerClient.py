#! python

'''
pyinstaller --clean --hidden-import flask --hidden-import requests --hidden-import rich --icon NONE --onefile ./FileServerClient.py

python FileServerClient.py -s [-t] [<ip>][:<port>] [<file>s...]
python FileServerClient.py -s -r [<ip>][:<port>] [-p <rx-path>]
python FileServerClient.py -c -t <ip>[:<port>] [<file>s...]
python FileServerClient.py [-c] [-r] <ip>[:<port>] [<file>s...] [-p <rx-path>]

client tx unchunk 1M

uchk 1.8
yuansheng open 1.1
my wrap 3.4

Resp 3.5

'''


import os
import re
import requests
import argparse
import time
import enum
import io
from libpycom.message import Messager, LEVEL
from libpycom.functions.Timer import Timer
from requests_toolbelt.multipart.encoder import MultipartEncoder
from rich.progress import Progress, BarColumn, TaskProgressColumn, TimeElapsedColumn, TimeRemainingColumn, RenderableColumn, SpinnerColumn, TransferSpeedColumn, DownloadColumn
from rich.console import Console
from typing import Literal, Iterable, Any
from flask import Flask, jsonify, send_file, request, stream_with_context, Response
from urllib.parse import unquote, quote
from pathlib import Path


class FileProgressWrapper:
    def __init__(self, file, mode: str = 'rb', progress: Progress = None, **kwargs):
        self.file_path = file
        self.mode = mode  # Requried: requests/utils.py/super_len:'''if "b" not in o.mode'''
        self.file = open(file, mode, **kwargs)
        self.progress = progress

        if progress:
            self.task = self.progress.add_task("", total=self.total)
            progress.start()

    @property
    def total(self):
        return os.path.getsize(self.file_path)

    def read(self, *args, **kwargs):
        chunk = self.file.read(Config.ChunkSize)
        if self.progress:
            self.progress.update(self.task, advance=len(chunk))
        return chunk

    def read_generator(self):
        while chunk := self.file.read(Config.ChunkSize):
            yield chunk
            if self.progress:
                self.progress.update(self.task, advance=len(chunk))

    # Requried:
    # requests/models.py/PreparedRequest/prepare_body/:'''is_stream=all([hasattr(data,"__iter__"),notisinstance(data,(basestring,list,tuple,Mapping)),])''',
    # used for exam body whether is stream

    def __iter__(self):
        return self.file.__iter__()

    def __next__(self):
        return self.file.__next__()

    # Requried:
    # requests/utils.py/super_len:'''fileno = o.fileno()''', used for getting file size
    def fileno(self):
        return self.file.fileno()

    def __del__(self):
        self.close()

    def close(self):
        self.file.close()
        if self.progress:
            self.progress.stop()


seq = '/'
POST_FILE_KEY = 'file'


def new_progress():
    return Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        DownloadColumn(),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        "/",
        TimeRemainingColumn(),
        RenderableColumn(),
        TransferSpeedColumn(),
    )


def new_progress_track(
    sequence: Iterable[Any],
    total: int = None,
    description: str = "",
) -> Iterable[Any]:

    progress = new_progress()

    with progress:
        task = progress.add_task(description, total=total)
        for item in sequence:
            yield item
            progress.update(task, advance=len(item), total=total)


class Config:
    IP = "0.0.0.0"
    Port = 8888
    RX_DirPath = "."
    NullDev = os.devnull
    ChunkSize = 1 * (2**(10 * 2))  # 1 MiB

    @staticmethod
    def FILENAME():
        return f"fsc_file_{time.time()}"

    @classmethod
    def isDevnull(cls, path):
        return path == cls.NullDev


class HeadersHandle:
    @staticmethod
    def get_Filename(headers):
        content_disposition = headers.get("Content-Disposition") or ""
        filename = re.findall('filename=(.+)', content_disposition)
        filename = filename[0] if filename else Config.FILENAME()
        return filename

    def set_Filename(value, headers=None):
        if headers is None:
            headers = {}
        _header = {
            "Content-Disposition": f"attachment; filename={quote(value)}"
        }
        headers = headers.copy()
        headers.update(_header)
        return headers

    @staticmethod
    def get_ContentLength(headers):
        file_size = int(headers.get('Content-Length') or 0)
        return file_size

    @staticmethod
    def set_ContentLength(value=None, headers=None):
        if headers is None:
            headers = {}

        _header = {
            "Content-Length": f"{int(value)}"
        }

        headers = headers.copy()
        headers.update(_header)
        return headers

    @staticmethod
    def get_FileSize(headers):
        file_size = int(headers.get('File-Size') or 0)
        return file_size

    @staticmethod
    def set_FileSize(value=None, file=None, headers=None):
        if headers is None:
            headers = {}

        if value is None:
            value = os.path.getsize(file)

        _header = {
            "File-Size": f"{int(value)}"
        }

        headers = headers.copy()
        headers.update(_header)
        return headers

    @staticmethod
    def get_Size(headers):
        if not (size := HeadersHandle.get_ContentLength(headers)):
            size = HeadersHandle.get_FileSize(headers)
        return size

    @staticmethod
    def set_Size(value=None, headers=None):
        headers = HeadersHandle.set_ContentLength(value, headers)
        headers = HeadersHandle.set_FileSize(value, headers)
        return headers


class FileServerClientFlag(enum.IntFlag):
    Client = enum.auto()
    Server = enum.auto()
    Transimit = enum.auto()
    Receive = enum.auto()

    ChunkAuto = enum.auto()
    ChunkFalse = enum.auto()
    ChunkTrue = enum.auto()

    Fast = ChunkAuto
    Stardard = ChunkFalse


class FileServerClient:
    def __init__(self, ip=Config.IP, port=Config.Port,
                 flag: FileServerClientFlag = FileServerClientFlag.Client | FileServerClientFlag.Receive | FileServerClientFlag.Fast,
                 cs_mode: Literal['server', 'client'] = 'client',
                 txrx_mode: Literal['transimit', 'receive'] = 'receive',
                 files: Iterable[str] = None,
                 rx_dir: str = ".",
                 chunked: Literal['auto', 'false' 'true'] = '',
                 level: LEVEL = LEVEL.INFO
                 ):

        # Args
        self.ip = ip
        self.port = port
        self.chucked = chunked

        try:
            self.server_mode = (cs_mode.lower()[0] == 's')
            self.client_mode = (cs_mode.lower()[0] == 'c')
        except Exception:
            raise f"Invalid cs_mode {cs_mode}"

        try:
            self.transimit_mode = (txrx_mode.lower()[0] == 't')
            self.receive_mode = (txrx_mode.lower()[0] == 'r')
        except Exception:
            raise TypeError(f"Invalid cs_mode {cs_mode}")

        _txrx_mode = txrx_mode.lower()
        self.txrx_mode = None
        if len(_txrx_mode) > 0:
            if _txrx_mode[0] == 't':
                self.txrx_mode = 'transimit'
            elif _txrx_mode[0] == 'r':
                self.txrx_mode = 'receive'
        if not self.txrx_mode:
            raise TypeError(f"Invalid txrx_mode {txrx_mode}")

        self.files = files

        self.tx_files = {}
        self.rx_dir = rx_dir
        self.host = f"http://{ip}:{port}"

        # Objects
        self.messager = Messager(level, level, NewProgress=new_progress, NewProgressTrack=new_progress_track)
        self.app = Flask(self.__class__.__name__)

        # --------------------------------------------------------- #
        # ----------------------- Server TX ----------------------- #
        # --------------------------------------------------------- #
        @self.app.route('/<path:path_or_filename>', methods=['GET'])
        @self.app.route('/', methods=['GET'])
        def server_tx_file(path_or_filename=None):
            print("i:", path_or_filename)
            path = None

            # "/"
            if len(self.tx_files) == 1 and path_or_filename is None:
                path_or_filename = next(iter(self.tx_files))

            if path_or_filename is not None:
                path_or_filename = unquote(path_or_filename)
                path_or_filename = self.posixify_path(path_or_filename)

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

            print(path)

            if path is None or not os.path.isfile(path):
                return jsonify({"Error": f"File {path_or_filename} not found"}), 404
            elif isinstance(path, list):
                return jsonify({"Error": f"Multi files {path} exsit"}), 404
            else:
                # f = open(path, 'rb')

                progress = self.messager.new_progress()
                ff = FileProgressWrapper(path, progress=progress)
                filesize = ff.total

                headers = {}
                headers = HeadersHandle.set_Filename(filename, headers)
                headers = HeadersHandle.set_Size(filesize, headers)

                return Response(ff.read_generator(), headers=headers)

        # --------------------------------------------------------- #
        # ----------------------- Server RX ----------------------- #
        # --------------------------------------------------------- #

        @self.app.route('/', methods=['POST'])
        def servers_rx_file():
            # Save the file
            filename = HeadersHandle.get_Filename(request.headers)
            filesize = HeadersHandle.get_Size(request.headers)

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

    def start_server(self):

        print(f"Server started at {self.host}")

        self.app.run(host=self.ip, port=self.port)

        print(f"Server ended at{self.host}")

    def add_tx_files(self, paths):
        for path_or_filename in paths:
            path_or_filename = self.posixify_path(path_or_filename)
            if os.path.isdir(path_or_filename):
                path_or_filename = path_or_filename.rstrip(seq)

            basename = os.path.basename(path_or_filename)
            self.tx_files.setdefault(basename, [])
            self.tx_files[basename].append(path_or_filename)

        print(self.tx_files)

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
            response = requests.get(url, stream=True)

            if response.status_code == 200:
                self.messager.debug(response.headers)

                if not filename:
                    filename = HeadersHandle.get_Filename(response.headers)
                rx_filepath = os.path.join(self.rx_dir, filename) if not Config.isDevnull(self.rx_dir) else self.rx_dir

                file_size = HeadersHandle.get_ContentLength(response.headers)
                content = response.iter_content(chunk_size=Config.ChunkSize)
                with open(rx_filepath, 'wb') as f:
                    for chunk in self.messager.message_progress(content, total=file_size):
                        f.write(chunk)

                print(f"Downloaded: {filename}")
            else:
                print(f"Error downloading {filename}: {response.status_code} {response.json().get('Error')}")

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
            f = FileProgressWrapper(path, progress=progress)

            # Progress.wrap_file
            # f = open(path, 'rb')
            # if progress := self.messager.new_progress():
            #     progress: Progress
            #     f = progress.wrap_file(f, total=filesize)
            #     progress.start()
            response = requests.post(url, headers=headers, data=f.read_generator(), stream=True)
            # progress.stop()
            f.close()

            if response.status_code == 200:
                print(f"Uploaded: {filename}")
            else:
                print(f"Error Uploaded {filename}: {response.json().get('Error')}")

    def run(self):
        if not Config.isDevnull(self.rx_dir):
            os.makedirs(self.rx_dir, exist_ok=True)

        if self.server_mode:
            if self.transimit_mode:
                self.add_tx_files(self.files)
                self.start_server()

            elif self.receive_mode:
                self.start_server()
            else:
                print("Invalid mode. Use -t/--transmit for transmit or -r/--receive for receive.")

        elif self.client_mode:
            if self.transimit_mode:
                self.start_client_tx(self.files)

            elif self.receive_mode:
                self.start_client_rx(self.files)
            else:
                print("Invalid mode. Use -t/--transmit for transmit or -r/--receive for receive.")

        else:
            print("Invalid mode. Use -s for server or -c for client.")

    @staticmethod
    def posixify_path(path):
        return str(Path(path).as_posix())


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

    parser.add_argument("-d", "--rx_dir", metavar="<Dir>", type=str, default=Config.RX_DirPath, help="Path of directory to save received files")

    # IP and port
    parser.add_argument('[<IP>]:[<Port>]', help=f"Target IP address and optional port (default: {Config.IP}:{Config.Port})")

    # 解析接收路径或文件列表
    parser.add_argument('<File>', nargs='*', type=str, help="Files or paths to transmit or receive (default: .)")

    parser.add_argument("-v", "--verbose", action='store_true', help="Verbose output")
    parser.add_argument("-f", "--fast", action='store_true', help="Chunked transfer encoding")

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


if __name__ == "__main__":
    args = parse_args()
    print(args)
    cs_mode = 'server' if args.server else 'client'
    txrx_mode = 'transmit' if args.transmit else 'receive'
    level = LEVEL.DEBUG if args.verbose else LEVEL.INFO
    print(level)

    server = FileServerClient(args.ip, args.port, cs_mode, txrx_mode, args.paths, args.rx_dir, level, args.chunked)
    server.run()
