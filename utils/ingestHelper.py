import os
import re
import json
import hashlib
from datetime import datetime
from typing import List, TypedDict, Optional
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
			created_at=createdAt,
			modified_at=modifiedAt
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

def getFileHash(filepath: str) -> str:
	try:
		hashMd5 = hashlib.md5()
		with open(filepath, "rb") as f:
			for chunk in iter(lambda: f.read(4096), b""):
				hashMd5.update(chunk)
		return hashMd5.hexdigest()
	except Exception:
		stat = os.stat(filepath)
		return hashlib.md5(f"{filepath}_{stat.st_mtime}_{stat.st_size}".encode()).hexdigest()

def getCachePath(base_dir: str = ".cache") -> str:
	cacheDir = os.path.join(os.getcwd(), base_dir)
	os.makedirs(cacheDir, exist_ok=True)
	return cacheDir

def getCachedContent(filepath: str, content_type: str = "transcription") -> Optional[str]:
	try:
		fileHash = getFileHash(filepath)
		cacheDir = getCachePath()
		cacheFile = os.path.join(cacheDir, f"{fileHash}_{content_type}.txt")

		if os.path.exists(cacheFile):
			with open(cacheFile, 'r', encoding='utf-8') as f:
				cachedContent = f.read().strip()
			if cachedContent:
				print(f"Using cached {content_type}")
				return cachedContent
		return None
	except Exception:
		return None

def saveToCache(filepath: str, content: str, content_type: str = "transcription") -> None:
	try:
		if not content or not content.strip():
			return

		fileHash = getFileHash(filepath)
		cacheDir = getCachePath()
		cacheFile = os.path.join(cacheDir, f"{fileHash}_{content_type}.txt")

		with open(cacheFile, 'w', encoding='utf-8') as f:
			f.write(content)
	except Exception as e:
		print(f"Error: Failed to cache {content_type}: {e}")

def clearCache(base_dir: str = ".cache") -> None:
	try:
		cacheDir = getCachePath(base_dir)
		for file in os.listdir(cacheDir):
			if file.endswith('.txt'):
				os.remove(os.path.join(cacheDir, file))
	except Exception as e:
		print(f"Error: failed to clear cache: {e}")
