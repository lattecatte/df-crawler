import scrapy
import csv

weapons = dict()

# sometimes the category "Bonuses:" is listed as "Stats:" on the forums
category_list = [" Resists:"]

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
        # needs a function that auto converts attr names into strings to print
        print("Name:", self.name)
        # resists
        print("Resists:", self.resists)

class ForumSpider(scrapy.Spider):
    name = 'forum-spider'
    start_urls = ['https://forums2.battleon.com/f/tm.asp?m=22094733']

    # parsing A-Z page
    def parse(self, response):
        # get item path from DOM tree <td class="msg"> <a>
        test_index = 0
        test_range = 100
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
            
        for index, message in enumerate(message_path):
            # get item name from <b> tag, sometimes the <b> tag and <font> are used interchangeably on the forums
            item_name = message.xpath("font/b/text() | b/font/text()").getall()
            item_name = [i.encode("utf-8") for i in item_name]
            
            # if item name exists, create object (object name is url + msg index in individual item page)
            if item_name:
                url = response.request.url
                url_num = url.replace("https://forums2.battleon.com/f/tm.asp?m=", "")
                obj_name = str(url_num) + "_" + str(index)
                weapons[obj_name] = Weapon()
            
            # get item info from main message path <td class="msg"> text and filter relevant categories
            item_info = message.xpath("text()").getall()
            item_info = filter_list(item_info, category_list)
            # item_info = 
            print((item_info))
            print("+++++++++++++++++++++++++++++++++++++")
