import os

class TitleHandler :
    def __init__(self, NUMBER_OF_TITLES_CAP, INDEX_FOLDER_PATH) :
        self.title_file_count = 0
        self.capacity = NUMBER_OF_TITLES_CAP
        self.titles = []
        self.folder = INDEX_FOLDER_PATH

    def addTitle(self, title, isLast = False) :
        if(isLast == False) :
            self.titles.append(title.replace("\n", " "))
        if(len(self.titles) == self.capacity or isLast) :
            title_file_name = "title_" + str(self.title_file_count) + ".txt"
            with open(os.path.join(self.folder, title_file_name), "w", encoding="utf-8") as title_fp:
                for heads in self.titles :
                    title_fp.write(heads + "\n")
            self.title_file_count += 1
            self.titles = []