#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-
#

r""" K2Classのテスト用として当面利用中
"""

if __name__ != '__main__':
    print("Do as main.(exit)")
    exit()

import K2
C = K2.Gen()
print("JsonLoaded?: " + C.ht_url)
g = C.get_accessible_symbols()
print(C.DP)
exit()
"""
g = C.get_accessible_symbols()
h = C.download_k2_summary(Z)
p = C.summary_picker(h)
print (C.deq_picker(i, p))
print(p)
"""
exit()
print(C.klogin())
print(C.ht_counter_print())




