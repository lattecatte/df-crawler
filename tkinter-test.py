import tkinter as tk
from tkinter import *
import tkinter.font as font
import sqlite3
import json
import webbrowser

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

def lb_item_select(event):
    # get index from listbox item select
    selected_index_tuple = lb.curselection()
    if selected_index_tuple:
        selected_index = selected_index_tuple[0]
        if en_text.get() == "":
            item_row = data[selected_index]
        else:
            item_row = filtered_data[selected_index]
        print(item_row)
        create_labels(item_row)

def open_link(link):
    webbrowser.open(link)

def on_enter(event):
    event.widget.config(foreground="blue")

def on_leave(event):
    event.widget.config(foreground="black")

def create_labels(row):
    # destroy all child widget before creating labels
    child_widgets = fr.winfo_children()
    for i in child_widgets:
        i.destroy()
    frame_labels = []
    # name
    name_label = tk.Label(fr, text=f"{row[column_dict['name']]}", font=name_font, bg="#ebe2c5", justify="left", wraplength=fr_width-4*fr_padx, cursor="hand2")
    name_label.pack(anchor="w", padx=5, pady=(5, 0))
    name_label.bind("<Enter>", on_enter)
    name_label.bind("<Leave>", on_leave)
    # name_label.config(command=open_link(row[column_dict['link']]))
    name_label.bind("<Button-1>", lambda event: open_link(row[column_dict['link']]))
    # weapon type and level
    type_label = tk.Label(fr, text=f"{row[column_dict['item_type']].strip()}, Lvl {row[column_dict['level']]}", font=bold12_font, fg="#007800", bg="#ebe2c5")
    type_label.pack(anchor="w", padx=5)
    # description
    desc_label = tk.Label(fr, text=f"{row[column_dict['description']].strip()}", font=standard12_font, bg="#ebe2c5", justify="left", wraplength=fr_width-4*fr_padx)
    desc_label.pack(anchor="w", padx=5, pady=(0,10))
    # damage and element
    dmg_fr = tk.Frame(fr, bg="#ebe2c5")
    dmg_fr.pack(anchor="w")
    if row[column_dict['damage_min']]:
        dmg_str_label = tk.Label(dmg_fr, text="Damage:", font=bold12_font, bg="#ebe2c5", justify="left")
        dmg_str_label.pack(side="left", anchor="nw", padx=(5,0))
        dmg_label = tk.Label(dmg_fr, text=f"{row[column_dict['damage_min']]}-{row[column_dict['damage_max']]}{row[column_dict['element']]}", font=standard12_font, bg="#ebe2c5", justify="left", wraplength=fr_width-18*fr_padx)
        dmg_label.pack(side="left", anchor="nw")
    # rarity
    rrt_fr = tk.Frame(fr, bg="#ebe2c5")
    rrt_fr.pack(anchor="w")
    rrt_str_label = tk.Label(rrt_fr, text="Rarity:", font=bold12_font, bg="#ebe2c5", justify="left")
    rrt_str_label.pack(side="left", anchor="nw", padx=(5,0))
    rrt_label = tk.Label(rrt_fr, text=f"{row[column_dict['rarity']]}", font=standard12_font, bg="#ebe2c5", justify="left",)
    rrt_label.pack(side="left", anchor="nw")
    # stats
    stats_fr = tk.Frame(fr, bg="#ebe2c5")
    stats_fr.pack(anchor="w")
    stats_str_label = tk.Label(stats_fr, text="Stats:", font=bold12_font, bg="#ebe2c5", justify="left")
    stats_str_label.pack(side="left", anchor="nw", padx=(5,0))
    stats_label = tk.Label(stats_fr, text=f"{row[column_dict['bonuses']].strip()}", font=standard12_font, bg="#ebe2c5", justify="left", wraplength=fr_width-16*fr_padx)
    stats_label.pack(side="left", anchor="nw", padx=(5,0))
    # resists
    res_fr = tk.Frame(fr, bg="#ebe2c5")
    res_fr.pack(anchor="w")
    res_str_label = tk.Label(res_fr, text="Resists:", font=bold12_font, bg="#ebe2c5", justify="left")
    res_str_label.pack(side="left", anchor="nw", padx=(5,0))
    res_label = tk.Label(res_fr, text=f"{row[column_dict['resists']].strip()}", font=standard12_font, bg="#ebe2c5", justify="left", wraplength=fr_width-18*fr_padx)
    res_label.pack(side="left", anchor="nw", padx=(5,0))
    # dummy label
    dummy_label = tk.Label(fr, bg="#ebe2c5")
    dummy_label.pack()
    # --- special (forum layout got reworked early may 2024)
    # tags
    tag_fr = tk.Frame(fr, bg="#ebe2c5")
    tag_fr.pack(anchor="w")
    if row[column_dict['da']] == True:
        da_label = tk.Label(tag_fr, text="DA", font=bold10_font, fg="#600246", bg="#ebe2c5", justify="left")
        da_label.pack(side="left", anchor="nw", padx=(5,0))
    dc_list = json.loads(row[column_dict['dc']])
    for i in dc_list:
        if i == True:
            dc_label = tk.Label(tag_fr, text="DC", font=bold10_font, fg="#007800", bg="#ebe2c5", justify="left")
            dc_label.pack(side="left", anchor="nw", padx=(5,0))
        else:
            dc_label = tk.Label(tag_fr, text="NON-DC", font=bold10_font, bg="#ebe2c5", justify="left")
            dc_label.pack(side="left", anchor="nw", padx=(5,0))
    if row[column_dict['dm']] == True:
        dm_label = tk.Label(tag_fr, text="DM", font=bold10_font, fg="#0cacaa", bg="#ebe2c5", justify="left",)
        dm_label.pack(side="left", anchor="nw", padx=(5,0))
    if row[column_dict['rare']] == True:
        rare_label = tk.Label(tag_fr, text="RARE", font=bold10_font, fg="#ed1c24", bg="#ebe2c5", justify="left")
        rare_label.pack(side="left", anchor="nw", padx=(5,0))
    if row[column_dict['seasonal']] == True:
        seasonal_label = tk.Label(tag_fr, text="SEASONAL", font=bold10_font, fg="#b37400", bg="#ebe2c5", justify="left")
        seasonal_label.pack(side="left", anchor="nw", padx=(5,0))
    if row[column_dict['special_offer']] == True:
        so_label = tk.Label(tag_fr, text="SPECIAL OFFER", font=bold10_font, fg="#ff6500", bg="#ebe2c5", justify="left")
        so_label.pack(side="left", anchor="nw", padx=(5,0))
    # non-inventory info
    loc_fr = tk.Frame(fr, bg="#ebe2c5")
    loc_fr.pack(anchor="w")
    loc_str_label = tk.Label(loc_fr, text="Location", font=bold10_font, bg="#ebe2c5", justify="left")
    loc_str_label.pack(side="left", anchor="nw", padx=(5,0))
    loc_label = tk.Label(loc_fr, text=f"{row[column_dict['location_name']]}", font=standard10_font, bg="#ebe2c5", justify="left", wraplength=fr_width-18*fr_padx)
    loc_label.pack(side="left", anchor="nw", padx=(5,0))

def write_callback(*args):
    global filtered_data
    search_term = en_text.get().strip().lower()
    filtered_data = [row for row in data if search_term in row[column_dict["name"]].lower()]
    lb.delete(0, tk.END)
    for row in filtered_data:
        lb.insert(tk.END, row[column_dict["name"]])

# initialize tkinter
root = tk.Tk(className="DFCrawler")
root.configure(bg="#eacea6")
root.geometry("800x1200")

# fonts
standard10_font = font.Font(family="Helvetica", size=10)
bold10_font = font.Font(family="Helvetica", size=10, weight="bold")
standard12_font = font.Font(family="Helvetica", size=12)
bold12_font = font.Font(family="Helvetica", size=12, weight="bold")
name_font = font.Font(family="Helvetica", size=16, weight="bold")

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

# create listbox
lb = tk.Listbox(root, width=30, height=40, font=bold10_font, bg="#ebe2c5", selectbackground="#cbd8fe", selectborderwidth=2, relief=tk.SOLID)
lb.grid(column=0, row=0, sticky=tk.NW, padx=5, pady=5)
for row in data:
    lb.insert(tk.END, row[column_dict["name"]])

# get lb dimensions for frame
root.update_idletasks()
lb_width = lb.winfo_width()
lb_height = lb.winfo_height()
fr_width = 500
fr_padx = 5

# create search entry
en_text = tk.StringVar() # tkinter StringVar for tracking search term
en = tk.Entry(root, textvariable=en_text, width=24)
en.grid(column=0, row=1, sticky=tk.W, padx=5)
en.bind("<KeyRelease>", write_callback)

# create sort by label
sort_by_label = tk.Label(root, text="Sort by:", font=standard10_font, bg="#eacea6")
sort_by_label.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)

# create radio buttons
rb_column = tk.StringVar() # tkinter StringVar for tracking radio button selection
sorting_columns = columns[0:3]
for idx, col in enumerate(sorting_columns):    
    rb = tk.Radiobutton(root, text=col, font=standard10_font, variable=rb_column, value=col, command=lambda c=col: rb_sort(c), bg="#eacea6")
    rb.grid(column=0, row=idx+3, sticky=tk.W, padx=5)

# create frame to hold item details
fr = tk.Frame(root, width=fr_width, height=lb_height, bg="#ebe2c5", bd=1, relief=tk.SOLID)
fr.grid(column=1, row=0, sticky=tk.NW, padx=fr_padx, pady=5)

# update listbox upon item selection
lb.bind("<<ListboxSelect>>", lb_item_select)
fr.pack_propagate(False)

root.mainloop()
