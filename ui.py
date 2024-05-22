import tkinter as tk
from tkinter import *
import tkinter.font as font
import sqlite3
import json
import webbrowser
from styles import *

def fetch_init_data():
    global c, data, resists_columns
    conn = sqlite3.connect(f"./data/{curr_item_type}.db")
    c = conn.cursor()
    c.execute(f"PRAGMA table_info({curr_item_type})")
    pragma = c.fetchall()
    integer_columns = [x[1] for x in pragma if x[2].upper() == "INTEGER"]
    non_resists_columns = ['rarity', 'level', 'damage_min', 'damage_max', 'str', 'int', 'dex', 'end', 'cha', 'luk', 'wis', 'crit', 'bonus', 'melee_def', 'pierce_def', 'magic_def', 'block', 'parry', 'dodge', 'all_resist']
    # resists_columns = list(set(integer_columns)- set(non_resists_columns))
    resists_columns = [x for x in integer_columns if x not in non_resists_columns]
    c.execute(f"SELECT * FROM {curr_item_type} ORDER BY {curr_sort} ASC")
    data = c.fetchall()
    c.close()
    conn.close()

def fetch_data():
    global c, data
    conn = sqlite3.connect(f"./data/{curr_item_type}.db")
    c = conn.cursor()
    # name sort requires ascending order whereas stats are descending
    curr_tag_query = f'where da = {curr_tags[0]} AND dm = {curr_tags[2]} AND rare = {curr_tags[3]} AND seasonal = {curr_tags[4]} AND special_offer = {curr_tags[5]}'
    if curr_sort == "name":
        c.execute(f"SELECT * FROM {curr_item_type} {curr_tag_query} ORDER BY {curr_sort} ASC")
    elif curr_sort == "damage":
        c.execute(f"SELECT * FROM {curr_item_type} {curr_tag_query} ORDER BY damage_min + damage_max DESC")
    elif curr_sort in resists_columns:
        if curr_sort == "health" or curr_sort == "mana":
            c.execute(f"SELECT * FROM {curr_item_type} {curr_tag_query} ORDER BY {curr_sort} + all_resist ASC")
        else:
            c.execute(f"SELECT * FROM {curr_item_type} {curr_tag_query} ORDER BY {curr_sort} + all_resist DESC")
    else:
        c.execute(f"SELECT * FROM {curr_item_type} {curr_tag_query} ORDER BY {curr_sort} DESC")
    data = c.fetchall()
    c.close()
    conn.close()

def keyword_filter(*args):
    global keyword
    keyword = en_text.get().strip().lower()
    keyworded_data = [row for row in data if keyword in row[column_dict["name"]].lower()]
    lb.delete(0, tk.END)
    for row in keyworded_data:
        lb.insert(tk.END, row[column_dict["name"]])

def item_type_filter(item_type):
    global curr_item_type, data
    curr_item_type = item_type
    fetch_data()
    
    keyworded_data = [row for row in data if keyword in row[column_dict["name"]].lower()]
    lb.delete(0, tk.END)
    if keyword == "":
        for row in data:
            lb.insert(tk.END, row[column_dict["name"]])
    else:
        for row in keyworded_data:
            lb.insert(tk.END, row[column_dict["name"]])
        
def tag_filter(index, tag_bv):
    global curr_tags
    curr_tags[index] = tag_bv
    # curr_tags_str = 
    print(curr_tags)
    fetch_data()
    
    keyworded_data = [row for row in data if keyword in row[column_dict["name"]].lower()]
    lb.delete(0, tk.END)
    if keyword == "":
        for row in data:
            lb.insert(tk.END, row[column_dict["name"]])
    else:
        for row in keyworded_data:
            lb.insert(tk.END, row[column_dict["name"]])

def stat_sort(column_name):
    global curr_sort, data
    curr_sort = column_name
    fetch_data()

    keyworded_data = [row for row in data if keyword in row[column_dict["name"]].lower()]
    lb.delete(0, tk.END)
    if keyword == "":
        for row in data:
            lb.insert(tk.END, row[column_dict["name"]])
    else:
        for row in keyworded_data:
            lb.insert(tk.END, row[column_dict["name"]])

def item_select(event):
    keyworded_data = [row for row in data if keyword in row[column_dict["name"]].lower()]
    # get index from listbox item select
    selected_index_tuple = lb.curselection()
    if selected_index_tuple:
        selected_index = selected_index_tuple[0]
        if keyword == "":
            item_row = data[selected_index]
        else:
            item_row = keyworded_data[selected_index]
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
    # --- special (forum layout got reworked early may 2024)
    # tags
    tag_fr = tk.Frame(fr, bg="#ebe2c5")
    tag_fr.pack(anchor="w", pady=20)
    if row[column_dict['da']] == True:
        da_label = tk.Label(tag_fr, text="DA", font=bold12_font, fg="#600246", bg="#ebe2c5", justify="left")
        da_label.pack(side="left", anchor="nw", padx=(5,0))
    dc_list = json.loads(row[column_dict['dc']])
    for i in dc_list:
        if i == True:
            dc_label = tk.Label(tag_fr, text="DC", font=bold12_font, fg="#007800", bg="#ebe2c5", justify="left")
            dc_label.pack(side="left", anchor="nw", padx=(5,0))
        else:
            dc_label = tk.Label(tag_fr, text="NON-DC", font=bold12_font, fg="#666666", bg="#ebe2c5", justify="left")
            dc_label.pack(side="left", anchor="nw", padx=(5,0))
    if row[column_dict['dm']] == True:
        dm_label = tk.Label(tag_fr, text="DM", font=bold12_font, fg="#0cacaa", bg="#ebe2c5", justify="left",)
        dm_label.pack(side="left", anchor="nw", padx=(5,0))
    if row[column_dict['rare']] == True:
        rare_label = tk.Label(tag_fr, text="RARE", font=bold12_font, fg="#ed1c24", bg="#ebe2c5", justify="left")
        rare_label.pack(side="left", anchor="nw", padx=(5,0))
    if row[column_dict['seasonal']] == True:
        seasonal_label = tk.Label(tag_fr, text="SEASONAL", font=bold12_font, fg="#b37400", bg="#ebe2c5", justify="left")
        seasonal_label.pack(side="left", anchor="nw", padx=(5,0))
    if row[column_dict['special_offer']] == True:
        so_label = tk.Label(tag_fr, text="SPECIAL OFFER", font=bold12_font, fg="#ff6500", bg="#ebe2c5", justify="left")
        so_label.pack(side="left", anchor="nw", padx=(5,0))
    
    # non-inventory info
    # location
    loc_fr = tk.Frame(fr, bg="#ebe2c5")
    loc_fr.pack(anchor="w")
    loc_str_label = tk.Label(loc_fr, text="Location:", font=bold10_font, bg="#ebe2c5", justify="left")
    loc_str_label.grid(column=0, row=0, padx=(5,0))
    loc_names = json.loads(row[column_dict['location_name']])
    loc_links = json.loads(row[column_dict['location_link']])
    for idx, ln in enumerate(loc_names):
        loc_label = tk.Label(loc_fr, text=ln.strip(), font=standard10_font, bg="#ebe2c5", justify="left", wraplength=fr_width-18*fr_padx)
        loc_label.grid(column=1, row=idx, sticky="nw")
        loc_label.bind("<Enter>", on_enter)
        loc_label.bind("<Leave>", on_leave)
        loc_label.bind("<Button-1>", lambda event, idx=idx: open_link(loc_links[idx]))
    # price
    price_fr = tk.Frame(fr, bg="#ebe2c5")
    price_fr.pack(anchor="w")
    price_str_label = tk.Label(price_fr, text="Price:", font=bold10_font, bg="#ebe2c5", justify="left")
    price_str_label.grid(column=0, row=0, padx=(5,0))
    prices = json.loads(row[column_dict['price']])
    for idx, pr in enumerate(prices):
        price_label = tk.Label(price_fr, text=pr.strip(), font=standard10_font, bg="#ebe2c5", justify="left", wraplength=fr_width-18*fr_padx)
        price_label.grid(column=1, row=idx, sticky="nw")
    # required items
    req_fr = tk.Frame(fr, bg="#ebe2c5")
    req_fr.pack(anchor="w")
    req_str_label = tk.Label(req_fr, text="Required Items:", font=bold10_font, bg="#ebe2c5", justify="left")
    req_str_label.grid(column=0, row=0, padx=(5,0))
    req_names = json.loads(row[column_dict['required_item_name']])
    req_links = json.loads(row[column_dict['required_item_link']])
    if row[column_dict['required_item_quantity']]:
        req_qtys = json.loads(row[column_dict['required_item_quantity']])
    for idx, rn in enumerate(req_names):
        if req_qtys:
            req_label = tk.Label(req_fr, text=f"{req_qtys[idx]} {rn}", font=standard10_font, bg="#ebe2c5", justify="left", wraplength=fr_width-18*fr_padx)
        else:
            req_label = tk.Label(req_fr, text=rn, font=standard10_font, bg="#ebe2c5", justify="left", wraplength=fr_width-18*fr_padx)
        req_label.grid(column=1, row=idx, sticky="nw")
        req_label.bind("<Enter>", on_enter)
        req_label.bind("<Leave>", on_leave)
        req_label.bind("<Button-1>", lambda event, idx=idx: open_link(req_links[idx]))
    # sellback
    sb_fr = tk.Frame(fr, bg="#ebe2c5")
    sb_fr.pack(anchor="w")
    sb_str_label = tk.Label(sb_fr, text="Sellback:", font=bold10_font, bg="#ebe2c5", justify="left")
    sb_str_label.grid(column=0, row=0, padx=(5,0))
    sellbacks = json.loads(row[column_dict['sellback']])
    for idx, sb in enumerate(sellbacks):
        sb_label = tk.Label(sb_fr, text=sb.strip(), font=standard10_font, bg="#ebe2c5", justify="left", wraplength=fr_width-18*fr_padx)
        sb_label.grid(column=1, row=idx, sticky="nw")

# initialize tkinter
root = tk.Tk(className="DFCrawler")
root.configure(bg="#eacea6")
root.geometry("800x1200")

# initialize fonts and images
standard10_font = font.Font(family="Helvetica", size=10)
bold10_font = font.Font(family="Helvetica", size=10, weight="bold")
standard12_font = font.Font(family="Helvetica", size=12)
bold12_font = font.Font(family="Helvetica", size=12, weight="bold")
name_font = font.Font(family="Helvetica", size=16, weight="bold")

# define initial sorting/filtering variables
keyword = ""
curr_item_type = "weapons"
curr_tags = [False, False, False, False, False, False]
curr_sort = "name"

# connect to db and fetchall data
fetch_init_data()

# get columns and column data types
columns = [i[0] for i in c.description]
print(columns)
column_dict = {col: index for index, col in enumerate(columns)}

# ========================
# column 0
# ========================

# create listbox
lb = tk.Listbox(root, width=30, height=40, font=bold10_font, bg="#ebe2c5", selectbackground="#cbd8fe", selectborderwidth=2, relief="solid")
lb.grid(column=0, row=0, sticky="nw", padx=5, pady=5)
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
en = tk.Entry(root, textvariable=en_text, width=25)
en.grid(column=0, row=1, sticky="nw", padx=5)
en.bind("<KeyRelease>", keyword_filter)

# create item type filter
it_filter_fr = tk.Frame(root, width=lb_width, bg="#ebe2c5")
it_filter_fr.grid(column=0, row=2, sticky="nw", padx=5)
it_sv = tk.StringVar(value="weapons")
item_types = ["weapons", "helms", "capes", "necklaces", "belts", "rings", "trinkets", "bracers"]
it_images = {}
it_images_light = {}
for item_type in item_types:
    it_images[item_type] = PhotoImage(file=f"./assets/item_type_filter/{item_type}.png")
    it_images_light[item_type] = PhotoImage(file=f"./assets/item_type_filter/{item_type}_light.png")
    item_rb = tk.Radiobutton(it_filter_fr, variable=it_sv, value=item_type, command=lambda i=item_type: item_type_filter(i), image=it_images[item_type], selectimage=it_images_light[item_type], indicatoron=0, borderwidth=0, highlightthickness=0)
    item_rb.pack(side="left", anchor="nw")

# create tag filter
tag_filter1_fr = tk.Frame(root, width=lb_width, bg="#ebe2c5")
tag_filter1_fr.grid(column=0, row=3, sticky="nw", padx=5)
tag_filter2_fr = tk.Frame(root, width=lb_width, bg="#ebe2c5")
tag_filter2_fr.grid(column=0, row=4, sticky="nw", padx=5)
tags = ["da", "dc", "dm", "seasonal", "special_offer", "rare"]
tag_images = {}
for idx, tag in enumerate(tags[:4]):
    tag_bv = tk.BooleanVar()
    tag_images[tag] = PhotoImage(file=f"./assets/tag_filter/{tag}.png")
    tag_cb = tk.Checkbutton(tag_filter1_fr, text=tag, variable=tag_bv, command=lambda i=idx, bv=tag_bv: tag_filter(i, bv.get()), image=tag_images[tag], indicatoron=0)
    tag_cb.pack(side="left", anchor="nw")
for idx, tag in enumerate(tags[4:]):
    tag_bv = tk.BooleanVar()
    tag_images[tag] = PhotoImage(file=f"./assets/tag_filter/{tag}.png")
    tag_cb = tk.Checkbutton(tag_filter2_fr, text=tag, variable=tag_bv, command=lambda i=idx, bv=tag_bv: tag_filter(i, bv.get()), image=tag_images[tag], indicatoron=0)
    tag_cb.pack(side="left", anchor="nw")

# ========================
# column 1
# ========================

# create item details frame
fr = tk.Frame(root, width=fr_width, height=lb_height, bg="#ebe2c5", bd=1, relief="solid")
fr.grid(column=1, row=0, sticky="nw", padx=fr_padx, pady=5)

# create sort by label
sort_by_label = tk.Label(root, text="Sort by:", font=standard10_font, bg="#eacea6")
sort_by_label.grid(column=1, row=1, sticky="nw", padx=5, pady=5)

# create radiobuttons
sort_sv = tk.StringVar() # tkinter StringVar for tracking radio button selection
sorting_columns_row1 = ['name', 'damage', 'crit', 'bonus', 'melee_def', 'block']
sorting_columns_row2 = ['str', 'int', 'dex', 'end', 'cha', 'luk', 'wis']
sort_fr = tk.Frame(root, bg="#ebe2c5")
sort_fr.grid(column=1, row=2, sticky="nw")

for idx, col in enumerate(sorting_columns_row1 + resists_columns):    
    rb = tk.Radiobutton(sort_fr, text=col, font=standard10_font, variable=sort_sv, value=col, command=lambda c=col: stat_sort(c), bg="#eacea6")
    rb.pack(side="left", anchor="nw")

# ========================

# update listbox upon item selection
lb.bind("<<ListboxSelect>>", item_select)
fr.pack_propagate(False)

root.mainloop()
