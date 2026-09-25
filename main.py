import tkinter as tk
from tkinter import ttk, messagebox

from app_state import AppState
from database import initialize_database

from services import student_service

from ui.sidebar import Sidebar
from ui.dashboard import Dashboard
from ui.calendar_view import CalendarView


class TeachingTrackerApp:

    def __init__(self, root):

        self.root = root
        self.state = AppState()

        self.root.title(
            "Teaching Tracker"
        )

        self.root.geometry(
            "1200x750"
        )

        self.root.minsize(
            950,
            600
        )

        self.setup_style()
        self.setup_ui()
        self.reload_students()

    def setup_style(self):

        self.style = ttk.Style()

        try:
            self.style.theme_use(
                "clam"
            )

        except tk.TclError:
            pass

    def setup_ui(self):

        self.main_frame = ttk.Frame(
            self.root
        )

        self.main_frame.pack(
            fill="both",
            expand=True
        )

        # -------------------------
        # SIDEBAR
        # -------------------------

        self.sidebar_frame = ttk.Frame(
            self.main_frame,
            width=240
        )

        self.sidebar_frame.pack(
            side="left",
            fill="y"
        )

        self.sidebar_frame.pack_propagate(
            False
        )

        self.sidebar = Sidebar(
            parent=self.sidebar_frame,
            on_student_selected=self.open_student_calendar,
            on_student_added=self.reload_students,
            on_delete_student=self.delete_student,
            on_dashboard=self.show_dashboard,
            on_calendar=self.show_selected_student_calendar
        )

        self.sidebar.frame.pack(
            fill="both",
            expand=True
        )

        # -------------------------
        # CONTENT
        # -------------------------

        self.content_frame = ttk.Frame(
            self.main_frame
        )

        self.content_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.dashboard_page = ttk.Frame(
            self.content_frame
        )

        self.dashboard_page.pack(
            fill="both",
            expand=True
        )

        self.dashboard = Dashboard(
            self.dashboard_page,
            self.state
        )

        self.dashboard.pack(
            fill="both",
            expand=True
        )

        self.show_dashboard()

    # =====================================================
    # STUDENTS
    # =====================================================

    def reload_students(self):

        try:

            students = student_service.get_students()

            old_selected_id = None

            if self.state.selected_student:

                old_selected_id = (
                    self.state.selected_student["id"]
                )

            self.state.set_students(
                students
            )

            selected_student = None

            if old_selected_id is not None:

                for student in students:

                    if student["id"] == old_selected_id:

                        selected_student = student
                        break

            if selected_student is None and students:

                selected_student = students[0]

            self.state.selected_student = (
                selected_student
            )

            if selected_student:

                self.sidebar.selected_student_id = (
                    selected_student["id"]
                )

            else:

                self.sidebar.selected_student_id = None

            self.sidebar.refresh(
                students
            )

            self.dashboard.refresh(
                students
            )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                f"Could not load students.\n\n{error}"
            )

    def select_student(
        self,
        student
    ):

        self.state.select_student(
            student
        )

        self.sidebar.selected_student_id = (
            student["id"]
        )

        self.dashboard.refresh(
            self.state.students
        )

    # =====================================================
    # CALENDAR
    # =====================================================

    def open_student_calendar(
        self,
        student
    ):

        self.select_student(
            student
        )

        CalendarView(
            self.root,
            self.state,
            student
        )

    def show_selected_student_calendar(self):

        student = (
            self.state.selected_student
        )

        if student is None:

            messagebox.showwarning(
                "No Student Selected",
                "Please select a student first."
            )

            return

        self.open_student_calendar(
            student
        )

    # =====================================================
    # DELETE
    # =====================================================

    def delete_student(
        self,
        student_id
    ):

        try:

            student_service.delete_student(
                self.state,
                student_id
            )

            self.sidebar.selected_student_id = None

            self.reload_students()

        except Exception as error:

            messagebox.showerror(
                "Delete Error",
                f"Could not delete student.\n\n{error}"
            )

    # =====================================================
    # DASHBOARD
    # =====================================================

    def show_dashboard(self):

        self.dashboard_page.pack(
            fill="both",
            expand=True
        )

        self.dashboard.refresh(
            self.state.students
        )


def main():

    root = tk.Tk()

    try:

        initialize_database()

    except Exception as error:

        messagebox.showerror(
            "Database Connection Error",
            f"Could not connect to PostgreSQL.\n\n{error}"
        )

        root.destroy()

        return

    TeachingTrackerApp(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()