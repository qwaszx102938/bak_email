# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pandas as pd
import os
import time 
import urllib
import shutil

class BakEmailPipeline(object):
	# @classmethod
	# def from_crawler(cls, crawler):
	#     return cls(
	#         mongo_uri=crawler.settings.get('MONGO_URI'),
	#         mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
	#     )

	def open_spider(self, spider):
		ttime='./'+time.ctime()+'_bak'
		ttime.replace(' ','_').replace(':',' ')
		if not os.path.exists(ttime):
			os.mkdir(ttime)
			os.mkdir(ttime+'/bak_files')
		self.temp_list=[]
		self.ttime=ttime

	def close_spider(self, spider):
		df=pd.DataFrame(self.temp_list,	columns=['title','sendUser',
			'receiveUser','copyToUser','secrectToUser','time','content','file_urls','files'])
		df['time']=pd.to_datetime(df['time'])
		df=df.sort(['time'],ascending=False).reset_index(drop=True)
		df.to_excel(self.ttime+'/email_bak.xlsx',encoding='gbk')
		for index in df.index:
			if not os.path.exists(self.ttime+'/bak_files/'+str(index)):
				os.mkdir(self.ttime+'/bak_files/'+str(index))
		for index,files_item in enumerate(df['files']):
			for file_item in files_item:
				f_temp=urllib.unquote((file_item['url'].split('/'))[-1])
				shutil.move(file_item['path'],self.ttime+'/bak_files/'+str(index)+'/'+f_temp)



	def process_item(self, item, spider):
		self.temp_list.append(dict(item))
		return item
