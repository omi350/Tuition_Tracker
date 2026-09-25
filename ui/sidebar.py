import tkinter as tk
from tkinter import ttk, messagebox

from services import student_service


class Sidebar:

    def __init__(
        self,
        parent,
        on_student_selected,
        on_student_added,
        on_delete_student,
        on_dashboard,
        on_calendar
    ):
        self.frame = ttk.Frame(parent)
        self.frame.configure(padding=15)

        self.on_student_selected = on_student_selected
        self.on_student_added = on_student_added
        self.on_delete_student = on_delete_student
        self.on_dashboard = on_dashboard
        self.on_calendar = on_calendar

        self.selected_student_id = None

        self.build_ui()

    def build_ui(self):

        ttk.Label(
            self.frame,
            text="Teaching Tracker",
            font=("Segoe UI", 18, "bold")
        ).pack(
            anchor="w",
            pady=(0, 20)
        )

        ttk.Button(
            self.frame,
            text="Dashboard",
            command=self.on_dashboard
        ).pack(
            fill="x",
            pady=3
        )

        ttk.Button(
            self.frame,
            text="Calendar",
            command=self.on_calendar
        ).pack(
            fill="x",
            pady=3
        )

        ttk.Separator(
            self.frame
        ).pack(
            fill="x",
            pady=15
        )

        ttk.Label(
            self.frame,
            text="Students",
            font=("Segoe UI", 11, "bold")
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

        self.student_list = ttk.Frame(self.frame)
        self.student_list.pack(
            fill="both",
            expand=True
        )

        ttk.Button(
            self.frame,
            text="+ Add Student",
            command=self.open_add_student
        ).pack(
            fill="x",
            pady=(10, 5)
        )

        ttk.Button(
            self.frame,
            text="Delete Student",
            command=self.delete_selected_student
        ).pack(
            fill="x"
        )

    def refresh(self, students):

        for widget in self.student_list.winfo_children():
            widget.destroy()

        for student in students:

            button = ttk.Button(
                self.student_list,
                text=student["name"],
                command=lambda s=student: self.select_student(s)
            )

            button.pack(
                fill="x",
                pady=2
            )

    def select_student(self, student):

        self.selected_student_id = student["id"]

        self.on_student_selected(student)

    def open_add_student(self):

        window = tk.Toplevel(self.frame)

        window.title("Add Student")
        window.geometry("400x400")
        window.resizable(False, False)

        frame = ttk.Frame(
            window,
            padding=20
        )

        frame.pack(
            fill="both",
            expand=True
        )

        ttk.Label(
            frame,
            text="Add Student",
            font=("Segoe UI", 18, "bold")
        ).pack(
            pady=(0, 20)
        )

        # Student name
        ttk.Label(
            frame,
            text="Student Name"
        ).pack(
            anchor="w"
        )

        name_entry = ttk.Entry(frame)

        name_entry.pack(
            fill="x",
            pady=(3, 10)
        )

        # Classes per week
        ttk.Label(
            frame,
            text="Classes Per Week"
        ).pack(
            anchor="w"
        )

        weekly_entry = ttk.Entry(frame)

        weekly_entry.pack(
            fill="x",
            pady=(3, 10)
        )

        # Salary
        ttk.Label(
            frame,
            text="Salary"
        ).pack(
            anchor="w"
        )

        salary_entry = ttk.Entry(frame)

        salary_entry.pack(
            fill="x",
            pady=(3, 10)
        )

        # Target
        ttk.Label(
            frame,
            text="Target Classes"
        ).pack(
            anchor="w"
        )

        target_entry = ttk.Entry(frame)

        target_entry.pack(
            fill="x",
            pady=(3, 15)
        )

        def save_student():

            try:
                name = name_entry.get().strip()

                weekly_days = int(
                    weekly_entry.get()
                )

                salary = float(
                    salary_entry.get()
                )

                target = int(
                    target_entry.get()
                )

                student_service.add_student(
                    name,
                    weekly_days,
                    target,
                    salary
                )

                window.destroy()

                self.on_student_added()

            except ValueError as error:

                messagebox.showerror(
                    "Invalid Information",
                    str(error),
                    parent=window
                )

            except Exception as error:

                messagebox.showerror(
                    "Save Error",
                    f"Could not save student.\n\n{error}",
                    parent=window
                )

        ttk.Button(
            frame,
            text="Save Student",
            command=save_student
        ).pack(
            fill="x",
            ipady=5
        )

        name_entry.focus()

    def delete_selected_student(self):

        if self.selected_student_id is None:

            messagebox.showwarning(
                "No Student Selected",
                "Please select a student first."
            )

            return

        confirm = messagebox.askyesno(
            "Delete Student",
            "Are you sure you want to delete this student?"
        )

        if not confirm:
            return

        self.on_delete_student(
            self.selected_student_id
        )