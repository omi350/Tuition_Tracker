
import psycopg
from datetime import date


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_CONFIG = {
    "host": "localhost",
    "dbname": "Tuition_Tracker",
    "user": "postgres",
    "password": "123456",
    "port": 1234
}


# ============================================================
# CONNECTION
# ============================================================

def get_connection():
    return psycopg.connect(**DB_CONFIG)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    with get_connection() as connection:

        with connection.cursor() as cursor:

            # ------------------------------------------------
            # PEOPLE / STUDENTS
            # ------------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS people (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    weekly_days INTEGER NOT NULL,
                    target INTEGER NOT NULL,
                    salary NUMERIC(12, 2) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # This is important for an existing database.
            # If the people table already existed without salary,
            # PostgreSQL will add the column here.

            cursor.execute("""
                ALTER TABLE people
                ADD COLUMN IF NOT EXISTS salary
                NUMERIC(12, 2) DEFAULT 0
            """)

            # ------------------------------------------------
            # CLASSES
            # ------------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS classes (
                    id SERIAL PRIMARY KEY,

                    person_id INTEGER NOT NULL
                        REFERENCES people(id)
                        ON DELETE CASCADE,

                    class_date DATE NOT NULL,

                    created_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP,

                    UNIQUE(person_id, class_date)
                )
            """)

            # ------------------------------------------------
            # PAYMENTS
            # ------------------------------------------------

            # Kept for compatibility with old data.
            # The new application does not need to use this
            # table for salary.

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id SERIAL PRIMARY KEY,

                    person_id INTEGER NOT NULL
                        REFERENCES people(id)
                        ON DELETE CASCADE,

                    amount NUMERIC(12, 2) NOT NULL
                        CHECK(amount >= 0),

                    payment_date DATE NOT NULL,

                    status VARCHAR(20) NOT NULL
                        CHECK(status IN ('paid', 'pending')),

                    payment_method VARCHAR(50),

                    notes TEXT,

                    created_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # ------------------------------------------------
            # INDEXES
            # ------------------------------------------------

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_classes_date
                ON classes(class_date)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_payments_date
                ON payments(payment_date)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_payments_status
                ON payments(status)
            """)

        connection.commit()


# ============================================================
# STUDENT FUNCTIONS
# ============================================================

def get_all_people():

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    id,
                    name,
                    weekly_days,
                    target,
                    salary
                FROM people
                ORDER BY name
            """)

            rows = cursor.fetchall()

    students = []

    for row in rows:

        students.append({
            "id": row[0],
            "name": row[1],
            "weekly_days": row[2],
            "target": row[3],
            "salary": float(row[4] or 0)
        })

    return students


def add_person_to_database(
    name,
    weekly_days,
    target,
    salary
):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                INSERT INTO people
                (
                    name,
                    weekly_days,
                    target,
                    salary
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING id
            """, (
                name,
                weekly_days,
                target,
                salary
            ))

            person_id = cursor.fetchone()[0]

        connection.commit()

    return person_id


def delete_person_from_database(person_id):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                DELETE FROM people
                WHERE id = %s
            """, (
                person_id,
            ))

        connection.commit()


# ============================================================
# CLASS FUNCTIONS
# ============================================================

def get_classes_for_person(person_id):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT class_date
                FROM classes
                WHERE person_id = %s
                ORDER BY class_date
            """, (
                person_id,
            ))

            rows = cursor.fetchall()

    return [
        row[0].isoformat()
        for row in rows
    ]


def add_class(person_id, class_date):

    if isinstance(class_date, str):

        class_date = date.fromisoformat(
            class_date
        )

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                INSERT INTO classes
                (
                    person_id,
                    class_date
                )
                VALUES
                (
                    %s,
                    %s
                )
                ON CONFLICT
                (
                    person_id,
                    class_date
                )
                DO NOTHING
            """, (
                person_id,
                class_date
            ))

        connection.commit()


def remove_class(person_id, class_date):

    if isinstance(class_date, str):

        class_date = date.fromisoformat(
            class_date
        )

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                DELETE FROM classes
                WHERE person_id = %s
                AND class_date = %s
            """, (
                person_id,
                class_date
            ))

        connection.commit()


# ============================================================
# OLD PAYMENT FUNCTIONS
# ============================================================

def add_payment(
    person_id,
    amount,
    payment_date,
    status,
    payment_method,
    notes
):

    if isinstance(payment_date, str):

        payment_date = date.fromisoformat(
            payment_date
        )

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                INSERT INTO payments
                (
                    person_id,
                    amount,
                    payment_date,
                    status,
                    payment_method,
                    notes
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (
                person_id,
                amount,
                payment_date,
                status,
                payment_method,
                notes
            ))

        connection.commit()


def get_payments_for_person(person_id):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    id,
                    amount,
                    payment_date,
                    status,
                    payment_method,
                    notes
                FROM payments
                WHERE person_id = %s
                ORDER BY
                    payment_date DESC,
                    id DESC
            """, (
                person_id,
            ))

            rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "amount": row[1],
            "payment_date": row[2].isoformat(),
            "status": row[3],
            "payment_method": row[4],
            "notes": row[5]
        }
        for row in rows
    ]


def delete_payment(payment_id):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                DELETE FROM payments
                WHERE id = %s
            """, (
                payment_id,
            ))

        connection.commit()


def get_payment_statistics():

    today = date.today()

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    COALESCE(
                        SUM(
                            CASE
                                WHEN status = 'paid'
                                AND EXTRACT(
                                    MONTH FROM payment_date
                                ) = %s
                                AND EXTRACT(
                                    YEAR FROM payment_date
                                ) = %s
                                THEN amount
                                ELSE 0
                            END
                        ),
                        0
                    ),

                    COUNT(
                        CASE
                            WHEN status = 'paid'
                            AND EXTRACT(
                                MONTH FROM payment_date
                            ) = %s
                            AND EXTRACT(
                                YEAR FROM payment_date
                            ) = %s
                            THEN 1
                        END
                    ),

                    COUNT(
                        CASE
                            WHEN status = 'pending'
                            THEN 1
                        END
                    )

                FROM payments
            """, (
                today.month,
                today.year,
                today.month,
                today.year
            ))

            payment_row = cursor.fetchone()

            cursor.execute("""
                SELECT COUNT(*)
                FROM classes
                WHERE EXTRACT(
                    MONTH FROM class_date
                ) = %s
                AND EXTRACT(
                    YEAR FROM class_date
                ) = %s
            """, (
                today.month,
                today.year
            ))

            class_count = cursor.fetchone()[0]

    return {
        "earnings": float(
            payment_row[0] or 0
        ),
        "received": payment_row[1] or 0,
        "pending": payment_row[2] or 0,
        "classes": class_count or 0
    }
