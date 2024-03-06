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

stats_list = ["STR", "DEX", "INT", "CHA", "LUK", "END", "WIS",
              "Melee Def", "Pierce Def", "Magic Def", "Block", "Parry", "Dodge", "Crit", "Bonus"]
stats_attr = ["strength", "dexterity", "intellect", "charisma", "luck", "endurance", "wisdom",
              "melee_def", "pierce_def", "magic_def", "block", "parry", "dodge", "crit", "bonus"]

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
        
        self.name = ""
        self.description = ""
        self.location = []
        self.price = [] # array because multiple sources of the weapon
        self.required_items = []
        self.sellback = []
        self.level = 0
        self.element = ""
        self.damage_min = 0
        self.damage_max = 0

        self.bonuses = []
        self.strength = 0
        self.dexterity = 0
        self.intellect = 0
        self.charisma = 0
        self.luck = 0
        self.endurance = 0
        self.wisdom = 0
        self.melee_def = 0
        self.pierce_def = 0
        self.magic_def = 0
        self.block = 0
        self.parry = 0
        self.dodge = 0
        self.crit = 0
        self.bonus = 0

        self.resists = []
        self.rarity = 0
        self.item_type = ""
        self.damage_type = ""

        self.special = False
        self.special_name = ""
        self.special_activation = ""
        self.special_damage = ""
        self.special_effect = ""
        self.special_element = ""
        self.special_damage_type = ""
        self.special_rate = ""
        # self.da = False
        # self.dc = False

    def append_attr(self, attr, value):
        self.__dict__[attr].append(value)

    def add_name_description(self, name, description):
        self.name = name
        self.description = description

    def print_properties(self):
        print("Name:", self.name)
        print("Description:", self.description)
        print("Location:", self.location)
        print("Price:", self.price)
        print("Required Items:", self.required_items)
        print("Sellback:", self.sellback)
        print("Level:", self.level)
        print("Damage:", self.damage_min, "-", self.damage_max)
        print("Element:", self.element)
        print("Bonuses:", self.bonuses)
        print("Resists:", self.resists)
        print("Rarity:", self.rarity)
        print("Item Type:", self.item_type)
        print("Damage Type:", self.damage_type)
        
        # if self.special == True:
        print("Special Name:", self.special_name)
        print("Special Activation:", self.special_activation)
        print("Special Damage:", self.special_damage)
        print("Special Effect:", self.special_effect)
        print("Special Element:", self.special_element)
        print("Special Damage Type:", self.special_damage_type)
        print("Special Rate:", self.special_rate)

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
                
                # get item description from <i> tag following <b>
                item_description = message.xpath("font/following-sibling::i[1]/text() | b/following-sibling::i[1]/text()").getall()
                item_description = [i.encode("utf-8") for i in item_description]
                
                # if item name exists, create object (object name is url + msg index in individual item page)
                if item_name:
                    url = response.request.url
                    url_num = url.replace("https://forums2.battleon.com/f/tm.asp?m=", "")
                    obj_name = str(url_num) + "_" + str(index)
                    weapons[obj_name] = Weapon()
                    weapons[obj_name].add_name_description(item_name, item_description)
                
                # get item info from main message path <td class="msg"> text and filter relevant categories
                item_info = message.xpath("text()").getall()
                item_info = filter_list(item_info, category_list)
                print(item_info)

                # removing the category strings and saving info into object properties
                for index, value in enumerate(item_info):
                    # iterating multiple if statements through category_list[i]
                    for n in range(len(category_list)): 
                        if value.startswith(category_list[n]):
                            # removing category strings
                            item_info[index] = value.replace(category_list[n], "")

                            # special case for the first few attributes that are arrays
                            if n <= 3:
                                weapons[obj_name].append_attr(category_attr[n], item_info[index])
                            # special case for damage (extracting min and max dmg)
                            elif n == 19:
                                weapons[obj_name].damage_min = item_info[index].split("-")[0]
                                weapons[obj_name].damage_max = item_info[index].split("-")[1]
                            # for the rest of the attributes that are variables
                            else:
                                setattr(weapons[obj_name], category_attr[n], item_info[index])
                            # # special case for bonuses
                            # elif n == 7 or n == 8:
                            #     bonuses = item_info[index].split(",")
                            #     weapons[obj_name].bonuses = bonuses
                            #     print(bonuses)


                            # # special case for resists
                            # elif n == 9:
                            #     resists = item_info[index].split(",")
                            #     weapons[obj_name].resists = resists

                            # # saving properly formatted value to object property

                print("+++++++++++++++++++++++++++++++++++++")
                print(url, obj_name)
                weapons[obj_name].print_properties()
                print("------")
                # print(item_info)

                csv_line.writerow(item_info)
                print("+++++++++++++++++++++++++++++++++++++")
