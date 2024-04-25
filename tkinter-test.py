import tkinter as tk
from tkinter import ttk
import sqlite3

conn = sqlite3.connect("./data/weapons.db")
c = conn.cursor()
c.execute("SELECT * FROM weapons")

data = c.fetchall()
column_names = [i[0] for i in c.description]
name_index = column_names.index("name")
