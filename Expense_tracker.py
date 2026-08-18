from datetime import datetime
import os


def choose_database():
    print("\n...Select Database ....")
    print("1. SQLite")
    print("2. MySQL")
    print("3. PostgreSQL")
    print("4. MongoDB")

    choice = input("Enter Your Choice (1-4) : ")
   
    if choice == "1":
        return "sqlite"
    elif choice == "2":
        return "mysql"
    elif choice == "3":
        return "postgresql"
    elif choice == "4":
        return "mongodb"
    else:
        print("Invalid Choice ! Defaulting to SQLite")
        return "sqlite"


def connect_database(selected_db): 
    
    if selected_db == "sqlite":
        import sqlite3
        connection = sqlite3.connect("expt database.db")
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
            )
        """)
        connection.commit()
        return connection, cursor

    elif selected_db == "mysql":
        import mysql.connector
        connection = mysql.connector.connect(
            host="localhost", 
            user="root", 
            password="", 
            database="Expenses"
        )
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            date DATE NOT NULL
            )
        """)
        connection.commit()
        return connection, cursor

    elif selected_db == "postgresql":
        import psycopg2
        connection = psycopg2.connect(
            host="127.0.0.1",
            database="Expenses",
            user="postgres",
            port=5432,
            password="password"
        )
        cursor = connection.cursor()
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS Expenses (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            expense_date DATE NOT NULL
            )
        """)
        connection.commit()
        return connection, cursor

    elif selected_db == "mongodb":
        from pymongo import MongoClient
        client = MongoClient("mongodb://axadch22_db_user:lp923K51J5lyuZb5@ac-cmqk9lb-shard-00-00.vcbw5zn.mongodb.net:27017,ac-cmqk9lb-shard-00-01.vcbw5zn.mongodb.net:27017,ac-cmqk9lb-shard-00-02.vcbw5zn.mongodb.net:27017/?ssl=true&replicaSet=atlas-am2yja-shard-0&authSource=admin&appName=Cluster0")
        db = client["Expenses"]
        collection = db["Expenses"]
        return client, collection



selected_db = choose_database()
print(f"You selected : {selected_db}")
connection, cursor = connect_database(selected_db)

expenses = []

while True:
    print("\n-------Expense Tracker-------")
    print("1:---Add Expenses :")
    print("2:---View Expenses :")
    print("3:---Total Expenses:")
    print("4:---Filter expenses:")
    print("5:---Export Summary to Txt")
    print("6:---Switch to Other Database---")
    
    try:
        choice = int(input("Enter Your Choice : "))
        if choice < 1 or choice > 6:
            print("Wrong Choice : Please choose from Given Options !!")
            continue
    except ValueError:
        print("Invalid Choice ! Please Enter a Valid Number.")
        continue

    # 1: Add Expenses
    if choice == 1:
        name = input("Enter Expense Name: ").strip()
        if not name.replace(" ", "").isalpha():
            print("Error: Expense Name must contain characters only.")
            continue
        
        # Amount validation loop
        while True:
            amount_str = input("Enter the Amount: ").strip()
            if amount_str == "":
                print("Error: Amount cannot be empty. Please enter a valid number.")
                continue
            try:
                amount = float(amount_str)
                if amount <= 0:
                    print("Error: Amount should be greater then zero !!")
                    continue
                break
            except ValueError:
                print("Invalid input! Please enter numbers only for the amount.")
        
        # Date validation loop
        while True:
            date_input = input("Enter Date (DD/MM/YY or DD-MM-YY, press enter for Today's Date): ").strip()
            if date_input == "":
                expense_date = datetime.now()
                break
                
            try:
                if "-" in date_input:
                    expense_date = datetime.strptime(date_input, "%d-%m-%Y")
                else:
                    expense_date = datetime.strptime(date_input, "%d/%m/%Y")

                if expense_date > datetime.now():
                    print("Error: The date is wrong and you are entering a future Date")
                    continue
                break
            except ValueError:
                print("Invalid date Format ! ")
                continue
        
        expenses.append([name, amount, expense_date])
        print(f"Expense added Successfully for {expense_date.strftime('%Y-%m-%d')}")

        # Save to the specific active database
        if selected_db == "sqlite":
            cursor.execute(
                "INSERT INTO Expenses (name, amount, date) VALUES (?, ?, ?)",
                (name, amount, expense_date.strftime("%Y-%m-%d"))
            )
            connection.commit()
            print("Expense Added to SQLite !")

        elif selected_db == "mongodb":
            expense_document = {
                "name": name,
                "amount": amount,
                "date": expense_date
            }
            cursor.insert_one(expense_document)
            print("Expense Successfully added to MongoDB!")

        elif selected_db == "mysql":
            cursor.execute(
                "INSERT INTO Expenses (name, amount, date) VALUES (%s, %s, %s)",
                (name, amount, expense_date.strftime("%Y-%m-%d"))
            )
            connection.commit()
            print("Expense Added to MySQL !")

        elif selected_db == "postgresql":
            cursor.execute(
                "INSERT INTO Expenses (name, amount, expense_date) VALUES (%s, %s, %s)",
                (name, amount, expense_date)
            )
            connection.commit()
            print("Expense Added to PostgreSQL Successfully !")

    # 2: View Expenses
    elif choice == 2:
        if selected_db == "sqlite":
            cursor.execute("SELECT * FROM Expenses")
            print("-- Expenses added in SQLite --")
            rows = cursor.fetchall()
            if not rows:
                print("No expenses recorded Yet!")
            else:
                for row in rows:
                    print(row)

        elif selected_db == "mongodb":
            print("\n--- ALL EXPENSES (MongoDB) ---")
            docs = list(cursor.find())
            if not docs:
                print("No expenses recorded Yet!")
            else:
                for doc in docs:
                    print(f"Name: {doc.get('name')}, Amount: {doc.get('amount')}, Date: {doc.get('date')}")

        elif selected_db == "mysql":
            print("\n... All Expenses Saved in MySQL ...")
            cursor.execute("SELECT * FROM Expenses")
            rows = cursor.fetchall()
            if not rows:
                print("No expenses recorded Yet!")
            else:
                for row in rows:
                    print(f"Name : {row[1]} | Amount : {row[2]} | Date : {row[3]}")

        elif selected_db == "postgresql":
            cursor.execute("SELECT * FROM Expenses")
            rows = cursor.fetchall()
            if not rows:
                print("No expenses recorded Yet!")
            else:
                print("-- Expenses Stored in PostgreSQL --")
                for item in rows:
                    print(f"Name: {item[1]} | Amount: {item[2]} | Date: {item[3]}")

    # 3: Total Expenses (From Database)
    elif choice == 3:
        total = 0.0
        if selected_db == "sqlite":
            cursor.execute("SELECT SUM(amount) FROM Expenses")
            result = cursor.fetchone()[0]
            total = result if result else 0.0

        elif selected_db == "mongodb":
            docs = cursor.find()
            total = sum(doc.get("amount", 0.0) for doc in docs)

        elif selected_db == "mysql":
            cursor.execute("SELECT SUM(amount) FROM Expenses")
            result = cursor.fetchone()[0]
            total = float(result) if result else 0.0

        elif selected_db == "postgresql":
            cursor.execute("SELECT SUM(amount) FROM Expenses")
            result = cursor.fetchone()[0]
            total = float(result) if result else 0.0

        print(f"Total Expense from {selected_db.upper()} : Rs {total}")

    # 4: Filter Expenses (From Database)
    elif choice == 4:
        search_query = input("Enter Expense Category/Name to search: ").strip().lower()
        print(f"--- Results for '{search_query}' in {selected_db.upper()} ---")
        
        found = False
        filtered_total = 0.0

        if selected_db == "sqlite":
            cursor.execute("SELECT name, amount, date FROM Expenses WHERE LOWER(name) LIKE ?", (f"%{search_query}%",))
            rows = cursor.fetchall()
            for row in rows:
                print(f"Name: {row[0]} | Amount: {row[1]} | Date: {row[2]}")
                filtered_total += float(row[1])
                found = True

        elif selected_db == "mongodb":
            docs = cursor.find({"name": {"$regex": search_query, "$options": "i"}})
            for doc in docs:
                print(f"Name: {doc.get('name')} | Amount: {doc.get('amount')} | Date: {doc.get('date')}")
                filtered_total += float(doc.get('amount', 0.0))
                found = True

        elif selected_db == "mysql":
            cursor.execute("SELECT name, amount, date FROM Expenses WHERE LOWER(name) LIKE %s", (f"%{search_query}%",))
            rows = cursor.fetchall()
            for row in rows:
                print(f"Name : {row[0]} | Amount : {row[1]} | Date : {row[2]}")
                filtered_total += float(row[1])
                found = True

        elif selected_db == "postgresql":
            cursor.execute("SELECT name, amount, expense_date FROM Expenses WHERE LOWER(name) LIKE %s", (f"%{search_query}%",))
            rows = cursor.fetchall()
            for row in rows:
                print(f"Name: {row[0]} | Amount: {row[1]} | Date: {row[2]}")
                filtered_total += float(row[1])
                found = True

        if not found:
            print("There is no item of this name !!")
        else:
            print("-" * 40)
            print(f"Total Filtered Expense: Rs {filtered_total}")

    # 5: Export Summary to Txt
    elif choice == 5:
        records_to_export = []

        if selected_db == "sqlite":
              cursor.execute("SELECT name, amount, date FROM Expenses")
              records_to_export = cursor.fetchall()

        elif selected_db == "mongodb":
              docs = cursor.find()
              records_to_export = [(doc.get("name"), doc.get("amount"), doc.get("date")) for doc in docs]

        elif selected_db == "mysql":
               cursor.execute("SELECT name, amount, date FROM Expenses")
               records_to_export = cursor.fetchall()

        elif selected_db == "postgresql":
             cursor.execute("SELECT name, amount, expense_date FROM Expenses")
             records_to_export = cursor.fetchall()

        if not records_to_export:
               print(f"No expenses found in {selected_db.upper()} to Export!")
        else:
            with open("expense_summary.txt", "w") as file:
              file.write(f"--- Expense Summary ({selected_db.upper()}) ---\n")
              for item in records_to_export:
                  file.write(f"Name: {item[0]} | Amount : {item[1]} | DATE : {item[2]}\n---------------------------\n")
            print(f"Successfully Exported all records from {selected_db.upper()} to 'expense_summary.txt'")

    # 6: Switch Database
    elif choice == 6:
        selected_db = choose_database()
        connection, cursor = connect_database(selected_db)
        print(f"Successfully switched to : {selected_db}")