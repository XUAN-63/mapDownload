import json
import math
import os
import random
import sys
import urllib.request

import numpy as np
from PIL import Image
from tqdm import tqdm, trange
from pyasn1.type.univ import Null


def latlon2px(z, lat, lon):
    x = 2**z*(lon+180)/360*256
    y = -(.5*math.log((1+math.sin(math.radians(lat))) /
                      (1-math.sin(math.radians(lat))))/math.pi-1)*256*2**(z-1)
    return x, y


def latlon2xy(z, lat, lon):
    x, y = latlon2px(z, lat, lon)
    x = int(x/256)  # ,int(x%256)
    y = int(y/256)  # ,int(y%256)
    return x, y


def swapValue(v1, v2):
    tmp = v1
    v1 = v2
    v2 = tmp
    return v1, v2


class map_Download():
    """
        瓦片地图下载的类
        下载指定区域指定缩放的瓦片图
        并将下载好的瓦片图拼接
    """

    def __init__(self):
        super().__init__()

        # google地球卫星瓦片地址
        googleSat_url = 'http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&'

        self.url_dict = {'google_sat': googleSat_url}

        # 瓦片地图的存储路径
        self.tiles_dir = ''
        # 合成后的图像名称
        self.merge_imgName = ''
        # 图像的缩放层级
        self.zoom = 1

        # 起始点的纬度和经度
        self.start_lat = 0.0
        self.start_lon = 0.0

        # 终止点的纬度和经度
        self.stop_lat = 0.0
        self.stop_lon = 0.0

        # 起始点的x, y坐标
        self._start_xy = []
        self._stop_xy = []

        # 地图的类型
        self.map_type = 'google_sat'

        # 瓦片地图的数量和命名
        self._rows = 0
        self._cols = 0


    def args_input(self,
                   start_latlon: float = ...,
                   stop_latlon: float = ...,
                   img_zoom: int = ...,
                   out_dir: str = ...,
                   img_type='google_sat',
                   img_name='merged.png'):
        """
            根据输入参数赋值类参数

        Arguments:
            start_latlon {list} -- 起始点[纬度,经度]
            stop_latlon {list} -- 终点[纬度,经度]
            img_zoom   {int} -- 地图的缩放层级
            out_dir {string} -- 瓦片地图的存储路径
            img_type {string} -- 地图的类型,默认谷歌卫星图
            img_name {string} -- 拼接后的文件名,默认"merged.png"
        """
        # 起始点的纬度和经度
        self.start_lat = start_latlon[0]
        self.start_lon = start_latlon[1]

        # 终止点的纬度和经度
        self.stop_lat = stop_latlon[0]
        self.stop_lon = stop_latlon[1]

        self.zoom = img_zoom

        # 瓦片地图的存储文件夹
        self.tiles_dir = out_dir

        # 拼接后的图像名称
        self.merge_imgName = img_name


    def get_xy(self):
        """
            计算区域起终点的坐标
        """
        # 起点和重点的瓦片坐标
        start_x, start_y = latlon2xy(self.zoom, self.start_lat, self.start_lon)
        stop_x, stop_y = latlon2xy(self.zoom, self.stop_lat, self.stop_lon)

        # 控制结束编号大于起始编号
        if(start_x > stop_x):
            start_x, stop_x = swapValue(start_x, stop_x)

        if(start_y, stop_y):
            start_y, stop_y = swapValue(start_y, stop_y)

        self._start_xy = [start_x, start_y]
        self._stop_xy = [stop_x, stop_y]



    def _info_write(self,
                    info_dir: str=''):
        """
            在瓦片文件夹中写入行列信息
        """
        info_path=''

        if info_dir=='':
            info_path=self.tiles_dir+'/info.json'
        else:
            info_path=info_dir+'/info.json'

        info = {"rows": self._rows, "cols": self._cols}

        with open(info_path, 'w') as f:
            json.dump(json.dumps(info), f)

    # ------------------------------------------------------------#
    
    def single_tile(self,
                    x: int,
                    y: int):
        """
            根据坐标下载单个瓦片      
        Arguments:
            x {int} -- x坐标
            y {int} -- y坐标
        
        Returns:
            png -- 返回下载的瓦片地图
        """                       
        
        map_url = self.url_dict[self.map_type]
        
        tiles_url = map_url+"x=" + \
                    str(x)+"&y="+str(y)+"&z="+str(self.zoom)


        try:
            req = urllib.request.urlopen(tiles_url, timeout=100)
            return req.read()
        except urllib.error.URLError as err:
            if hasattr(err, "code"):  # 判断状态码和原因
                print(err.code)
            if hasattr(err, 'reason'):
                print(err.reason)
            return Null
        
        
        

        




#-----------------------------------------------------------------------------------#  
    
    def tiles_download(self):
        """
            根据坐标下载区域内的瓦片地图
        """
        if (len(self._start_xy) == 0) | (len(self._stop_xy) == 0):
            self.get_xy()

        # 瓦片地图的编码
        id_x = 0
        id_y = 0

        # 瓦片地图起终点的xy坐标
        start_x, start_y = self._start_xy
        stop_x, stop_y = self._stop_xy

        map_url = self.url_dict[self.map_type]

        # 循环下载每个地图瓦片
        for x in tqdm(range(start_x, stop_x)):
            id_y = 0
            for y in range(start_y, stop_y):

                # 生成当前瓦片的地址链接
                tiles_url = map_url+"x=" + \
                    str(x)+"&y="+str(y)+"&z="+str(self.zoom)

                try:
                    req = urllib.request.urlopen(tiles_url, timeout=1000)
                except urllib.error.URLError as err:
                    if hasattr(err, "code"):  # 判断状态码和原因
                        print(err.code)
                    if hasattr(err, 'reason'):
                        print(err.reason)

                # 当前地图瓦片的文件名
                fname = self.tiles_dir+"/"+"tile-" + \
                    str(id_x)+"-"+str(id_y)+".png"
                with open(fname, "wb") as f:
                    f.write(req.read())

                id_y = id_y+1
            id_x = id_x+1

        # 设置瓦片地图的数量
        self.rows = id_x
        self.cols = id_y

        # 将信息写入json文件
        self._info_write()
    


    
    def tiles_merge(self,
                    in_dir='',
                    out_name='merged.png'):
        """将下载的瓦片地图拼接合并
        
        Keyword Arguments:
            in_dir {str} -- 瓦片地图的路径 (default: {''})
            out_name {str} -- 拼接后的图像路径 (default: {''})
        """
        if (in_dir == '') & (self.tiles_dir == ''):
            print('没有指定瓦片地图路径')
            exit(-1)
        if (out_name == '') & (self.merge_imgName == ''):
            print('没有指定的拼接图像路径')
            exit(-1)
        
        self.merge_imgName = self.tiles_dir+'/' + out_name

        # 如果类没有行列信息,则去读取json文件
        if (self._rows == 0) | (self._cols == 0):
            with open(self.tiles_dir+'/info.json') as f:
                img_info = json.loads(json.load(f))
                self._rows = img_info['rows']
                self._cols = img_info['cols']

        # 拼接后的图像
        merged_img = Image.new('RGBA', (self._rows*256, self._cols*256))

        for x in range(self._rows):
            for y in range(self._cols):
                # 当前瓦片的文件名
                cur_imgName = self.tiles_dir+'/' + \
                    'tile-'+str(x)+'-'+str(y)+'.png'
                cur_imgData = Image.open(cur_imgName)

                # 当前瓦片的放置坐标
                x_paste = x*256
                y_paste = y*256

                merged_img.paste(cur_imgData, (x_paste, y_paste))

        merged_img.save(self.merge_imgName)






if __name__ == '__main__':

    leftTop = [46.49, 6.6]
    rightDown = [46.53, 6.7]
    zoom = 15

    google_sat = map_Download()
    google_sat.args_input(leftTop, rightDown, zoom, 'image')
    # google_sat.tiles_download()
    google_sat.tiles_merge('image','merged.png')

    print('debug')
