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

def normalizeWhitespaces(content: str) -> str:
	content = content.strip()
	return re.sub(r'\s+', ' ', content)

# Returns a dict with all the document's metadata
def buildDocument(filepath: str, doc_type: str, content: str, language: str = "it") -> Document:

	if not os.path.exists(filepath):
		raise FileNotFoundError(f"Error: cannot find: {filepath}")

	try:
		fileStats = os.stat(filepath)

		createdAt = datetime.fromtimestamp(fileStats.st_ctime).isoformat()
		modifiedAt = datetime.fromtimestamp(fileStats.st_mtime).isoformat()

		filename = os.path.basename(filepath)

		content = normalizeWhitespaces(content)

		return Document(
			filename=filename,
			tags=[],
			type=doc_type,
			content=content,
			language=language,
			createdAt=createdAt,
			modifiedAt=modifiedAt
		)

	except OSError as e:
		raise OSError(f"Error: cannot find data from: {filepath}: {e}")


# Saves a document in JSON format in a specified directory
def saveDocumentJson(doc: Document, outputDir: str) -> None:

	if not doc.get("filename"):
		raise ValueError("Error: the document must have a valid name")

	try:
		Path(outputDir).mkdir(parents=True, exist_ok=True)

		base_name = Path(doc["filename"]).stem
		jsonFilename = f"{base_name}.json"
		json_filepath = os.path.join(outputDir, jsonFilename)

		with open(json_filepath, 'w', encoding='utf-8') as f:
			json.dump(doc, f, indent=2, ensure_ascii=False)

	except OSError as e:
		raise OSError(f"Error: cannot save the JSON document in {outputDir}: {e}")
