#!/usr/bin/env python3
"""
phonebook.py – PhoneBook Extended Console App  (TSIS 1)
Requires: psycopg2-binary
"""

import csv
import json
import os
import sys
from datetime import date, datetime

import psycopg2
from psycopg2.extras import RealDictCursor

from connect import get_connection, init_db

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _fmt_row(row: dict) -> str:
    """Pretty-print a contact row returned by DB functions."""
    bday = row.get("birthday") or ""
    grp  = row.get("group_name") or "—"
    ph   = row.get("phones") or "—"
    name = f"{row['first_name']} {row.get('last_name') or ''}".strip()
    return (
        f"  [{row['id']}] {name:<25} | {row.get('email') or '—':<30} | "
        f"bday:{bday!s:<12} | group:{grp:<10} | phones: {ph}"
    )


def _ask(prompt: str, default: str = "") -> str:
    val = input(f"{prompt} [{default}]: ").strip()
    return val if val else default


def _parse_date(s: str):
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    print(f"  ! Cannot parse date '{s}', skipping.")
    return None


# ─────────────────────────────────────────────────────────────
# CRUD helpers
# ─────────────────────────────────────────────────────────────

def _get_or_create_group(cur, name: str):
    if not name:
        return None
    cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (name,))
    row = cur.fetchone()
    if row:
        return row["id"]
    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (name,))
    return cur.fetchone()["id"]


def add_contact(conn):
    print("\n── Add Contact ──")
    first = input("First name: ").strip()
    if not first:
        print("First name required."); return
    last  = input("Last name : ").strip() or None
    email = input("Email     : ").strip() or None
    bday  = _parse_date(input("Birthday (YYYY-MM-DD): ").strip())
    grp   = input("Group (Family/Work/Friend/Other): ").strip() or None
    phone = input("Phone     : ").strip() or None
    ptype = input("Phone type (home/work/mobile) [mobile]: ").strip() or "mobile"

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        gid = _get_or_create_group(cur, grp)
        cur.execute(
            "INSERT INTO contacts (first_name, last_name, email, birthday, group_id) "
            "VALUES (%s,%s,%s,%s,%s) RETURNING id",
            (first, last, email, bday, gid)
        )
        cid = cur.fetchone()["id"]
        if phone:
            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                (cid, phone, ptype)
            )
    conn.commit()
    print(f"  ✓ Contact '{first}' added (id={cid}).")


def list_contacts(conn):
    print("\n── All Contacts ──")
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday,
                   g.name AS group_name,
                   STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            LEFT JOIN phones p ON p.contact_id = c.id
            GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
            ORDER BY c.first_name
        """)
        rows = cur.fetchall()
    if not rows:
        print("  (no contacts)")
        return
    for r in rows:
        print(_fmt_row(r))


def update_contact(conn):
    print("\n── Update Contact ──")
    cid = input("Enter contact ID to update: ").strip()
    if not cid.isdigit():
        print("Invalid ID."); return

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM contacts WHERE id=%s", (int(cid),))
        c = cur.fetchone()
        if not c:
            print("Contact not found."); return

        first = _ask("First name", c["first_name"])
        last  = _ask("Last name",  c["last_name"] or "")
        email = _ask("Email",      c["email"] or "")
        bday  = _parse_date(_ask("Birthday", str(c["birthday"]) if c["birthday"] else ""))
        grp   = _ask("Group", "")

        gid = _get_or_create_group(cur, grp) if grp else c["group_id"]
        cur.execute(
            "UPDATE contacts SET first_name=%s, last_name=%s, email=%s, birthday=%s, group_id=%s "
            "WHERE id=%s",
            (first, last or None, email or None, bday, gid, int(cid))
        )
    conn.commit()
    print("  ✓ Contact updated.")


def delete_contact(conn):
    print("\n── Delete Contact ──")
    cid = input("Enter contact ID to delete: ").strip()
    if not cid.isdigit():
        print("Invalid ID."); return
    confirm = input(f"Delete contact {cid}? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled."); return
    with conn.cursor() as cur:
        cur.execute("DELETE FROM contacts WHERE id=%s", (int(cid),))
    conn.commit()
    print("  ✓ Deleted.")


# ─────────────────────────────────────────────────────────────
# Phone management
# ─────────────────────────────────────────────────────────────

def add_phone_menu(conn):
    print("\n── Add Phone to Contact ──")
    name  = input("Contact name: ").strip()
    phone = input("Phone number: ").strip()
    ptype = input("Type (home/work/mobile) [mobile]: ").strip() or "mobile"
    with conn.cursor() as cur:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
    conn.commit()
    print("  ✓ Phone added.")


# ─────────────────────────────────────────────────────────────
# Group management
# ─────────────────────────────────────────────────────────────

def move_to_group_menu(conn):
    print("\n── Move Contact to Group ──")
    name  = input("Contact name: ").strip()
    group = input("Group name  : ").strip()
    with conn.cursor() as cur:
        cur.execute("CALL move_to_group(%s, %s)", (name, group))
    conn.commit()
    print("  ✓ Done.")


# ─────────────────────────────────────────────────────────────
# Search & Filter
# ─────────────────────────────────────────────────────────────

def search_menu(conn):
    print("\n── Search Contacts ──")
    query = input("Search (name / email / phone): ").strip()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM search_contacts(%s)", (query,))
        rows = cur.fetchall()
    if not rows:
        print("  (no results)")
        return
    for r in rows:
        print(_fmt_row(r))


def filter_by_group(conn):
    print("\n── Filter by Group ──")
    # Show available groups
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, name FROM groups ORDER BY name")
        groups = cur.fetchall()
    print("Available groups:")
    for g in groups:
        print(f"  {g['id']}. {g['name']}")
    grp = input("Enter group name: ").strip()

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday,
                   g.name AS group_name,
                   STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones
            FROM contacts c
            JOIN groups g ON g.id = c.group_id
            LEFT JOIN phones p ON p.contact_id = c.id
            WHERE g.name ILIKE %s
            GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
            ORDER BY c.first_name
        """, (grp,))
        rows = cur.fetchall()
    if not rows:
        print("  (no contacts in this group)")
        return
    for r in rows:
        print(_fmt_row(r))


def search_by_email(conn):
    print("\n── Search by Email ──")
    partial = input("Email fragment (e.g. gmail): ").strip()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday,
                   g.name AS group_name,
                   STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            LEFT JOIN phones p ON p.contact_id = c.id
            WHERE c.email ILIKE %s
            GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
            ORDER BY c.first_name
        """, (f"%{partial}%",))
        rows = cur.fetchall()
    if not rows:
        print("  (no results)")
        return
    for r in rows:
        print(_fmt_row(r))


# ─────────────────────────────────────────────────────────────
# Sorted list
# ─────────────────────────────────────────────────────────────

def sort_contacts(conn):
    print("\n── Sort Contacts ──")
    print("Sort by: 1) Name  2) Birthday  3) Date added")
    choice = input("Choice [1]: ").strip() or "1"
    order_map = {"1": "first_name", "2": "birthday", "3": "created_at"}
    order = order_map.get(choice, "first_name")
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday,
                   g.name AS group_name,
                   STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones,
                   c.created_at
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            LEFT JOIN phones p ON p.contact_id = c.id
            GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name, c.created_at
            ORDER BY {}
        """.format(order))
        rows = cur.fetchall()
    for r in rows:
        print(_fmt_row(r))


# ─────────────────────────────────────────────────────────────
# Paginated navigation
# ─────────────────────────────────────────────────────────────

def paginated_view(conn):
    print("\n── Paginated View ──")
    print("Sort by: 1) Name  2) Birthday  3) Date added")
    choice = input("Choice [1]: ").strip() or "1"
    order_map = {"1": "first_name", "2": "birthday", "3": "created_at"}
    order = order_map.get(choice, "first_name")

    page_size = 5
    offset    = 0

    while True:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM get_contacts_page(%s, %s, %s)",
                (page_size, offset, order)
            )
            rows = cur.fetchall()

        if not rows:
            print("  (no more contacts)")
            break

        print(f"\n  — Page (rows {offset+1}-{offset+len(rows)}) —")
        for r in rows:
            print(_fmt_row(r))

        nav = input("\n  [n]ext  [p]rev  [q]uit: ").strip().lower()
        if nav == "n":
            offset += page_size
        elif nav == "p":
            offset = max(0, offset - page_size)
        elif nav == "q":
            break


# ─────────────────────────────────────────────────────────────
# Import / Export
# ─────────────────────────────────────────────────────────────

def _contact_to_dict(row: dict) -> dict:
    """Convert a RealDictRow to a JSON-serialisable dict."""
    return {
        "first_name": row["first_name"],
        "last_name":  row.get("last_name"),
        "email":      row.get("email"),
        "birthday":   str(row["birthday"]) if row.get("birthday") else None,
        "group":      row.get("group_name"),
        "phones":     row.get("phones"),   # string from DB; split on import
    }


def export_to_json(conn):
    print("\n── Export to JSON ──")
    path = input("Output file [contacts.json]: ").strip() or "contacts.json"
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday,
                   g.name AS group_name,
                   STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            LEFT JOIN phones p ON p.contact_id = c.id
            GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
            ORDER BY c.first_name
        """)
        rows = cur.fetchall()

    # For export, get phones as structured list
    data = []
    for row in rows:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT phone, type FROM phones WHERE contact_id=%s", (row["id"],)
            )
            ph_rows = cur.fetchall()
        data.append({
            "first_name": row["first_name"],
            "last_name":  row["last_name"],
            "email":      row["email"],
            "birthday":   str(row["birthday"]) if row["birthday"] else None,
            "group":      row["group_name"],
            "phones":     [{"phone": r["phone"], "type": r["type"]} for r in ph_rows],
        })

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ {len(data)} contact(s) exported to '{path}'.")


def import_from_json(conn):
    print("\n── Import from JSON ──")
    path = input("JSON file [contacts.json]: ").strip() or "contacts.json"
    if not os.path.exists(path):
        print(f"  ! File '{path}' not found."); return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    added = skipped = overwritten = 0
    for entry in data:
        first = entry.get("first_name", "").strip()
        last  = entry.get("last_name", "")
        if not first:
            print("  ! Entry missing first_name, skipping."); skipped += 1; continue

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id FROM contacts WHERE first_name ILIKE %s AND "
                "(last_name ILIKE %s OR (last_name IS NULL AND %s IS NULL))",
                (first, last, last)
            )
            existing = cur.fetchone()

        if existing:
            action = input(
                f"  Contact '{first} {last}' already exists. [s]kip / [o]verwrite: "
            ).strip().lower()
            if action != "o":
                skipped += 1; continue
            # Delete old and re-insert
            with conn.cursor() as cur:
                cur.execute("DELETE FROM contacts WHERE id=%s", (existing["id"],))
            conn.commit()
            overwritten += 1
        else:
            added += 1

        # Insert
        bday = _parse_date(entry.get("birthday") or "")
        email = entry.get("email") or None
        grp   = entry.get("group") or None

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            gid = _get_or_create_group(cur, grp)
            cur.execute(
                "INSERT INTO contacts (first_name, last_name, email, birthday, group_id) "
                "VALUES (%s,%s,%s,%s,%s) RETURNING id",
                (first, last or None, email, bday, gid)
            )
            cid = cur.fetchone()["id"]
            for ph in entry.get("phones", []):
                cur.execute(
                    "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                    (cid, ph.get("phone"), ph.get("type", "mobile"))
                )
        conn.commit()

    print(f"  ✓ Import done: {added} added, {overwritten} overwritten, {skipped} skipped.")


def import_from_csv(conn):
    """Extended CSV import supporting email, birthday, group, phone type."""
    print("\n── Import from CSV ──")
    path = input("CSV file [contacts.csv]: ").strip() or "contacts.csv"
    if not os.path.exists(path):
        print(f"  ! File '{path}' not found."); return

    added = skipped = 0
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            first = row.get("first_name", "").strip()
            if not first:
                skipped += 1; continue
            last  = row.get("last_name", "").strip() or None
            email = row.get("email", "").strip()      or None
            bday  = _parse_date(row.get("birthday", ""))
            grp   = row.get("group", "").strip()      or None
            phone = row.get("phone", "").strip()      or None
            ptype = row.get("phone_type", "mobile").strip() or "mobile"

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                gid = _get_or_create_group(cur, grp)
                cur.execute(
                    "INSERT INTO contacts (first_name, last_name, email, birthday, group_id) "
                    "VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING id",
                    (first, last, email, bday, gid)
                )
                result = cur.fetchone()
                if result:
                    cid = result["id"]
                    if phone:
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                            (cid, phone, ptype)
                        )
                    added += 1
                else:
                    skipped += 1
            conn.commit()

    print(f"  ✓ CSV import done: {added} added, {skipped} skipped.")


# ─────────────────────────────────────────────────────────────
# Main menu
# ─────────────────────────────────────────────────────────────

MENU = """
══════════════════════════════
       PhoneBook  TSIS-1
══════════════════════════════
 1. List all contacts
 2. Add contact
 3. Update contact
 4. Delete contact
 ─────────────────────────────
 5. Add phone to contact
 6. Move contact to group
 ─────────────────────────────
 7. Search (name/email/phone)
 8. Filter by group
 9. Search by email
10. Sort contacts
11. Paginated view
 ─────────────────────────────
12. Export to JSON
13. Import from JSON
14. Import from CSV
 ─────────────────────────────
 0. Exit
══════════════════════════════
"""

ACTIONS = {
    "1":  list_contacts,
    "2":  add_contact,
    "3":  update_contact,
    "4":  delete_contact,
    "5":  add_phone_menu,
    "6":  move_to_group_menu,
    "7":  search_menu,
    "8":  filter_by_group,
    "9":  search_by_email,
    "10": sort_contacts,
    "11": paginated_view,
    "12": export_to_json,
    "13": import_from_json,
    "14": import_from_csv,
}


def main():
    # First run: initialise DB
    try:
        init_db()
    except Exception as e:
        print(f"DB init warning: {e}")

    conn = get_connection()
    try:
        while True:
            print(MENU)
            choice = input("Select option: ").strip()
            if choice == "0":
                print("Bye!"); break
            action = ACTIONS.get(choice)
            if action:
                try:
                    action(conn)
                except Exception as e:
                    conn.rollback()
                    print(f"  ✗ Error: {e}")
            else:
                print("  Invalid choice.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
