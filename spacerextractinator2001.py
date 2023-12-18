"""
Author: Britt van Tunen
This script extracts the spacers from a CRISPRCasFinder result.json file and counts their occurence per timepoint (T).

This script requires that 'json', 'csv' and "collections" be installed within the Python
environment you are running this script in.
"""

import json
import csv
from collections import Counter, defaultdict

def load_json(filename):
    """
    Load JSON data from a file and handle decoding errors.

    Parameters:
        filename (str): The path to the JSON file.

    Returns:
        dict: The loaded JSON data.
    """
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f'{filename} not found. Skipping...')
        return None
    except json.decoder.JSONDecodeError:
        with open(filename, 'r') as file:
            content = file.read()
        try:
            data = json.loads(content)
            return data
        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding JSON in {filename}: {e}")
            return None

def extract_spacers(data):
    """
    Extract spacer sequences from the given JSON data.

    Parameters:
        data (dict): The JSON data.

    Returns:
        list: A list of spacer sequences.
    """
    spacers = []
    for sequence in data['Sequences']:
        for crispr in sequence['Crisprs']:
            for region in crispr['Regions']:
                if region['Type'] == 'Spacer':
                    spacers.append(region['Sequence'])
    return spacers

def process_files():
    """
    Process JSON files, count spacers, and write results to a TSV file.

    Returns:
        None
    """
    spacer_counts = defaultdict(Counter)
    total_spacers = Counter()
    found_files = []

    with open('merged_spacers.tsv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter='\t')

        for file_number in range(1, 13):
            filename = f'S925-T{file_number}/result.json' #change to actual file path
            dataset_key = f'S925-T{file_number}' #change to actual subjectID

            data = load_json(filename)
            if data is None:
                continue

            found_files.append(f'925T{file_number}') #change to actual subjectID

            spacers = extract_spacers(data)

            spacer_counts[dataset_key].update(spacers)
            total_spacers.update(spacers)

        if found_files:
            headers = ['Spacer'] + found_files
            writer.writerow(headers)

        if any(spacer_counts.values()):
            all_spacers = set()
            for dataset, counts in spacer_counts.items():
                all_spacers.update(counts.keys())
            for spacer in all_spacers:
                counts_row = [spacer, *[counts[spacer] for counts in spacer_counts.values()]]
                writer.writerow(counts_row)

    print(f'Total number of spacers: {sum(total_spacers.values())}')
    print('Spacers extracted, counted, and merged successfully. The result is saved in merged_spacers.tsv.')

if __name__ == "__main__":
    process_files()
