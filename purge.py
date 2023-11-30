import os

class Purge:
    def __init__(self) :
        self.folderName = ""
        self.fileNamePrefix = ""

    def purgeFiles(self, folderName, fileNamePrefix) :
        self.folderName = folderName
        self.fileNamePrefix = fileNamePrefix
        for f in os.listdir(self.folderName):
            if f.startswith(self.fileNamePrefix):
                os.remove(os.path.join(self.folderName, f))