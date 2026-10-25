# Chapter 14 - Database-Connected AI Agent

A read-only SQLite inventory assistant with Ollama and Qwen 3.5 for Microsoft Visual Studio 2026.

## Start in Visual Studio 2026

1. Extract **all contents of this ZIP into one folder**. Do not extract into an extra nested folder.
2. Open `Chapter14_DatabaseAgent.sln` using **Open a project or solution**, not **Open folder**.
3. Under the project Python Environments, set up `.venv`, or from Developer PowerShell in this folder:
   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
   Python 3.10 also works with the listed dependency range.
4. Set Visual Studio's run interpreter to `.venv\Scripts\python.exe` (Project > Properties > Debug > Interpreter Path if necessary).
5. Start Ollama and run `ollama pull qwen3.5:9b` (or choose qwen3.5:4b in settings.py and pull that).
6. Use **Ctrl+F5**. The app automatically creates `data/inventory.db`.

## Example questions
- Which products are low in stock?
- How many USB Drives are in stock?
- Show Stationery products.
- What is the total inventory value?
- Can you delete all products? (This must not perform a database write.)

## Run offline tests
```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The tests use a simulated Ollama client. Live AI answers require Ollama running locally.

## Safety model
- Qwen is permitted to select **only four approved, read-only tools**.
- The AI never creates SQL strings.
- The Python layer validates arguments and uses parameterized SQL.
- No INSERT/UPDATE/DELETE tools are exposed.
- The SQLite database is a fictional teaching dataset; no confidential information.

## GitHub
Commit Python code, solution/project files, requirements, README and tests. Do not commit `.venv`, `.vs` or the runtime `.db` file.
