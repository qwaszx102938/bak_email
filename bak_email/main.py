# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

#入口函数
if __name__ == '__main__':
	userName=raw_input('insert oaAccount:')
	password=raw_input('insert password:')
	process = CrawlerProcess(get_project_settings())
# 'followall' is the name of one of the spiders of the project.
	process.crawl('bakEmail', userName=userName,password=password)
	process.start() # the script will block here until the crawling is finished
