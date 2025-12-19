import sqlite3

conn = sqlite3.connect('gateway.db')
cursor = conn.cursor()

# Deletar todas as invoices pendentes antigas
cursor.execute("DELETE FROM invoices WHERE status = 'pending'")

conn.commit()
conn.close()

print("✅ Ordens antigas deletadas!")
