import sqlite3

conn = sqlite3.connect("app/data/futurset_jobs.db")
cursor = conn.cursor()

# Get all titles and organizations
cursor.execute("""
    SELECT id, title, organization, gov_level, board_category, vacancies 
    FROM jobs 
    WHERE gov_level != 'Private' AND board_category != 'Corporate'
""")
rows = cursor.fetchall()

print(f"Total non-private rows in DB: {len(rows)}")

# Let's inspect Gujarat jobs
guj_jobs = [r for r in rows if r[3] == 'State' or 'Gujarat' in r[2] or 'Gujarat' in r[1]]
print(f"Total Gujarat State Gov jobs: {len(guj_jobs)}")

# Let's inspect Central jobs
cen_jobs = [r for r in rows if r[3] == 'Central' and 'Gujarat' not in r[2] and 'Corporate' not in r[4]]
print(f"Total Central Gov jobs: {len(cen_jobs)}")

# Check key Gujarat bodies:
guj_checks = {
    "GPSC": 0, "GSSSB": 0, "GPSSB": 0, "Police/LRD/PSI": 0, "High Court": 0,
    "GSRTC": 0, "Forest Guard": 0, "Vidhyasahayak": 0, "GETCO": 0, "DGVCL": 0,
    "MGVCL": 0, "PGVCL": 0, "UGVCL": 0, "GSECL": 0, "AMC": 0, "SMC": 0,
    "VMC": 0, "RMC": 0, "GMC": 0, "GMDC": 0, "GIDC": 0, "GWSSB": 0,
    "GMB": 0, "GPCB": 0, "GLPC": 0
}

for r in rows:
    text = f"{r[1]} {r[2]} {r[4]}".lower()
    for k in guj_checks.keys():
        sub = k.lower().split("/")[0]
        if sub in text:
            guj_checks[k] += 1

print("\n--- GUJARAT BODIES STATUS ---")
for k, v in guj_checks.items():
    print(f"  {k:20}: {'PRESENT (' + str(v) + ')' if v > 0 else 'MISSING'}")

# Check key Central bodies:
cen_checks = {
    "SSC CGL": 0, "SSC CHSL": 0, "SSC GD": 0, "SSC MTS": 0, "SSC CPO": 0, "SSC JE": 0, "SSC Steno": 0,
    "RRB ALP": 0, "RRB NTPC": 0, "RRB JE": 0, "RRB Group D": 0, "RPF": 0,
    "UPSC CSE": 0, "UPSC CDS": 0, "UPSC NDA": 0, "UPSC ESE": 0, "UPSC CAPF": 0,
    "SBI PO": 0, "SBI Clerk": 0, "IBPS PO": 0, "IBPS Clerk": 0, "IBPS SO": 0, "IBPS RRB": 0, "RBI Grade B": 0,
    "India Post GDS": 0, "Postal Assistant": 0,
    "Indian Army": 0, "Indian Navy": 0, "Air Force": 0, "Coast Guard": 0,
    "CISF": 0, "BSF": 0, "CRPF": 0, "ITBP": 0, "SSB": 0, "IB ACIO": 0,
    "AAI ATC": 0, "ISRO": 0, "DRDO": 0, "BARC": 0, "IPR": 0, "PRL": 0, "CSMCRI": 0, "Kandla Port": 0
}

for r in rows:
    text = f"{r[1]} {r[2]} {r[4]}".lower()
    for k in cen_checks.keys():
        parts = [p.strip() for p in k.lower().split()]
        if all(p in text for p in parts):
            cen_checks[k] += 1

print("\n--- CENTRAL BODIES STATUS ---")
for k, v in cen_checks.items():
    print(f"  {k:20}: {'PRESENT (' + str(v) + ')' if v > 0 else 'MISSING'}")
