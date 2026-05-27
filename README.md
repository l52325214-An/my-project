# My Python Project

A standard Python project template containing `src` and `test` directories.

## Project Structure

```text
├── src/            # Core source files
│   └── main.py     # Entry point of the application
├── test/           # Test files
│   └── test_main.py # Pytest unit tests
├── .gitignore      # Git ignore list
└── requirements.txt # Python dependencies
```

## Getting Started

### Prerequisites

- [Python](https://www.python.org/) (v3.8 or higher recommended)

### Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   ```
2. Activate the virtual environment:
   - On Windows (PowerShell):
     ```bash
     .venv\Scripts\Activate.ps1
     ```
   - On Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

To run the main application:

```bash
python src/main.py
```

### Running Tests

To run unit tests using `pytest`:

```bash
pytest
```
