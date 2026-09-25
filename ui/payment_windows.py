import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from decimal import Decimal, InvalidOperation

from services import payment_service


class PaymentWindow:
    def __init__(self, parent, student, on_saved=None):
        self.parent = parent
        self.student = student
        self.on_saved = on_saved

        self.window = tk.Toplevel(parent)
        self.window.title("Add Payment")
        self.window.geometry("420x420")
        self.window.resizable(False, False)

        self.build_ui()

    def build_ui(self):
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill="both", expand=True)

        title = ttk.Label(
            main_frame,
            text=f"Payment - {self.student['name']}",
            font=("Segoe UI", 16, "bold")
        )
        title.pack(pady=(0, 20))

        # Amount
        ttk.Label(main_frame, text="Amount").pack(anchor="w")

        self.amount_var = tk.StringVar()

        ttk.Entry(
            main_frame,
            textvariable=self.amount_var
        ).pack(fill="x", pady=(5, 15))

        # Date
        ttk.Label(main_frame, text="Payment Date").pack(anchor="w")

        self.date_var = tk.StringVar(
            value=date.today().isoformat()
        )

        ttk.Entry(
            main_frame,
            textvariable=self.date_var
        ).pack(fill="x", pady=(5, 15))

        # Status
        ttk.Label(main_frame, text="Status").pack(anchor="w")

        self.status_var = tk.StringVar(value="Paid")

        status_box = ttk.Combobox(
            main_frame,
            textvariable=self.status_var,
            values=["Paid", "Pending"],
            state="readonly"
        )
        status_box.pack(fill="x", pady=(5, 15))

        # Payment method
        ttk.Label(main_frame, text="Payment Method").pack(anchor="w")

        self.method_var = tk.StringVar()

        method_box = ttk.Combobox(
            main_frame,
            textvariable=self.method_var,
            values=[
                "Cash",
                "Bank",
                "Mobile Banking",
                "Other"
            ]
        )
        method_box.pack(fill="x", pady=(5, 15))

        # Notes
        ttk.Label(main_frame, text="Notes").pack(anchor="w")

        self.notes_text = tk.Text(
            main_frame,
            height=4,
            width=40
        )
        self.notes_text.pack(fill="x", pady=(5, 15))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.window.destroy
        ).pack(side="right", padx=(5, 0))

        ttk.Button(
            button_frame,
            text="Save Payment",
            command=self.save_payment
        ).pack(side="right")

    def save_payment(self):
        amount_text = self.amount_var.get().strip()
        payment_date = self.date_var.get().strip()
        status = self.status_var.get().strip().lower()
        payment_method = self.method_var.get().strip()
        notes = self.notes_text.get("1.0", "end").strip()

        # Validate amount
        if not amount_text:
            messagebox.showwarning(
                "Missing Amount",
                "Please enter a payment amount.",
                parent=self.window
            )
            return

        try:
            amount = Decimal(amount_text)
        except InvalidOperation:
            messagebox.showwarning(
                "Invalid Amount",
                "Please enter a valid number.",
                parent=self.window
            )
            return

        if amount < 0:
            messagebox.showwarning(
                "Invalid Amount",
                "Amount cannot be negative.",
                parent=self.window
            )
            return

        # Validate date
        try:
            date.fromisoformat(payment_date)
        except ValueError:
            messagebox.showwarning(
                "Invalid Date",
                "Please use the format YYYY-MM-DD.",
                parent=self.window
            )
            return

        try:
            payment_service.save_payment(
                self.student,
                amount,
                payment_date,
                status,
                payment_method,
                notes
            )

            messagebox.showinfo(
                "Payment Saved",
                "Payment has been saved successfully.",
                parent=self.window
            )

            if self.on_saved:
                self.on_saved()

            self.window.destroy()

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not save payment.\n\n{error}",
                parent=self.window
            )