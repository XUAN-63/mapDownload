import configparser

config=configparser.ConfigParser()
config.read('config.ini')

# 添加谷歌瓦片地址相关节
config.add_section('google-satellite')

config.set('google-satellite','url_CN','http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&')
config.set('google-satellite','url_MT','http://mt1.google.com/vt/lyrs=s&')


config.write(open("config.ini", "w"))

print('debug')