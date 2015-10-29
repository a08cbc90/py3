# -*- coding: utf-8 -*-
#

r"""
このファイルは K2/__init__(K2.Gen)から呼び出される。
直接importしてもエラーが出まくる。(仕様)

K2.Downloads.Symbols
    シンボル関係のダウンロードをを行う
"""

import datetime, json, re, urllib.parse, itertools
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
        k  = "all-" + self.kds_symbols
        if not k in self.DC:
            self.DP[k] = self.kds_c_symbols + self.get_main_symbols()

        return self.DP[k]


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

        """ dup entry check """
        d = {}
        for s in sorted(jl[self.kds_model][self.kds_symbols].keys()):
            """ '%3A' -> ':' などにurl unescapeさせる """
            s = urllib.parse.unquote(s)
            r = re.search(self.kds_scr_regex, s)
            if r:
                if r.group(2) in d:
                    if d[r.group(1)] > self.kds_s_atr_prio.index(r.group(3)):
                        continue
                    else:
                        d[r.group(1)] = self.kds_s_atr_prio.index(r.group(3))
                else:
                    d[r.group(1)] = self.kds_s_atr_prio.index(r.group(3))
            else:
                """ 一致しない Symbolは無視！ """
                pass

        s_set = set()
        for s in d.keys():
            s_set.add(s + '-' + self.kds_s_atr_prio[d[s]])

        return sorted(list(s_set))


    def download_k2_summary(self, symbol):
        """ サマリページのダウンロードをし、成功したらデータを返す
        アクセス数: 1回
        """
        try:
            s = self.download(
                self.k2_jso_site + self.kds_sum_dir + symbol,
                self.k2_jso_site + self.kds_sum_r_dir,
            ).decode()
        except AttributeError:
            """ 取得が失敗するとstrではなくNoneを返すため.decode()はAttributeErrorを吐きだす """
            return None

        return s


    def summary_picker(self, html='', p={}):
        """ サマリページから各種情報のスクレイピング処理
        アクセス数: 0回
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
        try:
            s = self.download(
                self.k2_jso_site + self.kds_deq_dir + symbol + self.kds_deq_dir2 + self.kds_sec(),
                self.k2_jso_site + self.kds_sum_dir + symbol,
            ).decode()
        except AttributeError:
            """ 取得が失敗するとstrではなくNoneを返すため.decode()はAttributeErrorを吐きだす """
            return None

        return s

    def deq_picker(self, j="", p={}):
        """ deq(json)から各種情報のスクレイピング処理
        アクセス数: 0回
        j: json-string,
        p: return-dictionary,
        """
        if self.json_invalid(j):
            return p
        j = json.loads(j)
        for i in self.kds_deq_pickl:
            """ 登録されている項目はpに値を詰める """
            if i in j[self.kds_model]:
                p[i] = j[self.kds_model][i]
            else:
                p[i] = None

        """ lastがなければprecloseを入れる """
        self.kds_s_last = self.kds_s_last or self.kds_s_preclose

        if (self.kds_s_hkb in p and self.kds_s_hkb and
            self.kds_s_last  in p and self.kds_s_last
        ):
            p[self.kds_s_jks] = p[self.kds_s_hkb] * p[self.kds_s_last]

        return p


    def download_k2_crt(self, symbol, ctype=0):
        """ dec(JSON)のダウンロードをし、成功したらデータを返す
        アクセス数: 1回
        """
        period      = self.kds_crt_jpe_a[ctype]
        intrtval    = self.kds_crt_jiv_a[ctype]
        indicator   = self.kds_crt_jid_a
        try:
            c = self.download(
                self.k2_jso_site + self.kds_crt_dir,
                self.k2_jso_site + self.kds_crt_r_dir + symbol,
                None,
                self.kds_crt_jf % (symbol, period, intrtval, indicator)
            ).decode()
        except AttributeError:
            """ 取得が失敗するとstrではなくNoneを返すため.decode()はAttributeErrorを吐きだす """
            return None
        return c

    def crt_picker(self, j="", ctype=0):
        """ crt(json)から各種情報のスクレイピング処理
        アクセス数: 0回
        j: json-string,
        ctype: 添え字
        """
        if self.json_invalid(j):
            return False

        j = json.loads(j)
        """ 整合性の検証 """
        if not self.kds_success in j:
            """ successを取得できなかった場合 """
            return False
        else:
            if not j[self.kds_success]:
                """ success値が無い場合 """
                return False

        if not self.kds_model in j:
            """ modelを取得できなかった場合 """
            return False
        
        if not self.kds_series in j[self.kds_model]:
            """ seriesを取得できなかった場合 """
            return False
        elif type(j[self.kds_model][self.kds_series]) != list:
            """ seriesがlist型であることを確認 """
            return False

        if len(j[self.kds_model][self.kds_series][0][self.kds_data]) < self.kds_s_d_lim[ctype]:
            """ dataに格納されている標本数が制限値以下の場合 """
            return False

        return j


    def crt_dig_to_str(self, dig=0):
        """ 1000 で割って%s にする。
        アクセス数: 0回
        1442814358000 ならば 1442814358
        """
        return '%d' % (dig / 1000)


    def crt_create_data(self, cj, ctype):
        """ ctrデータを取得する
        アクセス数: 0回
        ctype は将来の拡張性のために書いてるだけで今は何の意味も無い
        """
        d = {}
        for x in range(len(self.kds_crt_d_set)):
            for y in cj[self.kds_model][self.kds_series][x][self.kds_data]:
                k = self.crt_dig_to_str(y[0])
                if not k in d:
                    d[k] = {}

                for z in range(len(self.kds_crt_d_set[x])):
                    d[k][self.kds_crt_d_set[x][z]] = y[z+1]

        return d


    def s_sec_collection(self):
        """ s_secの種類の数だけ集める。
        集めたデータは self.DP[self.kds_s_sec] で保存する
        """
        s_sec = set()
        k = "accessible-" + self.kds_symbols
        for s in self.DP[k]:
            if self.kds_s_sec in self.DP[k][s]:
                if self.DP[k][s][self.kds_s_sec]:
                    s_sec.add(self.DP[k][s][self.kds_s_sec])

        self.DP[self.kds_s_sec] = list(s_sec)
        return self.DP[self.kds_s_sec]


    def s_mst_collection(self):
        """ s_mstの種類の数だけ集める。
        集めたデータは self.DP[self.kds_s_mst] で保存する
        """
        s_mst = set()
        k = "accessible-" + self.kds_symbols
        for s in self.DP[k]:
            if self.kds_s_mst in self.DP[k][s]:
                if self.DP[k][s][self.kds_s_mst]:
                    s_mst.add(self.DP[k][s][self.kds_s_mst])

        self.DP[self.kds_s_mst] = list(s_mst)
        return self.DP[self.kds_s_mst]


    def s_elk_collection(self):
        """ s_elkの種類の数だけ集める。
        集めたデータは self.DP[self.kds_s_elk] で保存する
        """
        s_elk = set()
        k = "accessible-" + self.kds_symbols
        for s in self.DP[k]:
            if self.kds_s_elk in self.DP[k][s]:
                if self.DP[k][s][self.kds_s_elk]:
                    s_elk.add(self.DP[k][s][self.kds_s_elk])

        self.DP[self.kds_s_elk] = list(s_elk)
        return self.DP[self.kds_s_elk]


    def accessible_symbol(self, symbol):
        """ シンボルがアクセス可能かを判断する
        アクセス数: 最大で (3) 回
        アクセス可能であれば True を
        アクセス不可であれば False を返す
        """
        """ [大前提]特殊シンボルは検索しない """
        if not re.search(self.kds_scr_regex, symbol):
            return False

        """ まず、サマリを取得する """
        html = self.download_k2_summary(symbol)
        ctype = 0
        if not html:
            """ htmlを取得できなかった場合 """
            return False

        p = {}
        """ サマリHtmlからhkb, sec, mstだけ抽出 """
        p = self.summary_picker(html, p)

        """ 次にdeqを取得する """
        deq_json = self.download_k2_deq(symbol)
        if not deq_json:
            """ deqを取得できなかった場合 """
            return False

        """ deq-Jsonからlast, preclose等を抽出 """
        p = self.deq_picker(deq_json, p)

        """ 整合性の検証 """
        if not self.kds_s_last in p:
            """ lastを取得できなかった場合 """
            return False

        if p[self.kds_s_last] < self.kds_s_last_lim[ctype]:
            """ laseが最低限を満たしていない場合 """
            return False

        """ 最後にcrtを取得する"""
        cj = self.download_k2_crt(symbol, ctype)
        if not cj:
            """ crtを取得できなかった場合 """
            return False

        cj = self.crt_picker(cj, ctype)
        if cj:
            """ crt(cj)データが要求を満たせた場合
            新規要素 crt を作成する
            """
            crt = self.crt_create_data(cj, ctype)
        else:
            """ crt(cj)データが要求を満たせなかった場合 """
            return False

        return [p, crt]


    def get_accessible_symbols(self):
        """ アクセス可能なシンボルの全取得
        アクセス数: 最大で (3s) 回
        crtも取得し、一時ファイルとして保存する場合がある。
        一時ファイルの有効期限内ならばそれを読み込む場合がある

        """
        k = "accessible-" + self.kds_symbols
        if k in self.DP:
            """ すでに取得済みなら実施しない """
            return self.DP[k]

        self.DP[k] = {}
        savefile = self.i_tmp_dir + '/' + self.kds_crt_dat_nm
        if self.kds_crt_dat_lt:
            file_avail = self.file_timestamp_delay(savefile) / 60
            if file_avail > self.kds_crt_dat_lt:
                self.rm(savefile)
            else:
                """ そのデータを更新して返す """
                accessible_symbols_json = self.rf(savefile)
                accessible_symbols_json = json.loads(accessible_symbols_json)
                for key in accessible_symbols_json.keys():
                    setattr(self, key, accessible_symbols_json[key])

                return sorted(self.DP[k].keys())

        """
        for s in self.get_all_symbols()[2000:2119]:
        """
        for s in self.get_all_symbols():
            """ 各シンボルに対して3回のアクセスを実施して有用か否かを判断する """
            res = self.accessible_symbol(s)
            if res:
                """ データを格納すべきと判断された場合 DP,DC にデータを格納 """
                self.DP[k][s] = res[0]
                self.DC[s]    = res[1]

        """ s_sec をDPに追加情報として記述する """
        self.s_sec_collection()
        """ s_mst をDPに追加情報として記述する """
        self.s_mst_collection()
        """ s_elk をDPに追加情報として記述する """
        self.s_elk_collection()

        if self.kds_crt_dat_lt and file_avail > self.kds_crt_dat_lt:
            """ crt_dat_ltが設定されている場合
            かつ、期限が切れている場合ファイルに保存する """
            accessible_symbols_json = json.dumps({"DP": self.DP, "DC": self.DC})
            self.wf(savefile, accessible_symbols_json)

        return sorted(self.DP[k].keys())


    def add_crts_gains(self):
        """ 各crtデータから各利得を集計する。
        """
        for symbol in self.DC.keys():
            self.add_crt_gains(symbol)

        self.create_cd_templates()
        """ ここから """
        return None


    def add_crt_gains(self, symbol=None):
        """ シンボルを受け取り、self.DC内に利得情報を追加していく
        """
        if not symbol:
            return None

        delay_box = [None] * self.kds_cd_gen_num
        for datetimestring in sorted(self.DC[symbol].keys(), reverse=True):
            if delay_box[0]:
                """ delay_box[0] に値が入っている=2週目以降の場合 """
                """ gains はdatetime時の利得となる """
                gains = []
                for day_list in list(delay_box):
                    if day_list == None:
                        """ day_listにデータがなくなったらそのdatetimeは終了 """
                        break
                    """ day_list が存在している場合には下記の処理を実施 """
                    gains.append(
                        [day_list[0] / self.DC[symbol][datetimestring][self.kds_crt_d_set[0][3]] - 1, 
                         day_list[1] / self.DC[symbol][datetimestring][self.kds_crt_d_set[0][3]] - 1]
                    )

                """ delay_boxの中身を取り出したgainsを集計し終えたら流し込む """
                self.DC[symbol][datetimestring][self.kds_s_gain] = gains

            """ ここからは1周目から全て行う処理 """
            delay_box.insert(
                0,
                [
                    self.DC[symbol][datetimestring][self.kds_crt_d_set[0][1]],
                    self.DC[symbol][datetimestring][self.kds_crt_d_set[0][2]],
                ]
            )
            delay_box.pop()
            """ 閾値のオーバーシュート処理 """
            for n in range(1, self.kds_cd_gen_num):
                if not delay_box[n]:
                    """ 参照すべき値が無くなった """
                    break

                delay_box[n][0] = max(delay_box[n][0], delay_box[0][0])
                delay_box[n][1] = min(delay_box[n][1], delay_box[0][1])

        return symbol


    def create_cd_templates(self, ctype=0):
        """ カテゴリ別cd元データを作成する
        """
        for mst in  self.DP[self.kds_s_mst] + ['all']:
            for sec in self.DP[self.kds_s_sec] + ['all']:
                for elk in self.DP[self.kds_s_elk] + ['all']:
                    for cdstrset in list(itertools.chain.from_iterable(self.kds_crt_d_set[5:6])):
                        """ cdstrsetはKeyName(str) """
                        for generation in range(self.kds_cd_gen_num):
                            """ generationは世代数(int) """
                            for h in range(2):
                                """ h は配列添え字(int) """
                                self.create_cd_templates_ses(mst, sec, elk, cdstrset, generation, h)


    def create_cd_templates_ses(self, m=None, s=None, e=None, c=None, g=0, h=0):
        """ 関数にばらしてみたけど・・・ """
        if m and s and e and c:
            for sym in self.DC.keys():
                self.create_cd_templates_ses_s(m, s, e, c, g, h, sym)
            return True

        else:
            return None


    def create_cd_templates_ses_s(self, m=None, s=None, e=None, c=None, g=0, h=0, symbol=None):
        """ こういう書き方でいいのかねぇ・・・ """
        k = "accessible-" + self.kds_symbols
        if not symbol:
            return None

        if (
            (m == self.DP[k][symbol][self.kds_s_mst] or m == 'all') and
            (s == self.DP[k][symbol][self.kds_s_sec] or s == 'all') and
            (e == self.DP[k][symbol][self.kds_s_elk] or e == 'all')
        ):
            
            """ h[0, 1] -> l[1, 0] """
            l = 1 - h
            I = {"T":[], 'L':(0.5 - h) * 200, 'tt':0, 'bl':0, 'ht':0}
            for t in  sorted(self.DC[symbol].keys()):
                print(m, s, e, c, g, h, I, self.DC[symbol][t])

            exit()



                    

            return True
        else:
            return None























