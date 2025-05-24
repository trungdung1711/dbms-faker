import random
from faker import Faker
import psycopg2
from tqdm import tqdm

fake = Faker()

# DB connection
conn = psycopg2.connect(
    dbname="demo_db",
    user="postgres",
    password="",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# ----- CONFIG -----
TOTAL_ORIGINS = 100
TOTAL_POWERS = 50
TOTAL_CHARACTERS = 100_000
BATCH_SIZE = 1000
GENDERS = ['male', 'female', 'other']
TYPES = ['anime', 'manga', 'movie', 'series']

# ----- 1. Insert Origins -----
print("Inserting origins...")
origin_data = [
    (
        fake.unique.sentence(nb_words=3).replace('.', ''),
        random.choice(TYPES),
        random.randint(1900, 2025)
    ) for _ in range(TOTAL_ORIGINS)
]
cursor.executemany("""
    INSERT INTO origins (title, type, year)
    VALUES (%s, %s, %s)
""", origin_data)
conn.commit()

# Fetch IDs
cursor.execute("SELECT id FROM origins")
origin_ids = [row[0] for row in cursor.fetchall()]

# ----- 2. Insert Powers -----
print("Inserting powers...")
power_names = [fake.unique.word().capitalize() for _ in range(TOTAL_POWERS)]
power_data = [(name, fake.text(max_nb_chars=100)) for name in power_names]
cursor.executemany("""
    INSERT INTO powers (name, description)
    VALUES (%s, %s)
""", power_data)
conn.commit()

# Fetch power IDs
cursor.execute("SELECT id FROM powers")
power_ids = [row[0] for row in cursor.fetchall()]

# ----- 3. Insert Characters -----
print("Inserting characters...")
character_ids = []
for _ in tqdm(range(TOTAL_CHARACTERS // BATCH_SIZE), desc="Characters"):
    batch = [
        (
            fake.name(),
            random.randint(10, 80),
            random.choice(GENDERS),
            fake.text(max_nb_chars=200),
            random.choice(origin_ids)
        ) for _ in range(BATCH_SIZE)
    ]
    cursor.executemany("""
        INSERT INTO characters (name, age, gender, description, origin_id)
        VALUES (%s, %s, %s, %s, %s)
    """, batch)
    conn.commit()
    cursor.execute("SELECT id FROM characters ORDER BY id DESC LIMIT %s", (BATCH_SIZE,))
    character_ids.extend([row[0] for row in cursor.fetchall()])

# ----- 4. Insert Character Powers -----
print("Assigning powers to characters...")
cp_batch = []
for char_id in tqdm(character_ids, desc="Character-Powers"):
    num_powers = random.randint(1, 5)
    assigned = random.sample(power_ids, num_powers)
    for pid in assigned:
        cp_batch.append((char_id, pid))

    if len(cp_batch) >= BATCH_SIZE:
        cursor.executemany("""
            INSERT INTO character_powers (character_id, power_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, cp_batch)
        conn.commit()
        cp_batch = []

# Insert remaining
if cp_batch:
    cursor.executemany("""
        INSERT INTO character_powers (character_id, power_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """, cp_batch)
    conn.commit()

# Done
cursor.close()
conn.close()
print("✅ Data generation complete.")
