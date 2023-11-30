import os

class SecondaryIndex:
    def __init__(self, INDEX_FOLDER_PATH):
        self.first_word_from_index = []
        self.index_folder = INDEX_FOLDER_PATH


    def createSecondaryIndex(self) :
        for f in os.listdir(self.index_folder):
            if f.startswith("index_"):
                fp = open(os.path.join(self.index_folder, f), "r", encoding="utf-8")
                
                line = fp.readline().strip("\n").split("=")
                if(len(line) > 0):
                    self.first_word_from_index.append(line[0])
                fp.close()
        
        self.first_word_from_index.sort()

        secondary_fname = "secondary_index.txt"
        secondary_fp = open(os.path.join(self.index_folder, secondary_fname), "w", encoding="utf-8")
        for word in self.first_word_from_index:
            secondary_fp.write(word + "\n")
        secondary_fp.close()
