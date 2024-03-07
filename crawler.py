import scrapy
import csv

weapons = dict()

# sometimes the category "Bonuses:" is listed as "Stats:" on the forums
category_list = [" Location:", " Price:", " Required Items:", " Sellback:",
                 " Level:", " Element:",
                 " Bonuses:", " Stats:", " Resists:", " Rarity:", " Item Type:", " Damage Type:",
                 " Special Name:", " Special Activation:", " Special Damage:", " Special Effect:", " Special Element:", " Special Damage Type:", " Special Rate:",
                 " Damage:"]

category_attr = ["location", "price", "required_items", "sellback",
                 "level", "element",
                 "bonuses", "bonuses", "resists", "rarity", "item_type", "damage_type",
                 "special_name", "special_activation", "special_damage", "special_effect", "special_element", "special_damage_type", "special_rate"]

# filter main_list to only contain elements that are available in sub_list
def filter_list(main_list, sub_list):
    return [m for m in main_list if any(m.startswith(s) for s in sub_list)]

class Weapon:
    def __init__(self):
                #  name, description, da, dc, location, price, required_items, sellback,
                #  level, damage_min, damage_max, element,
                #  strength, dexterity, intellect, charisma, luck, endurance, wisdom,
                #  melee_def, pierce_def, magic_def, block, parry, dodge, crit, bonus,

                #  rarity, item_type, damage_type):
        
        self.location = []
        self.price = [] # array because multiple sources of the weapon
        self.required_items = []
        self.sellback = []
        # self.da = False
        # self.dc = False

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
        test_index = 114
        test_range = 2
        az_item_path = response.xpath("//td[@class='msg']/a")[test_index:test_index+test_range]

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

        # start writing csv in mode "a" (considering moving this earlier or elsewhere)
        with open("blank.csv", mode="a") as csv_file:
            csv_line = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            for index, message in enumerate(message_path):
                # get item name from <b> tag, sometimes the <b> tag and <font> are used interchangeably on the forums
                item_name = message.xpath("font/b/text() | b/font/text()").getall()
                item_name = [i.encode("utf-8") for i in item_name]
                
                # if item name exists, create object (object name is url + msg index in individual item page)
                if item_name:
                    item_url = response.request.url
                    item_num = item_url.replace("https://forums2.battleon.com/f/tm.asp?m=", "")
                    item_id = str(item_num) + "_" + str(index)
                    weapons[item_id] = Weapon()
                    setattr(weapons[item_id], "name", item_name[0])
               
                # get item description from <i> tag following <b>
                item_description = message.xpath("font/following-sibling::i[1]/text() | b/following-sibling::i[1]/text()").getall()
                item_description = [i.encode("utf-8") for i in item_description]
                setattr(weapons[item_id], "description", item_description[0])
                
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
                            if m <= 3:
                                weapons[item_id].append_attr(category_attr[m], item_info[i])

                            # special case for damage (extracting min and max dmg)
                            elif m == 19:
                                weapons[item_id].damage_min = item_info[i].split("-")[0]
                                weapons[item_id].damage_max = item_info[i].split("-")[1]

                            # for the rest of the attributes that are variables
                            else:
                                setattr(weapons[item_id], category_attr[m], item_info[i])
                                
                                # special case for bonuses
                                if m == 6 or m == 7:
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
                                if m == 8:
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
                # print all object attributes in a new line
                for l in vars(weapons[item_id]):
                    print(l, ":", vars(weapons[item_id])[l])

                print(item_url, item_id)

                csv_line.writerow(item_info)
                print("+++++++++++++++++++++++++++++++++++++")
