# DFCrawler
DFcrawler is a web crawler and user interface that allows the user to view information on DragonFable's items taken from the DragonFable Encyclopedia section of the Battleon Forums.

![DFCrawler_sample](https://github.com/lattecatte/DFCrawler/assets/154484150/8110a541-269b-49f9-83dc-14c5d2376bde)

## Features
- Crawls the DragonFable Encyclopedia webpages via Scrapy.
- Saves crawled data into a database via SQLite.
- Access the database through user interface via Tkinter.
- Allows users to filter item types and sort by various stats.
- Links to the original DragonFable Encyclopedia pages of the item and other relevant information like its location and required items etc.

## Instructions
- Run weapons_crawler.py and accessories.py to update items after a game update.
- Run ui.py.
- Type in search bar to filter items based on keywords.
- Click on red item icons to filter item types.
- Click on tag icons to filter tags (clicked state = all items, unclicked state = filter out).
- Sort items by various stats/resistances.
