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
        self.window.geometry("500x650")
        self.window.resizable(False, False)

        self.build_ui()

        self.window.transient(parent)
        self.window.grab_set()

    def build_ui(self):

        # Main window layout
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

        main = ttk.Frame(
            self.window,
            padding=25
        )

        main.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        main.columnconfigure(0, weight=1)

        # =========================
        # TITLE
        # =========================

        ttk.Label(
            main,
            text="Add Payment",
            font=("Segoe UI", 22, "bold")
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 5)
        )

        ttk.Label(
            main,
            text=f"Student: {self.student['name']}",
            font=("Segoe UI", 11)
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=(0, 25)
        )

        # =========================
        # AMOUNT
        # =========================

        ttk.Label(
            main,
            text="Amount"
        ).grid(
            row=2,
            column=0,
            sticky="w"
        )

        self.amount_var = tk.StringVar()

        ttk.Entry(
            main,
            textvariable=self.amount_var,
            font=("Segoe UI", 11)
        ).grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(5, 15)
        )

        # =========================
        # DATE
        # =========================

        ttk.Label(
            main,
            text="Payment Date"
        ).grid(
            row=4,
            column=0,
            sticky="w"
        )

        self.date_var = tk.StringVar(
            value=date.today().isoformat()
        )

        ttk.Entry(
            main,
            textvariable=self.date_var,
            font=("Segoe UI", 11)
        ).grid(
            row=5,
            column=0,
            sticky="ew",
            pady=(5, 15)
        )

        # =========================
        # STATUS
        # =========================

        ttk.Label(
            main,
            text="Status"
        ).grid(
            row=6,
            column=0,
            sticky="w"
        )

        self.status_var = tk.StringVar(
            value="Paid"
        )

        ttk.Combobox(
            main,
            textvariable=self.status_var,
            values=[
                "Paid",
                "Pending"
            ],
            state="readonly",
            font=("Segoe UI", 11)
        ).grid(
            row=7,
            column=0,
            sticky="ew",
            pady=(5, 15)
        )

        # =========================
        # PAYMENT METHOD
        # =========================

        ttk.Label(
            main,
            text="Payment Method"
        ).grid(
            row=8,
            column=0,
            sticky="w"
        )

        self.method_var = tk.StringVar()

        ttk.Combobox(
            main,
            textvariable=self.method_var,
            values=[
                "Cash",
                "Bank",
                "Mobile Banking",
                "Other"
            ],
            font=("Segoe UI", 11)
        ).grid(
            row=9,
            column=0,
            sticky="ew",
            pady=(5, 15)
        )

        # =========================
        # NOTES
        # =========================

        ttk.Label(
            main,
            text="Notes"
        ).grid(
            row=10,
            column=0,
            sticky="w"
        )

        self.notes_text = tk.Text(
            main,
            height=6,
            font=("Segoe UI", 10)
        )

        self.notes_text.grid(
            row=11,
            column=0,
            sticky="ew",
            pady=(5, 20)
        )

        # =========================
        # BUTTON BAR
        # =========================

        button_frame = ttk.Frame(main)

        button_frame.grid(
            row=12,
            column=0,
            sticky="ew",
            pady=(10, 0)
        )

        button_frame.columnconfigure(
            0,
            weight=1
        )

        button_frame.columnconfigure(
            1,
            weight=1
        )

        # SAVE BUTTON
        save_button = tk.Button(
            button_frame,
            text="SAVE PAYMENT",
            command=self.save_payment,
            font=("Segoe UI", 11, "bold"),
            height=2,
            cursor="hand2"
        )

        save_button.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 5)
        )

        # CANCEL BUTTON
        cancel_button = tk.Button(
            button_frame,
            text="CANCEL",
            command=self.window.destroy,
            font=("Segoe UI", 11),
            height=2,
            cursor="hand2"
        )

        cancel_button.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(5, 0)
        )

        # Focus amount field
        self.window.after(
            100,
            lambda: self.amount_focus()
        )

    def amount_focus(self):

        children = self.window.winfo_children()

        if children:
            try:
                self.window.focus_force()
            except tk.TclError:
                pass

    def save_payment(self):

        amount_text = self.amount_var.get().strip()
        payment_date = self.date_var.get().strip()
        status = self.status_var.get().strip().lower()
        payment_method = self.method_var.get().strip()

        notes = self.notes_text.get(
            "1.0",
            "end"
        ).strip()

        # -------------------------
        # VALIDATE AMOUNT
        # -------------------------

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

        # -------------------------
        # VALIDATE DATE
        # -------------------------

        try:
            date.fromisoformat(payment_date)

        except ValueError:

            messagebox.showwarning(
                "Invalid Date",
                "Please use YYYY-MM-DD.",
                parent=self.window
            )

            return

        # -------------------------
        # VALIDATE STATUS
        # -------------------------

        if status not in (
            "paid",
            "pending"
        ):

            messagebox.showwarning(
                "Invalid Status",
                "Please select Paid or Pending.",
                parent=self.window
            )

            return

        # -------------------------
        # SAVE TO DATABASE
        # -------------------------

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