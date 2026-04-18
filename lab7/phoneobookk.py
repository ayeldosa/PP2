import csv
from connect import get_connection



def insert_from_console():
    username = input("Enter name: ")
    phone = input("Enter phone: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO phonebook (username, phone) VALUES (%s, %s)",
        (username, phone)
    )

    conn.commit()
    cur.close()
    conn.close()



def insert_from_csv(filename):
    conn = get_connection()
    cur = conn.cursor()

    with open(filename, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            cur.execute(
                "INSERT INTO phonebook (username, phone) VALUES (%s, %s)",
                (row[0], row[1])
            )

    conn.commit()
    cur.close()
    conn.close()



def query_data():
    keyword = input("Search name or phone: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM phonebook
        WHERE username ILIKE %s OR phone LIKE %s
    """, (f"%{keyword}%", f"%{keyword}%"))

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()



def update_contact():
    username = input("Enter username to update: ")
    new_name = input("New name (or press Enter): ")
    new_phone = input("New phone (or press Enter): ")

    conn = get_connection()
    cur = conn.cursor()

    if new_name:
        cur.execute(
            "UPDATE phonebook SET username=%s WHERE username=%s",
            (new_name, username)
        )

    if new_phone:
        cur.execute(
            "UPDATE phonebook SET phone=%s WHERE username=%s",
            (new_phone, username)
        )

    conn.commit()
    cur.close()
    conn.close()



def delete_contact():
    choice = input("Delete by (1) name or (2) phone: ")

    conn = get_connection()
    cur = conn.cursor()

    if choice == "1":
        username = input("Enter name: ")
        cur.execute("DELETE FROM phonebook WHERE username=%s", (username,))
    else:
        phone = input("Enter phone: ")
        cur.execute("DELETE FROM phonebook WHERE phone=%s", (phone,))

    conn.commit()
    cur.close()
    conn.close()



def menu():
    while True:
        print("\n1. Insert from console")
        print("2. Insert from CSV")
        print("3. Query")
        print("4. Update")
        print("5. Delete")
        print("6. Exit")

        choice = input("Choose: ")

        if choice == "1":
            insert_from_console()
        elif choice == "2":
            insert_from_csv("contacts.csv")
        elif choice == "3":
            query_data()
        elif choice == "4":
            update_contact()
        elif choice == "5":
            delete_contact()
        elif choice == "6":
            break


if __name__ == "__main__":
    menu()