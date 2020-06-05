import os
import urllib.request


class TilesDownloader():
    """
        瓦片地图下载器
    """

    def __init__(self):
        super().__init__()
        
        self.enableProxy=False
        self.imgsPath=""



    def download(self):
        
        try:
            req = urllib.request.urlopen(tiles_url, timeout=1000)
        except urllib.error.URLError as err:
            if hasattr(err, "code"):  # 判断状态码和原因
                print(err.code)
            if hasattr(err, 'reason'):
                print(err.reason)


if __name__ == "__main__":
    print(os.path.dirname(__file__))
    