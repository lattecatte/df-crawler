import sqlite3
import json

from .weapon_utils import *

str_attr = ["link", "name", "description", "item_type", "damage_type", "element",
            "special_name", "special_activation", "special_effect", "special_damage", "special_element", "special_damage_type", "special_rate",
            "bonuses", "resists"]
int_attr = ["rarity", "level", "damage_min", "damage_max",
            "str", "int", "dex", "end", "cha", "luk", "wis", "crit", "bonus", "melee_def", "pierce_def", "magic_def", "block", "parry", "dodge",
            "all_resist", "fire", "water", "wind", "ice", "stone", "nature", "energy", "light", "darkness", "bacon",
            "metal", "silver", "poison", "disease", "good", "evil", "ebil", "fear", "health", "mana", "immobility", "shrink"]
bool_attr = ["da", "dm", "rare", "seasonal", "special_offer"]
list_attr = ["dc", "location_name", "location_link", "price", "required_item_name", "required_item_link", "required_item_quantity", "sellback"]

# # check attribute data type in python and return corresponding data type for sqlite
# def get_sqlite_type(attribute):
#     if isinstance(attribute, str):
#         return "VARCHAR"
#     elif isinstance(attribute, int):
#         return "INTEGER"
#     elif isinstance(attribute, bool):
#         return "BOOLEAN"
#     elif isinstance(attribute, list):
#         return "TEXT" # to JSON
#     else:
#         return "TEXT"

def save_to_database():
    # connect to sqlite db
    conn = sqlite3.connect('weapons.db')
    c = conn.cursor()

    # column definitions
    str_column_def = ", ".join(f"{a} VARCHAR" for a in str_attr)
    int_column_def = ", ".join(f"{a} INTEGER" for a in int_attr)
    bool_column_def = ", ".join(f"{a} BOOLEAN" for a in bool_attr)
    list_column_def = ", ".join(f"{a} TEXT" for a in list_attr)
    column_def = ", ".join([str_column_def, int_column_def, bool_column_def, list_column_def])

    # create table with column definitions
    c.execute("DROP TABLE IF EXISTS weapons")
    c.execute(f"CREATE TABLE weapons({column_def})")

    # insert a row for each weapon (existing attributes)
    for weapon_id, weapon_obj in weapons.items():
        standard_attr = []
        standard_val = []
        for attr, val in weapon_obj.__dict__.items():
            print("----->", attr, val)
            # all is an SQL keyword so it has to be modified to prevent errors
            if attr == "all":
                attr = "all_resist"
            else:
                pass
            if attr in str_attr or attr in int_attr or attr in bool_attr or attr in list_attr:
                standard_attr.append(attr)
                standard_val.append(val)
        # decode utf-8 and dump list columns into json
        standard_val = [x.decode("utf-8") if isinstance(x, bytes) else x for x in standard_val]
        standard_val = [json.dumps(x) if type(x) == list else x for x in standard_val]
        standard_attr_str = ", ".join(f"{a}" for a in standard_attr)
        question_str = ", ".join(["?"] * len(standard_attr))

        c.execute(f"INSERT INTO weapons({standard_attr_str}) VALUES({question_str})", standard_val)
        
    conn.commit()
    conn.close()
