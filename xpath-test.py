import scrapy

class ForumSpider(scrapy.Spider):
    name = 'forum-spider'
    # start_urls = ['https://forums2.battleon.com/f/tm.asp?m=17643826']
    start_urls = ['https://forums2.battleon.com/f/tm.asp?m=20707418']

    def parse(self, response):
        message_path = response.xpath("//td[@class='msg']")
        message = message_path.getall()
        desc_path = message_path.xpath("b/following-sibling::node()[1][self::i]/text()")
        # da_path = message_path.xpath("font/following-sibling::text()[2] | b/following-sibling::text()[2]")
        # da_path = da_path.getall()
        print("------------------")
        print(message)
        print("++++++++++++")
        print(desc_path)
        # print(da_path)
        # print(message_path)
        # for index, msg_path in enumerate(message_path):
        #     desc_path = msg_path.xpath("font/following-sibling::i[1]/text() | b/following-sibling::i[1]/text()")
        #     print(desc_path)
        #     print("--------")
        #     da_path = desc_path.xpath("./following-sibling")
        #     print(da_path)font/following-sibling::i[1]/following-sibling::text()[2]"