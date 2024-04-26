import tkinter as tk
import sqlite3

def load_data(sort_by=None):
    # Connect to the SQLite database
    conn = sqlite3.connect('./data/weapons.db')
    c = conn.cursor()

    # Get the column names from the cursor description
    c.execute("SELECT * FROM weapons")
    column_names = [description[0] for description in c.description]

    # Check if the required columns are present in the table
    if 'name' not in column_names or 'rarity' not in column_names or 'level' not in column_names:
        print("Error: 'name', 'rarity', or 'level' columns not found in the database table.")
        conn.close()
        return None

    # Construct the SQL query dynamically based on user selection
    if sort_by:
        if sort_by in column_names:
            query = f"SELECT * FROM weapons ORDER BY {sort_by}"
        else:
            print(f"Error: '{sort_by}' column not found in the database table.")
            conn.close()
            return None
    else:
        query = "SELECT * FROM weapons"

    # Execute the SQL query
    c.execute(query)

    # Fetch all rows
    items = c.fetchall()

    # Close the connection
    conn.close()

    return items, column_names

def on_item_select(event):
    # Get the selected item
    selection = item_listbox.curselection()
    if selection:
        index = selection[0]
        selected_item = items[index]

        # Get the column indices for name, rarity, and level
        name_index = column_names.index('name')
        rarity_index = column_names.index('rarity')
        level_index = column_names.index('level')

        # Update the label with the selected item's details
        name_var.set(selected_item[name_index])
        rarity_var.set(selected_item[rarity_index])
        level_var.set(selected_item[level_index])

# Load initial data
items, column_names = load_data()

def update_listbox(sort_by=None):
    # Clear existing items from the listbox
    item_listbox.delete(0, tk.END)

    # Load data from the database
    global items
    items = load_data(sort_by)

    # Insert items into the listbox
    for item in items:
        item_listbox.insert(tk.END, item[0])

# Create the main window
root = tk.Tk()
root.title("Item Viewer")

# Create a frame for sorting options
sort_frame = tk.Frame(root)
sort_frame.pack()

# Create radio buttons for sorting
sort_var = tk.StringVar()
tk.Radiobutton(sort_frame, text="Name", variable=sort_var, value=None, command=lambda: update_listbox()).pack(side=tk.LEFT)
tk.Radiobutton(sort_frame, text="Rarity", variable=sort_var, value="rarity", command=lambda: update_listbox("rarity")).pack(side=tk.LEFT)
tk.Radiobutton(sort_frame, text="Level", variable=sort_var, value="level", command=lambda: update_listbox("level")).pack(side=tk.LEFT)

# Create a listbox to display item names
item_listbox = tk.Listbox(root)
item_listbox.pack()

# Create labels for displaying item details
name_var = tk.StringVar()
rarity_var = tk.StringVar()
level_var = tk.StringVar()

name_label = tk.Label(root, textvariable=name_var)
rarity_label = tk.Label(root, textvariable=rarity_var)
level_label = tk.Label(root, textvariable=level_var)

name_label.pack()
rarity_label.pack()
level_label.pack()

# Bind the listbox selection event to the on_item_select function
item_listbox.bind("<<ListboxSelect>>", on_item_select)

# Load initial data
update_listbox()

# Start the Tkinter event loop
root.mainloop()
