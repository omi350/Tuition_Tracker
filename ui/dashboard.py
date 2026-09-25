import tkinter as tk
from tkinter import ttk
from datetime import date

from services import class_service


class Dashboard(ttk.Frame):

    def __init__(self, parent, state):
        super().__init__(parent)

        self.state = state

        self.configure(
            padding=20
        )

        self.build_ui()

    def build_ui(self):

        # =========================
        # HEADER
        # =========================

        header = ttk.Frame(self)
        header.pack(
            fill="x",
            pady=(0, 20)
        )

        ttk.Label(
            header,
            text="Dashboard",
            font=("Segoe UI", 22, "bold")
        ).pack(side="left")

        self.selected_label = ttk.Label(
            header,
            text="No student selected",
            font=("Segoe UI", 11)
        )

        self.selected_label.pack(
            side="right"
        )

        # =========================
        # STAT CARDS
        # =========================

        stats = ttk.Frame(self)
        stats.pack(
            fill="x",
            pady=(0, 25)
        )

        for i in range(4):
            stats.columnconfigure(
                i,
                weight=1
            )

        self.students_value = self.create_card(
            stats,
            "Students",
            0
        )

        self.month_classes_value = self.create_card(
            stats,
            "Classes This Month",
            1
        )

        self.salary_value = self.create_card(
            stats,
            "Total Salary",
            2
        )

        self.all_classes_value = self.create_card(
            stats,
            "All Classes",
            3
        )

        # =========================
        # STUDENT OVERVIEW
        # =========================

        ttk.Label(
            self,
            text="Student Overview",
            font=("Segoe UI", 15, "bold")
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        container = ttk.Frame(self)
        container.pack(
            fill="both",
            expand=True
        )

        self.canvas = tk.Canvas(
            container,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=self.canvas.yview
        )

        self.student_frame = ttk.Frame(
            self.canvas
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.student_frame,
            anchor="nw"
        )

        self.student_frame.bind(
            "<Configure>",
            self.update_scroll_region
        )

        self.canvas.bind(
            "<Configure>",
            self.resize_student_frame
        )

        self.canvas.configure(
            yscrollcommand=scrollbar.set
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

    def create_card(
        self,
        parent,
        title,
        column
    ):

        card = ttk.Frame(
            parent,
            relief="ridge",
            borderwidth=1,
            padding=15
        )

        card.grid(
            row=0,
            column=column,
            sticky="nsew",
            padx=5
        )

        ttk.Label(
            card,
            text=title,
            font=("Segoe UI", 10)
        ).pack(
            anchor="w"
        )

        value = ttk.Label(
            card,
            text="0",
            font=("Segoe UI", 18, "bold")
        )

        value.pack(
            anchor="w",
            pady=(8, 0)
        )

        return value

    def update_scroll_region(
        self,
        event=None
    ):

        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    def resize_student_frame(
        self,
        event
    ):

        self.canvas.itemconfigure(
            self.canvas_window,
            width=event.width
        )

    # =========================
    # REFRESH DASHBOARD
    # =========================

    def refresh(
        self,
        students=None
    ):

        if students is None:
            students = self.state.students

        # Selected student

        if self.state.selected_student:

            self.selected_label.config(
                text=(
                    "Selected: "
                    + self.state.selected_student["name"]
                )
            )

        else:

            self.selected_label.config(
                text="No student selected"
            )

        # Student count

        self.students_value.config(
            text=str(len(students))
        )

        # Salary

        total_salary = 0

        for student in students:

            total_salary += float(
                student.get(
                    "salary",
                    0
                )
            )

        self.salary_value.config(
            text=f"{total_salary:,.2f}"
        )

        # Class counts

        total_classes = 0
        month_classes = 0

        today = date.today()

        for student in students:

            try:

                classes = class_service.load_classes(
                    student,
                    self.state
                )

                total_classes += len(classes)

                for class_date in classes:

                    parsed = date.fromisoformat(
                        str(class_date)
                    )

                    if (
                        parsed.year == today.year
                        and parsed.month == today.month
                    ):
                        month_classes += 1

            except Exception:

                pass

        self.all_classes_value.config(
            text=str(total_classes)
        )

        self.month_classes_value.config(
            text=str(month_classes)
        )

        # =========================
        # STUDENT LIST
        # =========================

        for widget in self.student_frame.winfo_children():
            widget.destroy()

        if not students:

            ttk.Label(
                self.student_frame,
                text="No students added yet.",
                font=("Segoe UI", 11)
            ).pack(
                pady=30
            )

            return

        for student in students:

            self.create_student_row(
                student
            )

    def create_student_row(
        self,
        student
    ):

        row = ttk.Frame(
            self.student_frame,
            relief="ridge",
            borderwidth=1,
            padding=15
        )

        row.pack(
            fill="x",
            pady=5
        )

        # LEFT SIDE

        left = ttk.Frame(row)

        left.pack(
            side="left",
            fill="x",
            expand=True
        )

        ttk.Label(
            left,
            text=student["name"],
            font=("Segoe UI", 13, "bold")
        ).pack(
            anchor="w"
        )

        ttk.Label(
            left,
            text=(
                f"Classes per week: "
                f"{student['weekly_days']}"
            )
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        ttk.Label(
            left,
            text=(
                f"Target: "
                f"{student['target']}"
            )
        ).pack(
            anchor="w"
        )

        ttk.Label(
            left,
            text=(
                f"Salary: "
                f"{student.get('salary', 0):,.2f}"
            )
        ).pack(
            anchor="w"
        )

        # RIGHT SIDE

        try:

            classes = class_service.load_classes(
                student,
                self.state
            )

            class_count = len(classes)

        except Exception:

            class_count = 0

        right = ttk.Frame(row)

        right.pack(
            side="right"
        )

        ttk.Label(
            right,
            text=str(class_count),
            font=("Segoe UI", 18, "bold")
        ).pack()

        ttk.Label(
            right,
            text="Total Classes"
        ).pack()

    def update(
        self,
        students=None
    ):

        self.refresh(
            students
        )