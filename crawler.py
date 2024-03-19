import scrapy
import csv
import re
import time

t_start = time.time()
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
        # self.da = False
        # self.dc = False

    def append_attr(self, attr, value):
        self.__dict__[attr].append(value)

    def add_name_description(self, name, description):
        self.name = name
        self.description = description

objects = [Weapon(link="", name="", description="", location_name=[], location_link=[], price=[],
                  required_item_name=[], required_item_link=[], required_item_quantity=[], sellback=[],
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
        test_range = 100
        az_item_path = response.xpath("//td[@class='msg']/a")#[test_index:test_index+test_range]

        for item in az_item_path:
            # get item name from <td class="msg"> <a> text
            az_item_name = item.xpath("text()").get().encode("utf-8")
            # get item url from <td class="msg"> <a href="">
            az_item_url = item.xpath("@href").get()

            # move on to parse_element
            yield scrapy.Request(url = response.urljoin(az_item_url),
                                 callback = self.parse_element)

    # parsing individual item page
    def parse_element(self, response):
        # get message path from DOM tree <td class="msg">
        message_path = response.xpath("//td[@class='msg']")
            
        for index, message in enumerate(message_path):
            # get item name from <b> tag, sometimes the <b> tag and <font> are used interchangeably on the forums
            item_name = message.xpath("font/b/text() | b/font/text()").getall()
            item_name = [i.encode("utf-8") for i in item_name]
            
            if item_name:
                # create object (object name is url + msg index in individual item page)
                item_url = response.request.url
                item_num = item_url.replace("https://forums2.battleon.com/f/tm.asp?m=", "")
                item_id = str(item_num) + "_" + str(index)
                weapons[item_id] = Weapon()
                objects.append(weapons[item_id])

                # set link
                setattr(weapons[item_id], "link", item_url)
                # set name
                setattr(weapons[item_id], "name", item_name[0])

                # get item description from <i> tag following <b>
                item_description = message.xpath("font/following-sibling::i[1]/text() | b/following-sibling::i[1]/text()").getall()
                item_description = [i.encode("utf-8") for i in item_description]
                setattr(weapons[item_id], "description", item_description[0])

                # get location names and links
                message_string = message.getall()[0]
                location_string = extract_content_between_words(message_string, "Location:", "Price:")
                
                for location in location_string:
                    location_string_trimmed = extract_content_between_words(location, 'href="', "</a>")
                    # location name
                    location_name = location_string_trimmed[0].split('">')[1]
                    weapons[item_id].append_attr("location_name", location_name)
                    # location link
                    location_link = location_string_trimmed[0].split('">')[0]
                    weapons[item_id].append_attr("location_link", location_link)
                    
                # get required item quantity, names and links
                req_string = extract_content_between_words(message_string, "Required Items:", "Sellback:")

                for index, req in enumerate(req_string):
                    # req quantity
                    clean_string = re.sub(r'<[^>]*>', '', req) # remove html tags
                    integers = re.findall(r'\b\d+\b', clean_string)
                    req_quantity = [int(num) for num in integers]
                    setattr(weapons[item_id], "required_item_quantity", req_quantity)

                    req_string_trimmed = extract_content_between_words(req, 'href="', "</a>")

                    for r in req_string_trimmed:
                        # req name
                        req_name = r.split('">')[1]
                        weapons[item_id].append_attr("required_item_name", req_name)
                        # req link
                        req_link = r.split('">')[0]
                        weapons[item_id].append_attr("required_item_link", req_link)
                    
                # get item info from main message path <td class="msg"> text and filter relevant categories
                item_info = message.xpath("text()").getall()
                item_info = filter_list(item_info, category_list)

                # removing the category strings and saving info into object attributes
                for i, info in enumerate(item_info):
                    # iterating multiple if statements through category_list[m]
                    for m in range(len(category_list)): 
                        if info.startswith(category_list[m]):
                            # removing category strings
                            item_info[i] = info.replace(category_list[m], "")

                            # special case for the first few attributes that are arrays
                            if m <= 1:
                                weapons[item_id].append_attr(category_attr[m], item_info[i])

                            # special case for damage (extracting min and max dmg)
                            elif m == 17:
                                weapons[item_id].damage_min = item_info[i].split("-")[0]
                                weapons[item_id].damage_max = item_info[i].split("-")[1]

                            # for the rest of the attributes that are variables
                            else:
                                setattr(weapons[item_id], category_attr[m], item_info[i])
                                
                                # special case for bonuses
                                if m == 4 or m == 5:
                                    item_bonuses = item_info[i].split(",")
                                    bonuses_attr = []
                    
                                    for j, stat in enumerate(item_bonuses): # stat == item_bonuses[j]
                                        if "+" in stat:
                                            bonuses_attr.append(stat.split("+")[0].strip().lower().replace(" ", "_"))
                                            stat = int(stat.split("+")[1])
                                            setattr(weapons[item_id], bonuses_attr[j], stat)
                                        elif "-" in stat:
                                            bonuses_attr.append(stat.split("-")[0].strip().lower().replace(" ", "_"))
                                            stat = -1 * int(stat.split("-")[1])
                                            setattr(weapons[item_id], bonuses_attr[j], stat)

                                # special case for resists
                                if m == 6:
                                    item_resists = item_info[i].split(",")
                                    resists_attr = []
                    
                                    for k, elem in enumerate(item_resists): # elem == item_resists[k]
                                        if "+" in elem:
                                            resists_attr.append(elem.split("+")[0].strip().lower().replace(" ", "_"))
                                            elem = int(elem.split("+")[1])
                                            setattr(weapons[item_id], resists_attr[k], elem)
                                        elif "-" in elem:
                                            resists_attr.append(elem.split("-")[0].strip().lower().replace(" ", "_"))
                                            elem = -1 * int(elem.split("-")[1])
                                            setattr(weapons[item_id], resists_attr[k], elem)
                          
                print("+++++++++++++++++++++++++++++++++++++")
                print(item_name)
                print(item_url, item_id, "\n")

                # print all object attributes in a new line
                for l in vars(weapons[item_id]):
                    print(l, ":", vars(weapons[item_id])[l])

                print("+++++++++++++++++++++++++++++++++++++")
        
        # export object attr to csv
        print("******************")

        # since attribute column order will be random, get the base attributes in the correct order from first object
        base_attributes = list(vars(objects[0]).keys())

        # extracting additional attributes dynamically  
        additional_attributes = set()
        for obj in objects:
            additional_attributes.update(set(vars(obj).keys()) - set(base_attributes))

        # writing to csv
        with open('all-weapons.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=base_attributes + list(additional_attributes))
            writer.writeheader()

            for obj in objects:
                writer.writerow(vars(obj))

t_end = time.time()
print(t_end - t_start)
                
