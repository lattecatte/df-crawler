import re
from datetime import datetime 
import inspect
import json

import scrapy
from scrapy.crawler import CrawlerProcess
import csv
import sqlite3

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

# check attribute data type in python and return acorresponding data type for sqlite
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

def save_to_database(obj):
    conn = sqlite3.connect("weapons.db")
    cursor = conn.cursor()

    # create table
    # attr_val_tuple_list = inspect.getmembers(obj.__class__, lambda a: not(inspect.isroutine(a)))
    # attr_type_str = ", ".join(f"{name} {get_sqlite_type(value)}" for name, value in attr_val_tuple_list if not name.startswith("__"))
    # print(attr_val_tuple_list)
    # print(attr_type_str)
    columns = inspect.getmembers(obj.__class__, lambda a: not(inspect.isroutine(a)))
    column_definitions = ', '.join(f'{name} {get_sqlite_type(value)}' for name, value in columns if not name.startswith('__'))
    # cursor.execute(f'CREATE TABLE IF NOT EXISTS my_table ({column_definitions})')
    print(columns)
    print("---------------------")
    print(column_definitions)

    # cursor.execute(f'CREATE TABLE IF NOT EXISTS weapons (id INTEGER PRIMARY KEY, {attr_type_str})')

    # # convert list to json
    # values = []
    # for attr, val in attr_val_tuple_list:
    #     if isinstance(val, list):
    #         values.append(json.dumps(getattr(obj, attr)))
    #     elif not attr.startswith("__"):
    #         values.append(getattr(obj, attr))

    # # insert data into table
    # cursor.execute(f"INSERT INTO weapons VALUES (NULL, {', '.join(['?'] * len(values))})", values)
    
    # conn.commit()
    # conn.close()

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
                  health=0, mana=0, immobility=0, shrink=0)]

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
        
        # # ----- export object attr to csv ----- #

        # # since attribute column order will be random, get the base attributes in the correct order from first object
        # base_attributes = list(vars(objects[0]).keys())

        # # extracting additional attributes dynamically  
        # additional_attributes = set()
        
        # for obj in objects:
        #     additional_attributes.update(set(vars(obj).keys()) - set(base_attributes))

        # # writing to csv
        # filename = "weapons-" + datetime.today().strftime('%Y-%m-%d')
        # with open(filename + ".csv", "w", newline="") as csvfile:
        #     writer = csv.DictWriter(csvfile, fieldnames=base_attributes + list(additional_attributes))
        #     writer.writeheader()

        #     for obj in objects:
        #         writer.writerow(vars(obj))

if __name__ == "__main__":
    process = CrawlerProcess(settings={
        # specify any settings if needed
        "LOG_ENABLED": False  # Disable logging if not needed
    })

    process.crawl(ForumSpider)
    process.start()

save_to_database(weapons)
# # save object attributes to database using sqlite3
# conn = sqlite3.connect("weps2.db")
# cursor = conn.cursor()

# cursor.execute('''CREATE TABLE weapons (
#                link VARCHAR,
#                name VARCHAR,
#                description VARCHAR)
#                da BOOL,
#                dm BOOL,
#                rare BOOL,
#                seasonal BOOL,
#                special_offer BOOL,
#                item_type VARCHAR,
#                damage_type VARCHAR,
#                rarity INTEGER,
#                level INTEGER,
#                damage_min INTEGER,
#                damage_max INTEGER,
#                element VARCHAR,
#                special_name VARCHAR,
#                special_activation VARCHAR,
#                special_effect VARCHAR,
#                special_damage VARCHAR,
#                special_element VARCHAR,
#                special_damage_type VARCHAR,
#                special_rate VARCHAR,
#                bonuses VARCHAR,
#                str INTEGER,
#                int INTEGER,
#                dex INTEGER,
#                end INTEGER,
#                cha INTEGER,
#                luk INTEGER,
#                wis INTEGER,
#                crit INTEGER,
#                bonus INTEGER,
#                melee_def INTEGER,
#                pierce_def INTEGER,
#                magic_def INTEGER,
#                block INTEGER,
#                parry INTEGER,
#                dodge INTEGER,
#                resists VARCHAR,
#                all INTEGER,
#                fire INTEGER,
#                water INTEGER,
#                wind INTEGER,
#                ice INTEGER,
#                stone INTEGER,
#                nature INTEGER,
#                energy INTEGER,
#                light INTEGER,
#                darkness INTEGER,
#                bacon INTEGER,
#                metal INTEGER,
#                silver INTEGER,
#                poison INTEGER,
#                disease INTEGER,
#                good INTEGER,
#                evil INTEGER,
#                ebil INTEGER,
#                fear INTEGER,
#                health INTEGER,
#                mana INTEGER,
#                immobility INTEGER,
#                shrink INTEGER''')

#             #    -- dc,
#             #    -- location_name,
#             #    -- location_link,
#             #    -- price,
#             #    -- required_item_name,
#             #    -- required_item_link,
#             #    -- required_item_quantity,
#             #    -- sellback,


# for obj in objects:
#     cursor.execute('''INSERT INTO weapons (link, name, description
#                                           da, dm, rare, seasonal, special_offer,
#                                           item_type, damage_type, rarity, level,
#                                           damage_min, damage_max, element,
#                                           special_name, special_activation, special_effect, special_damage, special_element, special_damage_type, special_rate,
#                                           bonuses, str, int, dex, end, cha, luk, wis, crit, bonus,
#                                           melee_def, pierce_def, magic_def, block, parry, dodge,
#                                           resists, all, fire, water, wind, ice, stone, nature, energy, light, darkness, bacon,
#                                           metal, silver, poison, disease, good, evil, ebil, fear, health, mana, immobility, shrink)
#                     VALUES (?, ?, ?)''', (obj.link, obj.name, obj.description,
#                                           obj.da, obj.dm, obj.rare, obj.seasonal, obj.special_offer,
#                                           obj.item_type, obj.damage_type, obj.rarity, obj.level,
#                                           obj.damage_min, obj.damage_max, obj.element,
#                                           obj.special_name, obj.special_activation, obj.special_effect, obj.special_damage, obj.special_element, obj.special_damage_type, obj.special_rate,
#                                           obj.bonuses, obj.str, obj.int, obj.dex, obj.end, obj.cha, obj.luk, obj.wis, obj.crit, obj.bonus,
#                                           obj.melee_def, obj.pierce_def, obj.magic_def, obj.block, obj.parry, obj.dodge,
#                                           obj.resists, obj.all, obj.fire, obj.water, obj.wind, obj.ice, obj.stone, obj.nature, obj.energy, obj.light, obj.darkness, obj.bacon,
#                                           obj.metal, obj.silver, obj.poison, obj.disease, obj.good, obj.evil, obj.ebil, obj.fear, obj.health, obj.mana, obj.immobility, obj.shrink))

# conn.commit()
# conn.close()