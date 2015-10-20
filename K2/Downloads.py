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

import datetime, json, re
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


    def download_k2_summary(self, symbol):
        """ サマリページのダウンロードをし、成功したらデータを返す
        """
        s = self.download(
            self.k2_jso_site + self.kds_sum_dir + symbol,
            self.k2_jso_site + self.kds_sum_r_dir,
        )
        return s.decode()


    def summary_picker(self, html):
        """ サマリページから各種情報のスクレイピング処理
        """
        p = {}
        """ sum_hkbの取得 """
        r = re.search(self.kds_sum_hkb_re, html, self.k2_re)
        if r:
            p[self.kds_sum_hkb] = int(re.sub(r',', '', r.group(2)))
        else:
            """ sum_hkb取得に失敗 またはsum_hkb概念が無いsymbol """
            p[self.kds_sum_hkb] = 0
            p[self.kds_sum_jks] = 0

        """ sum_secの取得 """
        r = re.search(self.kds_sum_sec_re, html, self.k2_re)
        if r:
            p[self.kds_sum_sec] = re.sub(r',', '', r.group(1))
            p[self.kds_sum_sec + '_'] = re.sub(r',', '', r.group(2))
        else:
            """ sum_sec取得に失敗 またはsum_sec概念が無いsymbol """
            p[self.kds_sum_sec] = ''
            p[self.kds_sum_sec + '_'] = ''
            
        return p


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


