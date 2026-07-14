# Divine Energy - Bill Generator

Generates itemized PDF receipts sized for an 80mm thermal receipt printer. Prompts for product name, price, quantity, and weight per item, plus a delivery charge, then outputs a PDF into a `bills` folder.

## Option 1: Just run the app (no install needed)

Download `BillGenerator.exe` from the [Releases](../../releases) page and the `assets` folder from this repo (must sit next to the exe). Double-click or run `BillGenerator.exe` from a terminal.

## Option 2: Run from source

Requires Python 3.

```
pip install -r requirements.txt
python bill_generator.py
```

## Rebuilding the standalone exe

```
pip install pyinstaller
pyinstaller --onefile --name BillGenerator bill_generator.py
```
