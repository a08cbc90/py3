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


    def get_all_symbols(self):
        """ 全シンボルの取得
        アクセス数: (1回)
        固有シンボル + メインシンボル
        ただし、多数のアクセス不可能なシンボルも混ざっていることに注意
        """
        if not 'all' in self.sym:
            self.sym['all'] = self.kds_c_symbols + self.get_main_symbols()

        return self.sym['all']


    def get_main_symbols(self):
        """ メインシンボルの全取得
        ただし、多数のアクセス不可能なシンボルも混ざっていることに注意
        アクセス数: 1回
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
        アクセス数: 1回
        """
        s = self.download(
            self.k2_jso_site + self.kds_sum_dir + symbol,
            self.k2_jso_site + self.kds_sum_r_dir,
        ).decode()
        return s


    def summary_picker(self, html='', p={}):
        """ サマリページから各種情報のスクレイピング処理
        html: html-script,
        p: return-dictonary,
        """
        """ s_hkbの取得 """
        r = re.search(self.kds_sum_hkb_re, html, self.k2_re)
        if r:
            p[self.kds_s_hkb] = int(re.sub(r',', '', r.group(2)))
        else:
            """ s_hkb取得に失敗 またはs_hkb概念が無いsymbol """
            p[self.kds_s_hkb] = 0
            p[self.kds_s_jks] = 0

        """ s_secの取得 """
        r = re.search(self.kds_sum_sec_re, html, self.k2_re)
        if r:
            p[self.kds_s_sec] = re.sub(r',', '', r.group(1))
            p[self.kds_s_sec + '_'] = re.sub(r',', '', r.group(2))
        else:
            """ s_sec取得に失敗 またはs_sec概念が無いsymbol """
            p[self.kds_s_sec] = ''
            p[self.kds_s_sec + '_'] = ''
            
        """ s_mstの取得 """
        r = re.search(self.kds_sum_mst_re, html, self.k2_re)
        if r:
            p[self.kds_s_mst] = re.sub(r',', '', r.group(1))
            p[self.kds_s_mst + '_'] = re.sub(r',', '', r.group(2))
        else:
            """ s_mst取得に失敗 またはs_mst概念が無いsymbol """
            p[self.kds_s_mst] = ''
            p[self.kds_s_mst + '_'] = ''

        return p


    def download_k2_deq(self, symbol):
        """ dec(JSON)のダウンロードをし、成功したらデータを返す
        アクセス数: 1回
        """
        s = self.download(
            self.k2_jso_site + self.kds_deq_dir + symbol + self.kds_deq_dir2 + self.kds_sec(),
            self.k2_jso_site + self.kds_sum_dir + symbol,
        ).decode()
        return s

    def deq_picker(self, j="", p={}):
        """ deq(json)から各種情報のスクレイピング処理
        j: json-string,
        p: return-dictionary,
        """
        if self.json_invalid(j):
            return p
        j = json.loads(j)
        print (p, self.kds_deq_pickl)
        for i in self.kds_deq_pickl:
            """ 登録されている項目はpに値を詰める """
            if i in j[self.kds_model]:
                p[i] = j[self.kds_model][i]
            else:
                p[i] = None

        if (self.kds_s_hkb in p and self.kds_s_hkb and
            self.kds_s_last  in p and self.kds_s_last
        ):
            p[self.kds_s_jks] = p[self.kds_s_hkb] * p[self.kds_s_last]

        return p


    def accessible_symbol(self, symbol):
        """ シンボルがアクセス可能かを判断する
        アクセス可能であれば True を
        アクセス不可であれば False を返す
        """
        return False


    def get_accessible_symbols(self):
        """ アクセス可能なシンボルの全取得
        アクセス数: 最大で 2s 回

        但し調査に時間がかかる。
        そしてこの関数に意味があるのか。
        """
        ret = []
        for s in self.get_all_symbols():
            """ 実際に確認してみる """
            #ret.insert(0, s)
            if self.accessible_symbol(s):
                ret.append(s)

        return ret



