"""
Patent Search Engine - Main Entry Point

This is the file you run to start the search engine!
"""

from src.interface import PatentSearchInterface

def main():
    """
    Main function to start the patent search engine.
    """
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║          🔍 PATENT SEARCH ENGINE 🔍                     ║
    ║                                                          ║
    ║     Semantic search for vehicle patent applications     ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # Create interface
    interface = PatentSearchInterface()

    # Setup (load data and create embeddings)
    print("\n🚀 Initializing search engine...")
    print("This may take a few minutes the first time.")

    if interface.setup(data_folder='data/patent_data_small'):
        # Run the main interface
        interface.run()
    else:
        print("\n❌ Failed to initialize search engine.")
        print("Please check that your data files are in the 'data/' folder.")

if __name__ == "__main__":
    main()