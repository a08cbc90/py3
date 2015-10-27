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
#print(C.DP)
exit()
""" 確認済み関数
print(C.klogin())
print(C.ht_counter_print())
g = C.get_accessible_symbols()
h = C.download_k2_summary(Z)
p = C.summary_picker(h)
print (C.deq_picker(i, p))
print(p)
print(C.s_sec_collection())
print(C.s_mst_collection())
print(C.s_elk_collection())
C.add_crts_gains()
"""
exit()




