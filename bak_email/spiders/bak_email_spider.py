#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Anthor: william xiao 
"""
from scrapy.spiders import Spider
from scrapy.http import Request, FormRequest
from bak_email.items import BakEmailItem


class BakEmailSipder(Spider):
	is_put = 0
	name = "bakEmail"
	start_urls = [
		''
	]

	headers = {
	"Accept": "*/*",
	"Accept-Encoding": "gzip,deflate",
	"Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
	"Connection": "keep-alive",
	"Content-Type":" application/x-www-form-urlencoded; charset=UTF-8",
	"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
	}
	def __init__(self, userName='',password='',*args, **kwargs):
		Spider.__init__(self,*args, **kwargs)
		if ((userName.replace(' ','')=='') or  (password.replace(' ','')=='')):
			print('请输入账号密码')
			self.closed('退出')
		else:
			self.userName=userName
			self.password=password

	#重写了爬虫类的方法, 实现了自定义请求, 运行成功后会调用callback回调函数
	def start_requests(self):
		return [Request("http://my.gdtel.com", 
			#meta = {'cookiejar' : 1}, 
			callback = self.post_login)]

	#FormRequeset出问题了
	def post_login(self, response):
		print 'Preparing login'
		#下面这句话用于抓取请求网页后返回网页中的_xsrf字段的文字, 用于成功提交表单
		# print __VIEWSTATE
		# print __EVENTVALIDATION
		#FormRequeset.from_response是Scrapy提供的一个函数, 用于post表单
		#登陆成功后, 会调用after_login回调函数
		return [FormRequest.from_response(response,   #"http://www.zhihu.com/login",
							#meta = {'cookiejar' : response.meta['cookiejar']},
							headers = self.headers,
							formdata = {
							'txtUserName': self.userName,
							'txtPassword': self.password
							},
							callback = self.after_login,
							dont_filter = True
							)]

	def after_login(self, response) :
		if '佛山' not in response.body:
			return [FormRequest.from_response(response,   #"http://www.zhihu.com/login",
								#meta = {'cookiejar' : response.meta['cookiejar']},
								headers = self.headers,
								callback = self.after_login,
								dont_filter = True
								)]
		else:
			return [Request("http://gdeiac-oa.gdtel.com:8081/Default.aspx",
			 #meta = {'cookiejar' : 1},
			  callback = self.after_login_two)]

	def after_login_two(self, response) :
		if '中国电信广东公司' not in response.body:
			return [FormRequest.from_response(response,
								#meta = {'cookiejar' : response.meta['cookiejar']},
								headers = self.headers,
								callback = self.after_login_two,
								dont_filter = True
								)]
		else:
			return [Request("http://hub6.gdtel.com/ep/HomePage.nsf/UserLogin?OpenForm", 
					#meta = {'cookiejar' : 1},
					callback=self.email_box_login)]
			#return [Request("http://um23.gdtel.com/mail/xiaowb.nsf/WebMailFolder?OpenForm&login&view=($Inbox)#", meta = {'cookiejar' : 1})]


	def email_box_login(self,response):
		#开启收件箱的链接
		return [Request("http://um23.gdtel.com/mail/"+self.userName+".nsf/WebMailFolder?OpenForm&login&view=($Inbox)#",
				 #meta = {'cookiejar' : 1},
				 callback=self.parse_inbox_page)]

	def parse_inbox_page(self,response):
		temp=response.xpath(u'//div[@class="pages"]/a[text()="下一页"]/@href')
		if len(temp)>0:
			temp='http://um23.gdtel.com/mail/'+self.userName+'.nsf/WebMailFolder'+temp.extract()[0]
			yield Request(temp, 
					#meta = {'cookiejar' : 1},
					callback=self.parse_inbox_page)
		for ir in response.xpath('//div[@id="FromUser"]/a/@onclick'):
			temp_str=ir.re('''\'[^\,]*\/.*\?''')[0].replace("'","").replace("?","")
			temp_str='http://um23.gdtel.com/mail/'+self.userName+'.nsf/'+temp_str
			yield Request(temp_str, 
					#meta = {'cookiejar' : 1},
					callback=self.parse_each_email)


	def parse_each_email(self,response):
		temp=response.xpath(u'//td[@class="press-text1"]/parent::tr/td[2]')
		if len(temp)>0:
			item = BakEmailItem()
			item['time'] = ''.join(temp[0].xpath('text()').extract())
			item['sendUser'] = ''.join(temp[1].xpath('text()').extract())
			item['receiveUser'] = ''.join(temp[2].css('textarea').xpath('text()').extract())
			item['copyToUser'] = ''.join(temp[3].css('textarea').xpath('text()').extract())
			item['secrectToUser'] = ''.join(temp[4].css('textarea').xpath('text()').extract())
			item['title'] = ''.join(temp[5].xpath('text()').extract())
			content=response.xpath(u'//td[@valign="top"]/table[@class="wirte-infor" and @valign="top"]/tr/td[@valign="top"]')
			item['content']=''.join(content.extract())
			#爬取附件
			#if 'A0609ECCD70C8005482579E500556CAA/C56DA60117F33C9248257EFF0010F6E1' in response.url:
			files=response.xpath('//table[@border="1" and @cellspacing="2" and @cellpadding="4"]/tr[@valign="middle"]/td[1]/a/@href').re('\/.*\?')
			# print(len(files))
			# for file in files:
			#     print file.extract()
			item['file_urls']=['http://um23.gdtel.com'+(f.replace("?","")) for f in files]
			yield item


		# for i in temp.extract():
		#     print i

	def parse(self, response):
		pass
		#print response.body
		# problem = Selector(response)
		# item = BakEmailItem()
		# item['url'] = response.url
		# item['name'] = problem.xpath('//span[@class="name"]/text()').extract()
		# print item['name']
		# item['title'] = problem.xpath('//h2[@class="zm-item-title zm-editable-content"]/text()').extract()
		# item['description'] = problem.xpath('//div[@class="zm-editable-content"]/text()').extract()
		# item['answer']= problem.xpath('//div[@class=" zm-editable-content clearfix"]/text()').extract()
		# return item
