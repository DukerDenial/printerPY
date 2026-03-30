import sqlite3
from datetime import datetime

def handler(request):
    path = request.path

    conn = sqlite3.connect("../cartridges.db")
    cur = conn.cursor()

    # ---------------- ПРИНТЕРЫ ----------------
    if path.endswith("/printers"):
        cur.execute("SELECT DISTINCT printer FROM cartridges")
        return [p[0] for p in cur.fetchall()]

    # ---------------- КАРТРИДЖИ ----------------
    if "/cartridges/" in path:
        printer = path.split("/")[-1]

        cur.execute("""
        SELECT id, cartridge, quantity, min_quantity
        FROM cartridges
        WHERE printer=? AND cartridge!='-'
        """, (printer,))

        rows = cur.fetchall()

        return [
            {"id": r[0], "name": r[1], "qty": r[2], "min": r[3]}
            for r in rows
        ]

    # ---------------- UPDATE ----------------
    if path.endswith("/update"):
        data = request.json()
        cid = data["id"]
        action = data["action"]

        if action == "plus":
            cur.execute("UPDATE cartridges SET quantity = quantity + 1 WHERE id=?", (cid,))
        elif action == "minus":
            cur.execute("UPDATE cartridges SET quantity = MAX(quantity - 1, 0) WHERE id=?", (cid,))

        cur.execute("SELECT cartridge FROM cartridges WHERE id=?", (cid,))
        cart = cur.fetchone()[0]

        cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cartridge TEXT,
            action TEXT,
            date TEXT
        )
        """)

        cur.execute(
            "INSERT INTO history (cartridge, action, date) VALUES (?, ?, ?)",
            (cart, action, datetime.now().strftime("%Y-%m-%d %H:%M"))
        )

        conn.commit()
        return {"ok": True}

    # ---------------- HISTORY ----------------
    if path.endswith("/history"):
        cur.execute("SELECT cartridge, action, date FROM history ORDER BY id DESC LIMIT 50")
        return cur.fetchall()

    # ---------------- STATS ----------------
    if path.endswith("/stats"):
        cur.execute("""
        SELECT cartridge, COUNT(*)
        FROM history
        WHERE action='minus'
        GROUP BY cartridge
        """)
        return cur.fetchall()

    return {"error": "not found"}
