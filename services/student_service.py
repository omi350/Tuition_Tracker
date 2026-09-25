from database import (
    get_all_people,
    add_person_to_database,
    delete_person_from_database
)


def get_students():
    return get_all_people()


def load_students(state):
    students = get_students()
    state.set_students(students)

    if state.selected_student is not None:
        selected_id = state.selected_student["id"]

        state.selected_student = next(
            (
                student
                for student in students
                if student["id"] == selected_id
            ),
            None
        )

    return students


def add_student(name, weekly_days, target, salary):
    name = name.strip()

    if not name:
        raise ValueError("Student name cannot be empty.")

    if weekly_days < 0:
        raise ValueError("Classes per week cannot be negative.")

    if target < 0:
        raise ValueError("Target cannot be negative.")

    if salary < 0:
        raise ValueError("Salary cannot be negative.")

    return add_person_to_database(
        name,
        weekly_days,
        target,
        salary
    )


def delete_student(state, student_id):
    delete_person_from_database(student_id)

    state.students = [
        student
        for student in state.students
        if student["id"] != student_id
    ]

    if (
        state.selected_student is not None
        and state.selected_student["id"] == student_id
    ):
        state.clear_selection()

    state.class_cache.pop(student_id, None)


def get_student_by_id(state, student_id):
    for student in state.students:
        if student["id"] == student_id:
            return student

    return None