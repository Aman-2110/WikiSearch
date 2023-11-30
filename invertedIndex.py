from collections import defaultdict
import heapq
import math
import os

class BuildInvertedIndex :
    def __init__(self, TEMP_INVERTED_INDEX_FILE_CAP, PRIMARY_INVERTED_INDEX_FILE_CAP, INDEX_FOLDER_PATH) :
        # temporary inverted index
        self.temp_inverted_index = {}
        self.temp_capacity = TEMP_INVERTED_INDEX_FILE_CAP
        self.temp_index_size = 0
        self.temp_file_index = 0

        # primary inverted index
        self.primary_index_cap = PRIMARY_INVERTED_INDEX_FILE_CAP
        self.primary_index_file_size = 0
        self.primary_file_index = 0
        self.primary_inverted_index = {}

        self.index_folder_path = INDEX_FOLDER_PATH
        self.total_doc_count = 0
        self.total_unique_words = 0
        
    def build_inverted_index(self, wikiData, docID, isLast = False) :
        title_dict = defaultdict(int)
        infobox_dict = defaultdict(int)
        body_dict = defaultdict(int)
        category_dict = defaultdict(int)
        link_dict = defaultdict(int)
        reference_dict = defaultdict(int)
        
        combined_words_dict = defaultdict(int)
        
        # title
        for word in wikiData["title"]:
            title_dict[word] += 1
            combined_words_dict[word] += 1
        
        # infobox
        infobox_dict = defaultdict(int)
        for word in wikiData["infobox"]:
            infobox_dict[word] += 1
            combined_words_dict[word] += 1

        # body
        body_dict = defaultdict(int)
        for word in wikiData["body"]:
            body_dict[word] += 1
            combined_words_dict[word] += 1

        # category
        category_dict = defaultdict(int)
        for word in wikiData["category"]:
            category_dict[word] += 1
            combined_words_dict[word] += 1

        # link
        link_dict = defaultdict(int)
        for word in wikiData["link"]:
            link_dict[word] += 1
            combined_words_dict[word] += 1

        # references
        ref_dict = defaultdict(int)
        for word in wikiData["references"]:
            reference_dict[word] += 1
            combined_words_dict[word] += 1

        for word, word_freq in combined_words_dict.items():
            posting = str(docID) + " "
            if(title_dict[word] > 0):
                posting += "t" + str(title_dict[word])
            if(infobox_dict[word] > 0):
                posting += "i" + str(infobox_dict[word])
            if(body_dict[word] > 0):
                posting += "b" + str(body_dict[word])
            if(category_dict[word] > 0):
                posting += "c" + str(category_dict[word])
            if(link_dict[word] > 0):
                posting += "l" + str(link_dict[word])
            if(ref_dict[word] > 0):
                posting += "r" + str(reference_dict[word])

            # merge into inverted_index
            if(word not in self.temp_inverted_index):
                self.temp_inverted_index[word] = {"doc_count":0, "word_freq": 0, "posting_list": []}
            
            self.temp_inverted_index[word]["doc_count"] += 1
            self.temp_inverted_index[word]["word_freq"] += word_freq
            self.temp_inverted_index[word]["posting_list"].append(posting)
            self.temp_index_size += len(posting)

        if(self.temp_index_size >= self.temp_capacity or isLast) :
            temp_index_fn = "temp_index_" + str(self.temp_file_index) + ".txt"
            
            with open(os.path.join(self.index_folder_path, temp_index_fn), "w", encoding="utf-8") as temp_index_fp:
                for word in sorted(self.temp_inverted_index.keys()):
                    word_dict = self.temp_inverted_index[word]
                    temp_index_fp.write(word + "=" + str(word_dict["doc_count"]) + "=" + str(word_dict["word_freq"]) + "=" + "|".join(word_dict["posting_list"]) + "\n")
            
            self.temp_file_index += 1
            self.temp_index_size = 0
            self.temp_inverted_index = {}

            if(isLast) :
                self.total_doc_count = docID + 1
                self.merge_temp_indexes()


    def getIDF(self, NUMBER_OF_DOCS_WITH_WORD):
        return math.log10(self.total_doc_count / NUMBER_OF_DOCS_WITH_WORD)

    def merge_temp_indexes(self) : 

        temp_fp_list = []
        min_heap = []

        self.primary_inverted_index = {"word": "", "doc_count": 0, "word_freq": 0, "IDF": 0.0, "posting_list": ""} 

        curr_top_element_of_temp_file = {}
        for ind in range(self.temp_file_index) :
            temp_index_fn = "temp_index_" + str(ind) + ".txt"

            temp_fp_list.append(open(os.path.join(self.index_folder_path, temp_index_fn), "r", encoding="utf-8"))
            line = temp_fp_list[ind].readline().strip("\n")
            if(line != "") :
                word, doc_count, word_freq, posting_list = line.split("=")
                min_heap.append((word, ind))
                curr_top_element_of_temp_file[ind] = {"doc_count": int(doc_count), "word_freq": int(word_freq), "posting_list": posting_list}
            else :
                temp_fp_list[ind].close()

        heapq.heapify(min_heap)
        isFirst = True
        primary_inverted_index_fp = None
        while(len(min_heap) > 0) :
            word, ind = heapq.heappop(min_heap)
            if(word == self.primary_inverted_index["word"]) :
                self.primary_inverted_index["doc_count"] += curr_top_element_of_temp_file[ind]["doc_count"]
                self.primary_inverted_index["word_freq"] += curr_top_element_of_temp_file[ind]["word_freq"]
                self.primary_inverted_index["posting_list"] += "|" + curr_top_element_of_temp_file[ind]["posting_list"]
            else :
                if(isFirst) :
                    isFirst = False
                    primary_index_fn = "index_" + str(self.primary_file_index) + ".txt"
                    primary_inverted_index_fp = open(os.path.join(self.index_folder_path, primary_index_fn), "w", encoding="utf-8")
                else :
                    self.total_unique_words += 1

                    line = self.primary_inverted_index["word"] + "=" + str(self.getIDF(self.primary_inverted_index["doc_count"])) + "=" + str(self.primary_inverted_index["doc_count"]) + "=" + str(self.primary_inverted_index["word_freq"]) + "=" + self.primary_inverted_index["posting_list"] + "\n"
                    primary_inverted_index_fp.write(line)

                    self.primary_index_file_size += len(line)

                    if(self.primary_index_file_size > self.primary_index_cap) :
                        primary_inverted_index_fp.close()

                        self.primary_index_file_size = 0
                        self.primary_file_index += 1
                        primary_index_fn = "index_" + str(self.primary_file_index) + ".txt"
                        primary_inverted_index_fp = open(os.path.join(self.index_folder_path, primary_index_fn), "w", encoding="utf-8")


                self.primary_inverted_index["word"] = word
                self.primary_inverted_index["doc_count"] = curr_top_element_of_temp_file[ind]["doc_count"]
                self.primary_inverted_index["word_freq"] = curr_top_element_of_temp_file[ind]["word_freq"]
                self.primary_inverted_index["posting_list"] = curr_top_element_of_temp_file[ind]["posting_list"]

            line = temp_fp_list[ind].readline().strip("\n")
            if(line != "") :
                word, doc_count, word_freq, posting_list = line.split("=")
                heapq.heappush(min_heap, (word, ind))
                curr_top_element_of_temp_file[ind] = {"doc_count": int(doc_count), "word_freq": int(word_freq), "posting_list": posting_list}
            else:
                temp_fp_list[ind].close()

        # writing last word in index file
        self.total_unique_words += 1

        line = self.primary_inverted_index["word"] + "=" + str(self.getIDF(self.primary_inverted_index["doc_count"])) + "=" + str(self.primary_inverted_index["doc_count"]) + "=" + str(self.primary_inverted_index["word_freq"]) + "=" + self.primary_inverted_index["posting_list"] + "\n"
        primary_inverted_index_fp.write(line)
        primary_inverted_index_fp.close()    