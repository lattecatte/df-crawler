import scrapy

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