# WikiSearch

A high-performance search engine for Wikipedia dumps that implements an inverted index-based search system with field-specific weightage.

## Features

- Processes Wikipedia XML dumps to create an efficient search index
- Field-specific indexing (Title, Infobox, Body, Category, Links, References)
- Weighted field searching for better relevance
- Memory-efficient indexing using disk-based merging
- Support for multiple index files with secondary indexing
- Top-K document retrieval based on relevance scoring

## System Requirements

- Python 3.x
- NLTK library with required datasets:
  - stopwords
  - punkt

## Project Structure

```
WikiSearch/
├── indexer.py            # Main indexer that processes XML dumps
├── invertedIndex.py      # Handles inverted index creation and merging
├── preprocessor.py       # Text preprocessing utilities
├── purge.py             # Cleanup utilities for index files
├── searcher.ipynb       # Interactive search interface
├── searcher.py          # Search implementation
├── secondaryIndex.py    # Secondary index management
├── titlehandler.py      # Title processing and storage
├── stats.txt           # Statistics about the index
└── INDEX_FOLDER/       # Contains generated index files
    ├── index_*.txt     # Primary index files
    ├── secondary_index.txt
    └── title_*.txt     # Title index files
```

## How It Works

### Indexing Process

1. **XML Processing**: The system reads the Wikipedia XML dump and processes each article.
2. **Field Separation**: For each article, content is separated into different fields:
   - Title
   - Infobox
   - Body text
   - Categories
   - Links
   - References

3. **Text Processing**:
   - Case folding
   - Tokenization
   - Stopword removal
   - Stemming

4. **Index Creation**:
   - Creates temporary index files with a size cap
   - Merges temporary indexes into primary index files
   - Generates secondary index for efficient searching
   - Maintains title files for document retrieval

### Search Process

1. **Query Processing**:
   - Applies same text processing as indexing
   - Identifies relevant index files using secondary index

2. **Scoring**:
   - Field-specific weights for better relevance
   - IDF (Inverse Document Frequency) calculation
   - Combined score computation

3. **Results**:
   - Returns top-K documents based on relevance score
   - Includes document titles and IDs
   - Provides query processing time

## Configuration

Key parameters can be configured in the indexer and searcher:

- `NUMBER_OF_TITLES_CAP`: Number of titles per title file (default: 2000)
- `TEMP_INVERTED_INDEX_FILE_CAP`: Size cap for temporary index files (default: 1MB)
- `PRIMARY_INVERTED_INDEX_FILE_CAP`: Size cap for primary index files (default: 1MB)
- `MAX_WORD_CAP`: Maximum word length (default: 30)
- `SECTION_WEIGHT`: Field weights for scoring
- `K`: Number of top documents to return (default: 10)

## Usage

1. Place your Wikipedia XML dump in the project root as `wikiDump.xml`

2. Run the indexer:
```bash
python indexer.py
```

3. Use the searcher (either through notebook or Python script):
```bash
# Using the notebook
jupyter notebook searcher.ipynb

# Or using the Python script
python searcher.py
```

4. Query results will be saved in the `out` directory

## Stats

The system generates statistics in `stats.txt` including:
- Total number of documents processed
- Total words encountered
- Total unique words
- Index size
- Number of index files
- Processing time