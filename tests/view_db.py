import sqlite3
import os

db_path = os.path.join("data", "security_audit.db")

if not os.path.exists(db_path):
    print(f"[-] Database file not found at: {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n=== CURRENT LOGIN AUDIT LOGS ===")
    print(f"{'ID':<5} | {'TIMESTAMP':<20} | {'USERNAME':<15} | {'STATUS':<10}")
    print("-" * 60)
    
    cursor.execute("SELECT id, timestamp, username, status FROM login_audit ORDER BY id ASC")
    for row in cursor.fetchall():
        print(f"{row[0]:<5} | {row[1]:<20} | {row[2]:<15} | {row[3]:<10}")
        
    conn.close()