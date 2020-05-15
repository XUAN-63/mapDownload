# -*- coding: utf-8 -*-
import os
import sys
import time
import json

from PIL import Image, ImageFile

from PyQt5 import QtGui
from PyQt5.QtCore import QObject, QSettings, Qt, QThread, QUrl, pyqtSlot,pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QApplication, QFileDialog, QGraphicsPixmapItem,
                             QGraphicsScene, QMainWindow, QMessageBox)

from pyMap import map_Download
from PyQt5Ui.Ui_mainWindows import Ui_MainWindow


class ui_tileDownload(QThread, map_Download,QMainWindow):
    def __init__(self, argsList, parent=None):
        """
            界面化地图下载类
            采用多线程

        Arguments:
            QThread {class} -- 线程类
            argsList {list} -- 参数列表
            [起始纬度, 起始经度, 终止纬度, 终止经度]

        """
        super().__init__(parent=parent)

        # 起始点得纬度和经度
        self.start_lat = float(argsList[0])
        self.start_lon = float(argsList[1])

        # 终止点的纬度和经度
        self.stop_lat = float(argsList[2])
        self.stop_lon = float(argsList[3])

        # 地图缩放层级
        self.zoom = int(argsList[4])

        # 瓦片地图的存放路径
        self.tiles_dir = argsList[5]



    proValue = pyqtSignal(int)
    # 重载父类方法
    def run(self):

        # 当前缩放层级的文件夹
        zoom_dir=self.tiles_dir+'/zoom'+str(self.zoom)

        # 新建当前缩放层级的文件夹
        if (not os.path.exists(zoom_dir)):
            os.mkdir(zoom_dir)

        # 计算瓦片地图坐标
        super().get_xy()

        start_x, start_y = self._start_xy
        stop_x, stop_y = self._stop_xy

        # 计算文件行列
        self._rows = stop_x-start_x
        self._cols = stop_y-start_y

        # x坐标跨度
        scale = stop_x-start_x

        for x in range(start_x, stop_x):
            for y in range(start_y, stop_y):
               
                # 当前瓦片编码     
                tile_name = zoom_dir+'/' "tile-" + \
                    str(x-start_x)+"-"+str(y-start_y)+".png"

                if (not os.path.exists(tile_name)):
                    # 下载当前位置瓦片
                    tile_png = super().single_tile(x, y)
                    # 写入磁盘
                    with open(tile_name,'wb') as f:
                        f.write(tile_png)
                   
                    # 延时1s,防止ip被封
                    time.sleep(1.0)

                # 进度信息
                proIdx = int(((x-start_x)/scale)*100.0)

                # 回调进度条
                self.proValue.emit(proIdx)

        self._info_write(zoom_dir)

        self.proValue.emit(100)


class mergerimg_Thread(QThread):

    def __init__(self, 
                in_dir:str,
                out_name:str='merged.png',
                parent=None):
        super().__init__(parent=parent)

        self.tiles_dir=in_dir
        self.merged_name=out_name

    proValue=pyqtSignal(int)
    def run(self):
        merged_path=self.tiles_dir+'/'+self.merged_name

        # 读取文件的行列信息
        rows=0;cols=0
        with open((self.tiles_dir+'/info.json'),'r') as f:
            imgs_info=json.loads(json.load(f))
            rows=imgs_info['rows']
            cols=imgs_info['cols']

        mergedMat=Image.new('RGBA', (rows*256, cols*256))
        
        # 读取所有的地图瓦片进行合并
        for x in range(rows):
            for y in range(cols):
                # 当前瓦片的文件名
                cur_imgName = self.tiles_dir+'/' + \
                    'tile-'+str(x)+'-'+str(y)+'.png'
                cur_imgData = Image.open(cur_imgName)

                # 当前瓦片的放置坐标
                x_paste = x*256
                y_paste = y*256

                mergedMat.paste(cur_imgData, (x_paste, y_paste))

                proIdx = int((x/rows)*100.0)

                self.proValue.emit(proIdx)
        
        # 完成拼接,写入文件
        mergedMat.save(merged_path)
        self.proValue.emit(100)


class TInteractObj(QObject):
    """
    一个槽函数供js调用(内部最终将js的调用转化为了信号),
    一个信号供js绑定,
    这个一个交互对象最基本的组成部分.
    """

    # 定义信号,该信号会在js中绑定一个js方法.
    sig_send_to_js = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 交互对象接收到js调用后执行的回调函数.
        self.receive_str_from_js_callback = None

    # str表示接收str类型的信号,信号是从js发出的.
    @pyqtSlot(str)
    def receive_str_from_js(self, str):
        self.receive_str_from_js_callback(str)


class mywin(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        super(mywin, self).__init__(parent)
        self.setupUi(self)

        # 初始化界面
        self.initUI()

        # ------- 连接各控件功能-------
        self.signal_Connect()

    def initUI(self):
        '''----测试数据----'''
        # --函数测试通过删除

        self.ledit_StartLat.setText(str(46.49))
        self.ledit_StartLon.setText(str(6.6))
        self.ledit_StopLat.setText(str(46.53))
        self.ledit_StopLon.setText(str(6.7))
        self.spinBox_zoom.setValue(15)

        #testWeb=myClass()
        #self.browser=QWebEngineView()
        #self.browser=QWebEngineView(self.centralwidget)
        #self.browser.setObjectName("browser_test")
        #self.gridLayout.addWidget(self.browser,0,1,2,1)
        #myChannel=QWebChannel()
        
        #self.browser.page().setWebChannel(myChannel)
        #myChannel.registerObject('testObject',testWeb)
        #self.browser.load(QUrl('E:///PySpace/tilesMap/index.html'))
        #self.browser.show()
        self.webBrowser.load(QUrl.fromLocalFile(os.path.abspath('./map/map.html')))
        self.interact_obj=TInteractObj(self)
        self.interact_obj.receive_str_from_js_callback = self.receive_data

        channel=QWebChannel(self.webBrowser.page())
        channel.registerObject("interact_obj",self.interact_obj)
        self.webBrowser.page().setWebChannel(channel)
    

    def receive_data(self, data):
        import math
        box_dict=json.loads(data)
        box_point=box_dict['features'][0]['geometry']['coordinates'][0]

        Lon_list=[]
        Lat_list=[]
        for ii in range(0,4):
            Lon_list.append(box_point[ii][0])
            Lat_list.append(box_point[ii][1])
        
        rightDownLon=max(Lon_list)
        rightDownLat=max(Lat_list)

        leftUpLon=min(Lon_list)
        leftUpLat=min(Lat_list)

        self.ledit_StartLat.setText(str(round(leftUpLat,2)))
        self.ledit_StartLon.setText(str(round(leftUpLon,2)))

        self.ledit_StopLat.setText(str(round(rightDownLat,2)))
        self.ledit_StopLon.setText(str(round(rightDownLon,2)))
        
    
    @pyqtSlot()
    def on_pushButton_clicked(self):
        self.interact_obj.sig_send_to_js.emit(self.webBrowser.toPlainText())
    
        
    def signal_Connect(self):

        # 文件夹选择按钮
        self.tbu_DirDiaglog.clicked.connect(self.open_downloadDir)

        # 下载按钮
        self.pBu_Download.clicked.connect(self.download_map)

        # 拼接文件夹选择按钮
        self.tbu_megerDir.clicked.connect(self.open_megerDir)

        # 拼接按钮
        self.pBu_Merge.clicked.connect(self.merge_tilesImg)

    
    def open_downloadDir(self):
        # 选择瓦片地图存储地址

        dir_dialog = QFileDialog.getExistingDirectory(self, caption='选择文件夹')
        self.cbox_TilesDir.addItem(dir_dialog)
        
    def open_megerDir(self):
        merge_dir=QFileDialog.getExistingDirectory(self,caption='选择需要合并的文件夹')
        self.cbox_Merge.addItem(merge_dir)
        self.cbox_Merge.setCurrentText(merge_dir)
    
    def download_map(self):

        # -----获取各输入框的数字---------

        # 起始点的纬度
        start_lat = self.ledit_StartLat.text()
        if (not start_lat.replace('.', '').isdigit()):
            print('输入的起始纬度有误')

        # 起始点的经度
        start_lon = self.ledit_StartLon.text()
        if (not start_lon.replace('.', '').isdigit()):
            print('输入的起始经度有误')

        # 终点的纬度
        stop_lat = self.ledit_StopLat.text()
        if (not stop_lat.replace('.', '').isdigit()):
            print('输入的终止纬度有误')

        # 终点的经度
        stop_lon = self.ledit_StopLon.text()
        if (not stop_lon.replace('.', '').isdigit()):
            print('输入的终止经度有误')

        # 缩放系数
        zoom = self.spinBox_zoom.value()

        # 参数列表
        paraList = [start_lat,
                    start_lon,
                    stop_lat,
                    stop_lon,
                    zoom,
                    self.cbox_TilesDir.currentText()]

        # 开一个线程进行地图下载
        self.backend = ui_tileDownload(paraList)
        self.backend.proValue.connect(self.handleProgress)
        self.backend.start()



    def merge_tilesImg(self):
        
        meger_dir=self.cbox_Merge.currentText()

        self.backend=mergerimg_Thread(meger_dir)
        self.backend.proValue.connect(self.handleProgress)
        self.backend.start()

        self.backend.finished.connect(lambda:self.viewRes(meger_dir))
    
    def viewRes(self,img_dir):
        ImageFile.LOAD_TRUNCATED_IMAGES = True

        img=Image.open(img_dir+'/merged.png')
        img=img.convert('RGB')
        x = img._size[0]                                      #获取图像大小
        y = img._size[1]
        img=img.tobytes('raw','RGB')
        
        
        zoomscale=1                                        #图片放缩尺度
        
        frame = QImage(img, x, y, QImage.Format_RGB888)
        pix = QPixmap.fromImage(frame)
        self.item=QGraphicsPixmapItem(pix)                      #创建像素图元
        #self.item.setScale(self.zoomscale)
        self.scene=QGraphicsScene()                             #创建场景
        self.scene.addItem(self.item)
        self.graphics_Mapview.setScene(self.scene)


        print('debug')

    def handleProgress(self, data: int):
        """处理抛出线程

        Arguments:
            data {int} -- 当前进度值
        """

        self.progressBar.setValue(data)





if __name__ == '__main__':
   
    app = QApplication(sys.argv)
    myui = mywin()
    myui.show()
    sys.exit(app.exec_())
    print('debug')
