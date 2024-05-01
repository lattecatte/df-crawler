import tkinter as tk
from tkinter import ttk
import sqlite3

def rb_sort(column_name):
    global data
    conn = sqlite3.connect("./data/weapons.db")
    c = conn.cursor()
    c.execute(f"SELECT * FROM weapons ORDER BY {column_name} ASC")
    data = c.fetchall()

    lb.delete(0, tk.END)
    for row in data:
        lb.insert(tk.END, row[column_dict["name"]])

    c.close()
    conn.close()

# def set_label(var):
#     var_str = 
#     var.config(text=f"Name: {item_row[column_dict['name']]}")

def lb_item_select(event):
    # get index from listbox item select
    selected_index_tuple = lb.curselection()
    selected_index = selected_index_tuple[0]

    if selected_index:
        # item_name = lb.get(selected_index)
        item_row = data[selected_index]
        print(item_row)
        name_label.config(text=f"Name: {item_row[column_dict['name']]}")
        

# initialize tkinter
root = tk.Tk()
root.title = "kekw"
root.geometry("1000x750")

# connect to db and fetchall data
conn = sqlite3.connect("./data/weapons.db")
c = conn.cursor()
c.execute("SELECT * FROM weapons ORDER BY name ASC")
data = c.fetchall()
c.close()
conn.close()

# get columns
columns = [i[0] for i in c.description]
print(columns)
column_dict = {col: index for index, col in enumerate(columns)}
# tkinter IntVar for tracking radio button selection
rb_column = tk.StringVar()

# create radio buttons
for col in columns[0:3]:
    rb = ttk.Radiobutton(root, text=col, variable=rb_column, value=col, command=lambda c=col: rb_sort(c))
    rb.pack()

# create listbox
lb = tk.Listbox(root, width=100, height=30)
lb.pack()
for row in data:
    lb.insert(tk.END, row[column_dict["name"]])

# create labels to display item info
name_label = tk.Label(root, text="Name:")
description_label = tk.Label(root, text="Description:")
name_label.pack()
description_label.pack()

# update listbox upon item selection
lb.bind("<<ListboxSelect>>", lb_item_select)

root.mainloop()
