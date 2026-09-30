import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import get_connection


RANDOM_SEED = 42


CAPACITY_RANGES = {
    "BBMP Health Centre": (5, 15),
    "BBMP Urban Family Welfare Centre": (5, 15),
    "BBMP Maternity Home": (10, 30),
    "BBMP Referral Hospital": (30, 100),
    "BBMP Referral/UCHC Facility": (30, 100),
}


def get_capacity_range(hospital_type):
    return CAPACITY_RANGES.get(
        hospital_type,
        (5, 15)
    )


def seed_simulated_beds():
    random.seed(RANDOM_SEED)

    connection = get_connection()

    hospitals = connection.execute("""
        SELECT id, name, hospital_type
        FROM hospitals
        ORDER BY id
    """).fetchall()

    for hospital_id, name, hospital_type in hospitals:
        minimum, maximum = get_capacity_range(hospital_type)

        total_beds = random.randint(minimum, maximum)

        available_beds = random.randint(
            max(1, int(total_beds * 0.20)),
            max(1, int(total_beds * 0.60))
        )

        connection.execute("""
            UPDATE hospitals
            SET
                total_beds = ?,
                available_beds = ?,
                bed_data_source = 'simulated'
            WHERE id = ?
        """, (
            total_beds,
            available_beds,
            hospital_id
        ))

    connection.commit()
    connection.close()

    print(f"Seeded simulated bed data for {len(hospitals)} hospitals.")


if __name__ == "__main__":
    seed_simulated_beds()