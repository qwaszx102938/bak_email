# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from scrapy.item import Item,Field

class BakEmailItem(Item):
	time= Field()
	sendUser=Field()
	receiveUser = Field()
	copyToUser = Field()
	secrectToUser = Field()
	title = Field()
	content=Field()
	file_urls=Field()
	files=Field()

