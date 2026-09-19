from app.database import get_db_connection, sync_all_catalog_jobs, init_db

conn = get_db_connection()
c = conn.cursor()

# Check and add district and qualification_level columns if not present
c.execute("PRAGMA table_info(jobs)")
existing_cols = [col[1] for col in c.fetchall()]

if "district" not in existing_cols:
    c.execute("ALTER TABLE jobs ADD COLUMN district TEXT DEFAULT 'All Gujarat'")
    print("Added column district")

if "qualification_level" not in existing_cols:
    c.execute("ALTER TABLE jobs ADD COLUMN qualification_level TEXT DEFAULT 'Graduate'")
    print("Added column qualification_level")

# Fix IAF job title
c.execute("UPDATE jobs SET title='Indian Air Force Agniveer Vayu (Musician & Non-Combatant Intake 01/2026) (3,500 Posts)' WHERE id=118 OR title LIKE '%Medical Assistant%'")
conn.commit()
conn.close()

# Re-sync seeds
count = sync_all_catalog_jobs()
print(f"Catalog synced: {count} recruitments")
