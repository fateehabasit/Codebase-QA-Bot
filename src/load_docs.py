import os
from langchain_community.document_loaders import TextLoader

CODE_EXTENSIONS = (".cpp", ".h", ".hpp", ".cmake")

def load_repo_files(repo_path):
    docs = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(CODE_EXTENSIONS) or file == "CMakeLists.txt":
                filepath = os.path.join(root, file)
                try:
                    loader = TextLoader(filepath, encoding="utf-8")
                    file_docs = loader.load()
                    for d in file_docs:
                        d.metadata["source"] = filepath
                    docs.extend(file_docs)
                except Exception as e:
                    print(f"Skipped {filepath}: {e}")
    return docs

if __name__ == "__main__":
    docs = load_repo_files("data/repo/OOP Project Social Network Application")
    print(f"Loaded {len(docs)} files")