#!/usr/bin/env python2.7
#coding=utf-8
#恰逢今日金中校庆，注释以记之
#金中136

from oscToWordpress import oscToWordpress

Mytrans = oscToWordpress()

Mytrans.setFile('blogs_backup.html')#从oschina导出html文件
Mytrans.setCommentStatus(u'open')#是否开放评论
Mytrans.setAuthor(u'chliny')#作者

Mytrans.setBlogLink(u'http://myoldbloglink')#原博客地址，非必须
Mytrans.setBlogTitle(u'chliny')#原博客名称，非必须

Mytrans.trans()#开始转换


