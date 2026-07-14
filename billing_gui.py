import os
import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk
from PIL import Image

import billing_core as core

GOLD = "#C9A227"
GOLD_HOVER = "#B08D1B"
RED = "#B3261E"
RED_HOVER = "#8C1D17"

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")


def style_treeview():
    mode = ctk.get_appearance_mode()
    if mode == "Dark":
        bg, fg, field_bg, selected = "#2b2b2b", "#e6e6e6", "#2b2b2b", "#3a3a3a"
    else:
        bg, fg, field_bg, selected = "#ffffff", "#1a1a1a", "#ffffff", "#e6d18f"

    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Bill.Treeview",
        background=field_bg,
        foreground=fg,
        fieldbackground=field_bg,
        rowheight=28,
        borderwidth=0,
        font=("Segoe UI", 11),
    )
    style.configure(
        "Bill.Treeview.Heading",
        background=bg,
        foreground=GOLD,
        font=("Segoe UI", 11, "bold"),
        borderwidth=0,
    )
    style.map("Bill.Treeview", background=[("selected", selected)])


class BillingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Divine Energy - Bill Generator")
        self.geometry("980x680")
        self.minsize(860, 600)

        self.items = []
        self.editing_index = None

        style_treeview()
        self._build_header()

        self.tabs = ctk.CTkTabview(self, fg_color="transparent")
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.tabs.add("New Bill")
        self.tabs.add("Sales Summary")

        self._build_new_bill_tab(self.tabs.tab("New Bill"))
        self._build_summary_tab(self.tabs.tab("Sales Summary"))

        self.tabs.configure(command=self._on_tab_change)

    # ---------- Header ----------

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        if os.path.exists(core.LOGO_PATH):
            img = Image.open(core.LOGO_PATH)
            logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(48, 48))
            logo_label = ctk.CTkLabel(header, image=logo_img, text="")
            logo_label.pack(side="left", padx=(0, 12))

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")
        ctk.CTkLabel(
            title_frame, text="Divine Energy", font=ctk.CTkFont(size=22, weight="bold"), text_color=GOLD
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_frame, text="Bill Generator", font=ctk.CTkFont(size=13), text_color="gray60"
        ).pack(anchor="w")

    # ---------- New Bill tab ----------

    def _build_new_bill_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        form = ctk.CTkFrame(parent, corner_radius=10)
        form.grid(row=0, column=0, sticky="ew", pady=(10, 10))
        form.grid_columnconfigure((0, 1, 2), weight=1)

        self.name_entry = ctk.CTkEntry(form, placeholder_text="Product name")
        self.name_entry.grid(row=0, column=0, sticky="ew", padx=(15, 5), pady=15)

        self.price_entry = ctk.CTkEntry(form, placeholder_text="Price")
        self.price_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=15)

        self.qty_entry = ctk.CTkEntry(form, placeholder_text="Quantity")
        self.qty_entry.grid(row=0, column=2, sticky="ew", padx=5, pady=15)

        self.add_button = ctk.CTkButton(
            form, text="+ Add Item", fg_color=GOLD, hover_color=GOLD_HOVER, text_color="black",
            width=120, command=self._on_add_or_update
        )
        self.add_button.grid(row=0, column=3, padx=(5, 10), pady=15)

        self.cancel_edit_button = ctk.CTkButton(
            form, text="Cancel", width=80, fg_color="gray40", hover_color="gray30",
            command=self._cancel_edit
        )

        self.form_status = ctk.CTkLabel(parent, text="", text_color=RED, anchor="w")
        self.form_status.grid(row=0, column=0, sticky="sw", padx=15, pady=(0, 0))

        # Items table
        table_frame = ctk.CTkFrame(parent, corner_radius=10)
        table_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        columns = ("product", "price", "qty", "subtotal")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", style="Bill.Treeview", selectmode="browse"
        )
        self.tree.heading("product", text="Product")
        self.tree.heading("price", text="Price")
        self.tree.heading("qty", text="Qty")
        self.tree.heading("subtotal", text="Subtotal")
        self.tree.column("product", anchor="w", width=320)
        self.tree.column("price", anchor="e", width=100)
        self.tree.column("qty", anchor="e", width=80)
        self.tree.column("subtotal", anchor="e", width=120)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(15, 0), pady=15)
        self.tree.bind("<Double-1>", lambda e: self._start_edit_selected())

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=15, padx=(0, 15))

        # Row action buttons
        row_actions = ctk.CTkFrame(parent, fg_color="transparent")
        row_actions.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkButton(
            row_actions, text="Edit Selected", width=130, command=self._start_edit_selected
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            row_actions, text="Delete Selected", width=130, fg_color=RED, hover_color=RED_HOVER,
            command=self._delete_selected
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            row_actions, text="Clear All", width=100, fg_color="gray40", hover_color="gray30",
            command=self._clear_all
        ).pack(side="left")

        # Delivery + totals + generate
        bottom = ctk.CTkFrame(parent, corner_radius=10)
        bottom.grid(row=3, column=0, sticky="ew")
        bottom.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(bottom, text="Delivery Charge:").grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        self.delivery_entry = ctk.CTkEntry(bottom, placeholder_text="0")
        self.delivery_entry.grid(row=0, column=1, sticky="w", pady=(15, 5))
        self.delivery_entry.bind("<KeyRelease>", lambda e: self._refresh_totals())

        self.items_total_label = ctk.CTkLabel(bottom, text="Items Total: 0.00", anchor="e")
        self.items_total_label.grid(row=1, column=0, columnspan=2, sticky="e", padx=15)

        self.grand_total_label = ctk.CTkLabel(
            bottom, text="Grand Total: 0.00", font=ctk.CTkFont(size=18, weight="bold"), text_color=GOLD, anchor="e"
        )
        self.grand_total_label.grid(row=2, column=0, columnspan=2, sticky="e", padx=15, pady=(0, 10))

        self.generate_button = ctk.CTkButton(
            bottom, text="Generate Bill", height=44, font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=GOLD, hover_color=GOLD_HOVER, text_color="black", command=self._on_generate
        )
        self.generate_button.grid(row=3, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 15))

    # ---------- Sales Summary tab ----------

    def _build_summary_tab(self, parent):
        parent.grid_columnconfigure((0, 1, 2), weight=1)

        self.summary_cards = {}
        for i, key in enumerate(("today", "month", "all_time")):
            card = ctk.CTkFrame(parent, corner_radius=10)
            card.grid(row=0, column=i, sticky="nsew", padx=10, pady=15)
            title = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=13), text_color="gray60")
            title.pack(pady=(15, 0))
            total = ctk.CTkLabel(card, text="0.00", font=ctk.CTkFont(size=26, weight="bold"), text_color=GOLD)
            total.pack(pady=(5, 0))
            count = ctk.CTkLabel(card, text="0 bills", font=ctk.CTkFont(size=12), text_color="gray60")
            count.pack(pady=(0, 15))
            self.summary_cards[key] = (title, total, count)

        ctk.CTkButton(parent, text="Refresh", width=100, command=self._refresh_summary).grid(
            row=1, column=0, sticky="w", padx=10
        )

    def _on_tab_change(self):
        if self.tabs.get() == "Sales Summary":
            self._refresh_summary()

    def _refresh_summary(self):
        summary = core.get_sales_summary()
        if summary is None:
            for title, total, count in self.summary_cards.values():
                title.configure(text="No data")
                total.configure(text="0.00")
                count.configure(text="0 bills")
            return

        today, month, all_time = summary["today"], summary["month"], summary["all_time"]

        t_title, t_total, t_count = self.summary_cards["today"]
        t_title.configure(text=f"Today ({today['date']})")
        t_total.configure(text=f"{today['total']:.2f}")
        t_count.configure(text=f"{today['count']} bill(s)")

        m_title, m_total, m_count = self.summary_cards["month"]
        m_title.configure(text=f"This Month ({month['label']})")
        m_total.configure(text=f"{month['total']:.2f}")
        m_count.configure(text=f"{month['count']} bill(s)")

        a_title, a_total, a_count = self.summary_cards["all_time"]
        a_title.configure(text="All Time")
        a_total.configure(text=f"{all_time['total']:.2f}")
        a_count.configure(text=f"{all_time['count']} bill(s)")

    # ---------- Item form logic ----------

    def _clear_form(self):
        self.name_entry.delete(0, "end")
        self.price_entry.delete(0, "end")
        self.qty_entry.delete(0, "end")
        self.form_status.configure(text="")

    def _set_form_error(self, message):
        self.form_status.configure(text=message)

    def _read_form(self):
        name = self.name_entry.get().strip()
        price_raw = self.price_entry.get().strip()
        qty_raw = self.qty_entry.get().strip()

        if not name:
            self._set_form_error("Product name is required.")
            return None
        try:
            price = float(price_raw)
        except ValueError:
            self._set_form_error("Price must be a number.")
            return None
        try:
            quantity = int(qty_raw)
        except ValueError:
            self._set_form_error("Quantity must be a whole number.")
            return None

        self.form_status.configure(text="")
        return {"name": name, "price": price, "quantity": quantity}

    def _on_add_or_update(self):
        item = self._read_form()
        if item is None:
            return

        if self.editing_index is None:
            self.items.append(item)
        else:
            self.items[self.editing_index] = item
            self._cancel_edit(clear_form=False)

        self._clear_form()
        self._refresh_table()
        self._refresh_totals()

    def _start_edit_selected(self):
        selection = self.tree.selection()
        if not selection:
            return
        index = self.tree.index(selection[0])
        item = self.items[index]

        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, item["name"])
        self.price_entry.delete(0, "end")
        self.price_entry.insert(0, str(item["price"]))
        self.qty_entry.delete(0, "end")
        self.qty_entry.insert(0, str(item["quantity"]))

        self.editing_index = index
        self.add_button.configure(text="Update Item")
        self.cancel_edit_button.grid(row=0, column=4, padx=(0, 10), pady=15)

    def _cancel_edit(self, clear_form=True):
        self.editing_index = None
        self.add_button.configure(text="+ Add Item")
        self.cancel_edit_button.grid_forget()
        if clear_form:
            self._clear_form()

    def _delete_selected(self):
        selection = self.tree.selection()
        if not selection:
            return
        index = self.tree.index(selection[0])
        del self.items[index]
        if self.editing_index == index:
            self._cancel_edit()
        self._refresh_table()
        self._refresh_totals()

    def _clear_all(self):
        if not self.items:
            return
        if messagebox.askyesno("Clear All", f"Clear all {len(self.items)} item(s)?"):
            self.items = []
            self._cancel_edit()
            self._refresh_table()
            self._refresh_totals()

    def _refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for item in self.items:
            subtotal = item["price"] * item["quantity"]
            self.tree.insert(
                "", "end", values=(item["name"], f"{item['price']:.2f}", item["quantity"], f"{subtotal:.2f}")
            )

    def _get_delivery_charge(self):
        raw = self.delivery_entry.get().strip() or "0"
        try:
            return float(raw)
        except ValueError:
            return 0.0

    def _refresh_totals(self):
        items_total = sum(item["price"] * item["quantity"] for item in self.items)
        delivery = self._get_delivery_charge()
        grand_total = items_total + delivery
        self.items_total_label.configure(text=f"Items Total: {items_total:.2f}")
        self.grand_total_label.configure(text=f"Grand Total: {grand_total:.2f}")

    def _on_generate(self):
        if not self.items:
            messagebox.showwarning("No Items", "Add at least one item before generating a bill.")
            return

        delivery_charge = self._get_delivery_charge()
        output_path, grand_total = core.generate_bill(self.items, delivery_charge)

        self.items = []
        self._cancel_edit()
        self.delivery_entry.delete(0, "end")
        self._refresh_table()
        self._refresh_totals()

        if messagebox.askyesno(
            "Bill Generated",
            f"Bill saved:\n{output_path}\n\nGrand Total: {grand_total:.2f}\n\nOpen the PDF now?",
        ):
            os.startfile(output_path)


if __name__ == "__main__":
    app = BillingApp()
    app.mainloop()
