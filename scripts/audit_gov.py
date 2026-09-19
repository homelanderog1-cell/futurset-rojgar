import sqlite3

conn = sqlite3.connect("app/data/futurset_jobs.db")
cursor = conn.cursor()

def check_kw(kw):
    cursor.execute("""
        SELECT COUNT(*), GROUP_CONCAT(title, ' --- ') 
        FROM jobs 
        WHERE (title LIKE ? OR organization LIKE ?) 
          AND gov_level != 'Private' 
          AND board_category != 'Corporate'
    """, (f"%{kw}%", f"%{kw}%"))
    return cursor.fetchone()

targets = [
    # Gujarat targets
    "Talati", "Forest Guard", "Vanpal", "Vanrakshak", "Vidhyasahayak", "TET", "TAT",
    "High Court", "GSRTC", "AMC", "SMC", "VMC", "RMC", "GMC", "GMDC", "GIDC", "GWSSB",
    "GMB", "GPCB", "GLPC", "GETCO", "DGVCL", "MGVCL", "PGVCL", "UGVCL", "GSECL",
    "Police", "PSI", "LRD", "Constable", "Mamlatdar", "CDPO", "Chief Officer",
    # Central targets
    "SSC CGL", "SSC CHSL", "SSC GD", "SSC MTS", "SSC CPO", "SSC JE", "SSC Steno",
    "RRB ALP", "RRB NTPC", "RRB JE", "RRB Group D", "RPF",
    "SBI PO", "SBI Clerk", "IBPS PO", "IBPS Clerk", "IBPS SO", "IBPS RRB", "RBI Grade B",
    "NABARD", "SEBI", "SIDBI", "LIC",
    "India Post", "GDS", "Postal Assistant",
    "Indian Army", "Indian Navy", "Air Force", "Coast Guard", "CISF", "BSF", "CRPF", "ITBP", "SSB", "IB ACIO",
    "AAI", "ATC", "Airport",
    "ISRO", "DRDO", "BARC", "IPR", "PRL", "CSMCRI", "C-DAC", "NIC",
    "Kandla", "Deendayal Port"
]

missing = []
found = []
for t in targets:
    cnt, titles = check_kw(t)
    if cnt == 0:
        missing.append(t)
        print(f"[MISSING] {t}")
    else:
        found.append((t, cnt))
        print(f"[FOUND {cnt:2d}] {t}")

print(f"\nSummary: {len(found)} targets found, {len(missing)} missing.")
