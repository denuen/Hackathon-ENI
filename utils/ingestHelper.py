import os
import re
import json
from datetime import datetime
from typing import List, TypedDict
from pathlib import Path


class Document(TypedDict):

	filename: str
	tags: List[str]
	type: str
	content: str
	language: str
	created_at: str
	modified_at: str

def normalize_whitespaces(content: str) -> str:
	content = content.strip()
	return re.sub(r'\s+', ' ', content)

# Returns a dict with all the document's metadata
def build_document(filepath: str, doc_type: str, content: str, language: str = "it") -> Document:

	if not os.path.exists(filepath):
		raise FileNotFoundError(f"Error: cannot find: {filepath}")

	try:
		file_stats = os.stat(filepath)

		created_at = datetime.fromtimestamp(file_stats.st_ctime).isoformat()
		modified_at = datetime.fromtimestamp(file_stats.st_mtime).isoformat()

		filename = os.path.basename(filepath)

		content = normalize_whitespaces(content)

		return Document(
			filename=filename,
			tags=[],
			type=doc_type,
			content=content,
			language=language,
			created_at=created_at,
			modified_at=modified_at
		)

	except OSError as e:
		raise OSError(f"Error: cannot find data from: {filepath}: {e}")


# Saves a document in JSON format in a specified directory
def save_document_json(doc: Document, output_dir: str) -> None:

	if not doc.get("filename"):
		raise ValueError("Error: the document must have a valid name")

	try:
		Path(output_dir).mkdir(parents=True, exist_ok=True)

		base_name = Path(doc["filename"]).stem
		json_filename = f"{base_name}.json"
		json_filepath = os.path.join(output_dir, json_filename)

		with open(json_filepath, 'w', encoding='utf-8') as f:
			json.dump(doc, f, indent=2, ensure_ascii=False)

	except OSError as e:
		raise OSError(f"Error: cannot save the JSON document in {output_dir}: {e}")
