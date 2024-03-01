import scrapy
import csv

class ForumSpider(scrapy.Spider):
    name = 'forum-spider'
    start_urls = ['https://forums2.battleon.com/f/tm.asp?m=22094733']

    def parse(self, response):
        ITEM_SELECTOR = "//td[@class='msg']/a"
        item_path = response.xpath(ITEM_SELECTOR)[0:1]

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

        with open("blank.csv", mode="w") as csv_file:
            item_info = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            for message in message_path:
                message_blob = message.xpath("text()").getall()
                filtered_message_blob = filter(lambda x : x != ",", message_blob)

                print("+++++++++++++++++++++++++++++++++++++")
                # yield {"message": message_name}
                print(filtered_message_blob)
                
                item_info.writerow(filtered_message_blob)
                print("+++++++++++++++++++++++++++++++++++++")
