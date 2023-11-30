import os
import xml.sax
from datetime import datetime
from preprocessor import Preprocessor
from titlehandler import TitleHandler
from invertedIndex import BuildInvertedIndex
from secondaryIndex import SecondaryIndex
from purge import Purge

XML_PATH = "wikiDump.xml"
INDEX_FOLDER_PATH = os.path.abspath("INDEX_FOLDER")
STATS_FILE_PATH = os.path.abspath("stats.txt")

NUMBER_OF_TITLES_CAP = 2000 # Number of titles per title file
TEMP_INVERTED_INDEX_FILE_CAP = 1000000 # 1MB 
PRIMARY_INVERTED_INDEX_FILE_CAP = 1000000 # 1MB
MAX_WORD_CAP = 30

TOTAL_DOC_COUNT = 0
TOTAL_WORDS_ENCOUNTERED = 0
TOTAL_UNIQUE_WORDS = 0

primary_indexer_start_time = 0
primary_indexer_end_time = 0
title_file_count = 0
primary_index_file_count = 0

class WikiHandler(xml.sax.ContentHandler) :
    def __init__(self):
        # Document data
        self.docID = -1 
        self.doc_data = {}
        self.doc_tag = ["title", "text"]
        self.current_tag = ""
        self.wiki_data = {}
        self.wiki_data_fields = ["title", "body", "infobox", "category", "link", "references"]

        # preprocessing
        self.PP = Preprocessor(MAX_WORD_CAP)

        # title handler
        self.TT = TitleHandler(NUMBER_OF_TITLES_CAP, INDEX_FOLDER_PATH)

        # inverted index builder
        self.IIB = BuildInvertedIndex(TEMP_INVERTED_INDEX_FILE_CAP, PRIMARY_INVERTED_INDEX_FILE_CAP, INDEX_FOLDER_PATH)

        # secondary index builder
        self.SIB = SecondaryIndex(INDEX_FOLDER_PATH)

        # Purger
        self.Purger = Purge()

    def startElement(self, tag, attrs) :
        self.current_tag = tag

        #start of new document
        if tag == "page": 
            self.doc_data = {}
            for tag in self.doc_tag:
                self.doc_data[tag] = ""
            self.wiki_data = {}
            for f in self.wiki_data_fields:
                self.wiki_data[f] = ""
            
    def endElement(self, tag) :
        if(tag == "page"):
            if len(self.doc_data["title"]) > 0 and len(self.doc_data["text"]) > 0:
                self.wiki_data["title"] = self.PP.process_title(self.doc_data["title"])
                # self.wiki_data["title"] = ["title"]
                self.wiki_data["infobox"], self.wiki_data["body"], self.wiki_data["category"], self.wiki_data["link"], self.wiki_data["ref"] = self.PP.process_text(self.doc_data["text"])
                # self.wiki_data["infobox"], self.wiki_data["body"], self.wiki_data["category"], self.wiki_data["link"], self.wiki_data["ref"] = ["infobox"], ["body"], ["category"], ["link"], ["ref"]
            
                self.docID += 1

                self.TT.addTitle(self.doc_data["title"])

                self.IIB.build_inverted_index(self.wiki_data, self.docID)
                
        if tag == "mediawiki" : 
            global TOTAL_DOC_COUNT, TOTAL_WORDS_ENCOUNTERED
            TOTAL_DOC_COUNT = self.docID + 1
            TOTAL_WORDS_ENCOUNTERED = self.PP.TotalWordsEncountered

            
            self.TT.addTitle(title = None, isLast = True)
            global title_file_count
            title_file_count = self.TT.title_file_count

            for f in self.wiki_data_fields:
                self.wiki_data[f] = "" 

            self.IIB.build_inverted_index(self.wiki_data, self.docID, isLast = True)
            global TOTAL_UNIQUE_WORDS
            TOTAL_UNIQUE_WORDS = self.IIB.total_unique_words

            global primary_index_file_count
            primary_index_file_count = self.IIB.primary_file_index + 1
            
            global primary_indexer_end_time
            primary_indexer_end_time = datetime.utcnow()
            
            self.SIB.createSecondaryIndex()

            self.Purger.purgeFiles(INDEX_FOLDER_PATH, "temp_index_")
            
    def characters(self, content) :
        if self.current_tag in self.doc_tag :
            self.doc_data[self.current_tag] += content.strip() + " "

def get_index_size():
    size = 0
    for path, dirs, files in os.walk(INDEX_FOLDER_PATH):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)
    return size

def generate_stats() :
    stat_fp = open(STATS_FILE_PATH, "w", encoding="utf-8")
    stat_fp.write("Total Documents : " + str(TOTAL_DOC_COUNT) + "\n")
    stat_fp.write("Total Words Encountered : " + str(TOTAL_WORDS_ENCOUNTERED) + "\n")
    stat_fp.write("Total Unique Words : " + str(TOTAL_UNIQUE_WORDS) + "\n")
    stat_fp.write("Total Index Size : " + str(get_index_size()) + "\n") 
    stat_fp.write("Tilte File Count : " + str(title_file_count) + "\n")
    stat_fp.write("Primary Index File Count : " + str(primary_index_file_count) + "\n")
    stat_fp.write("Primary Index Creation Time: %.2f seconds\n" % (primary_indexer_end_time - primary_indexer_start_time).total_seconds())

def indexer() :
    # purge already available indexes
    Purger = Purge()
    Purger.purgeFiles(INDEX_FOLDER_PATH, "temp_index_")
    Purger.purgeFiles(INDEX_FOLDER_PATH, "index_")
    Purger.purgeFiles(INDEX_FOLDER_PATH, "title_")
    Purger.purgeFiles(INDEX_FOLDER_PATH, "secondary_")

    global primary_indexer_start_time
    
    primary_indexer_start_time = datetime.utcnow()

    handler = WikiHandler()

    parser = xml.sax.make_parser()

    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    parser.setContentHandler(handler)

    parser.parse(XML_PATH)

def main() :
    indexer()
    generate_stats()

if __name__ == "__main__":
    main()