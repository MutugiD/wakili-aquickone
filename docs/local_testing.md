# Local Testing Guide: Wakili Quick1

## Prerequisites

- Python 3.8+
- All dependencies installed (`pip install -r requirements.txt`)
- `.env` file with required API keys (e.g., OpenAI)

## Running the System

1. Open a terminal in the project root.
2. Run the main test harness:
   ```
   python test_orchestrator.py
   ```
3. Observe the output in the terminal for test results and agent responses.

## Checking Drafted Outputs

- All generated legal documents (demand letters, plaints, briefs, affidavits) are saved in:
  - `docs/outputs/`
- Filenames are timestamped, e.g., `demand_letter_20240613_153000.txt`
- Each drafting event is logged in `docs/outputs/draft_events_log.csv` with:
  - Timestamp
  - Document type
  - Filename
  - Context (facts, research, user input)

## Custom Testing

- To test custom scenarios, edit or extend `test_orchestrator.py` with new queries and context.
- You can also call the orchestrator or DraftingAgent directly in a Python shell.

## Troubleshooting

- Ensure your `.env` file is present and correct.
- Check for errors in the terminal output.
- If outputs are not being saved, verify that `docs/outputs/` exists and is writable.

## Next Steps

- Review generated documents for legal accuracy and compliance.
- Use the event log for traceability and auditing.
- Extend the system with new document types or agents as needed.
