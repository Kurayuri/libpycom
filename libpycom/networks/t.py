from time import sleep
from urllib.request import urlopen
import os
from rich.progress import Progress, BarColumn, TaskProgressColumn, TimeElapsedColumn, TimeRemainingColumn, RenderableColumn, SpinnerColumn, TransferSpeedColumn, DownloadColumn

from rich.progress import wrap_file

response = open("/home/kurayuri/App.tar",'rb')
# size = int(response.headers["Content-Length"])

progress=  Progress(
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

with progress:
    with progress.wrap_file(response, os.path.getsize("/home/kurayuri/App.tar")) as file:
        for line in file:
            print(line.decode("utf-8"), end="")
            sleep(0.1)