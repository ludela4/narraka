import datetime


class Ghost:
    def __init__(self, path):
        self.face_symbols = {
            "[普通]": 0,
            "[笑い]": 1,
            "[泣き]": 2,
            "[怒り]": 3,
            "[紹介]": 4,
            "[放心]": 5,
            "[振り向き]": 6
        }
        self.name = "ちーちゃん"
        self.path = path

    def Base(self):
        with open(self.path+"/prompt_template.txt", "r") as f:
            s = f.read()
        return {"role": "user", "content": s+self.params()}

    def OnInterval(self):
        return {"role": "user", "content": "{ランダムトーク}"+self.params()}

    def OnClicked(self):
        return {"role": "user", "content": "{ユーザーアクション: 体をつつく}"+self.params()}

    def OnBoot(self):
        return {"role": "user", "content": "起動しました。"+self.params()}

    def OnClose(self):
        return {"role": "user", "content": "さようなら　{コマンド: シャットダウン}"+self.params()}

    def params(self):
        dt_now = datetime.datetime.now()
        dt_now_s = dt_now.strftime('%Y年%m月%d日 %H:%M:%S')
        params = f"""
        ステータス:
        日時: {dt_now_s}
        キャラクタ: {self.name}"""
        return params
