#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-
#

r""" log/ ディレクトリをつくる。
"""

if __name__ != '__main__':
    print("Do as main.(exit)")
    exit()

import K2
C = K2.Gen()

g = C.get_accessible_symboles()
h = C.download_k2_summary(g[1997])
print(C.summary_picker(h))
exit()
print(C.klogin())
print(C.ht_counter_print())




