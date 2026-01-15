import json
import os
from pathlib import Path
from typing import List, Dict

class PatentDataLoader:
    """
    This class loads patent data from JSON files.
    Think of it as a librarian who organizes all the patent books.
    """

    def __init__(self, data_folder: str):
        """
        Initialize the loader with the folder containing patent files.

        Args:
            data_folder: Path to folder with JSON files (e.g., 'data/')
        """
        self.data_folder = data_folder
        self.patents = []

    def load_all_patents(self) -> List[Dict]:
        """
        Load all patent JSON files from the data folder.

        Returns:
            List of patent dictionaries
        """
        print("📚 Loading patent files...")

        # Find all JSON files in the data folder
        json_files = list(Path(self.data_folder).glob("patents_ipa*.json"))

        if not json_files:
            print(f"⚠️  No patent files found in {self.data_folder}")
            return []

        print(f"Found {len(json_files)} patent files")

        # Load each file
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    patents_batch = json.load(f)

                    # Debug: show first patent structure
                    if self.patents == [] and patents_batch:
                        print(f"\n🔍 DEBUG: First patent structure from {file_path.name}:")
                        first_patent = patents_batch[0]
                        print(f"   Keys: {list(first_patent.keys())}")
                        for key in list(first_patent.keys())[:5]:  # Show first 5 fields
                            value = str(first_patent[key])[:100]  # First 100 chars
                            print(f"   {key}: {value}...")

                    # Process each patent
                    for patent in patents_batch:
                        processed_patent = self._process_patent(patent)
                        if processed_patent:  # Only add if valid
                            self.patents.append(processed_patent)

                print(f"✅ Loaded {len(patents_batch)} patents from {file_path.name}")
                print(f"   ➡️  Successfully processed: {len([p for p in self.patents if p])} patents so far")

            except Exception as e:
                print(f"❌ Error loading {file_path.name}: {e}")
                import traceback
                traceback.print_exc()

        print(f"\n🎉 Total patents loaded: {len(self.patents)}")
        return self.patents

    def _process_patent(self, patent: Dict) -> Dict:
        """
        Process a single patent and handle missing fields - FLEXIBLE VERSION
        """
        lower_map = {k.lower(): v for k, v in patent.items()}

        def pick(*keys):
            for key in keys:
                key_lower = key.lower()
                if key_lower in lower_map:
                    return lower_map[key_lower]
            return None

        # Document number: accept common variants (doc_number, publication_number, etc.)
        document_number = pick(
            'document number', 'document_number', 'doc_number', 'docnumber',
            'publication_number', 'application_number', 'patent_id', 'id'
        )
        if not document_number:
            document_number = f"PATENT_{id(patent)}"

        # Create processed patent - ACCEPT ALL PATENTS
        processed = {
            'document_number': str(document_number),
            'title': pick('title', 'Title') or 'No Title Available',
            'abstract': pick('abstract', 'Abstract') or '',
            'claims': pick('claims', 'Claims') or [],
            'detailed_description': pick('detailed_description', 'Detailed Description', 'description') or [],
            'classification_code': pick('classification code', 'classification_code', 'classification') or 'N/A',
            'bibtext_citation': pick('bibtext citation', 'Bibtext Citation', 'bibtex') or 'N/A'
        }

        # Create a searchable text field
        processed['searchable_text'] = self._create_searchable_text(processed)

        return processed

    def _create_searchable_text(self, patent: Dict) -> str:
        """
        Combine different parts of the patent into one searchable text.
        """
        parts = []

        # Add title (most important)
        if patent['title'] and patent['title'] != 'No Title Available':
            parts.append(f"Title: {patent['title']}")

        # Add abstract (very important)
        if patent['abstract']:
            parts.append(f"Abstract: {patent['abstract']}")

        # Add claims (important for legal definitions)
        if patent['claims']:
            if isinstance(patent['claims'], list):
                claims_text = ' '.join(str(c) for c in patent['claims'])
            else:
                claims_text = str(patent['claims'])
            parts.append(f"Claims: {claims_text}")

        # Add detailed description (can be long, so limit it)
        if patent['detailed_description']:
            if isinstance(patent['detailed_description'], list):
                desc_text = ' '.join(str(d) for d in patent['detailed_description'][:3])
            else:
                desc_text = str(patent['detailed_description'])
            parts.append(f"Description: {desc_text[:1000]}")

        return ' '.join(parts)

    def get_patent_by_id(self, document_number: str) -> Dict:
        """Find a specific patent by its document number."""
        for patent in self.patents:
            if patent['document_number'] == document_number:
                return patent
        return None

    def get_statistics(self) -> Dict:
        """Get statistics about the loaded patents."""
        total = len(self.patents)
        with_abstract = sum(1 for p in self.patents if p['abstract'])
        with_claims = sum(1 for p in self.patents if p['claims'])

        return {
            'total_patents': total,
            'with_abstract': with_abstract,
            'with_claims': with_claims,
            'missing_abstract': total - with_abstract,
            'missing_claims': total - with_claims
        }