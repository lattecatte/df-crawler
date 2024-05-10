import sqlite3
import json
from datetime import datetime
import os

from .item_utils import *

str_attr = ["link", "name", "description", "item_type", "damage_type", "element",
            "special_name", "special_activation", "special_effect", "special_damage", "special_element", "special_damage_type", "special_rate",
            "bonuses", "resists"]
int_attr = ["rarity", "level", "damage_min", "damage_max",
            "str", "int", "dex", "end", "cha", "luk", "wis", "crit", "bonus", "melee_def", "pierce_def", "magic_def", "block", "parry", "dodge",
            "all_resist", "fire", "water", "wind", "ice", "stone", "nature", "energy", "light", "darkness", "bacon",
            "metal", "silver", "poison", "disease", "good", "evil", "ebil", "fear", "health", "mana", "immobility", "shrink"]
bool_attr = ["da", "dm", "rare", "seasonal", "special_offer"]
list_attr = ["dc", "location_name", "location_link", "price", "required_item_name", "required_item_link", "required_item_quantity", "sellback"]

# check attribute data type in python and return corresponding data type for sqlite
def get_sqlite_type(attribute):
    if isinstance(attribute, str):
        return "VARCHAR"
    elif isinstance(attribute, int):
        return "INTEGER"
    elif isinstance(attribute, bool):
        return "BOOLEAN"
    elif isinstance(attribute, list):
        return "TEXT" # to JSON
    else:
        return "TEXT"

def save_to_database(item_type):
    # connect to sqlite db
    formatted_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = f"./data/{item_type}.db"
    full_path = f"./data/{item_type}_{formatted_date}.db"
    conn = sqlite3.connect(full_path)
    c = conn.cursor()

    # column definitions
    str_column_def = ", ".join(f"{a} VARCHAR" for a in str_attr)
    int_column_def = ", ".join(f"{a} INTEGER" for a in int_attr)
    bool_column_def = ", ".join(f"{a} BOOLEAN" for a in bool_attr)
    list_column_def = ", ".join(f"{a} TEXT" for a in list_attr)
    column_def = ", ".join([str_column_def, int_column_def, bool_column_def, list_column_def])

    # create table with column definitions
    c.execute(f"DROP TABLE IF EXISTS {item_type}")
    c.execute(f"CREATE TABLE {item_type}({column_def})")

    # insert a row for each item (existing attributes)
    for item_id, item_obj in items.items():
        row_attr = []
        row_val = []
        for attr, val in item_obj.__dict__.items():
            # print("----->", attr, val)
            # all is an SQL keyword so it has to be modified to prevent errors
            if attr == "all":
                attr = "all_resist"
            # non standard attributes
            elif attr not in str_attr + int_attr + bool_attr + list_attr:
                # print(item_obj.name, item_obj.link, attr, get_sqlite_type(attr))
                # escape attr str with single quotes
                c.execute(f"ALTER TABLE {item_type} ADD COLUMN '{attr}' INTEGER") # use {get_sqlite_type(attr)} instead of INTEGER for future uses that are not limited to resists
                int_attr.append(attr)
            row_attr.append(attr)
            row_val.append(val)
        # decode utf-8 and dump list columns into json
        row_val = [x.decode("utf-8") if isinstance(x, bytes) else x for x in row_val]
        row_val = [json.dumps(x) if type(x) == list else x for x in row_val]
        row_attr_str = ", ".join(f"'{a}'" for a in row_attr)
        question_str = ", ".join(["?"] * len(row_attr))
        c.execute(f"INSERT INTO {item_type}({row_attr_str}) VALUES({question_str})", row_val)
    conn.commit()
    conn.close()
    
    # rename and replace old .db file
    if os.path.exists(path):
        os.remove(path)
    os.rename(full_path, path)
    print(f"Created {item_type}.db")

def split_accessories():
    formatted_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    acc_list = ["helms", "capes", "necklaces", "belts", "rings", "trinkets", "bracers"]
    acc_path = {a: f"./data/{a}.db" for a in acc_list}
    acc_full_path = {a: f"./data/{a}_{formatted_date}.db" for a in acc_list}
    
    conn = sqlite3.connect("./data/accessories.db")
    c = conn.cursor()
    # helms.db
    c.execute("ATTACH DATABASE ? AS helms_db", (acc_full_path["helms"],))
    c.execute('''CREATE TABLE helms_db.helms AS
              SELECT * FROM accessories
              WHERE TRIM(equip_spot) = "Head"''')
    # # capes.db
    c.execute("ATTACH DATABASE ? AS capes_db", (acc_full_path["capes"],))
    c.execute('''CREATE TABLE capes_db.capes AS
              SELECT * FROM accessories
              WHERE TRIM(equip_spot) = "Back"''')
    # necklaces.db
    c.execute("ATTACH DATABASE ? AS necklaces_db", (acc_full_path["necklaces"],))
    c.execute('''CREATE TABLE necklaces_db.necklaces AS
              SELECT * FROM accessories
              WHERE TRIM(equip_spot) = "Neck"''')
    # belts.db
    c.execute("ATTACH DATABASE ? AS belts_db", (acc_full_path["belts"],))
    c.execute('''CREATE TABLE belts_db.belts AS
              SELECT * FROM accessories
              WHERE TRIM(equip_spot) = "Waist"''')
    # rings.db
    c.execute("ATTACH DATABASE ? AS rings_db", (acc_full_path["rings"],))
    c.execute('''CREATE TABLE rings_db.rings AS
              SELECT * FROM accessories
              WHERE TRIM(equip_spot) = "Finger"''')
    # trinkets.db
    c.execute("ATTACH DATABASE ? AS trinkets_db", (acc_full_path["trinkets"],))
    c.execute('''CREATE TABLE trinkets_db.trinkets AS
              SELECT * FROM accessories
              WHERE TRIM(equip_spot) = "Trinket"''')
    # bracers.db
    c.execute("ATTACH DATABASE ? AS bracers_db", (acc_full_path["bracers"],))
    c.execute('''CREATE TABLE bracers_db.bracers AS
              SELECT * FROM accessories
              WHERE TRIM(equip_spot) = "Wrist"''')
    conn.commit()
    conn.close()

    # rename and replace old .db files
    for path in acc_path:
        if os.path.exists(path):
            os.remove(path)
    for key in acc_full_path:
        if key in acc_path:
            os.rename(acc_full_path[key], acc_path[key])
    print("Splitted accessories.db")
