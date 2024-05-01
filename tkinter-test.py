import tkinter as tk
from tkinter import ttk
import tkinter.font as font
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
        for idx, lab in enumerate(labels):
            # # labels[idx].config(text=f"Name: {item_row[column_dict['name']]}")
            lab.config(text=f"{columns[idx]}: {item_row[column_dict[columns[idx]]]}")

        lbd.insert(tk.END, "kekw")
        
        

# initialize tkinter
root = tk.Tk(className="DFCrawler")
root.configure(bg="#eacea6")

# root.geometry("1000x750")

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

# create sort by label
sort_by_label = tk.Label(root, text="Sort by:", bg="#eacea6")
sort_by_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

# create radio buttons
# tkinter IntVar for tracking radio button selection
rb_column = tk.StringVar()
sorting_columns = columns[0:3]
rb_grid_count = len(sorting_columns) + 1
for idx, col in enumerate(sorting_columns):
    rb = tk.Radiobutton(root, text=col, variable=rb_column, value=col, command=lambda c=col: rb_sort(c), bg="#eacea6")
    rb.grid(column=0, row=idx+1, sticky=tk.W, padx=5)

# create listbox
custom_font = font.Font(family="Helvetica", size=10, weight="bold")
custom_style = ttk.Style()
lb = tk.Listbox(root, width=50, height=30, font=custom_font, bg="#ebe2c5", selectbackground="#cbd8fe", selectborderwidth=2, relief="solid")
lb.grid(column=0, row=rb_grid_count+1, rowspan=50, sticky=tk.NW, padx=5, pady=5)
for row in data:
    lb.insert(tk.END, row[column_dict["name"]])

# create labels to display item info
labels = []
for idx, col in enumerate(columns):
    label = tk.Label(root, text=f"{columns[idx]}:", bg="#eacea6")
    label.grid(column=1, row=rb_grid_count+idx+1, sticky=tk.NW, padx=5)
    labels.append(label)

# REMEMBER TO CHANGE THIS TO FRAME
lbd = tk.Listbox(root, width=50, height=30, font=custom_font, bg="#ebe2c5", selectbackground="#cbd8fe", selectborderwidth=2, relief="solid")
lbd.grid(column=2, row=rb_grid_count+1, rowspan=50, sticky=tk.NW, padx=5, pady=5)

# update listbox upon item selection
lb.bind("<<ListboxSelect>>", lb_item_select)

root.mainloop()
