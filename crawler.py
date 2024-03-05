import scrapy
import csv

weapons = dict()

# filter main_list to only contain elements that are available in sub_list
def filter_message(main_list, sub_list):
    return [m for m in main_list if any(s in m for s in sub_list)]

class Weapon:
    def __init__(self):
                #  name, description, da, dc, location, price, required_items, sellback,
                #  level, damage_min, damage_max, element,
                #  strength, dexterity, intellect, charisma, luck, endurance, wisdom,
                #  melee_def, pierce_def, magic_def, block, parry, dodge, crit, bonus,

                #  rarity, item_type, damage_type):
        
        self.name = ""
        self.description = ""
        # self.da = False
        # self.dc = False
        self.location = []
        self.price = [] # array because multiple sources of the weapon
        self.required_items = []
        self.sellback = []
        self.level = 0
        self.damage_min = 0
        # self.damage_max = 0
        # self.element = ""
        # self.strength = 0
        # self.dexterity = 0
        # self.intellect = 0
        # self.charisma = 0
        # self.luck = 0
        # self.endurance = 0
        # self.wisdom = 0
        # self.melee_def = 0
        # self.pierce_def = 0
        # self.magic_def = 0
        # self.block = 0
        # self.parry = 0
        # self.dodge = 0
        # self.crit = 0
        # self.bonus = 0
        # self.rarity = 0
        # self.item_type = ""
        # self.damage_type = ""

    def add_info(self, name, description):
        self.name = name
        self.description = description

# "Location: ", "Price: ", "Required Items: ", "Sellback: ",  "Level: ", "Damage: ", "Element: ",
# "Bonuses: ", "Resists: ", "Rarity: ", "Item Type: ", "Damage Type: "
    def add_info_by_index(self, integer, value):
        if integer == 0:
            self.location.append(value)
        elif integer == 1:
            self.price.append(value)
        elif integer == 2:
            self.required_items.append(value)
        elif integer == 3:
            self.sellback.append(value)
        elif integer == 4:
            self.level = value
        # elif integer == 5:
        #     self.damage =
        
    def print_properties(self):
        print("Name:", self.name)
        print("Description:", self.description)
        print("Price:", self.price)
        print("Required Items:", self.required_items)
        print("Sellback:", self.sellback)
        print("Level:", self.level)
        print("Damage MIN:", self.damage_min)

class ForumSpider(scrapy.Spider):
    name = 'forum-spider'
    start_urls = ['https://forums2.battleon.com/f/tm.asp?m=22094733']

    # parsing A-Z page
    def parse(self, response):
        # get item path from DOM tree <td class="msg"> <a>
        az_item_path = response.xpath("//td[@class='msg']/a")[100:105]

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

        # start writing csv in mode "a" (considering moving this earlier)
        with open("blank.csv", mode="a") as csv_file:
            csv_line = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            for index, message in enumerate(message_path):
                # get current url, message index number and create object
                url = response.request.url
                url_num = url.replace("https://forums2.battleon.com/f/tm.asp?m=", "")
                obj_name = str(url_num) + "_" + str(index)
                weapons[obj_name] = Weapon()

                # get item name from <b> tag
                item_name = message.xpath("font/b/text()").getall()
                item_name = [i.encode("utf-8") for i in item_name]
                # get item description from <i> tag following <b>
                item_description = message.xpath("font/following-sibling::i[1]/text()").getall()
                item_description = [i.encode("utf-8") for i in item_description]
                # assign object properties
                weapons[obj_name].add_info(item_name, item_description)

                # get item info from main message path <td class="msg"> text and filter relevant categories
                item_info = message.xpath("text()").getall()
                categories = ["Location: ", "Price: ", "Required Items: ", "Sellback: ",  "Level: ", "Damage: ", "Element: ", "Bonuses: ", "Resists: ", "Rarity: ", "Item Type: ", "Damage Type: "]
                item_info = filter_message(item_info, categories)

                # removing the category strings and saving them into object properties

                for index, value in enumerate(item_info):
                    # iterating multiple if statements through categories[i]
                    for n in range(len(categories)): 
                        if categories[n] in value:
                            # removing category strings
                            item_info[index] = value.replace(categories[n], "")

                            # special case for damage (extracting min and max dmg)
                            if n == 5:
                                min_dmg = item_info[index].split("-")[0]
                                

                            # saving properly formatted value to object property
                            else:
                                weapons[obj_name].add_info_by_index(n, item_info[index])

                # for index, value in enumerate(item_info)[0:6]:
                #     # Price
                #     if categories[1] in value:
                #         item_info[index] = value.replace(categories[1], "")
                #         weapons[obj_name].add_info_by_index(1, item_info[index])


                            

                print("+++++++++++++++++++++++++++++++++++++")
                print(url)
                weapons[obj_name].print_properties()
                print("------")
                print(item_info)


                csv_line.writerow(item_info)
                print("+++++++++++++++++++++++++++++++++++++")
