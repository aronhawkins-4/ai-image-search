import chromadb
from chromadb.config import Settings
from collections import defaultdict
import os


def remove_duplicate_paths():
    """Remove entries from ChromaDB collection that have duplicate metadata['path'] values."""

    # Connect to ChromaDB
    chromadb_client = chromadb.HttpClient(host="localhost", port=8000)

    try:
        collection = chromadb_client.get_collection("image_collection")
    except Exception as e:
        print(f"Error getting collection: {e}")
        return

    # Get all entries from the collection
    print("Fetching all entries from collection...")
    all_entries = collection.get(include=['metadatas', 'documents'])

    if not all_entries['ids']:
        print("No entries found in collection.")
        return

    print(f"Found {len(all_entries['ids'])} total entries.")

    # Group entries by path
    path_to_entries = defaultdict(list)

    for i, entry_id in enumerate(all_entries['ids']):
        metadata = all_entries['metadatas'][i] if all_entries['metadatas'] else {
        }
        path = metadata.get('path', '')

        if path:  # Only consider entries with a valid path
            # Use only the filename (not the full path) for grouping
            filename = os.path.basename(str(path))
            if filename:
                path_to_entries[filename].append({
                    'id': entry_id,
                    'index': i,
                    'metadata': metadata
                })
    print("Paths found:")
    for path in path_to_entries.keys():
        print(path)
    # Find duplicates and select which ones to remove
    ids_to_remove = []
    duplicates_found = 0

    for path, entries in path_to_entries.items():
        if len(entries) > 1:
            duplicates_found += 1
            print(f"Found {len(entries)} duplicates for path: {path}")

            # Keep the first entry, mark the rest for removal
            for entry in entries[1:]:
                ids_to_remove.append(entry['id'])
                print(f"  Marking for removal: {entry['id']}")

    print(f"\nFound {duplicates_found} paths with duplicates.")
    print(f"Total entries to remove: {len(ids_to_remove)}")

    if not ids_to_remove:
        print("No duplicates found. Nothing to remove.")
        return

    # Confirm before deletion
    response = input(
        f"\nDo you want to remove {len(ids_to_remove)} duplicate entries? (y/N): ")
    if response.lower() != 'y':
        print("Operation cancelled.")
        return

    # Remove duplicate entries
    print("Removing duplicate entries...")
    try:
        collection.delete(ids=ids_to_remove)
        print(f"Successfully removed {len(ids_to_remove)} duplicate entries.")

        # Verify removal
        remaining_entries = collection.get(include=['metadatas'])
        print(f"Collection now has {len(remaining_entries['ids'])} entries.")

    except Exception as e:
        print(f"Error removing entries: {e}")


if __name__ == "__main__":
    remove_duplicate_paths()
