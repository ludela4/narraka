import glob
class Shell:
    def __init__(self,path):
        self.path=path
        self.surfaces = sorted(glob.glob(self.path+"/surface[0-9]*.png"))

    def getSurfacePathFromId(self,id):
        return self.surfaces[id]