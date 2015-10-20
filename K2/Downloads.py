# -*- coding: utf-8 -*-
#

r"""
このファイルは K2/__init__(K2.Gen)から呼び出される。
直接importしてもエラーが出まくる。(仕様)

K2.Downloads.Symbols
    シンボル関係のダウンロードをを行う
K2.Downloads.Jsons
    JSON関係のダウンロードをを行う(未実装!)
"""

import datetime, json
class Symbols():
    """ Symbol関係
    ダウンロードとか、割り当てとか
    それ及びそれにかかわる関数セット
    """
    def __init__(self):
        """ 初期化
        """
        j = self.rj(self.i_conf)
        for x, y in j['K2.Downloads.Symbols'].items():
            x = "kds_" + x
            setattr(self, x, y)
        self.sym = {}


    def kds_sec(self):
        """ 特殊なIntを取得 %sを千倍にしたstr
        2014/08/21  14:45:55 ならば
        str(14428143585) + "000" で "144281435000"
        """
        return datetime.datetime.now().strftime('%s000')


    def get_all_symboles(self):
        """ 全シンボルの取得
        固有シンボル + メインシンボル
        ただし、多数のアクセス不可能なシンボルも混ざっていることに注意
        """
        if not 'all' in self.sym:
            self.sym['all'] = self.kds_c_symbols + self.get_main_symboles()

        return self.sym['all']


    def get_main_symboles(self):
        """ メインシンボルの全取得
        ただし、多数のアクセス不可能なシンボルも混ざっていることに注意
        """
        """ GET SCR """
        j = self.download(
            self.k2_jso_site + self.kds_scr_dir + self.kds_sec(),
            self.k2_jso_site + self.kds_scr_rdir,
        )
        """ 取得できているか確認。だめぽなら空リストの返却 """
        try:
            j = j.decode()
        except:
            self.logw("メインシンボルの取得中ダウンロード失敗したお")
            return []

        if self.json_invalid(j):
            self.logw("メインシンボルの取得中JSON取得失敗したお")
            return []

        jl = json.loads(j)
        return sorted(jl[self.kds_model][self.kds_symbols].keys())



    def get_accessible_symboles(self):
        """ アクセス可能なシンボルの全取得
        但し調査に時間がかかる。
        そしてこの関数に意味があるのか。
        """
        ret = []
        for s in self.get_all_symboles():
            """ 実際に確認してみる """
            #ret.insert(0, s)
            ret.append(s)
        
        return ret


