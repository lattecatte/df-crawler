import scrapy
from scrapy.crawler import CrawlerProcess
import csv
import re
import tkinter as tk
from tkinter import ttk

weapons = dict()

# sometimes the category "Bonuses:" is listed as "Stats:" on the forums
category_list = [" Price:", " Sellback:", " Level:", " Element:",
                 " Bonuses:", " Stats:", " Resists:", " Rarity:", " Item Type:", " Damage Type:",
                 " Special Name:", " Special Activation:", " Special Damage:", " Special Effect:", " Special Element:", " Special Damage Type:", " Special Rate:",
                 " Damage:"]

category_attr = ["price", "sellback", "level", "element",
                 "bonuses", "bonuses", "resists", "rarity", "item_type", "damage_type",
                 "special_name", "special_activation", "special_damage", "special_effect", "special_element", "special_damage_type", "special_rate"]

# extract content between two keywords
def extract_content_between_words(page, start_word, end_word):
    pattern = re.compile(r'{}(.*?){}'.format(re.escape(start_word), re.escape(end_word)), re.DOTALL)
    matches = re.findall(pattern, page)
    return matches

# filter main_list to only contain elements that are available in sub_list
def filter_list(main_list, sub_list):
    return [m for m in main_list if any(m.startswith(s) for s in sub_list)]

class Weapon:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.location_name = []
        self.location_link = []
        self.price = [] # array because multiple sources of the weapon
        self.required_item_name = []
        self.required_item_link = []
        self.sellback = []
        self.dc = []

    def append_attr(self, attr, value):
        self.__dict__[attr].append(value)

    def add_name_description(self, name, description):
        self.name = name
        self.description = description

objects = [Weapon(link="", name="", description="", da=False, dc=[], dm=False, rare=False, seasonal=False, special_offer=False,
                  location_name=[], location_link=[], price=[], required_item_name=[], required_item_link=[], required_item_quantity=[], sellback=[],
                  item_type="", damage_type="", rarity=0, level=0, damage_min=0, damage_max=0, element="",
                  special_name="", special_activation="", special_effect="", special_damage="", special_element="", special_damage_type="", special_rate="",
                  bonuses="", str=0, int=0, dex=0, end=0, cha=0, luk=0, wis=0, crit=0, bonus=0, melee_def=0, pierce_def=0, magic_def=0, block=0, parry=0, dodge=0,
                  resists="", all=0, fire=0, water=0, wind=0, ice=0, stone=0, nature=0, energy=0, light=0, darkness=0, bacon=0,
                  metal=0, silver=0, poison=0, disease=0, good=0, evil=0, ebil=0, fear=0,
                  doom=0, love=0, hunger=0, marketability=0, health=0, mana=0, immobility=0, shrink=0)]

class ForumSpider(scrapy.Spider):
    name = 'forum-spider'
    start_urls = ['https://forums2.battleon.com/f/tm.asp?m=22094733']

    # parsing A-Z page
    def parse(self, response):
        # get item path from DOM tree <td class="msg"> <a>
        test_index = 0
        test_range = 20
        item_path = response.xpath("//td[@class='msg']/a")[test_index:test_index+test_range]

        for item in item_path:
            # # get item name from <td class="msg"> <a> text
            # item_name = item.xpath("text()").get().encode("utf-8")

            # get item url from <td class="msg"> <a href="">
            item_url = item.xpath("@href").get()

            # move on to parse_element
            yield scrapy.Request(url = response.urljoin(item_url), callback = self.parse_element)

    # parsing individual item page
    def parse_element(self, response):
        # get message path from DOM tree <td class="msg">
        message_path = response.xpath("//td[@class='msg']")
            
        for index, msg_path in enumerate(message_path):
            # get name from <b> tag, sometimes the <b> tag and <font> are used interchangeably on the forums
            name_path = msg_path.xpath("font/b/text() | b/font/text()")
            name = name_path.getall()
            name = [x.encode("utf-8") for x in name]
            
            if name:
                # create object (object name is url + msg index in individual item page)
                url = response.request.url
                url_num = url.replace("https://forums2.battleon.com/f/tm.asp?m=", "")
                id = str(url_num) + "_" + str(index)

                weapons[id] = Weapon()
                objects.append(weapons[id])

                # set link and name
                setattr(weapons[id], "link", url)
                setattr(weapons[id], "name", name[0])

                # get description from <i> tag following <b>
                desc_path = msg_path.xpath("font/following-sibling::i/text() | b/following-sibling::i/text()")
                desc = desc_path.getall()
                desc = [x.encode("utf-8") for x in desc]
                setattr(weapons[id], "description", desc[0])

                # get dm, rare, seasonal, special offer tags from images in <img>
                img_path = msg_path.xpath("img/@src | li/img/@src")
                img = img_path.getall()
                if "https://media.artix.com/encyc/df/tags/DM.jpg" in [x for x in img]:
                    setattr(weapons[id], "dm", True)
                else:
                    setattr(weapons[id], "dm", False)

                if "https://media.artix.com/encyc/df/tags/Rare.jpg" in [x for x in img]:
                    setattr(weapons[id], "rare", True)
                else:
                    setattr(weapons[id], "rare", False)

                if "https://media.artix.com/encyc/df/tags/Seasonal.jpg" in [x for x in img]:
                    setattr(weapons[id], "seasonal", True)
                else:
                    setattr(weapons[id], "seasonal", False)
                
                if "https://media.artix.com/encyc/df/tags/SpecialOffer.jpg" in [x for x in img]:
                    setattr(weapons[id], "special_offer", True)
                else:
                    setattr(weapons[id], "special_offer", False)

                # get da tag status from " (No DA Required) "
                message = msg_path.getall()[0]
                if "(No DA Required)" in message:
                    setattr(weapons[id], "da", False)
                else:
                    setattr(weapons[id], "da", True)

                # get location names and links (multiple)
                location = extract_content_between_words(message, "Location:", "Price:")
                
                for loc in location:
                    location_trimmed = extract_content_between_words(loc, 'href="', "</a>")

                    location_name = location_trimmed[0].split('">')[1]
                    weapons[id].append_attr("location_name", location_name)

                    location_link = location_trimmed[0].split('">')[0]
                    weapons[id].append_attr("location_link", location_link)
                    
                # get required item quantity, name and link
                req = extract_content_between_words(message, "Required Items:", "Sellback:")

                for index, rq in enumerate(req):
                    clean_string = re.sub(r'<[^>]*>', '', rq) # remove html tags
                    integers = re.findall(r'\b\d+\b', clean_string)
                    req_quantity = [int(x) for x in integers]
                    setattr(weapons[id], "required_item_quantity", req_quantity)

                    req_trimmed = extract_content_between_words(rq, 'href="', "</a>")

                    for r in req_trimmed:
                        req_name = r.split('">')[1]
                        weapons[id].append_attr("required_item_name", req_name)

                        req_link = r.split('">')[0]
                        weapons[id].append_attr("required_item_link", req_link)
                    
                # get information from main message path <td class="msg"> text and filter relevant categories
                info_path = msg_path.xpath("text()")
                information = filter_list(info_path.getall(), category_list)

                # removing the category strings and saving info into object attributes
                for index, info in enumerate(information):
                    # iterating multiple if statements through category_list[n]
                    for n in range(len(category_list)): 
                        if info.startswith(category_list[n]):
                            # removing category strings eg. "Price:" and only leaving value
                            information[index] = info.replace(category_list[n], "")

                            # special case for arrays price and sellback
                            if n <= 1:
                                weapons[id].append_attr(category_attr[n], information[index])
                                
                            # special case for damage (extracting min and max dmg)
                            elif n == 17:
                                setattr(weapons[id], "damage_min", information[index].split("-")[0])
                                setattr(weapons[id], "damage_max", information[index].split("-")[1])

                            # for the rest of the attributes that are variables
                            else:
                                setattr(weapons[id], category_attr[n], information[index])
                                
                                # special case for bonuses
                                if n == 4 or n == 5:
                                    bonuses = information[index].split(",")
                                    bonuses_name = []
                    
                                    for j, bon in enumerate(bonuses):
                                        if "+" in bon:
                                            # auto generate bonuses/resists names
                                            bonuses_name.append(bon.split("+")[0].strip().lower().replace(" ", "_"))
                                            bonuses_value = int(bon.split("+")[1])
                                            setattr(weapons[id], bonuses_name[j], bonuses_value)
                                        elif "-" in bon:
                                            bonuses_name.append(bon.split("-")[0].strip().lower().replace(" ", "_"))
                                            bonuses_value = -1 * int(bon.split("-")[1])
                                            setattr(weapons[id], bonuses_name[j], bonuses_value)

                                # special case for resists
                                if n == 6:
                                    resists = information[index].split(",")
                                    resists_name = []
                    
                                    for k, res in enumerate(resists):
                                        if "+" in res:
                                            resists_name.append(res.split("+")[0].strip().lower().replace(" ", "_"))
                                            resists_value = int(res.split("+")[1])
                                            setattr(weapons[id], resists_name[k], resists_value)
                                        elif "-" in res:
                                            resists_name.append(res.split("-")[0].strip().lower().replace(" ", "_"))
                                            resists_value = -1 * int(res.split("-")[1])
                                            setattr(weapons[id], resists_name[k], resists_value)
                
                # get dc tag from sellback     
                for index, slb in enumerate(weapons[id].sellback):
                    if "Dragon Coins" in slb:
                        weapons[id].append_attr("dc", True)
                    else:
                        weapons[id].append_attr("dc", False)

                # debug

                print(name)
                print(url, id, "\n")

                # print all object attributes in a new line
                for l in vars(weapons[id]):
                    print(l, ":", vars(weapons[id])[l])

                print("+++++++++++++++++++++++++++++++++++++")
        
        # export object attr to csv

        # since attribute column order will be random, get the base attributes in the correct order from first object
        base_attributes = list(vars(objects[0]).keys())

        # extracting additional attributes dynamically  
        additional_attributes = set()
        
        for obj in objects:
            additional_attributes.update(set(vars(obj).keys()) - set(base_attributes))

        # writing to csv
        with open('test2.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=base_attributes + list(additional_attributes))
            writer.writeheader()

            for obj in objects:
                writer.writerow(vars(obj))

if __name__ == "__main__":
    process = CrawlerProcess(settings={
        # Specify any settings if needed
        'LOG_ENABLED': False  # Disable logging if not needed
    })

    process.crawl(ForumSpider)
    process.start()

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
root.title("Object Viewer")

# Create UI elements
search_label = tk.Label(root, text="Search by Object Name:")
search_label.grid(row=0, column=0, sticky="w")

search_entry = tk.Entry(root)
search_entry.grid(row=0, column=1, sticky="we")

search_button = tk.Button(root, text="Search", command=search)
search_button.grid(row=0, column=2, sticky="w")

sort_by = tk.StringVar(root)
sort_by.set("name")  # default sorting attribute
sort_by.trace_add("write", on_sort_changed)

sort_label = tk.Label(root, text="Sort by:")
sort_label.grid(row=1, column=0, sticky="w")

sort_by_name_button = tk.Radiobutton(root, text="Name", variable=sort_by, value="name")
sort_by_name_button.grid(row=1, column=1, sticky="w")

sort_by_price_button = tk.Radiobutton(root, text="Price", variable=sort_by, value="price")
sort_by_price_button.grid(row=1, column=2, sticky="w")

sort_by_bonuses_button = tk.Radiobutton(root, text="Bonuses", variable=sort_by, value="bonuses")
sort_by_bonuses_button.grid(row=1, column=3, sticky="w")

object_listbox = tk.Listbox(root)
object_listbox.grid(row=2, column=0, columnspan=4, sticky="nsew")
object_listbox.bind("<<ListboxSelect>>", show_attributes)

name_label = tk.Label(root, text="")
name_label.grid(row=3, column=4, sticky="w")

price_label = tk.Label(root, text="")
price_label.grid(row=4, column=4, sticky="w")

bonuses_label = tk.Label(root, text="")
bonuses_label.grid(row=5, column=4, sticky="w")

update_listbox()

root.mainloop()