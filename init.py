#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-
#

r""" log/ ディレクトリをつくる。
"""

if __name__ != '__main__':
    print("Do as main.(exit)")
    exit()

import Base
B = Base.Util()
C = Base.HttpClient()
''' normal download '''
C.download("http://docs.python.jp/3/library/urllib.request.html")
''' ref+ download '''
C.download("http://google.com/", "https://foo.bar.baz.jp/")
''' download + savefile '''
C.download("http://google.com/",None , "tmp/google_index.html")
print(C.ht_counter_print())




