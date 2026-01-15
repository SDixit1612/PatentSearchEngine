import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import pickle
import os

class PatentSearchEngine:
    """
    The brain of the search engine!
    This converts text to numbers and finds similar patents.
    """

    def __init__(self, patents: List[Dict], model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the search engine.

        Args:
            patents: List of patent dictionaries
            model_name: Name of the sentence transformer model to use
        """
        self.patents = patents
        self.model_name = model_name
        self.embeddings = None

        print(f"🤖 Loading AI model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("✅ Model loaded!")

    def create_embeddings(self, save_path: str = 'embeddings/patent_embeddings.pkl'):
        """
        Convert all patents to embeddings (numbers).

        Embeddings are like converting words to coordinates on a map.
        Similar words are close together on the map.

        Args:
            save_path: Where to save the embeddings
        """
        print(f"\n🔢 Creating embeddings for {len(self.patents)} patents...")
        print("⏳ This might take a few minutes...")

        # Extract searchable text from each patent
        texts = [patent['searchable_text'] for patent in self.patents]

        # Convert texts to embeddings (this is the magic!)
        # Each text becomes a list of 384 numbers
        self.embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32  # Process 32 patents at a time
        )

        print(f"✅ Created embeddings with shape: {self.embeddings.shape}")

        # Save embeddings so we don't have to recreate them every time
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            pickle.dump(self.embeddings, f)
        print(f"💾 Saved embeddings to {save_path}")

    def load_embeddings(self, load_path: str = 'embeddings/patent_embeddings.pkl'):
        """
        Load previously saved embeddings.

        Args:
            load_path: Path to saved embeddings file
        """
        try:
            with open(load_path, 'rb') as f:
                self.embeddings = pickle.load(f)
            print(f"✅ Loaded embeddings from {load_path}")
            print(f"   Shape: {self.embeddings.shape}")
            return True
        except FileNotFoundError:
            print(f"⚠️  No saved embeddings found at {load_path}")
            return False

    def search(self, query: str, top_k: int = 5,
               classification_filter: str = None,
               title_keyword: str = None) -> List[Dict]:
        """
        Search for patents similar to the query.

        This is the main search function!

        Args:
            query: What the user wants to search for
            top_k: How many results to return
            classification_filter: Filter by classification code (e.g., 'B60B')
            title_keyword: Filter by keyword in title

        Returns:
            List of matching patents with similarity scores
        """
        if self.embeddings is None:
            raise ValueError("❌ No embeddings! Run create_embeddings() first.")

        print(f"\n🔍 Searching for: '{query}'")

        # Step 1: Convert query to embedding
        query_embedding = self.model.encode([query])[0]

        # Step 2: Calculate similarity with all patents
        # Cosine similarity measures how "close" two vectors are
        # Returns values from -1 (opposite) to 1 (identical)
        similarities = cosine_similarity(
            [query_embedding],
            self.embeddings
        )[0]

        # Step 3: Apply filters if requested (HYBRID SEARCH)
        valid_indices = self._apply_filters(
            classification_filter,
            title_keyword
        )

        # Step 4: Get top results
        results = []

        # Sort indices by similarity (highest first)
        sorted_indices = np.argsort(similarities)[::-1]

        for idx in sorted_indices:
            # Skip if doesn't pass filters
            if valid_indices is not None and idx not in valid_indices:
                continue

            patent = self.patents[idx].copy()
            patent['similarity_score'] = float(similarities[idx])
            results.append(patent)

            # Stop when we have enough results
            if len(results) >= top_k:
                break

        print(f"✅ Found {len(results)} results")
        return results

    def _apply_filters(self, classification_filter: str = None,
                       title_keyword: str = None) -> List[int]:
        """
        Apply filters to limit which patents can be returned.

        This is the HYBRID SEARCH part!

        Args:
            classification_filter: Classification code prefix (e.g., 'B60B')
            title_keyword: Keyword that must appear in title

        Returns:
            List of valid patent indices, or None if no filters
        """
        if classification_filter is None and title_keyword is None:
            return None

        valid_indices = []

        for idx, patent in enumerate(self.patents):
            # Check classification filter
            if classification_filter:
                if not patent['classification_code'].startswith(classification_filter):
                    continue

            # Check title keyword filter
            if title_keyword:
                if title_keyword.lower() not in patent['title'].lower():
                    continue

            # Patent passed all filters
            valid_indices.append(idx)

        print(f"🔧 Filters applied: {len(valid_indices)} patents match")
        return valid_indices

    def search_by_patent_id(self, document_number: str, top_k: int = 5) -> List[Dict]:
        """
        Find patents similar to a given patent.

        Args:
            document_number: Document number of the reference patent
            top_k: How many similar patents to return

        Returns:
            List of similar patents
        """
        # Find the patent
        reference_patent = None
        reference_idx = None

        for idx, patent in enumerate(self.patents):
            if patent['document_number'] == document_number:
                reference_patent = patent
                reference_idx = idx
                break

        if reference_patent is None:
            print(f"❌ Patent {document_number} not found")
            return []

        # Use its searchable text as the query
        query = reference_patent['searchable_text']
        results = self.search(query, top_k + 1)  # +1 because it will find itself

        # Remove the reference patent from results
        results = [r for r in results if r['document_number'] != document_number]

        return results[:top_k]

    def get_search_statistics(self, results: List[Dict]) -> Dict:
        """
        Get statistics about search results.

        Args:
            results: List of search results

        Returns:
            Dictionary with statistics
        """
        if not results:
            return {'count': 0}

        scores = [r['similarity_score'] for r in results]

        return {
            'count': len(results),
            'avg_similarity': np.mean(scores),
            'max_similarity': np.max(scores),
            'min_similarity': np.min(scores)
        }


# Example usage
if __name__ == "__main__":
    from src.data_loader import PatentDataLoader

    # Load patents
    loader = PatentDataLoader('data/patent_data_small')
    patents = loader.load_all_patents()

    # Create search engine
    engine = PatentSearchEngine(patents)

    # Try to load existing embeddings, or create new ones
    if not engine.load_embeddings():
        engine.create_embeddings()

    # Test search
    results = engine.search("electric vehicle battery system", top_k=5)

    print("\n🎯 Search Results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   Score: {result['similarity_score']:.4f}")
        print(f"   Document: {result['document_number']}")
        print(f"   Classification: {result['classification_code']}")