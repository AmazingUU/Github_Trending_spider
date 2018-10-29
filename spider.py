import pymysql
import requests
from bs4 import BeautifulSoup


def get_html(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print('requests error:',str(e))

def get_content(url):
    html = get_html(url)
    soup = BeautifulSoup(html,'lxml')
    li_list = soup.find_all('li',{'class':'col-12 d-block width-full py-4 border-bottom'})
    for i in range(len(li_list)):
        title = li_list[i].find('a').text
        url = 'https://github.com' + li_list[i].find('a')['href']
        developer = title.split('/')[0].strip()
        project_name = title.split('/')[1].strip()
        desc = li_list[i].find('p',{'class':'col-9 d-inline-block text-gray m-0 pr-4'}).text.strip()
        try:
            language = li_list[i].find('span',{'itemprop':'programmingLanguage'}).text.strip()
        except:
            language = '无'
        total_star = li_list[i].find('a',{'class':'muted-link d-inline-block mr-3'}).text.strip().replace(',','')
        try:
            today_star = li_list[i].find('span',{'class':'d-inline-block float-sm-right'}).text.strip().split(' ')[0].replace(',','')
        except:
            today_star = 0
        # print('排名:{}\t作者:{}\t项目名:{}\n链接:{}\n简介:{}\n语言:{}\t总star:{}\t今日新增star:{}\n\n'.format(
        #     i + 1,developer,project_name,url,desc,language,total_star,today_star
        # ))
        data = {'ranking':i + 1,'author':developer,'project_name':project_name,'url':url,
                'description':desc,'language':language,'total_star':total_star,'today_star':today_star}
        return data

def db_connect():
    try:
        db = pymysql.connect('localhost','root','Teamo=0112','spider')
        return db
    except Exception as e:
        print('db connect fail,e:',str(e))
        return None

def save_to_db(data):
    try:
        with db.cursor() as cursor:
            sql = 'insert into spider(ranking,author,project_name,url,description,language,total_star,today_star,create_time)' \
                  'values(%s,%s,%s,%s,%s,%s,%s,%s,now())'
            cursor.execute(sql,(data['ranking'],data['author'],data['project_name'],
                                data['url'],data['description'],data['language'],
                                data['total_star'],data['today_star']))
            db.commit()
            print('insert to db success')
    except Exception as e:
        print('insert to db fail,e:',str(e))

if __name__ == '__main__':
    data = get_content('https://github.com/trending')
    db = db_connect()
    if db:
        save_to_db(data)
        db.close()
