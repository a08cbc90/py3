# -*- coding: utf-8 -*-
#

r""" 基本関数一式
end-if: A blank line
end-for: A blank line
end-def: 2 blank lines
end-class: 3 blank lines

http
+ util

"""

import json, os, re, gzip, logging
class Util():
    """ Utilは他の Classes が継承しやすいように初めのほうに
    書く必要がある。
    """
    def __init__(self):
        """ BaseEnv
        最低限の設定であり、他のinitで上書きしない前提の属性とする
        Base.Util:
            i_conf    :  コンフィグファイル位置(あまり変えたくない)'./conf/config.json'
            i_log_dir :  ログディレクトリ
            i_conf_dir: コンフィグディレクトリ(あまり変えたくない)'./conf'
            i_tmp_dir :  一時ディレクトリ
        """
        self.i_conf = 'conf/config.json'
        j = self.rj(self.i_conf)
        for atr, val in j['Base.Util'].items():
            setattr(self, atr, val)

        for dir in [self.i_log_dir, self.i_conf_dir, self.i_tmp_dir]:
            self.make_dir(dir)

        self.L = logging.getLogger('Util')
        self.logger_init()
        self.i_log_path = self.i_log_dir + '/BaseUtil.log'
        self.logger_add_file(self.i_log_path)


    def logger_init(self):
        """ ロガーを生成する関数 """
        """ ロギングフォーマッタ(共通) """
        self.LF = logging.Formatter(
            fmt     = '%(asctime)s %(levelname)s: %(message)s',
            datefmt = '%y/%m/%d %H:%M:%S'
        )

        """ ロガーを生成 """
        self.L = logging.getLogger('util')
        """ このロガーが判断するエラーレベル """
        self.L.setLevel(logging.DEBUG)

        """ STDERRの設定 """
        create_logging_handler_stderr = logging.StreamHandler()
        """ STDERRが判断するエラーレベル """
        create_logging_handler_stderr.setLevel(logging.DEBUG)
        """ このハンドラにフォーマッタ(共通)を登録する """
        create_logging_handler_stderr.setFormatter(self.LF)

        """ STDERRを生成したロガーに組み込む """
        self.L.addHandler(create_logging_handler_stderr)
        return True


    def logger_add_file(self, filepath=None):
        """ STDERRに出力されるロガーにファイルロギングも追加する """
        if not filepath:
            return False
        """ ハンドラの作成(ファイルハンドラ) """
        create_logging_handler_file = logging.FileHandler(filename=filepath, mode='a')
        """ このハンドラが判断するエラーレベル """
        create_logging_handler_file.setLevel(logging.INFO)
        """ このハンドラにフォーマッタ(共通)を登録する """
        create_logging_handler_file.setFormatter(self.LF)
        """ このハンドラをロガーに組み込む """
        self.L.addHandler(create_logging_handler_file)
        return True


    def logd(self, string):
        """ ロギング
        self.i_log_path にロギングする(DEBUG)
        """
        self.L.debug(string)


    def loge(self, string):
        """ ロギング&プリント
        self.i_log_path にロギングする(ERROR)
        """
        self.L.error(string)


    def logw(self, string):
        """ ロギング&プリント
        self.i_log_path にロギングする(WARNING)
        """
        self.L.warning(string)


    def json_valid(self, json_str=""):
        """ JSONとして成立して無ければFalse
        JSONとして正しいstringならTrueを返す
        """
        if not json_str:
            """ 変数が存在しない場合 True """
            return False

        if type(json_str) is bytes:
            try:
                """ bytes型はstrに変更できれば通過 """
                json_str = json_str.decode()
            except:
                """ 変更 できない場合False """
                return False
        elif type(json_str) is str:
            """ str型はそのまま """
            pass
        else:
            """ str型でない場合 True """
            return False

        try:
            json.JSONDecoder().decode(json_str)
        except TypeError:
            """ 何らかの型異常 """
            return False
        except ValueError:
            """ Json構文エラー """
            return False

        return True


    def json_invalid(self, json_str=""):
        """ JSONとして成立して無ければTrue
        JSONとして正しいstringならFalseを返す
        """
        return not self.json_valid(json_str)


    def make_dir(self, path):
        """ path(ディレクトリ)を再帰的に作成
        成功時: pathを返す
        失敗時: Noneを返す
        """
        try:
            os.makedirs(path)
        except FileExistsError:
            return None

        return path


    def dir_exist(self, path):
        """ path がディレクトリで存在すればTrue
        そうでなければFalse
        """
        return os.path.isdir(path)


    def file_exist(self, filepath):
        """ path がFileで存在すればTrue
        そうでなければFalse
        """
        return os.path.isfile(filepath)


    def rj(self, filepath='/dev/null', errstop=True):
        """ ReadJson
        filepath の中身がjsonだと仮定して取得を試み
        読み込んだ内容を返す。
        試験内容:
            filepathを入れてない場合: None(正常)
            filepathが存在しない場合: None(正常)
            json形式ではない場合: ValueError/AttributeError: None
        """
        if not self.file_exist(filepath):
            return None
        
        try:
            with open(filepath) as jp:
                j = json.load(jp)
        except AttributeError: 
            if errstop:
                raise
            return None
        except ValueError: 
            if errstop:
                raise
            return None

        return j


    def wf(self, filepath=None, string=None, compress=False):
        """ WriteFile
        String または bytes型の場合のみをファイルに書き込む。
        そこまでのDirが用意されていなくてもDirを作るように努力する
        試験項目:
            filepathがNone: Noneを返す
            stringがNone: 空ファイルを作成しようとする
        """
        if not filepath:
            """ パスが存在しない場合処理しない """
            return None

        if not string:
            """ 指定がない場合、空ファイルを作成する """
            string = ""

        """ ディレクトリ部分の検出 """
        hit = re.match("/.*/", filepath)
        if hit:
            dir_path = hit.group()
        else:
            """ ディレクトリ部分がない場合、カレントディレクトリとして処理する """
            dir_path = "./"

        if not self.dir_exist(dir_path):
            """ ディレクトリの作成、パーミッションエラーが発生すると止まる """
            self.make_dir(dir_path)

        if compress:
            if type(string) is str:
                """ 書き込み内容がStr型の場合Bin型に変更する """
                string = string.encode()
                string = gzip.compress(string, compresslevel=6)
            else:
                """ 書き込み内容がStr型でない場合は圧縮をしない """
                pass

        if type(string) is str:
            """ Str型の場合 """
            with open(filepath, "w") as fp:
                fp.write(string)
        elif type(string) is bytes:
            """ バイナリの場合 """
            with open(filepath, "wb") as fp:
                fp.write(string)
        else:
            """ それ以外の型の場合何もしない """
            return None

        """ 正常に終了した場合はその文字を返す """
        return string


    def af(self, filepath=None, string=None):
        """ AddFile
        String または bytes型の場合のみをファイルに追記する。
        そこまでのDirが用意されていなくてもDirを作るように努力する
        圧縮オプションは搭載しない
        正常終了時は、追記した部分のみStringを返す
        """
        if not filepath:
            """ パスが存在しない場合処理しない """
            return None

        if not string:
            """ 指定がない場合、空ファイルを作成する """
            string = ""

        """ ディレクトリ部分の検出 """
        hit = re.match("/.*/", filepath)
        if hit:
            dir_path = hit.group()
        else:
            """ ディレクトリ部分がない場合、カレントディレクトリとして処理する """
            dir_path = "./"

        if not self.dir_exist(dir_path):
            """ ディレクトリの作成、パーミッションエラーが発生すると止まる """
            self.make_dir(dir_path)

        if type(string) is str:
            """ Str型の場合 """
            with open(filepath, "a") as fp:
                fp.write(string)
        elif type(string) is bytes:
            """ バイナリの場合 """
            with open(filepath, "ab") as fp:
                fp.write(string)
        else:
            """ それ以外の型の場合何もしない """
            return None

        """ 正常に終了した場合はその文字を返す """
        return string


    def rf(self, filepath=None, compress=False):
        """ ReadFile
        ファイルをStringとして読み込む
        2015/09/23 zip対応
        """
        if not self.file_exist(filepath):
            """ 存在しない場合は None を返す """
            return None

        if compress:
            with open(filepath, "rb") as fp:
                data = fp.read()
                data = gzip.decompress(data).decode()
        else:
            with open(filepath) as fp:
                data = fp.read()

        return data


    def rm(self, filepath=None):
        """ REmove
        ファイルを削除する。消えたかどうかは判定しない
        """
        try:
            os.remove(filepath)
        except:
            return None

        return None


    def epoch_second_to_ymdhms(self, epochsec=0):
        """ 1417651200 -> '2014/12/04 09:00:00' """
        return datetime.datetime.fromtimestamp(int(epochsec)).strftime("%Y/%m/%d %H:%M:%S")


    def file_timestamp_delay(self, path=None):
        """ ファイルのModifyタイムスタンプが現在から何秒ずれているかを整数で返す
        ファイルが無い場合は 1900年前との差を返す。
        未来のタイムスタンプであれば 数値は負の整数に成る。
        """
        """ t = 現在時刻[sec] """
        t = datetime.datetime.now().strftime('%s')
        if not self.file_exist(path):
            """ ファイルが存在しない場合 """
            return int(t)

        return int(int(t) - os.stat(path).st_mtime)


import http.cookiejar, urllib, gzip, datetime, time, socket
class HttpClient(Util):
    """ 汎用的なhttp[s]通信ができるClassを目指す
    """
    def __init__(self):
        """ http[s]用の変数
        ht_url: デフォルトのURL
        ht_referer:    デフォルトのリファラ
        ht_output_path: デフォルトの保存先
        ht_ua:  デフォルトのクライアント
        ht_cookie: デフォルトのクッキーファイル
        ht_cookie_jarnal: Mozilla形式のクッキー定義
        ht_log_level: デフォルトのログレベル
        ht_log_path: デフォルトのログ保存位置
        ht_header: 実際に使用するヘッダー共通部分
        ht_counter: このクラスを使用した際の履歴を記憶する。
        """
        Util.__init__(self)
        j = self.rj(self.i_conf)
        for x, y in j['Base.HttpClient'].items():
            setattr(self, x, y)

        """ ht_log_path = './log/foobar.log' """
        self.ht_log_path = self.i_log_dir + '/' + self.ht_log_file
        """ ht_cookie   = './tmp/foobaz.cookie' """
        self.ht_cookie   = self.i_tmp_dir + '/' + self.ht_cookie
        """ ヘッダーにUserAgentの項目を追記 """
        self.ht_header['User-Agent'] = self.ht_ua
        self.ht_cookie_jarnal = http.cookiejar.MozillaCookieJar()
        self.logger_add_file(self.ht_log_path)


    def ht_counter_print(self):
        """ 
        統計情報のサマリとエラーログを表示
        """
        """ 全行表示は如何なものか
        for error_ary in self.ht_counter['fail_description']:
            self.logw("%s ErrCode: %d, Descroption: '%s'" % error_ary)
        """
        self.logw("%s ErrCode: %d, Descroption: '%s'" % self.ht_counter['fail_description'][-1])

        for i in ["total", "post", "fail"]:
            self.logw("%s:\t\t%d" %(i, self.ht_counter[i]))

        return None


    def ht_load_cookie(self, *unknown_args, **unknown_dicts):
        """ クッキーを読み込む
        """
        if self.file_exist(self.ht_cookie):
            self.ht_cookie_jarnal.load(self.ht_cookie, ignore_discard=True, ignore_expires=False)


    def ht_save_cookie(self, *unknown_args, **unknown_dicts):
        """ クッキーを保存する
        """
        if self.ht_cookie_jarnal:
            self.ht_cookie_jarnal.save(self.ht_cookie, ignore_discard=True, ignore_expires=False)


    def download(self, url=None, referer=None, output=None, post_string=None):
        """ クッキー対応ダウンロード
        post_string を指定していない場合GETとしてダウンロードする
        output をしていない場合ファイル保存しない
        ダウンロードしたデータは return で返す。
        """
        """ ダウンロード回数を1回増やす """
        self.ht_counter['total'] += 1
        """ url 指定が無ければ self.ht_url を使用する """
        url = url or self.ht_url
        if not url:
            """ それでもurl指定が無い場合 """
            """ エラー回数を1回増やす """
            self.ht_counter['fail'] += 1
            """ エラー内容の記載 """
            self.ht_counter['fail_description'].append((date_time, -4, "url not specified."))
            return None

        """ referer 指定が無ければ self.ht_referer を使用する """
        referer = referer or self.ht_referer or None
        """ cookie を ファイルから読み込む"""
        self.ht_load_cookie()
        """ クッキーの組み込み準備 (Mozila形式) """
        urhcp = urllib.request.HTTPCookieProcessor(self.ht_cookie_jarnal)
        """ OpenerDirectorインスタンスの作成 """
        urbo  = urllib.request.build_opener(urhcp)
        """ OpenerDirectorインスタンスをurlopen用に連結 """
        urio  = urllib.request.install_opener(urbo)

        """ デフォルトのヘッダーテンプレートをコピー(そのまま使うと後が大変) """
        headers = dict(self.ht_header)

        """ POST用のオブジェクト初期化 """
        post_obj = None

        if post_string: # POSTデータがある場合
            """ POSTデータがある場合 """
            """ POSTダウンロード回数を1回増やす """
            self.ht_counter['post'] += 1
            if type(post_string) is bytes:
                """ bytes型ならそのまま(json形式を意識) """
                post_obj = post_string
                if self.json_valid(post_string):
                    """ 中身がJsonの場合 """
                    """ header に json 追加 """
                    headers['Content-Type'] = 'application/json'
            elif type(post_string) is str:
                """ str型ならbytes型に変換する """
                post_obj = post_string.encode()
                """post_string がJsonとして成立するかを確認する必要がある"""
                if self.json_valid(post_string):
                    """ 中身がJsonの場合 """
                    """ header に json 追加 """
                    headers['Content-Type'] = 'application/json'
            else:
                """ POSTオブジェクトが辞書形式の場合 """
                """ POST用のオブジェクトを作成 """
                post_obj = urllib.parse.urlencode(post_string).encode(encoding='ascii')

        if referer:
            """ リファラーがある場合 """
            """ header に referer 追加 """
            headers['Referer'] = referer

        """ エラーがあった場合に備えて時刻の取得 """
        date_time = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

        for retry in range(self.ht_retry - 1, -1, -1):
            if self.download_interval:
                """ ダウンロード間隔が定められている場合はここで調整 """
                time.sleep(self.download_interval)

            try:
                """ リクエストobj作成 """
                urr = urllib.request.Request(url, post_obj, headers)
                """ open_obj作成(この段階で各serverにはSYNが飛んでる) """
                uru = urllib.request.urlopen(urr, timeout=self.ht_retry)

            except urllib.error.HTTPError as err:
                """ 404 や 500などのhttp-responseでErrorの場合 """
                """ エラー回数を1回増やす """
                self.ht_counter['fail'] += 1
                """ エラー内容の記載 """
                self.ht_counter['fail_description'].append((date_time, err.code, err.reason))
                """ エラー内容の出力 """
                self.ht_counter_print()
                if err.code == 404:
                    """ 404 の場合は何回アクセスしても無駄なので諦める """
                    return None
                if retry:
                    """ retry が0を示していない場合はループの先頭に戻る """
                    continue
                """ retry == 0 なので諦める """
                return None

            except urllib.error.URLError as err:
                """ SYNから？タイムアウトやドメインが引けなかった場合 """
                """ エラー回数を1回増やす """
                self.ht_counter['fail'] += 1
                """ エラー内容の記載 (-2に意味はないｗ)"""
                self.ht_counter['fail_description'].append((date_time, -2, err.reason))
                """ エラー内容の出力 """
                self.ht_counter_print()
                """ ここを retry/continue にするか return にするかは悩みどころ """
                return None

            except socket.timeout:
                """ socket.timeout の場合 """
                """ エラー回数を1回増やす """
                self.ht_counter['fail'] += 1
                """ エラー内容の記載 (-3に意味はないｗ)"""
                self.ht_counter['fail_description'].append((date_time, -3, "socket.timeout"))
                """ エラー内容の出力 """
                self.ht_counter_print()
                if retry:
                    """ retry が0を示していない場合はループの先頭に戻る """
                    continue
                """ retry == 0 なので諦める """
                return None

            except:
                """  その他未知のエラーはその都度対応すること """
                self.loge("unknown Error occurd")
                """ プログラムが止まる """
                raise

        """ サーバ側のchar-setが未指定ならUTF8 """
        ururhgcc = uru.headers.get_content_charset() or 'utf-8'

        if uru.info().get("Content-Encoding") == "gzip":
            """ zip エンコードのものは 解凍して差し上げる """
            download_data = gzip.decompress(uru.read())
        else:
            """ そうでもないなら 普通に展開 """
            download_data = uru.read()

        if output:
            """ 出力指定がある場合には ファイルに保存する """
            with open(output, 'wb') as fp:
                fp.write(download_data)

        """ その都度cookieを更新保存する """
        self.ht_save_cookie()
        return download_data

    def mail(self, sj='', fm='', to='', bd=''):
        ''' Server Side Settings '''
        ms = ms or "mailserver.anyway.example.co.jp"
        sp = sp or 587
        id = id or "SadlyMyIdHasGone.."
        pw = pw or "By The Way, Could you see that 1?"
        sj = sj or '中国の劇場前にある名探偵コナンの等身大フィギュアが怖すぎると話題に'
        fm = fm or 'defaultuser@anyway.example.co.jp'
        to = to or 'vividvervet@ubuntu.debian.or.jp'
        bd = bd or '''中国で10月23日から上映されている「名探偵コナン 業火の向日葵」がかなり好評。
        それにあわせて劇場前には等身大フィギュアが設置されている。この展示物フィギュアの
        質が悪いと中国で酷評されているのだ。
        中国のネットユーザは「どうみても老人だろ」「眉毛はどこ？」「粗悪だ...」と書かれている。
        パネルは公式っぽいが設置された等身大フィギュアは劇場が宣伝の為に作ったと思われる。'''

        pass

















