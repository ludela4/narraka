import datetime
import yaml
import os


class Ghost:
    def __init__(self, path):
        self.face_symbols = {}
        self.name = ""
        self.path=path
        self.loadData(path+"/ghost.yaml")
        

    def loadData(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.data = yaml.safe_load(f)
        else:
            raise Exception("ghost.yaml not found")
        self.name = self.data.get("name", "noname")
        self.face_symbols = self.data.get("face_symbols", {})
        if "base" in self.data.keys():
            self.base_prompt = self.data["base"]
        else:
            basefile = self.data.get("basefile", "prompt_template.txt")
            
            basefile_path=self.path+f"/{basefile}"
            if os.path.exists(basefile_path):
                with open(basefile_path, "r") as f:
                    self.base_prompt = f.read()
            else:
                raise Exception(f"{basefile} not found")
            

    def Base(self):
        return {"role": "user", "content": self.base_prompt+self.params()}

    def OnInterval(self):
        prompt=self.data.get("OnInterval","{ランダムトーク}")
        return {"role": "user", "content": prompt+self.params()}

    def OnClicked(self):
        prompt=self.data.get("OnClicked","{ユーザーアクション: 体をつつく}")
        return {"role": "user", "content": prompt+self.params()}

    def OnBoot(self):
        prompt=self.data.get("OnBoot","起動しました。")
        return {"role": "user", "content":prompt+self.params()}

    def OnClose(self):
        prompt=self.data.get("OnClose","さようなら　{コマンド: シャットダウン}")
        return {"role": "user", "content": prompt+self.params()}

    def params(self):
        dt_now = datetime.datetime.now()
        dt_now_s = dt_now.strftime('%Y年%m月%d日 %H:%M:%S')
        params = f"""
        ステータス:
        日時: {dt_now_s}
        キャラクタ: {self.name}"""
        return params
