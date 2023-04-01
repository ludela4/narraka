import glob
class Shell:
    def __init__(self,path):
        self.path=path
        self.surfaces = sorted(glob.glob(self.path+"/surface[0-9]*.png"))
        print(f"{path}, surfaces: ",self.surfaces)

    def getSurfacePathFromId(self,id):
        return self.surfaces[id]