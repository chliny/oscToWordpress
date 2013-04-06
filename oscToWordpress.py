#!/usr/bin/env python2.7
#coding=utf-8

import codecs
import time
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class oscToWordpress:
    
    def readFile(self,filename):
        file = codecs.open(filename,'rb','utf8') 
        content = file.read()
        patern = ur'<div class=\'blogList\'>.*?<\/body>'
        contentObj =re.search(patern,content,re.S)
        file.close()
        return contentObj.group()

    #写入新的可被wordpress导入的文件
    def writeFile(self,filename,content):
        file = codecs.open(filename,'w','utf8')
        file.write(content)
        file.close()

    #获取文章内容
    def getPost(self,content):
        patern = ur'<div class=\'content\'>.*?(<\/div>|<div class=\'commentList\'>)'
        outPut = re.search(patern,content,re.S)
        result = self.filter_tags(outPut.group())
        return result

    #获取标题
    def getTitle(self,content):
        patern = ur'<a name="blog_.*?</a>'
        titleObj = re.search(patern,content)
        title = self.filter_tags(titleObj.group())
        return title

    #获取文章发表时间
    def getPubdate(self,content):
        patern = ur'<div class=\'date\'>([^<]*)</div>'
        dateObj = re.search(patern,content)
        dateObj = re.search(ur'\uFF1A(.*)',dateObj.group(1))
        return dateObj.group(1)

    #获取标签，多个标签以,隔开
    def getTags(self,content):
        patern = ur'<div class=\'tags\'>([^<]*)</div>'
        tagsObj = re.search(patern,content)
        tagsObj = re.search(ur'\uFF1A(.*)',tagsObj.group(1))
        return tagsObj.group(1)
    
    #获取文章分类
    def getCatalog(self,content):
        patern = ur'<div class=\'catalog\'>([^<]*)</div>'
        catalogObj = re.search(patern,content)
        catalogObj = re.search(ur'\uFF1A(.*)',catalogObj.group(1))
        return catalogObj.group(1)

    #获取文章链接
    def getLink(self,content):
        patern = ur'href="([^"]*)">'
        linkObj = re.search(patern,content)
        return linkObj.group(1)

    #从文章链接获取文章Id
    def getId(self,link):
        item = re.split('/',link)
        return item[-1]
    
    #过滤html标签
    def filter_tags(self,htmlstr):
        #先过滤CDATA
        re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
        re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
        re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
        re_br=re.compile('<br\s*?/?>')#处理换行
        re_h=re.compile('</?\w+[^>]*>')#HTML标签
        re_comment=re.compile('<!--[^>]*-->')#HTML注释
        re_prevPre = re.compile('<pre[^>]*>')#代码高亮标签
        re_nexPre = re.compile('<\/pre>')
        s=re_cdata.sub('',htmlstr)#去掉CDATA
        s=re_script.sub('',s) #去掉SCRIPT
        s=re_style.sub('',s)#去掉style
        s=re_br.sub('\n',s)#将br转换为换行
        s=re_prevPre.sub('[code]',s)#将代码高亮转成code标签
        s = re_nexPre.sub('[/code]',s)#同上，处理闭标签部分
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
 
    #对所有文章进行切分
    def cutPost(self,allContent):
        patern = ur'<div class=\'blog\'>'
        contentList = re.split(patern,allContent,re.S)
        del contentList[0]
        outPut = []
        for word in contentList:
             result = {}
             result['post'] = self.getPost(word).strip() 
             result['title'] = self.getTitle(word)
             result['tags'] = self.getTags(word)
             result['link'] = self.getLink(word)
             result['id'] = self.getId(result['link'])
             result['catalog'] = self.getCatalog(word)
             result['date'] = self.getPubdate(word)
             outPut.append(result)
        return outPut

    #整合成一个完成的xml
    def toWordpress(self,contentList):
        header = self.getHeader()
        contentStr = header[:]
        for blog in contentList:
            contentStr += u'\t<item>\n'
            contentStr += u'\t\t<title>'+blog['title']+'</title>\n'
            contentStr += u'\t\t<link>'+blog['link']+'</link>\n'
            contentStr += u'\t\t<pubDate>'+blog['date']+'</pubDate>\n'
            contentStr += u'\t\t<dc:creator>'+self.author+'</dc:creator>\n'
            contentStr += u'\t\t<description></description>\n'
            contentStr += u'\t\t<content:encoded><![CDATA['+blog['post']+']]></content:encoded>\n'
            contentStr += u'\t\t<excerpt:encoded><![CDATA[]]></excerpt:encoded>\n'
            contentStr += u'\t\t<wp:post_id>'+blog['id']+'</wp:post_id>\n'
            contentStr += u'\t\t<wp:post_date>'+blog['date']+'</wp:post_date>\n'
            contentStr += u'\t\t<wp:post_date_gmt>'+blog['date']+'</wp:post_date_gmt>\n'
            contentStr += u'\t\t<wp:comment_status>'+self.comment_status+'</wp:comment_status>\n'
            contentStr += u'\t\t<wp:ping_status>open</wp:ping_status>\n'
            contentStr += u'\t\t<wp:post_name>'+blog['title']+'</wp:post_name>\n'
            contentStr += u'\t\t<wp:status>publish</wp:status>\n'
            contentStr += u'\t\t<wp:post_parent>0</wp:post_parent>\n'
            contentStr += u'\t\t<wp:menu_order>0</wp:menu_order>\n'
            contentStr += u'\t\t<wp:post_type>post</wp:post_type>\n'
            contentStr += u'\t\t<wp:post_password></wp:post_password>\n'
            contentStr += u'\t\t<wp:is_sticky>0</wp:is_sticky>\n'

            for tag in blog['tags'].split(','):
                contentStr += u'\t\t<category domain="post_tag" nicename="'+tag+'"><![CDATA['+tag+']]></category>\n'

            contentStr += u'\t\t<category domain="category" nicename="'+blog['catalog']+'"><![CDATA['+blog['catalog']+']]></category>\n'
            contentStr += u'\t\t<wp:postmeta>\n'
            contentStr += u'\t\t\t<wp:meta_key>_syntaxhighlighter_encoded</wp:meta_key>\n'
            contentStr += u'\t\t\t<wp:meta_value><![CDATA[1]]></wp:meta_value>\n'
            contentStr += u'\t\t</wp:postmeta>\n'
            contentStr += u'\t\t<wp:postmeta>\n'
            contentStr += u'\t\t\t<wp:meta_key>_edit_last</wp:meta_key>\n'
            contentStr += u'\t\t\t<wp:meta_value><![CDATA[1]]></wp:meta_value>\n'
            contentStr += u'\t\t</wp:postmeta>\n'
            contentStr += u'\t</item>\n'

        footer = self.getFooter()
        contentStr += footer

        return contentStr 

    def getHeader(self):
        header = u'<?xml version="1.0" encoding="UTF-8" ?>\n\
\n\
<rss version="2.0"\n\
\txmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"\n\
\txmlns:content="http://purl.org/rss/1.0/modules/content/"\n\
\txmlns:wfw="http://wellformedweb.org/CommentAPI/"\n\
\txmlns:dc="http://purl.org/dc/elements/1.1/"\n\
\txmlns:wp="http://wordpress.org/export/1.2/"\n\
>\n\
\n\
<channel>\n\
\t<title>'+self.blogTitle+'</title>\n\
\t<link>'+self.blogLink+'</title>\n\
\t<description></description>\n\
\t<pubDate>'+str(time.time())+'</pubDate>\n\
\t<language>zh-CN</language>\n\
\t<wp:wxr_version>1.2</wp:wxr_version>\n\
\t<wp:base_site_url>'+self.blogLink+'</wp:base_site_url>\n\
\t<wp:base_blog_url>'+self.blogLink+'</wp:base_blog_url>\n'
        return header

    def getFooter(self):
        footer = '</channel>\n</rss>'
        return footer


    def __init__(self,filename):
        allContent = self.readFile(filename)
        contentList = self.cutPost(allContent)
        wordpressContent = self.toWordpress(contentList)
        self.writeFile('wordpress'+str(time.time())+'.xml',wordpressContent)

    author = u'chliny'#作者
    comment_status = u'open'#是否开放评论
    blogTitle = u'chliny'#原博客名称
    blogLink = u'http://my.oschina.net/chliny/blog'#原博客地址


if __name__ == "__main__":
    filename = './blogs_20130325.html'
    trans = oscToWordpress(filename)

