import tkinter as tk
from tkinter import ttk
import sqlite3

def column_sorting(column_name):
    conn = sqlite3.connect("./data/weapons.db")
    c = conn.cursor()
    c.execute(f"SELECT * FROM weapons ORDER BY {column_name} ASC")
    data = c.fetchall()

    lb.delete(0, tk.END)
    for row in data:
        lb.insert(tk.END, row[column_dict["name"]])

    c.close()
    conn.close()

def on_item_select(event):
    # Get the selected item
    selected_index = lb.curselection()
    print(selected_index)
    print(selected_index[0])

    if selected_index:
        selected_item = lb.get(selected_index[0])
        print(selected_item)
        name_label.config(text=f"Name: {selected_item}")
        

root = tk.Tk()
root.title = "kekw"
root.geometry("1000x750")

# connect to db
conn = sqlite3.connect("./data/weapons.db")
c = conn.cursor()
c.execute("SELECT * FROM weapons ORDER BY name ASC")

# fetch column names
columns = [i[0] for i in c.description]
column_dict = {col: index for index, col in enumerate(columns)}

# tkinter IntVar for tracking selected column
selected_column = tk.StringVar()

# create radio buttons
for col in columns[0:3]:
    rb = ttk.Radiobutton(root, text=col, variable=selected_column, value=col, command=lambda c=col: column_sorting(c))
    rb.pack()

# create listbox
lb = tk.Listbox(root, width=100, height=30)
lb.pack()

# fetch data and display in listbox
data = c.fetchall()
for row in data:
    lb.insert(tk.END, row[column_dict["name"]])

# create labels to display item info
name_label = tk.Label(root, text="Name:")
description_label = tk.Label(root, text="Description:")
name_label.pack()
description_label.pack()

# Bind the listbox selection event to the on_item_select function
lb.bind("<<ListboxSelect>>", on_item_select)


c.close()
conn.close()
root.mainloop()
