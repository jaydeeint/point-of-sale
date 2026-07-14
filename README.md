# Divine Energy - Bill Generator

A desktop app that generates itemized PDF receipts sized for an 80mm thermal receipt printer, and logs every transaction to `transactions.xlsx`.

## Option 1: Just run the app (no install needed)

Download the zip from the [Releases](../../releases) page, unzip it, and run `BillGenerator.exe`. Keep the `assets` folder next to it.

## Option 2: Run from source

Requires Python 3.

```
pip install -r requirements.txt
python billing_gui.py
```

A console-only version is also available (`bill_generator.py`) if you prefer a terminal-based flow instead of the GUI.

## Features

- Add, edit, and delete individual line items before generating a bill (no need to start over on a mistake)
- Live-updating item and grand totals as you type
- Delivery charge support
- Every bill logs its line items to `transactions.xlsx`
- Sales Summary tab: today / this month / all-time totals
- Receipts sized and cropped for 80mm thermal printers, with your logo

## Rebuilding the standalone exe

```
pip install pyinstaller
pyinstaller --onefile --windowed --name BillGenerator billing_gui.py
```
