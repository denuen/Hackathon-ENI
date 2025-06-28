import os
import subprocess
import tempfile
import re
import json
import csv
from pathlib import Path
from typing import Set, List
from utils.ingestHelper import Document, buildDocument, saveDocumentJson, normalizeWhitespaces

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

DOCUMENT_EXTENSIONS: Set[str] = {
	'.pdf', '.txt', '.doc', '.docx', '.odt', '.rtf',
	'.ppt', '.pptx', '.odp',
	'.xlsx', '.xls', '.ods', '.csv',
	'.xml', '.json'
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

def isValidDocument(filepath: str) -> bool:
	ext = Path(filepath).suffix.lower()
	return ext in DOCUMENT_EXTENSIONS


def isValidMedia(filepath: str) -> bool:
	ext = Path(filepath).suffix.lower()
	return ext in AUDIO_EXTENSIONS or ext in VIDEO_EXTENSIONS


# Extracts text from documents
def extractTextFromFile(filepath: str) -> str:

	file_ext = Path(filepath).suffix.lower()

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
				return text_content.strip()
			else:
				print("Warning: No text content extracted from PDF")
				return ""

		except Exception as e:
			print(f"Error extracting PDF with pdfplumber: {e}")
			# Fallback to Tika if pdfplumber fails
			pass

	# Fallback to Tika for other document types
	if parser is None:
		return ""

	try:
		parsed = parser.from_file(filepath, requestOptions={
			'timeout': 300,
			'headers': {
				'X-Tika-OCRLanguage': 'ita+eng',
				'X-Tika-OCREngine': 'tesseract',
				'X-Tika-ExtractInlineImages': 'true',
				'X-Tika-OCRStrategy': 'auto',
			}
		})

		content = parsed.get('content', '') or ''

		if not content.strip():
			return ""

		content = normalizeWhitespaces(content)

		return content

	except Exception as e:
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
			simple_cmd = [
				'ffmpeg', '-i', videoPath,
				'-vn', '-acodec', 'pcm_s16le',
				'-ar', '16000', '-ac', '1',
				'-preset', 'ultrafast', '-y', audioPath
			]
			subprocess.run(simple_cmd, capture_output=True, text=True, check=True)
			return os.path.exists(audioPath) and os.path.getsize(audioPath) > 0
		except:
			return False

	except FileNotFoundError:
		return False

# Transcribes audio files
def transcribeAudio(filepath: str) -> str:

	if whisper is None:
		raise RuntimeError("Whisper not found.")

	try:
		global whisper_model
		if whisper_model is not None:
			model = whisper_model
		else:
			model = whisper.load_model(WHISPER_MODEL)

		result = model.transcribe(
			filepath,
			language="it",
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
			initial_prompt="Trascrizione di contenuto aziendale ENI in italiano.",
		)

		text = result.get('text', '').strip()
		if not text:
			return ""

		text = normalizeWhitespaces(text)
		text = postProcessNamingForCorporate(text)

		return text

	except Exception as e:
		return ""


# Processes media files (audio/video) and returns transcribed content
def ProcessMediaFile(filepath: str) -> str:

	fileExt = Path(filepath).suffix.lower()

	if fileExt in AUDIO_EXTENSIONS:
		return transcribeAudio(filepath)

	if fileExt in VIDEO_EXTENSIONS:
		with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmpAudio:
			tmpAudioPath = tmpAudio.name

		try:
			if extractAudioFromVideo(filepath, tmpAudioPath):
				return transcribeAudio(tmpAudioPath)
			else:
				return ""
		finally:
			if os.path.exists(tmpAudioPath):
				os.unlink(tmpAudioPath)

	return ""

# Processes all files in input directory and saves extracted content as JSON
def Ingest(input_dir: str, output_json_dir: str) -> None:

	if not os.path.exists(input_dir):
		raise FileNotFoundError(f"Error: input directory not found: {input_dir}")

	if not os.path.isdir(input_dir):
		raise ValueError(f"Error: the specified path is not a directory: {input_dir}")

	processedCnt = 0
	skippedCnt = 0
	errorCnt = 0

	global whisper_model
	if whisper is not None:
		try:
			whisper_model = whisper.load_model(WHISPER_MODEL)
		except:
			whisper_model = None
	else:
		whisper_model = None

	files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
	total_files = len(files)

	for i, filename in enumerate(files):
		filepath = os.path.join(input_dir, filename)

		print(f"[{i+1}/{total_files}] Processing: {filename}")

		try:
			file_extension = Path(filepath).suffix.lower().lstrip('.')

			content = ""
			if isValidDocument(filepath):
				content = extractTextFromFile(filepath)
			elif isValidMedia(filepath):
				content = ProcessMediaFile(filepath)
			else:
				skippedCnt += 1
				continue

			if not content.strip():
				skippedCnt += 1
				continue

			document = buildDocument(
				filepath=filepath,
				doc_type=file_extension,
				content=content,
				language="it"
			)

			saveDocumentJson(document, output_json_dir)

			processedCnt += 1

		except Exception as e:
			errorCnt += 1
			continue

	print(f"\n=== EXTRACTION SUMMARY ===")
	print(f"Files processed: {processedCnt}")
	print(f"Files skipped: {skippedCnt}")
	print(f"Files with errors: {errorCnt}")
	print(f"Total examined: {processedCnt + skippedCnt + errorCnt}")


def postProcessNamingForCorporate(text: str) -> str:

	if not text or not text.strip():
		return ""

	text = normalizeWhitespaces(text)

	corporate_corrections = {
		'ebitda': 'EBITDA',
		'ebita': 'EBITA',
		'roi': 'ROI',
		'roe': 'ROE',
		'roa': 'ROA',
		'kpi': 'KPI',
		'ceo': 'CEO',
		'cfo': 'CFO',
		'coo': 'COO',
		'pnl': 'P&L',
		'bilancio': 'bilancio',
		'fatturato': 'fatturato',
		'ricavi': 'ricavi',
		'costi': 'costi',
		'margini': 'margini',
		'budget': 'budget',
		'forecast': 'forecast',
		'gws': 'GWS',
		'lng': 'LNG',
		'gnl': 'GNL',
		'upstream': 'upstream',
		'downstream': 'downstream',
		'midstream': 'midstream',
		'raffinazione': 'raffinazione',
		'petrolchimico': 'petrolchimico',
		'esplorazione': 'esplorazione',
		'produzione': 'produzione',
		'barili': 'barili',
		'boe': 'BOE',
		'bcf': 'BCF',
		'tcf': 'TCF',
		'quindi': 'quindi',
		'tuttavia': 'tuttavia',
		'infatti': 'infatti',
		'inoltre': 'inoltre',
		'pertanto': 'pertanto',
		'comunque': 'comunque',
		'sicuramente': 'sicuramente',
		'naturalmente': 'naturalmente',
		'miliardo': 'miliardo',
		'milioni': 'milioni',
		'migliaia': 'migliaia',
		'percento': 'percento',
		'virgola': ',',
		'punto': '.',
	}

	for wrong, correct in corporate_corrections.items():
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
