import tkinter as tk
from tkinter import ttk

class Object:
    def __init__(self, name, price, bonuses):
        self.name = name
        self.price = price
        self.bonuses = bonuses

class SortButton(tk.Radiobutton):
    def __init__(self, master=None, **kwargs):
        kwargs["indicatoron"] = 0
        # kwargs["bg"] = "White"
        kwargs["selectcolor"] = "#BA3D65"
        kwargs["width"] = 10
        kwargs["height"] = 1
        super().__init__(master, **kwargs)

# Sample data
objects = [
    Object("Object1", 20, 5),
    Object("Object2", 15, 8),
    Object("Object3", 30, 2),
    Object("Object4", 25, 7),
    Object("Object5", 10, 3)
]

def update_listbox():
    object_listbox.delete(0, tk.END)
    for obj in sorted(objects, key=lambda x: getattr(x, sort_by.get())):
        object_listbox.insert(tk.END, obj.name)

def show_attributes(event):
    selected_index = object_listbox.curselection()[0]
    selected_object = objects[selected_index]
    name_label.config(text=f"Name: {selected_object.name}")
    price_label.config(text=f"Price: {selected_object.price}")
    bonuses_label.config(text=f"Bonuses: {selected_object.bonuses}")

def search():
    search_text = search_entry.get().lower()
    object_listbox.delete(0, tk.END)
    for obj in objects:
        if search_text in obj.name.lower():
            object_listbox.insert(tk.END, obj.name)

def on_sort_changed(*args):
    update_listbox()

# Initialize tkinter window
root = tk.Tk()
root.tk_setPalette(foreground="White", background="#202020")
root.title("Object Viewer")

# Create UI elements
search_label = tk.Label(root, text="Search by Object Name:")
search_entry = tk.Entry(root, bg="#404040")
search_button = tk.Button(root, text="Search", command=search, bg="#BA3D65", activebackground="#BA164B", width=10, height=1)

search_label.pack()
search_entry.pack()
search_button.pack()

sort_by = tk.StringVar(root)
sort_by.set("name")  # default sorting attribute
sort_by.trace_add("write", on_sort_changed)

sort_label = tk.Label(root, text="Sort by:")
sort_label.pack()

sort_by_name_button = SortButton(root, text="Name", variable=sort_by, value="name")
sort_by_price_button = SortButton(root, text="Price", variable=sort_by, value="price")
sort_by_bonuses_button = SortButton(root, text="Bonuses", variable=sort_by, value="bonuses")

sort_by_name_button.pack()
sort_by_price_button.pack()
sort_by_bonuses_button.pack()

object_listbox = tk.Listbox(root, bg="#404040", selectbackground="#BA3D65")
object_listbox.pack()
object_listbox.bind("<<ListboxSelect>>", show_attributes)

name_label = tk.Label(root, text="")
price_label = tk.Label(root, text="")
bonuses_label = tk.Label(root, text="")

name_label.pack()
price_label.pack()
bonuses_label.pack()

update_listbox()

root.mainloop()


