#!/usr/bin/env python2.7
#coding=utf-8

import codecs
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class oscToWordpress:
    
    def readFile(self,filename):
        file = codecs.open(filename,'rb','utf8') 
        content = file.read()
        #content = content.encode('utf8')
        #content = unicode(content,'utf8')
        patern = ur'<div class=\'blogList\'>.*?<\/body>'
        contentObj =re.search(patern,content,re.S)
        file.close()
        return contentObj.group()

    def getPost(self,content):
        patern = ur'<div class=\'content\'>.*?(<\/div>|<div class=\'commentList\'>)'
        outPut = re.search(patern,content,re.S)
        result = self.filter_tags(outPut.group())
        print result
        return result

    def getTitle(self,content):
        return "!!"

    def getPubdate(self,content):
        return "!!"

    def getTags(self,content):
        return "!!"
    
    def getCatalog(self,content):
        return "!!"
    
    def filter_tags(self,htmlstr):
        #先过滤CDATA
        re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
        re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
        re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
        re_br=re.compile('<br\s*?/?>')#处理换行
        re_h=re.compile('</?\w+([^>]|^(pre))*>')#HTML标签
        re_comment=re.compile('<!--[^>]*-->')#HTML注释
        s=re_cdata.sub('',htmlstr)#去掉CDATA
        s=re_script.sub('',s) #去掉SCRIPT
        s=re_style.sub('',s)#去掉style
        s=re_br.sub('\n',s)#将br转换为换行
        s=re_h.sub('',s) #去掉HTML 标签
        s=re_comment.sub('',s)#去掉HTML注释
        #去掉多余的空行
        blank_line=re.compile('\n+')
        s=blank_line.sub('\n',s)
        s=self.replaceCharEntity(s)#替换实体
        return s
     
    ##替换常用HTML字符实体.
    #使用正常的字符替换HTML中特殊的字符实体.
    #你可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
    #@param htmlstr HTML字符串.
    def replaceCharEntity(self,htmlstr):
        CHAR_ENTITIES={'nbsp':' ','160':' ',
                        'lt':'<','60':'<',
                        'gt':'>','62':'>',
                        'amp':'&','38':'&',
                        'quot':'"','34':'"',}
        re_charEntity=re.compile(r'&#?(?P<name>\w+);')
        sz=re_charEntity.search(htmlstr)
        while sz:
            entity=sz.group()#entity全称，如&gt;
            key=sz.group('name')#去除&;后entity,如&gt;为gt
            try:
                htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1)
                sz=re_charEntity.search(htmlstr)
            except KeyError:
                #以空串代替
                htmlstr=re_charEntity.sub('',htmlstr,1)
                sz=re_charEntity.search(htmlstr)
        return htmlstr
     
    def repalce(self,s,re_exp,repl_string):
        return re_exp.sub(repl_string,s)
 
    def cutPost(self,allContent):
        patern = ur'<div class=\'blog\'>'
        contentList = re.split(patern,allContent,re.S)
        del contentList[0]
        result = {}
        outPut = []
        for word in contentList:
             result['post'] = self.getPost(word) 
             result['title'] = self.getTitle(word)
             result['tags'] = self.getTags(word)
             result['catalog'] = self.getCatalog(word)
             outPut.append(result)
        return outPut

    def __init__(self,filename):
        allContent = self.readFile(filename)
        contentList = self.cutPost(allContent)

if __name__ == "__main__":
    filename = './blogs_20130325.html'
    trans = oscToWordpress(filename)



