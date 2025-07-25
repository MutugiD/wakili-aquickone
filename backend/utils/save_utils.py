import os
from datetime import datetime
import csv

def save_drafted_document(doc_type: str, content: str, context: dict = None, outputs_dir: str = None) -> str:
    """
    Save the drafted document to the outputs directory with a timestamped filename.
    Log the event to a CSV file for traceability.
    Returns the path to the saved file.
    """
    if outputs_dir is None:
        outputs_dir = os.path.join(os.path.dirname(__file__), '../../docs', 'outputs')
    outputs_dir = os.path.abspath(outputs_dir)
    os.makedirs(outputs_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{doc_type}_{timestamp}.txt"
    file_path = os.path.join(outputs_dir, filename)

    # Save the document
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Log the event
    log_path = os.path.join(outputs_dir, 'draft_events_log.csv')
    log_fields = ['timestamp', 'doc_type', 'filename', 'context']
    log_exists = os.path.exists(log_path)
    with open(log_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=log_fields)
        if not log_exists:
            writer.writeheader()
        writer.writerow({
            'timestamp': timestamp,
            'doc_type': doc_type,
            'filename': filename,
            'context': str(context) if context else ''
        })

    return file_path