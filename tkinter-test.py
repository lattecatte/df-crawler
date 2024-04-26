import tkinter as tk
from tkinter import ttk
import sqlite3

conn = sqlite3.connect("./data/weapons.db")
c = conn.cursor()
c.execute("SELECT * FROM weapons ORDER BY name ASC")
data = c.fetchall()

columns = [i[0] for i in c.description]

# dict matching column name with column index
column_dict = dict()
for index, cn in enumerate(columns):
    column_dict[cn] = index

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
    
root = tk.Tk()
root.title = "kekw"
root.geometry("1000x750")

# tkinter IntVar for all columns
column_sort_vars = {}
for col in columns[0:3]:
    column_sort_vars[col] = tk.IntVar()
    rb = ttk.Radiobutton(root, text=col, variable=column_sort_vars[col], command=lambda c=col: column_sorting(c))
    rb.pack()

lb = tk.Listbox(root, width=100, height=30)
lb.pack()

for row in data:
    lb.insert(tk.END, row[column_dict["name"]])

c.close()
conn.close()
root.mainloop()
