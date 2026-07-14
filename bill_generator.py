import billing_core as core


def get_items():
    items = []
    print("Enter items for the bill. Type 'reset' as the product names to clear all items and start over.\n")
    while True:
        names_raw = input("Product names (separated by ,): ").strip()
        if names_raw.lower() == "reset":
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

        prices_raw = input("Prices (separated by ,): ").strip()
        quantities_raw = input("Quantities (separated by ,): ").strip()

        names = [n.strip() for n in names_raw.split(",") if n.strip()]
        price_tokens = [p.strip() for p in prices_raw.split(",") if p.strip()]
        quantity_tokens = [q.strip() for q in quantities_raw.split(",") if q.strip()]

        if not names or not (len(names) == len(price_tokens) == len(quantity_tokens)):
            print(
                f"Mismatch: {len(names)} name(s), {len(price_tokens)} price(s), "
                f"{len(quantity_tokens)} quantity(ies). Counts must match. Try again.\n"
            )
            continue

        try:
            prices = [float(p) for p in price_tokens]
            quantities = [int(q) for q in quantity_tokens]
        except ValueError:
            print("Prices must be numbers and quantities must be whole numbers. Try again.\n")
            continue

        batch = [{"name": n, "price": p, "quantity": q} for n, p, q in zip(names, prices, quantities)]

        print("\nConfirm these items:")
        for item in batch:
            subtotal = item["price"] * item["quantity"]
            print(f"  {item['name']}: {item['quantity']} x {item['price']:.2f} = {subtotal:.2f}")
        confirm = input("Add these items? (y/n): ").strip().lower()
        if confirm != "y":
            print("Discarded. Let's re-enter.\n")
            continue

        items.extend(batch)
        print(f"\n{len(batch)} item(s) added. Total items so far: {len(items)}\n")

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


def show_sales_summary():
    summary = core.get_sales_summary()
    if summary is None:
        print("No transactions recorded yet.")
        return

    today = summary["today"]
    month = summary["month"]
    all_time = summary["all_time"]

    print("\n--- Sales Summary ---")
    print(f"Today ({today['date']}): {today['count']} bill(s), Total: {today['total']:.2f}")
    print(f"This Month ({month['label']}): {month['count']} bill(s), Total: {month['total']:.2f}")
    print(f"All Time: {all_time['count']} bill(s), Total: {all_time['total']:.2f}")
    print("---------------------\n")


def make_bill():
    items = get_items()
    if not items:
        print("No items entered. Nothing to print.")
        return

    delivery_charge = get_delivery_charge()
    output_path, grand_total = core.generate_bill(items, delivery_charge)

    print(f"\nBill saved to: {output_path}")
    print(f"Transaction logged to: {core.EXCEL_PATH}")
    print(f"Grand Total: {grand_total:.2f}")


def main():
    print("1. Generate a new bill")
    print("2. View sales summary")
    choice = input("Choose an option (1/2): ").strip()

    if choice == "2":
        show_sales_summary()
        return

    make_bill()


if __name__ == "__main__":
    main()
