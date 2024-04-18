import re
from datetime import datetime 
import inspect
import scrapy
from scrapy.crawler import CrawlerProcess
import sqlite3
import json

# sometimes the category "Bonuses:" is listed as "Stats:" on the forums
category_list = [" Price:", " Sellback:", " Level:", " Element:",
                 " Bonuses:", " Stats:", " Resists:", " Rarity:", " Item Type:", " Damage Type:",
                 " Special Name:", " Special Activation:", " Special Damage:", " Special Effect:", " Special Element:", " Special Damage Type:", " Special Rate:",
                 " Damage:"]
category_attr = ["price", "sellback", "level", "element",
                 "bonuses", "bonuses", "resists", "rarity", "item_type", "damage_type",
                 "special_name", "special_activation", "special_damage", "special_effect", "special_element", "special_damage_type", "special_rate"]
weapons = dict()
objects = []
str_attr = ["link", "name", "description", "item_type", "damage_type", "element",
            "special_name", "special_activation", "special_effect", "special_damage", "special_element", "special_damage_type", "special_rate",
            "bonuses", "resists"]
int_attr = ["rarity", "level", "damage_min", "damage_max",
            "str", "int", "dex", "end", "cha", "luk", "wis", "crit", "bonus", "melee_def", "pierce_def", "magic_def", "block", "parry", "dodge",
            "all_resist", "fire", "water", "wind", "ice", "stone", "nature", "energy", "light", "darkness", "bacon",
            "metal", "silver", "poison", "disease", "good", "evil", "ebil", "fear", "health", "mana", "immobility", "shrink"]
bool_attr = ["da", "dm", "rare", "seasonal", "special_offer"]
list_attr = ["dc", "location_name", "location_link", "price", "required_item_name", "required_item_link", "required_item_quantity", "sellback"]
# extract content between two keywords
def extract_content_between_words(page, start_word, end_word):
    pattern = re.compile(r'{}(.*?){}'.format(re.escape(start_word), re.escape(end_word)), re.DOTALL)
    matches = re.findall(pattern, page)
    return matches

# filter main_list to only contain elements that are available in sub_list
def filter_list(main_list, sub_list):
    return [m for m in main_list if any(m.startswith(s) for s in sub_list)]

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
            if attr == "all":
                attr = "all_resist"
            else:
                pass
            if attr in str_attr or attr in int_attr or attr in bool_attr or attr in list_attr:
                standard_attr.append(attr)
                standard_val.append(val)
        standard_val = [x.decode("utf-8") if isinstance(x, bytes) else x for x in standard_val]
        standard_val = [json.dumps(x) if type(x) == list else x for x in standard_val]
        print("-------------")
        print(standard_attr)
        print("++++++++++++")
        print(standard_val)
        standard_attr_str = ", ".join(f"{a}" for a in standard_attr)
        question_str = ", ".join(["?"] * len(standard_attr))

        # if standard_attr_str:
        c.execute(f"INSERT INTO weapons({standard_attr_str}) VALUES({question_str})", standard_val)
        
    conn.commit()
    conn.close()

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

class ForumSpider(scrapy.Spider):
    name = 'forum-spider'
    start_urls = ['https://forums2.battleon.com/f/tm.asp?m=22094733']

    # parsing A-Z page
    def parse(self, response):
        # get item path from DOM tree <td class="msg"> <a>
        test_index = 0
        test_range = 100
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
                    if "Dragon Coins" or "N/A" in slb:
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
        
if __name__ == "__main__":
    process = CrawlerProcess(settings={
        # specify any settings if needed
        "LOG_ENABLED": False  # disable logging if not needed
    })
    process.crawl(ForumSpider)
    process.start()

save_to_database()