import sqlite3

class Object:
    def __init__(self, name, price, bonuses):
        self.name = name
        self.price = price
        self.bonuses = bonuses

# Sample data
objects = [
    Object("Object1", 20, 5),
    Object("Object2", 15, 8),
    Object("Object3", 30, 2),
    Object("Object4", 25, 7),
    Object("Object5", 10, 3)
]
# Connect to SQLite database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create a table to store your objects' data
cursor.execute('''CREATE TABLE IF NOT EXISTS objects (
                name VARCHAR,
                price INTEGER,
                bonuses INTEGER,
                ...
                )''')

# Insert data into the table
for obj in objects:
    cursor.execute('''INSERT INTO objects (attribute1, attribute2, ...)
                    VALUES (?, ?, ...)''', (obj.name, obj.price, obj.bonuses,...))

# Commit changes and close connection
conn.commit()
conn.close()
