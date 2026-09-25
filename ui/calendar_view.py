import tkinter as tk
from tkinter import ttk, messagebox
from calendar import monthrange
from datetime import date

from services import class_service


class CalendarView:

    def __init__(self, parent, state, student):

        self.parent = parent
        self.state = state
        self.student = student

        self.window = tk.Toplevel(parent)

        self.window.title(
            f"Classes - {student['name']}"
        )

        self.window.geometry(
            "850x650"
        )

        self.window.minsize(
            700,
            550
        )

        self.current_year = date.today().year
        self.current_month = date.today().month

        self.build_ui()
        self.refresh()

    # ======================================================
    # BUILD UI
    # ======================================================

    def build_ui(self):

        main_frame = ttk.Frame(
            self.window,
            padding=20
        )

        main_frame.pack(
            fill="both",
            expand=True
        )

        # -------------------------------
        # Header
        # -------------------------------

        header = ttk.Frame(main_frame)

        header.pack(
            fill="x",
            pady=(0, 15)
        )

        ttk.Button(
            header,
            text="← Previous",
            command=self.previous_month
        ).pack(
            side="left"
        )

        self.month_label = ttk.Label(
            header,
            text="",
            font=("Segoe UI", 20, "bold")
        )

        self.month_label.pack(
            side="left",
            expand=True
        )

        ttk.Button(
            header,
            text="Next →",
            command=self.next_month
        ).pack(
            side="right"
        )

        # -------------------------------
        # Student information
        # -------------------------------

        info_frame = ttk.Frame(main_frame)

        info_frame.pack(
            fill="x",
            pady=(0, 15)
        )

        ttk.Label(
            info_frame,
            text=f"Student: {self.student['name']}",
            font=("Segoe UI", 12, "bold")
        ).pack(
            side="left"
        )

        ttk.Label(
            info_frame,
            text=f"Target: {self.student['target']}",
            font=("Segoe UI", 11)
        ).pack(
            side="right"
        )

        # -------------------------------
        # Legend
        # -------------------------------

        legend = ttk.Frame(main_frame)

        legend.pack(
            fill="x",
            pady=(0, 15)
        )

        self.legend_item(
            legend,
            "First Class",
            "#e74c3c"
        )

        self.legend_item(
            legend,
            "Normal Class",
            "#c8e6c9"
        )

        self.legend_item(
            legend,
            "Final Class",
            "#222222"
        )

        # -------------------------------
        # Calendar
        # -------------------------------

        self.calendar_frame = ttk.Frame(
            main_frame
        )

        self.calendar_frame.pack(
            fill="both",
            expand=True
        )

    # ======================================================
    # LEGEND
    # ======================================================

    def legend_item(
        self,
        parent,
        text,
        color
    ):

        frame = ttk.Frame(parent)

        frame.pack(
            side="left",
            padx=(0, 20)
        )

        box = tk.Label(
            frame,
            text="  ",
            bg=color,
            width=2
        )

        box.pack(
            side="left",
            padx=(0, 5)
        )

        ttk.Label(
            frame,
            text=text
        ).pack(
            side="left"
        )

    # ======================================================
    # PREVIOUS MONTH
    # ======================================================

    def previous_month(self):

        if self.current_month == 1:

            self.current_month = 12
            self.current_year -= 1

        else:

            self.current_month -= 1

        self.refresh()

    # ======================================================
    # NEXT MONTH
    # ======================================================

    def next_month(self):

        if self.current_month == 12:

            self.current_month = 1
            self.current_year += 1

        else:

            self.current_month += 1

        self.refresh()

    # ======================================================
    # REFRESH
    # ======================================================

    def refresh(self):

        for widget in self.calendar_frame.winfo_children():

            widget.destroy()

        year = self.current_year
        month = self.current_month

        self.month_label.config(
            text=date(
                year,
                month,
                1
            ).strftime("%B %Y")
        )

        # ----------------------------------------------
        # Load classes directly from database
        # ----------------------------------------------

        try:

            class_dates = class_service.refresh_classes(
                self.student,
                self.state
            )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                f"Could not load classes.\n\n{error}",
                parent=self.window
            )

            return

        # Make sure they are strings
        class_dates = set(
            str(class_date)
            for class_date in class_dates
        )

        # ----------------------------------------------
        # Sort recorded classes
        # ----------------------------------------------

        sorted_classes = sorted(
            class_dates
        )

        class_numbers = {}

        for number, class_date in enumerate(
            sorted_classes,
            start=1
        ):

            class_numbers[class_date] = number

        # ----------------------------------------------
        # Weekday headers
        # ----------------------------------------------

        weekdays = [
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat",
            "Sun"
        ]

        for column, weekday in enumerate(
            weekdays
        ):

            self.calendar_frame.columnconfigure(
                column,
                weight=1
            )

            ttk.Label(
                self.calendar_frame,
                text=weekday,
                anchor="center",
                font=("Segoe UI", 10, "bold")
            ).grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=2,
                pady=2
            )

        # ----------------------------------------------
        # Calendar days
        # ----------------------------------------------

        first_weekday, number_of_days = monthrange(
            year,
            month
        )

        for day in range(
            1,
            number_of_days + 1
        ):

            position = (
                first_weekday
                + day
                - 1
            )

            row = (
                position // 7
                + 1
            )

            column = (
                position % 7
            )

            date_string = date(
                year,
                month,
                day
            ).isoformat()

            class_number = class_numbers.get(
                date_string
            )

            self.create_day(
                date_string,
                day,
                row,
                column,
                class_number
            )

            self.calendar_frame.rowconfigure(
                row,
                weight=1
            )

    # ======================================================
    # CREATE DAY
    # ======================================================

    def create_day(
        self,
        date_string,
        day,
        row,
        column,
        class_number
    ):

        # ----------------------------------------------
        # No class
        # ----------------------------------------------

        if class_number is None:

            button = tk.Button(
                self.calendar_frame,
                text=str(day),
                font=("Segoe UI", 11),
                bg="white",
                activebackground="#eeeeee",
                relief="solid",
                borderwidth=1,
                command=lambda:
                    self.toggle_date(date_string)
            )

        # ----------------------------------------------
        # First class
        # ----------------------------------------------

        elif class_number == 1:

            button = tk.Button(
                self.calendar_frame,
                text=f"{day}\nFIRST CLASS",
                font=("Segoe UI", 10, "bold"),
                fg="white",
                bg="#e74c3c",
                activebackground="#c0392b",
                relief="solid",
                borderwidth=1,
                command=lambda:
                    self.toggle_date(date_string)
            )

        # ----------------------------------------------
        # Final class
        # ----------------------------------------------

        elif (
            self.student["target"] > 0
            and class_number == self.student["target"]
        ):

            button = tk.Button(
                self.calendar_frame,
                text=f"{day}\nFINAL CLASS",
                font=("Segoe UI", 10, "bold"),
                fg="white",
                bg="#222222",
                activebackground="#000000",
                relief="solid",
                borderwidth=1,
                command=lambda:
                    self.toggle_date(date_string)
            )

        # ----------------------------------------------
        # Normal class
        # ----------------------------------------------

        else:

            button = tk.Button(
                self.calendar_frame,
                text=f"{day}\nCLASS {class_number}",
                font=("Segoe UI", 10, "bold"),
                fg="#333333",
                bg="#c8e6c9",
                activebackground="#a5d6a7",
                relief="solid",
                borderwidth=1,
                command=lambda:
                    self.toggle_date(date_string)
            )

        button.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=3,
            pady=3,
            ipadx=5,
            ipady=12
        )

    # ======================================================
    # ADD / REMOVE CLASS
    # ======================================================

    def toggle_date(
        self,
        class_date
    ):

        try:

            exists = class_service.has_class(
                self.student,
                class_date,
                self.state
            )

            if exists:

                class_service.remove_student_class(
                    self.student,
                    class_date,
                    self.state
                )

            else:

                class_service.add_student_class(
                    self.student,
                    class_date,
                    self.state
                )

            # Reload from PostgreSQL
            self.refresh()

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                f"Could not update class.\n\n{error}",
                parent=self.window
            )