import time
from typing import List, Dict
from src.data_loader import PatentDataLoader
from src.search_engine import PatentSearchEngine

class PatentSearchInterface:
    """
    The user-friendly interface for the search engine.
    This is what users interact with!
    """

    def __init__(self):
        """Initialize the interface."""
        self.loader = None
        self.engine = None
        self.patents = []

    def setup(self, data_folder: str = 'data/'):
        """
        Set up the search engine.

        Args:
            data_folder: Folder containing patent JSON files
        """
        print("=" * 60)
        print("🚀 PATENT SEARCH ENGINE")
        print("=" * 60)

        # Load data
        print("\n[1/3] Loading patent data...")
        self.loader = PatentDataLoader(data_folder)
        self.patents = self.loader.load_all_patents()

        if not self.patents:
            print("❌ No patents loaded. Please check your data folder.")
            return False

        # Show statistics
        stats = self.loader.get_statistics()
        print(f"\n📊 Loaded {stats['total_patents']} patents")

        # Create search engine
        print("\n[2/3] Setting up search engine...")
        self.engine = PatentSearchEngine(self.patents)

        # Load or create embeddings
        print("\n[3/3] Preparing search index...")
        if not self.engine.load_embeddings():
            print("Creating new embeddings (this will take a few minutes)...")
            self.engine.create_embeddings()

        print("\n✅ Setup complete! Ready to search.")
        return True

    def display_results(self, results: List[Dict], show_details: bool = False):
        """
        Display search results in a nice format.

        Args:
            results: List of patent results
            show_details: Whether to show full details
        """
        if not results:
            print("\n😢 No results found. Try a different query.")
            return

        print(f"\n{'='*60}")
        print(f"📄 SEARCH RESULTS ({len(results)} found)")
        print(f"{'='*60}")

        for i, result in enumerate(results, 1):
            print(f"\n[{i}] {result['title']}")
            print(f"    📊 Relevance Score: {result['similarity_score']:.4f}")
            print(f"    📋 Document Number: {result['document_number']}")
            print(f"    🏷️  Classification: {result['classification_code']}")

            if show_details and result['abstract']:
                abstract = result['abstract'][:200]
                print(f"    📝 Abstract: {abstract}...")

        print(f"\n{'='*60}")

    def basic_search_mode(self):
        """Simple search interface."""
        print("\n" + "="*60)
        print("🔍 BASIC SEARCH MODE")
        print("="*60)
        print("Enter your search query (or 'quit' to exit)")
        print("Example: 'electric vehicle battery management'")
        print("="*60)

        while True:
            query = input("\n🔎 Search: ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break

            if not query:
                print("⚠️  Please enter a search query.")
                continue

            # Perform search
            start_time = time.time()
            results = self.engine.search(query, top_k=5)
            search_time = time.time() - start_time

            # Display results
            self.display_results(results)
            print(f"⏱️  Search completed in {search_time:.3f} seconds")

            # Ask if they want details
            show_more = input("\nShow abstracts? (y/n): ").strip().lower()
            if show_more == 'y':
                self.display_results(results, show_details=True)

    def advanced_search_mode(self):
        """Advanced search with filters."""
        print("\n" + "="*60)
        print("🔧 ADVANCED SEARCH MODE (with filters)")
        print("="*60)
        print("Enter your search query and optional filters")
        print("="*60)

        while True:
            print("\n" + "-"*60)
            query = input("🔎 Search query: ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break

            if not query:
                print("⚠️  Please enter a search query.")
                continue

            # Get filters
            print("\nOptional filters (press Enter to skip):")
            classification = input("  Classification code (e.g., B60B): ").strip() or None
            title_keyword = input("  Title must contain: ").strip() or None

            try:
                top_k = int(input("  Number of results (default 5): ").strip() or "5")
            except ValueError:
                top_k = 5

            # Perform search
            start_time = time.time()
            results = self.engine.search(
                query=query,
                top_k=top_k,
                classification_filter=classification,
                title_keyword=title_keyword
            )
            search_time = time.time() - start_time

            # Display results
            self.display_results(results, show_details=True)
            print(f"\n⏱️  Search completed in {search_time:.3f} seconds")

            # Show statistics
            stats = self.engine.get_search_statistics(results)
            if results:
                print(f"📈 Average similarity: {stats['avg_similarity']:.4f}")

    def patent_similarity_mode(self):
        """Find patents similar to a given patent."""
        print("\n" + "="*60)
        print("🔗 PATENT SIMILARITY SEARCH")
        print("="*60)
        print("Find patents similar to a specific patent")
        print("="*60)

        while True:
            doc_number = input("\n📄 Enter patent document number (or 'quit'): ").strip()

            if doc_number.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break

            if not doc_number:
                print("⚠️  Please enter a document number.")
                continue

            # Find similar patents
            start_time = time.time()
            results = self.engine.search_by_patent_id(doc_number, top_k=5)
            search_time = time.time() - start_time

            if results:
                print(f"\n✅ Found {len(results)} similar patents:")
                self.display_results(results, show_details=True)
                print(f"\n⏱️  Search completed in {search_time:.3f} seconds")
            else:
                print(f"\n❌ Patent {doc_number} not found in database.")

    def run(self):
        """Main interface loop."""
        while True:
            print("\n" + "="*60)
            print("📋 MAIN MENU")
            print("="*60)
            print("1. Basic Search")
            print("2. Advanced Search (with filters)")
            print("3. Find Similar Patents")
            print("4. Show Statistics")
            print("5. Quit")
            print("="*60)

            choice = input("\nSelect option (1-5): ").strip()

            if choice == '1':
                self.basic_search_mode()
            elif choice == '2':
                self.advanced_search_mode()
            elif choice == '3':
                self.patent_similarity_mode()
            elif choice == '4':
                self.show_statistics()
            elif choice == '5':
                print("\n👋 Thank you for using Patent Search Engine!")
                break
            else:
                print("⚠️  Invalid choice. Please select 1-5.")

    def show_statistics(self):
        """Show database statistics."""
        stats = self.loader.get_statistics()

        print("\n" + "="*60)
        print("📊 DATABASE STATISTICS")
        print("="*60)
        print(f"Total Patents: {stats['total_patents']}")
        print(f"Patents with Abstract: {stats['with_abstract']}")
        print(f"Patents with Claims: {stats['with_claims']}")
        print(f"Missing Abstract: {stats['missing_abstract']}")
        print(f"Missing Claims: {stats['missing_claims']}")
        print("="*60)


# Example usage
if __name__ == "__main__":
    interface = PatentSearchInterface()

    if interface.setup('data/'):
        interface.run()