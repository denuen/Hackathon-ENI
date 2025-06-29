import os
import subprocess
import tempfile
import re
import json
import csv
from pathlib import Path
from typing import Set, List, Dict, Optional
from utils.ingestHelper import Document, buildDocument, saveDocumentJson, normalizeWhitespaces, getFileHash, getCachePath, getCachedContent, saveToCache, clearCache


try:
	from langdetect import detect, LangDetectException
except ImportError:
	detect = None
	LangDetectException = None

try:
	import pdfplumber
except ImportError:
	pdfplumber = None

try:
	from tika import parser
except ImportError:
	parser = None

try:
	import whisper
except ImportError:
	whisper = None

try:
	from pydub import AudioSegment
	from pydub.effects import normalize
except ImportError:
	AudioSegment = None

try:
	from PIL import Image
	import pytesseract
except ImportError:
	Image = None
	pytesseract = None

DOCUMENT_EXTENSIONS: Set[str] = {
	'.pdf', '.txt', '.doc', '.docx', '.odt', '.rtf',
	'.ppt', '.pptx', '.odp',
	'.xlsx', '.xls', '.ods', '.csv',
	'.xml', '.json'
}
IMAGE_EXTENSIONS: Set[str] = {
	'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif',
	'.gif', '.webp', '.svg'
}
AUDIO_EXTENSIONS: Set[str] = {
	'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg',
	'.wma', '.amr', '.opus'
}
VIDEO_EXTENSIONS: Set[str] = {
	'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.webm', '.m4v',
	'.flv', '.3gp', '.mpg', '.mpeg'
}

WHISPER_MODEL = "base"
CHUNK_DURATION = 30

whisperModel = None
configData = None

def loadConfig(config_path: str = "config.json") -> Dict:
	global configData
	if configData is None:
		try:
			with open(config_path, 'r', encoding='utf-8') as f:
				configData = json.load(f)
		except FileNotFoundError:
			configData = {
				"default_language": "auto",
				"ocr_languages": ["eng", "ita"],
				"whisperModel": "base",
				"whisper_initial_prompts": {
					"it": "Trascrizione di contenuto aziendale ENI in italiano.",
					"en": "Transcription of ENI corporate content in English."
				},
				"corporate_terms": {
					"en": {"ebitda": "EBITDA", "roi": "ROI"},
					"it": {"ebitda": "EBITDA", "roi": "ROI"}
				}
			}
	return configData

def detectLanguage(text: str, fallback: str = "en") -> str:
	if not detect or not text or len(text.strip()) < 20:
		return fallback

	try:
		sample = text[:1000] if len(text) > 1000 else text
		detectedLang = detect(sample)

		langMapping = {
			"it": "it", "en": "en", "fr": "fr", "de": "de",
			"es": "es", "pt": "pt", "ca": "es", "gl": "es"
		}

		return langMapping.get(detectedLang, fallback)

	except (LangDetectException, Exception):
		return fallback

def convert_to_tika_codes(langs: List[str]) -> str:
	langMap = {
		"en": "eng", "it": "ita", "fr": "fra",
		"de": "deu", "es": "spa", "pt": "por"
	}
	return "+".join([langMap.get(lang, "eng") for lang in langs])

def apply_corporate_corrections(text: str, lang: str, config: Dict) -> str:
	if not text or not text.strip():
		return ""

	text = normalizeWhitespaces(text)

	corporate_terms = config.get("corporate_terms", {}).get(lang, {})

	for wrong, correct in corporate_terms.items():
		pattern = r'\b' + re.escape(wrong) + r'\b'
		text = re.sub(pattern, correct, text, flags=re.IGNORECASE)

	text = re.sub(r'\s+([,.!?;:])', r'\1', text)
	text = re.sub(r'([,.!?;:])\s*([a-zA-Z])', r'\1 \2', text)
	text = re.sub(r'\s+', ' ', text)

	sentences = re.split(r'([.!?]+)', text)
	result = []
	for i, sentence in enumerate(sentences):
		if i % 2 == 0 and sentence.strip():
			sentence = sentence.strip()
			if sentence:
				sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
		result.append(sentence)

	return ''.join(result).strip()

def isValidDocument(filepath: str) -> bool:
	ext = Path(filepath).suffix.lower()
	return ext in DOCUMENT_EXTENSIONS


def isValidImage(filepath: str) -> bool:
	ext = Path(filepath).suffix.lower()
	return ext in IMAGE_EXTENSIONS


def isValidMedia(filepath: str) -> bool:
	ext = Path(filepath).suffix.lower()
	return ext in AUDIO_EXTENSIONS or ext in VIDEO_EXTENSIONS


# Extracts text from documents with language detection support and caching
def extractTextFromFile(filepath: str, ocr_langs: Optional[List[str]] = None) -> str:

	file_ext = Path(filepath).suffix.lower()
	config = loadConfig()

	if ocr_langs is None:
		ocr_langs = config.get("ocr_languages", ["eng", "ita"])

	if file_ext in ['.pdf', '.doc', '.docx', '.odt', '.rtf', '.ppt', '.pptx', '.odp']:
		cached_text = getCachedContent(filepath, "extraction")
		if cached_text:
			return cached_text

	if file_ext == '.txt':
		try:
			encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
			content = ""

			for encoding in encodings:
				try:
					with open(filepath, 'r', encoding=encoding) as f:
						content = f.read()
					break
				except UnicodeDecodeError:
					continue

			if not content:
				return ""

			content = normalizeWhitespaces(content)
			return content.strip()

		except Exception as e:
			return ""

	if file_ext in ['.xlsx', '.xls', '.csv', '.ods']:
		try:
			if file_ext == '.csv':
				try:
					encodings = ['utf-8', 'latin1', 'cp1252', 'utf-8-sig']

					for encoding in encodings:
						try:
							with open(filepath, 'r', encoding=encoding) as f:
								sample = f.read(1024)
								f.seek(0)

								delimiter = ','
								if ';' in sample and sample.count(';') > sample.count(','):
									delimiter = ';'
								elif '\t' in sample:
									delimiter = '\t'

								reader = csv.reader(f, delimiter=delimiter)
								rows = list(reader)

								if not rows:
									return ""

								headers = rows[0]
								table_data = []

								for row in rows[1:]:
									row_obj = {}
									for i, value in enumerate(row):
										if i < len(headers):
											row_obj[headers[i]] = value
										else:
											row_obj[f"Column_{i+1}"] = value
									table_data.append(row_obj)

								table_structure = {
									"type": "table",
									"headers": headers,
									"data": table_data,
									"rows_count": len(table_data)
								}

								content = json.dumps(table_structure, ensure_ascii=False, indent=2)
								return content

						except UnicodeDecodeError:
							continue
						except Exception as e:
							continue

				except Exception as e:
					pass

			try:
				import pandas as pd

				if file_ext in ['.xlsx', '.xls']:
					df_dict = pd.read_excel(filepath, sheet_name=None)

					excel_data = {
						"type": "spreadsheet",
						"sheets": {}
					}

					for sheet_name, sheet_df in df_dict.items():
						sheet_df = sheet_df.fillna('')

						headers = sheet_df.columns.tolist()
						table_data = []

						for _, row in sheet_df.iterrows():
							row_obj = {}
							for col in headers:
								row_obj[col] = str(row[col])
							table_data.append(row_obj)

						excel_data["sheets"][sheet_name] = {
							"headers": headers,
							"data": table_data,
							"rows_count": len(table_data)
						}

					content = json.dumps(excel_data, ensure_ascii=False, indent=2)
					return content

			except ImportError:
				pass
			except Exception as e:
				pass

		except Exception as e:
			pass

		return ""

	if file_ext == '.pdf':
		if pdfplumber is None:
			print("Warning: pdfplumber not available, skipping PDF extraction")
			return ""

		try:
			text_content = ""
			with pdfplumber.open(filepath) as pdf:
				for page_num, page in enumerate(pdf.pages, 1):
					try:
						page_text = page.extract_text()
						if page_text:
							text_content += f"\n--- Page {page_num} ---\n"
							text_content += page_text
					except Exception as e:
						print(f"Warning: Failed to extract text from page {page_num}: {e}")
						continue

			if text_content.strip():
				text_content = normalizeWhitespaces(text_content)
				result_text = text_content.strip()
				saveToCache(filepath, result_text, "extraction")
				return result_text
			else:
				print("Warning: No text content extracted from PDF")
				return ""

		except Exception as e:
			print(f"Error extracting PDF with pdfplumber: {e}")
			# Fallback to Tika if pdfplumber fails
			pass

	# Fallback to Tika for other document types with dynamic language support
	if parser is None:
		return ""

	try:
		tikaLangs = convert_to_tika_codes(ocr_langs)

		parsed = parser.from_file(filepath, requestOptions={
			'timeout': 300,
			'headers': {
				'X-Tika-OCRLanguage': tikaLangs,
				'X-Tika-OCREngine': 'tesseract',
				'X-Tika-ExtractInlineImages': 'true',
				'X-Tika-OCRStrategy': 'auto',
			}
		})

		content = parsed.get('content', '') or ''

		if not content.strip():
			return ""

		content = normalizeWhitespaces(content)

		saveToCache(filepath, content, "extraction")

		return content

	except Exception as e:
		print(f"Error: tika extraction failed: {e}")
		return ""

# Extracts audio from video files with optimized settings for faster processing
def extractAudioFromVideo(videoPath: str, audioPath: str) -> bool:

	try:
		cmd = [
			'ffmpeg', '-i', videoPath,
			'-vn',
			'-acodec', 'pcm_s16le',
			'-ar', '16000',
			'-ac', '1',
			'-threads', '0',
			'-avoid_negative_ts', 'make_zero',
			'-preset', 'ultrafast',
			'-y',
			audioPath
		]
		result = subprocess.run(cmd, capture_output=True, text=True, check=True)

		if os.path.exists(audioPath) and os.path.getsize(audioPath) > 0:
			return True
		else:
			return False

	except subprocess.CalledProcessError as e:
		try:
			simpleCmd = [
				'ffmpeg', '-i', videoPath,
				'-vn', '-acodec', 'pcm_s16le',
				'-ar', '16000', '-ac', '1',
				'-preset', 'ultrafast', '-y', audioPath
			]
			subprocess.run(simpleCmd, capture_output=True, text=True, check=True)
			return os.path.exists(audioPath) and os.path.getsize(audioPath) > 0
		except:
			return False

	except FileNotFoundError:
		return False

# Transcribes audio files with dynamic language support and caching
def transcribeAudio(filepath: str, language: Optional[str] = None, initial_prompt: Optional[str] = None) -> str:

	if whisper is None:
		raise RuntimeError("Whisper not found.")

	cached_transcription = getCachedContent(filepath, "transcription")
	if cached_transcription:
		return cached_transcription

	config = loadConfig()

	try:
		global whisperModel
		if whisperModel is not None:
			model = whisperModel
		else:
			modelName = config.get("whisperModel", "base")
			model = whisper.load_model(modelName)

		whisperLanguage = None if language == "auto" or language is None else language

		if initial_prompt is None and language:
			initial_prompt = config.get("whisper_initial_prompts", {}).get(
				language,
				"Professional transcription."
			)

		result = model.transcribe(
			filepath,
			language=whisperLanguage,
			task="transcribe",
			temperature=0.0,
			word_timestamps=False,
			condition_on_previous_text=False,
			compression_ratio_threshold=2.4,
			no_speech_threshold=0.6,
			beam_size=1,
			best_of=1,
			fp16=True,
			verbose=False,
			patience=None,
			length_penalty=None,
			suppress_tokens=[-1],
			initial_prompt=initial_prompt,
		)

		text = result.get('text', '').strip()
		if not text:
			return ""

		text = normalizeWhitespaces(text)

		if not language or language == "auto":
			detectedLang = detectLanguage(text, "en")
		else:
			detectedLang = language

		text = apply_corporate_corrections(text, detectedLang, config)

		saveToCache(filepath, text, "transcription")

		return text

	except Exception as e:
		print(f"   ❌ Transcription failed: {e}")
		return ""


# Processes media files (audio/video) and returns transcribed content with language support
def ProcessMediaFile(filepath: str, language: Optional[str] = None, initial_prompt: Optional[str] = None) -> str:

	fileExt = Path(filepath).suffix.lower()

	if fileExt in AUDIO_EXTENSIONS:
		return transcribeAudio(filepath, language=language, initial_prompt=initial_prompt)

	if fileExt in VIDEO_EXTENSIONS:
		with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmpAudio:
			tmpAudioPath = tmpAudio.name

		try:
			if extractAudioFromVideo(filepath, tmpAudioPath):
				return transcribeAudio(tmpAudioPath, language=language, initial_prompt=initial_prompt)
			else:
				return ""
		finally:
			if os.path.exists(tmpAudioPath):
				os.unlink(tmpAudioPath)

	return ""

# Processes all files in input directory with multilingual support
def Ingest(input_dir: str, output_json_dir: str, config_path: str = "config.json") -> None:

	if not os.path.exists(input_dir):
		raise FileNotFoundError(f"Error: input directory not found: {input_dir}")

	if not os.path.isdir(input_dir):
		raise ValueError(f"Error: the specified path is not a directory: {input_dir}")

	config = loadConfig(config_path)

	processedCnt = 0
	skippedCnt = 0
	errorCnt = 0

	global whisperModel
	if whisper is not None:
		try:
			modelName = config.get("whisperModel", "base")
			whisperModel = whisper.load_model(modelName)
		except Exception as e:
			print(f"Failed to load Whisper model: {e}")
			whisperModel = None
	else:
		whisperModel = None

	files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
	total_files = len(files)


	for i, filename in enumerate(files):
		filepath = os.path.join(input_dir, filename)

		print(f"[{i+1}/{total_files}] Processing: {filename}")

		try:
			file_extension = Path(filepath).suffix.lower().lstrip('.')

			content = ""
			languageDetected = config.get("default_language", "auto")

			if isValidDocument(filepath):
				content = extractTextFromFile(filepath, ocr_langs=config.get("ocr_languages"))

				if content.strip() and config.get("default_language") == "auto":
					languageDetected = detectLanguage(content, "en")
					print(f"Detected language: {languageDetected}")

			elif isValidImage(filepath):
				content = extractTextFromImage(filepath, ocr_langs=config.get("ocr_languages"))

				if content.strip() and config.get("default_language") == "auto":
					languageDetected = detectLanguage(content, "en")
					print(f"Detected language: {languageDetected}")

			elif isValidMedia(filepath):
				if config.get("default_language") == "auto":
					languageDetected = None
				else:
					languageDetected = config.get("default_language")

				initial_prompt = None
				if languageDetected:
					initial_prompt = config.get("whisper_initial_prompts", {}).get(languageDetected)

				content = ProcessMediaFile(
					filepath,
					language=languageDetected,
					initial_prompt=initial_prompt
				)

				if content.strip() and languageDetected is None:
					languageDetected = detectLanguage(content, "en")
					print(f"Detected language: {languageDetected}")

			else:
				print(f"Error: unsupported file type")
				skippedCnt += 1
				continue

			if not content.strip():
				print(f"Error: no content extracted")
				skippedCnt += 1
				continue

			if isValidDocument(filepath) or isValidImage(filepath):
				content = apply_corporate_corrections(content, languageDetected, config)

			document = buildDocument(
				filepath=filepath,
				doc_type=file_extension,
				content=content,
				language=languageDetected or "unknown"
			)

			saveDocumentJson(document, output_json_dir)
			processedCnt += 1


		except Exception as e:
			print(f"Error: error processing {filename}: {str(e)}")
			errorCnt += 1
			continue

	print(f"\n=== EXTRACTION SUMMARY ===")
	print(f"Files processed: {processedCnt}")
	print(f"Files skipped: {skippedCnt}")
	print(f"Files with errors: {errorCnt}")
	print(f"Total examined: {processedCnt + skippedCnt + errorCnt}")
	print(f"Cache directory: {getCachePath()}")


# Legacy function
def postProcessNamingForCorporate(text: str) -> str:
	config = loadConfig()
	return apply_corporate_corrections(text, "it", config)

# Extracts text from images using OCR with language detection support and caching
def extractTextFromImage(filepath: str, ocr_langs: Optional[List[str]] = None) -> str:

	if Image is None or pytesseract is None:
		return ""

	config = loadConfig()

	if ocr_langs is None:
		ocr_langs = config.get("ocr_languages", ["eng", "ita"])

	cached_text = getCachedContent(filepath, "extraction")
	if cached_text:
		return cached_text

	try:
		with Image.open(filepath) as img:
			if img.mode != 'RGB':
				img = img.convert('RGB')

			lang_codes = '+'.join(ocr_langs)

			custom_config = f'--oem 3 --psm 6 -l {lang_codes}'

			extracted_text = pytesseract.image_to_string(img, config=custom_config)

			if not extracted_text.strip():
				return ""

			extracted_text = normalizeWhitespaces(extracted_text)
			result_text = extracted_text.strip()

			saveToCache(filepath, result_text, "extraction")

			return result_text

	except Exception as e:
		return ""
