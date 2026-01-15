# Patent Search Engine 🔍

A semantic search engine for vehicle patent applications using AI-powered embeddings.

## 📋 Problem Statement

This project solves the problem of efficiently searching through thousands of patent documents to find relevant prior art and similar inventions. Traditional keyword search often misses semantically similar patents that use different terminology. This semantic search engine understands the *meaning* of queries, not just exact word matches.

**Specific problem solved:** Given a natural language query (e.g., "electric vehicle battery management"), find the most relevant patent documents from a database of vehicle-related patents filed in 2024-present.

## 🎯 How It Works

### Core Search Engine (Part 1)
1. **Data Loading**: Reads patent JSON files and handles missing fields
2. **Text Processing**: Combines title, abstract, and claims into searchable text
3. **Embedding Creation**: Converts text to 384-dimensional vectors using `all-MiniLM-L6-v2` model
4. **Similarity Search**: Uses cosine similarity to find patents closest to the query
5. **Results**: Returns top-K most relevant patents with similarity scores

### Enhancement: Hybrid Search (Part 2)
I chose **Hybrid Search** because it adds practical filtering that patent agents need:
- **Classification Filter**: Search only within specific patent classes (e.g., B60B for wheels)
- **Title Keyword Filter**: Require specific terms in the patent title
- **Combined Approach**: Semantic search + metadata filters for precision

**Performance Notes:**
- Without filters: ~0.05 seconds per search
- With filters: ~0.06 seconds per search (filters applied post-similarity calculation)
- Could be optimized by pre-indexing classification codes

## 🚀 How to Run

### Prerequisites
```bash
pip install -r requirements.txt
```

### Setup
1. Place patent JSON files in `data/` folder
2. Run the main program:
```bash
python main.py
```

### First Run
The first time you run it, the engine will:
1. Load all patents (~30 seconds)
2. Create embeddings (~2-5 minutes depending on dataset size)
3. Save embeddings for future use

### Subsequent Runs
- Loads saved embeddings (~2 seconds)
- Ready to search immediately!

## 📖 Usage Examples

### Basic Search
```
Search: electric vehicle battery management
```
Returns top 5 patents about EV batteries

### Advanced Search with Filters
```
Search query: autonomous driving sensors
Classification code: B60W
Title must contain: vehicle
Number of results: 10
```
Returns patents about autonomous driving, filtered to class B60W

### Find Similar Patents
```
Enter patent document number: US20240123456
```
Returns patents similar to the specified patent

## 📁 Project Structure
```
patent-search-project/
│
├── data/                          # Patent JSON files
├── embeddings/                    # Saved embeddings (auto-generated)
├── src/
│   ├── data_loader.py            # Loads and processes patents
│   ├── search_engine.py          # Core search logic
│   └── interface.py              # User interface
├── main.py                       # Run this file!
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🧠 Technical Details

- **Model**: `all-MiniLM-L6-v2` (384-dimensional embeddings)
- **Similarity Metric**: Cosine similarity
- **Missing Data**: Patents without document number are skipped; other fields default to "N/A"
- **Search Time**: ~0.05-0.06 seconds per query
- **Embedding Generation**: ~1-2 seconds per 100 patents

## 🎥 Demo Video

See `demo_video.mp4` for a 2-minute walkthrough showing:
1. Basic search functionality
2. Advanced search with filters
3. Finding similar patents
4. Performance metrics

## 🔧 Future Improvements

- Two-phase ranking with cross-encoders for top results
- Support for uploading external patent documents
- Multi-user support with session management
- Query history and saved searches

## 📝 Notes

- Data handling decision: Patents missing document numbers are excluded; other missing fields are filled with defaults
- Enhancement choice: Hybrid search was selected for its practical utility in patent searching
- The code is structured to make adding additional enhancements easy

---

