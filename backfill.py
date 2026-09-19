import sqlite3

def backfill():
    conn = sqlite3.connect('app/data/futurset_jobs.db')
    c = conn.cursor()
    c.execute("""
    UPDATE jobs SET selection_mode = 'direct_merit'
    WHERE title LIKE '%GDS%' OR title LIKE '%Merit%' OR selection_process LIKE '%Direct Selection%' OR selection_process LIKE '%100% Direct Merit%';
    """)
    c.execute("""
    UPDATE jobs SET selection_mode = 'walk_in'
    WHERE title LIKE '%Walk-in%' OR organization LIKE '%AIASL%' OR selection_process LIKE '%Walk-in%';
    """)
    c.execute("""
    UPDATE jobs SET selection_mode = 'apprenticeship'
    WHERE title LIKE '%Apprentice%' OR board_category = 'Apprenticeship';
    """)
    c.execute("""
    UPDATE jobs SET is_btech_cse = 1
    WHERE qualification LIKE '%Computer%' OR qualification LIKE '%B.Tech CSE%' OR qualification LIKE '%Information Technology%' OR qualification LIKE '%Software%' OR title LIKE '%Software%' OR title LIKE '%Programmer%' OR title LIKE '%Scientist%';
    """)
    conn.commit()
    conn.close()
    print("Backfill completed successfully!")

if __name__ == '__main__':
    backfill()
