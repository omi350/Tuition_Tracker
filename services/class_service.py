from database import (
    get_classes_for_person,
    add_class,
    remove_class
)


def _get_student_id(student):
    """
    Accept either:
        student dictionary
    or:
        student ID
    """
    if isinstance(student, dict):
        return student["id"]

    return student


def get_classes(state, student):
    """
    Get a student's classes.

    Uses the cache after the first database load.
    """

    student_id = _get_student_id(student)

    if student_id not in state.class_cache:
        state.class_cache[student_id] = set(
            get_classes_for_person(student_id)
        )

    return state.class_cache[student_id]


def load_classes(student, state):
    """
    Compatibility function for the dashboard.
    """

    return get_classes(state, student)


def refresh_classes(student, state):
    """
    Force reload classes from PostgreSQL.
    """

    student_id = _get_student_id(student)

    state.class_cache[student_id] = set(
        get_classes_for_person(student_id)
    )

    return state.class_cache[student_id]


def add_student_class(student, class_date, state):
    """
    Add a class for a student.
    """

    student_id = _get_student_id(student)

    add_class(
        student_id,
        class_date
    )

    refresh_classes(
        student,
        state
    )


def remove_student_class(student, class_date, state):
    """
    Remove a class for a student.
    """

    student_id = _get_student_id(student)

    remove_class(
        student_id,
        class_date
    )

    refresh_classes(
        student,
        state
    )


def toggle_class(state, student, class_date):
    """
    Add or remove a class.

    Returns:
        True  -> class was added
        False -> class was removed
    """

    student_id = _get_student_id(student)

    dates = get_classes(
        state,
        student_id
    )

    if class_date in dates:

        remove_class(
            student_id,
            class_date
        )

        dates.remove(class_date)

        return False

    add_class(
        student_id,
        class_date
    )

    dates.add(class_date)

    return True


def has_class(student, class_date, state):
    """
    Check whether a class exists on a particular date.
    """

    dates = get_classes(
        state,
        student
    )

    return class_date in dates


def get_class_number(state, student, class_date):
    """
    Return the class number for a date.

    Example:
        First class  -> 1
        Second class -> 2
        Third class  -> 3
    """

    dates = sorted(
        get_classes(
            state,
            student
        )
    )

    try:
        return dates.index(class_date) + 1

    except ValueError:
        return None


def get_class_type(state, student, class_date):
    """
    Returns:
        first
        normal
        target
        None
    """

    number = get_class_number(
        state,
        student,
        class_date
    )

    if number is None:
        return None

    if isinstance(student, dict):
        target = student["target"]
    else:
        target = None

        for data in state.students:
            if data["id"] == student:
                target = data["target"]
                break

        if target is None:
            return None

    if number == 1:
        return "first"

    if target > 0 and number == target:
        return "target"

    return "normal"


def get_progress(total_classes, target):
    """
    Calculate progress toward the target.
    """

    if target <= 0:
        return 0, 0

    current = total_classes % target

    if total_classes > 0 and current == 0:
        current = target

    percentage = min(
        (current / target) * 100,
        100
    )

    return current, percentage


def get_month_classes(
    state,
    student,
    year,
    month
):
    """
    Return classes for a particular month.
    """

    dates = get_classes(
        state,
        student
    )

    result = []

    for class_date in dates:

        try:
            parsed = date.fromisoformat(
                str(class_date)
            )

            if (
                parsed.year == year
                and parsed.month == month
            ):
                result.append(parsed)

        except (
            ValueError,
            TypeError
        ):
            continue

    return result