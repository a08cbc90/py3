# -*- coding: utf-8 -*-
#

r"""
K2.Gen
    klogin()
"""

import Base
import datetime, re, hashlib, base64
class Gen(
    Base.HttpClient,
):
    """ 金のジェネレータークラス2号君
    きっと使用メモリは 将来12GBくらいになる。
    """
    def __init__(self):
        """ 基礎情報の登録
        ドメイン名やら、データフォルダやらを書きまくるので少し長い。
        """
        Base.HttpClient.__init__(self)
        j = self.rj(self.i_conf)
        for x, y in j['K2.Gen'].items():
            x = "kg_" + x
            setattr(self, x, y)

        """ クッキーファイルパスは乗り換える """
        self.ht_cookie      = self.i_tmp_dir + '/' + self.kg_cookie
        self.k2_top_site    = self.kg_proto + self.kg_l_host + '.' + self.kg_domain + '/'
        self.k2_jso_site    = self.kg_proto + self.kg_i_host + '.' + self.kg_domain + '/'
        self.k2_data_dir    = self.kg_dat_dir
        self.make_dir(self.k2_data_dir)
        self.k2_js_fpx      = self.k2_data_dir + '/'
        self.k2_js_fsx      = datetime.datetime.now().strftime('%y%m%d') + self.kg_json_sx
        self.k2_js_f1       = self.k2_js_fpx + 'k2_3' +  self.k2_js_fsx
        self.k2_re          = re.I | re.M | re.U
        self.k2_login_post  = self.login_post_gen()
        self.k2_logfile     = self.i_log_dir + '/' + self.kg_logfile
        self.logger_add_file(self.k2_logfile)


    def login_post_gen(self):
        """ ログイン時に使用するPOSTデータの生成 """
        sstr = self.rf(self.kg_li_sec_f)

        """ 外部要素ridを計算する """
        ro = re.search(('%s\s*(\S+)' % self.kg_li_sec_d), sstr, self.k2_re)
        if ro:
            rid = hashlib.sha512(ro.group(1).encode()).digest()
        else:
            rid = hashlib.sha512(
                datetime.datetime.now().strftime('%y%m%d%S').encode()
            ).digest()

        """ 外部要素risを計算する """
        ro = re.search(('%s\s*(\S+)' % self.kg_li_sec_s), sstr, self.k2_re)
        if ro:
            ris = hashlib.sha512(ro.group(1).encode()).digest()
        else:
            ris = hashlib.sha512(
                datetime.datetime.now().strftime('%S%A%s').encode()
            ).digest()

        """ コンフィグの一部から ts と js を生成 """
        ts = hashlib.sha512(self.k2_top_site.encode()).digest()
        js = hashlib.sha512(self.k2_jso_site.encode()).digest()

        bytestream = ''
        """ 外部要素とコンフィグの一部を組み合わせて暗号素材を生成 """
        for i in [rid, ris]:
            for j in [ts, js]:
                p = hashlib.sha512(i + j).digest()
                bytestream += base64.b64encode(p).decode()

        """ 暗号素材の不要な文字を消去 """
        bytestream = re.sub(r'\W*', r'', bytestream)

        """ post骨格の成型 """
        post = self.kg_li_pos_b
        for i, j in [['D', r'"'], ['C', r':'], ['c', r',']]:
            post = re.sub(r'%s' % i, r'%s' % j, post)

        """ 暗号素材から要素のつまみ食い """
        bytestreamarray = list(bytestream)
        for i in self.kg_li_pos_a:
            s = ''
            for j in i:
                j = bytestreamarray[j]
                s += j
                bytestreamarray.remove(j)
            post = re.sub('S', s, post, 1)

        return post


    def klogin(self):
        """ ログインをするところ
        主目的はクッキーの保存
        """
        """ ログインの前にクッキーを消す 色々判定が面倒なのでイニシャライズすることに。 """
        self.rm(self.ht_cookie)

        """ 認証を開始 """
        data = self.download(
            self.k2_top_site + self.kg_li_tpsx,
            self.k2_top_site + self.kg_li_rfsx,
            None,
            self.k2_login_post
        ).decode("shift_jis")

        """ 認証の成功を確認する """
        rs_obj = re.search(self.kg_li_pat, data, self.k2_re)
        if not rs_obj:
            self.loge("ログインに失敗すた。")
            exit(4)

        """ ネクストホップアドレスの割り当て """
        next_url = self.k2_top_site + rs_obj.group()

        """ ネクストホップアドレスも踏んでcookieを完成させる """
        data = self.download(
            next_url,
            self.k2_top_site + self.kg_li_myp,
        ).decode()

        """ ネクストホップアドレスの正常性確認 """
        if not re.search(self.kg_li_n_pat, data, self.k2_re):
            self.loge("ネクストホップアドレス取得に失敗すた。")
            exit(5)

        return True



