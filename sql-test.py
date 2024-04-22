import sqlite3
import inspect
import json

class MyClass:
    def __init__(self, integer_attr, string_attr, array_attr, boolean_attr):
        self.integer_attr = integer_attr
        self.string_attr = string_attr
        self.array_attr = array_attr
        self.boolean_attr = boolean_attr

def get_sqlite_type(value):
    if isinstance(value, int):
        return 'INTEGER'
    elif isinstance(value, str):
        return 'VARCHAR'
    elif isinstance(value, bool):
        return 'BOOLEAN'
    elif isinstance(value, list):
        return 'TEXT'  # Storing as text, can be JSON serialized
    else:
        return 'TEXT'

def save_to_database(obj):
    conn = sqlite3.connect('my_database.db')
    c = conn.cursor()

    # Create table if not exists
    columns = inspect.getmembers(obj.__class__, lambda a: not(inspect.isroutine(a)))
    column_definitions = ', '.join(f'{name} {get_sqlite_type(value)}' for name, value in columns if not name.startswith('__'))
    c.execute(f'CREATE TABLE IF NOT EXISTS my_table ({column_definitions})')

    # Convert arrays to JSON for storage
    values = []
    for name, value in columns:
        if isinstance(value, list):
            values.append(json.dumps(getattr(obj, name)))
        elif not name.startswith('__'):
            values.append(getattr(obj, name))

    # Insert data into the table
    c.execute(f"INSERT INTO my_table VALUES (NULL, {', '.join(['?'] * len(values))})", values)

    # Commit changes and close connection
    conn.commit()
    conn.close()

# Example usage
obj = MyClass(42, "Hello", [1, 2, 3], True)
# save_to_database(obj)
print(obj)
