import os
import sys
from pathlib import Path
from ingest.extractor import Ingest

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():

	inputDirectory = os.path.join(project_root, "input")
	outputDirectory = os.path.join(project_root, "output")

	print(f"Directory input: {inputDirectory}")
	print(f"Directory output: {outputDirectory}")

	if not os.path.exists(inputDirectory):
		print(f"Input directory not found...creating: {inputDirectory}")
		os.makedirs(inputDirectory, exist_ok=True)
		print("Input directory is empty, please add the necessary files")
		return

	files = [f for f in os.listdir(inputDirectory) if os.path.isfile(os.path.join(inputDirectory, f))]
	if not files:
		print("No files found in the input directory")
		return

	print(f"{len(files)} files found")
	for file in files:
		print(f"  - {file}")

	try:
		Ingest(inputDirectory, outputDirectory)

	except Exception as e:
		print(f"\nIngest error: {e}")
		sys.exit(1)


if __name__ == "__main__":
	main()
