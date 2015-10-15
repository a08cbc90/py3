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

import json, os, re, gzip
class Util():
    """ Utilは他の Classes が継承しやすいように初めのほうに
    書く必要がある。
    """

    def __init__(self):
        """ BaseEnv
        最低限の設定であり、他のinitで上書きしない前提の属性とする
        Util:
            i_conf    :  コンフィグファイル位置(あまり変えたくない)'./conf/config.json'
            i_log_dir :  ログディレクトリ
            i_conf_dir: コンフィグディレクトリ(あまり変えたくない)'./conf'
            i_tmp_dir :  一時ディレクトリ
        """
        self.i_conf = 'conf/config.json'
        j = self.rj(self.i_conf)
        for atr, val in j['Util'].items():
            setattr(self, atr, val)

        for dir in [self.i_log_dir, self.i_conf_dir, self.i_tmp_dir]:
            self.make_dir(dir)


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


    def rj(self, filepath='/dev/null'):
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
            return None
        except ValueError: 
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

        return int(os.stat(path).st_mtime - int(t))

import http.cookiejar, urllib, gzip, datetime, time, socket
class HttpClient(Util):
    """ 汎用的なhttp[s]通信ができるClassを目指す
    """
    def __init__(self):
        """
        ht_url: デフォルトのURL
        ht_refferer:    デフォルトのリファラ
        ht_output_path: デフォルトの保存先
        ht_ua:  デフォルトのクライアント
        ht_cookie: デフォルトのクッキーファイル
        ht_log_level: デフォルトのログレベル
        ht_log_path: デフォルトのログ保存位置
        ht_header: 実際に使用するヘッダー共通部分
        ht_cookie_jarnal: Mozilla形式のクッキー定義
        ht_counter: このクラスを使用した際の履歴を記憶する。
        """
        Util.__init__(self)
        j = self.rj(self.i_conf)
        for x, y in j['HttpClient'].items():
            setattr(self, x, y)

        self.ht_log_path = self.i_log_dir + '/' + self.ht_log_file
        self.ht_cookie   = self.i_tmp_dir + '/' + self.ht_cookie
        self.ht_header['User-Agent'] = self.ht_ua


























