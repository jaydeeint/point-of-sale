import os
import sys
from datetime import date

import fitz
from fpdf import FPDF

MM_TO_PT = 72 / 25.4

if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(__file__)

OUTPUT_DIR = os.path.join(APP_DIR, "bills")
LOGO_PATH = os.path.join(APP_DIR, "assets", "logo.png")

PAGE_WIDTH = 80
MARGIN = 4
USABLE_WIDTH = PAGE_WIDTH - (2 * MARGIN)


def get_items():
    items = []
    print("Enter items for the bill. Type 'reset' as the product name to clear all items and start over.\n")
    while True:
        name = input("Product name: ").strip()
        if not name:
            print("Product name cannot be blank. Try again.\n")
            continue
        if name.lower() == "reset":
            if items:
                confirm_reset = input(f"Clear all {len(items)} item(s) entered so far? (y/n): ").strip().lower()
                if confirm_reset == "y":
                    items = []
                    print("All items cleared. Starting over.\n")
                else:
                    print("Reset cancelled.\n")
            else:
                print("No items to reset.\n")
            continue
        try:
            price = float(input("Price: ").strip())
            quantity = int(input("Quantity: ").strip())
            weight = float(input("Weight: ").strip() or 0)
        except ValueError:
            print("Price/weight must be numbers and quantity must be a whole number. Try again.\n")
            continue

        print(f"\nConfirm: {name} x{quantity} @ {price:.2f}, Weight: {weight:.2f} kg")
        confirm = input("Add this item? (y/n): ").strip().lower()
        if confirm != "y":
            print("Item discarded. Let's re-enter it.\n")
            continue

        items.append({"name": name, "price": price, "quantity": quantity, "weight": weight})
        print(f"Added: {name} x{quantity} @ {price:.2f}\n")

        generate = input("Generate bill now? (y/n): ").strip().lower()
        if generate == "y":
            break
    return items


def get_delivery_charge():
    while True:
        raw = input("Delivery charge (0 for none): ").strip() or "0"
        try:
            return float(raw)
        except ValueError:
            print("Delivery charge must be a number. Try again.")


def estimate_page_height(items):
    header_height = 46 if os.path.exists(LOGO_PATH) else 20
    items_height = len(items) * 15
    footer_height = 30
    safety_buffer = 20
    return header_height + items_height + footer_height + safety_buffer


class BillPDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_PATH):
            logo_w = 24
            self.image(LOGO_PATH, x=(self.w - logo_w) / 2, y=4, w=logo_w)
            self.set_y(4 + logo_w + 2)
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 6, "RECEIPT", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 7)
        self.cell(0, 4, f"Date: {date.today().isoformat()}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)


def dashed_separator(pdf):
    y = pdf.get_y() + 1
    pdf.set_dash_pattern(dash=1, gap=1)
    pdf.line(MARGIN, y, PAGE_WIDTH - MARGIN, y)
    pdf.set_dash_pattern()
    pdf.set_y(y + 2)


def build_pdf(items, delivery_charge, output_path):
    pdf = BillPDF()
    pdf.set_margins(MARGIN, MARGIN, MARGIN)
    pdf.set_auto_page_break(False)
    page_height = estimate_page_height(items)
    pdf.add_page(format=(PAGE_WIDTH, page_height))

    items_total = 0.0
    for item in items:
        subtotal = item["price"] * item["quantity"]
        items_total += subtotal

        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(USABLE_WIDTH, 4, item["name"], new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 8)
        pdf.cell(USABLE_WIDTH / 2, 4, f"{item['quantity']} x {item['price']:.2f}")
        pdf.cell(USABLE_WIDTH / 2, 4, f"{subtotal:.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 7)
        pdf.cell(USABLE_WIDTH, 4, f"Weight: {item['weight']:.2f} kg", new_x="LMARGIN", new_y="NEXT")

        dashed_separator(pdf)

    delivery_display = "None" if delivery_charge == 0 else f"{delivery_charge:.2f}"
    grand_total = items_total + delivery_charge

    pdf.set_font("Helvetica", "", 8)
    pdf.cell(USABLE_WIDTH / 2, 5, "Items Total")
    pdf.cell(USABLE_WIDTH / 2, 5, f"{items_total:.2f}", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(USABLE_WIDTH / 2, 5, "Delivery Charge")
    pdf.cell(USABLE_WIDTH / 2, 5, delivery_display, align="R", new_x="LMARGIN", new_y="NEXT")

    dashed_separator(pdf)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(USABLE_WIDTH / 2, 6, "Grand Total")
    pdf.cell(USABLE_WIDTH / 2, 6, f"{grand_total:.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

    content_height_mm = min(pdf.get_y() + MARGIN, page_height)

    pdf.output(output_path)
    trim_to_content(output_path, page_height, content_height_mm)
    return grand_total


def trim_to_content(pdf_path, page_height_mm, content_height_mm):
    doc = fitz.open(pdf_path)
    page = doc[0]
    width_pt = page.rect.width
    top_pt = page_height_mm * MM_TO_PT
    bottom_pt = (page_height_mm - content_height_mm) * MM_TO_PT
    page.set_mediabox(fitz.Rect(0, bottom_pt, width_pt, top_pt))
    doc.saveIncr()
    doc.close()


def main():
    items = get_items()
    if not items:
        print("No items entered. Nothing to print.")
        return

    delivery_charge = get_delivery_charge()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"bill_{date.today().isoformat()}_{len(os.listdir(OUTPUT_DIR)) + 1}.pdf"
    output_path = os.path.join(OUTPUT_DIR, filename)

    grand_total = build_pdf(items, delivery_charge, output_path)

    print(f"\nBill saved to: {output_path}")
    print(f"Grand Total: {grand_total:.2f}")


if __name__ == "__main__":
    main()
