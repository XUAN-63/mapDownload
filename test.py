import random
import urllib3
import urllib

import urllib.request
import requests
from urllib3.contrib.socks import SOCKSProxyManager
import urllib3.contrib.pyopenssl
import certifi

from urllib import request

mt_url='http://mt1.google.com/vt/lyrs=s&'

map_url = 'http://www.google.com/maps/vt?lyrs=s@189&gl=cn&'
        
tiles_url = mt_url+"x=" + \
                    str(33969)+"&y="+str(23175)+"&z="+str(16)

tiles_url2=map_url+"x=" + str(33969)+"&y="+str(23175)+"&z="+str(16)
proxies = [{'http':'socks5h://127.0.0.1:1080'},
                   {'https':'socks5h://127.0.0.1:1080'}]
proxy = proxies[0]


header={'User-Agent': 
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'}



proxy = SOCKSProxyManager('socks5://localhost:1080/',headers=header,timeout=urllib3.Timeout(connect=10.0, read=20.0))


#req=urllib.request.Request(tiles_url,headers=header)

#req1=requests.get(tiles_url,headers=header,timeout=1000)
#response = urllib.request.urlopen(req,timeout=1000)
req=proxy.urlopen('GET',tiles_url)


http=urllib3.PoolManager(num_pools=2, headers=header,timeout=100)
req1=http.urlopen('GET',tiles_url2)



#req  = urllib.request.Request(tiles_url,headers=header)

print('debug')

