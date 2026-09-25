from datetime import date


class AppState:

    def __init__(self):
        # All students loaded from the database
        self.students = []

        # Currently selected student
        self.selected_student = None

        # Current calendar month
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month

        # Cached class dates
        self.class_cache = {}

    def set_students(self, students):
        self.students = students

    def select_student(self, student):
        self.selected_student = student

    def clear_selection(self):
        self.selected_student = None

    def clear_class_cache(self):
        self.class_cache.clear()