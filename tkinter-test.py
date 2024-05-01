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

        # create labels inside frame
        # destroy all child widget before creating labels
        child_widgets = fr.winfo_children()
        for i in child_widgets:
            i.destroy()
        frame_labels = []
        # name
        name_font = font.Font(family="Helvetica", size=16, weight="bold")
        name_label = tk.Label(fr, text=f"{item_row[column_dict['name']]}", font=name_font, bg="#ebe2c5", justify="left", wraplength=fr_width-4*fr_padx)
        name_label.pack(anchor="w", padx=5, pady=(5, 0))
        # weapon type and level
        type_font = font.Font(family="Helvetica", size=12, weight="bold")
        type_label = tk.Label(fr, text=f"{item_row[column_dict['item_type']].rstrip()}, Lvl {item_row[column_dict['level']]}", font=type_font, fg="#007800", bg="#ebe2c5")
        type_label.pack(anchor="w")
        # description
        desc_label = tk.Label(fr, text=f"{item_row[column_dict['description']]}", font=standard12_font, bg="#ebe2c5", justify="left", wraplength=fr_width-4*fr_padx)
        desc_label.pack(anchor="w", padx=5)
        # damage string
        dmg_str_label = tk.Label(fr, text="Damage:", font=bold12_font, bg="#ebe2c5", justify="left", wraplength=fr_width-4*fr_padx)
        dmg_str_label.pack(anchor="w", padx=(5,0))
        # damage and element
        dmg_label = tk.Label(fr, text=f"{item_row[column_dict['damage_min']]}-{item_row[column_dict['damage_max']]}{item_row[column_dict['element']]}", font=standard12_font, bg="#ebe2c5", justify="left", wraplength=fr_width-4*fr_padx)
        dmg_label.pack(anchor="w", padx=(5,0))
        # rarity string
        rrt_str_label = tk.Label(fr, text="Rarity:", font=bold12_font, bg="#ebe2c5", justify="left", wraplength=fr_width-4*fr_padx)
        rrt_str_label.pack(anchor="w", padx=(5,0))
        # rarity
        rrt_label = tk.Label(fr, text=f"{item_row[column_dict['rarity']]}", font=standard12_font, bg="#ebe2c5", justify="left", wraplength=fr_width-4*fr_padx)
        rrt_label.pack(anchor="w", padx=(5,0))
        # stats string
        stats_str_label = tk.Label(fr, text="Stats:", font=bold12_font, bg="#ebe2c5", justify="left", wraplength=fr_width-4*fr_padx)
        stats_str_label.pack(anchor="w", padx=(5,0))
        # stats
        stats_label = tk.Label(fr, text=f"{item_row[column_dict['bonuses']].lstrip()}", font=standard12_font, bg="#ebe2c5", justify="left", wraplength=fr_width-4*fr_padx)
        stats_label.pack(anchor="w", padx=(5,0))
        # resists string
        resists_str_label = tk.Label(fr, text="Resists:", font=bold12_font, bg="#ebe2c5", justify="left", wraplength=fr_width-4*fr_padx)
        resists_str_label.pack(anchor="w", padx=(5,0))
        # resists
        resists_label = tk.Label(fr, text=f"{item_row[column_dict['resists']].lstrip()}", font=standard12_font, bg="#ebe2c5", justify="left", wraplength=fr_width-4*fr_padx)
        resists_label.pack(anchor="w", padx=(5,0))
        # dummy label
        dummy_label = tk.Label(fr, bg="#ebe2c5")
        dummy_label.pack()
        # special
        if item_row[column_dict['special_name']]:
            sp_name_str_label = tk.Label(fr, text="Special Name:", font=bold12_font, bg="#ebe2c5", justify="left", wraplength=fr_width-4*fr_padx)
            sp_name_str_label.pack(anchor="w", padx=(5,0))
            sp_name_label = tk.Label(fr, text=f"{item_row[column_dict['special_name']].lstrip()}", font=standard10_font, bg="#ebe2c5", justify="left", wraplength=fr_width-4*fr_padx)
            sp_name_label.pack(anchor="w", padx=(5,0))
            sp_act_str_label = tk.Label(fr, text="Special Activation:", font=bold12_font, bg="#ebe2c5", justify="left", wraplength=fr_width-4*fr_padx)
            sp_act_str_label.pack(anchor="w", padx=(5,0))
            sp_act_label = tk.Label(fr, text=f"{item_row[column_dict['special_activation']].lstrip()}", font=standard10_font, bg="#ebe2c5", justify="left", wraplength=fr_width-4*fr_padx)
            sp_act_label.pack(anchor="w", padx=(5,0))



# initialize tkinter
root = tk.Tk(className="DFCrawler")
root.configure(bg="#eacea6")
root.geometry("1000x750")

# fonts
standard10_font = font.Font(family="Helvetica", size=10)
bold10_font = font.Font(family="Helvetica", size=10, weight="bold")
standard12_font = font.Font(family="Helvetica", size=12)
bold12_font = font.Font(family="Helvetica", size=12, weight="bold")

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
sort_by_label = tk.Label(root, text="Sort by:", font=standard12_font, bg="#eacea6")
sort_by_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

# create radio buttons
rb_column = tk.StringVar() # tkinter IntVar for tracking radio button selection
sorting_columns = columns[0:3]
rb_grid_count = len(sorting_columns) + 1
for idx, col in enumerate(sorting_columns):
    rb = tk.Radiobutton(root, text=col, font=standard12_font, variable=rb_column, value=col, command=lambda c=col: rb_sort(c), bg="#eacea6")
    rb.grid(column=0, row=idx+1, sticky=tk.W, padx=5)

# create listbox
custom_font = font.Font(family="Helvetica", size=10, weight="bold")
custom_style = ttk.Style()

lb = tk.Listbox(root, width=30, height=30, font=custom_font, bg="#ebe2c5", selectbackground="#cbd8fe", selectborderwidth=2, relief=tk.SOLID)
lb.grid(column=0, row=rb_grid_count+1, rowspan=50, sticky=tk.NW, padx=5, pady=5)
for row in data:
    lb.insert(tk.END, row[column_dict["name"]])

# create labels to display item info
labels = []
for idx, col in enumerate(columns):
    label = tk.Label(root, text=f"{columns[idx]}:", bg="#eacea6")
    label.grid(column=2, row=rb_grid_count+idx+1, sticky=tk.NW, padx=5)
    labels.append(label)

# get lb dimensions for frame
root.update_idletasks()
lb_height = lb.winfo_height()
fr_width = 500
fr_padx = 5

# create frame to hold item details
fr = tk.Frame(root, width=fr_width, height=lb_height, bg="#ebe2c5", bd=1, relief=tk.SOLID)
fr.grid(column=1, row=rb_grid_count+1, rowspan=50, sticky=tk.NW, padx=fr_padx, pady=5)

# update listbox upon item selection
lb.bind("<<ListboxSelect>>", lb_item_select)
fr.pack_propagate(False)

root.mainloop()
