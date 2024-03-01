import scrapy
import csv

def filter_message(string, substring):
    return [str for str in string if any(sub in str for sub in substring)]

class Weapon:
    def __init__(self, name, description, da, dc, location, price, required_items, sellback,
                 level, damage_min, damage_max, element,
                 strength, dexterity, intellect, charisma, luck, endurance, wisdom,
                 melee_def, pierce_def, magic_def, block, parry, dodge, crit, bonus,

                 rarity, item_type, damage_type):
        self.name = ""
        self.description = ""
        self.da = False
        self.dc = False
        self.location = ""
        self.price = 0
        self.required_items = ""
        self.sellback = 0
        self.level = 0
        self.damage_min = 0
        self.damage_max = 0
        self.element = ""
        self.strength = 0
        self.dexterity = 0
        self.intellect = 0
        self.charisma = 0
        self.luck = 0
        self.endurance = 0
        self.wisdom = 0
        self.melee_def = 0
        self.pierce_def = 0
        self.magic_def =0
        self.block = 0
        self.parry = 0
        self.dodge = 0
        self.crit = 0
        self.bonus = 0


class ForumSpider(scrapy.Spider):
    name = 'forum-spider'
    start_urls = ['https://forums2.battleon.com/f/tm.asp?m=22094733']

    def parse(self, response):
        ITEM_SELECTOR = "//td[@class='msg']/a"
        item_path = response.xpath(ITEM_SELECTOR)[0:5]

        for item in item_path:
            item_name = item.xpath("text()").get().encode("utf-8")
            item_link = item.xpath("@href").get()

            # print(item_name, item_link)
            # print("------------------------------------------")
            yield scrapy.Request(url = response.urljoin(item_link),
                                 callback = self.parse_element)
            # yield {"Name": item_name,
            #        "Link": item_link}
            # print("------------------------------------------")

    def parse_element(self, response):
        MSG_NAME = "//td[@class='msg']"
        message_path = response.xpath(MSG_NAME)

        with open("blank.csv", mode="a") as csv_file:
            csv_line = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            for message in message_path:
                item_name = message.xpath("font/b/text()").getall()
                item_name = [i.encode("utf-8") for i in item_name]

                item_description = message.xpath("font/following-sibling::i[1]/text()").getall()
                item_description = [i.encode("utf-8") for i in item_description]
                
                item_info = message.xpath("text()").getall()
                substring = ["Location:", "Price", "Required Items:", "Sellback:",  "Level:", "Damage:", "Element:", "Bonuses:", "Resists:", "Rarity:", "Item Type:", "Damage Type:"]
                item_info = filter_message(item_info, substring)

                print("+++++++++++++++++++++++++++++++++++++")
                # yield {"message": message_name}
                print(item_name)
                print(item_description)
                print(item_info)
                
                csv_line.writerow(item_info)
                print("+++++++++++++++++++++++++++++++++++++")
