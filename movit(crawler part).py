# MOVIT for MOVie In Time

import requests # 需先安裝requests --> pip install requests
from bs4 import BeautifulSoup # 需先安裝beautifulsoup4 --> pip install beautifulsoup4

# 確認使用者欲觀看之電影名 以及 選擇是否結束程式
movie_name = input('您想看的電影是？ (請勿輸入錯誤名稱/縮寫，可僅輸入關鍵字) \n電影名：').strip().lower()
if movie_name == 'exit':
    quit()
while movie_name == '': #排除僅輸入空白字元的input，以免後面出現程序錯誤
    movie_name = input('請輸入欲觀看電影名！請勿輸入錯誤名稱/縮寫，可僅輸入關鍵字。\n電影名：').strip().lower()

# 確認使用者預計觀影日期 以及 簡單確認格式是否正常
movie_date = input('您想哪一天看呢？ 輸入格式：2022/05/20\n觀影日期：').strip()
while movie_date == '' or movie_date.count('/') != 2 or movie_date.replace('/','').isdigit() == False:
    if movie_date == '':
        movie_date = input('請輸入欲觀影日期！輸入格式：2022/05/20\n觀影日期：').strip()
    elif movie_date.count('/') != 2:
        movie_date = input('請依格式輸入觀影日期！輸入格式：2022/05/20\n觀影日期：').strip()
    elif movie_date.replace('/','').isdigit() == False:
        movie_date = input('請年/月/日請以半形數字填寫！輸入格式：2022/05/20\n觀影日期：').strip()
# 更改收到的日期格式 2022/05/20 --> 2022 年 05 月 20 日 用於判斷電影上映日條件
movie_date = movie_date.strip('/').split('/')
movie_date = movie_date[0] + ' 年 ' + movie_date[1] + ' 月 ' + movie_date[2] + ' 日 '
print()

# 抓電影目錄(共三頁)
menu_url = ['https://www.vscinemas.com.tw/vsweb/film/index.aspx?p=1']
res = requests.get(menu_url[0])
soup = BeautifulSoup(res.text, 'html.parser')
base_url = 'https://www.vscinemas.com.tw/vsweb/film/index.aspx'
other_page = [base_url + s.get('href') for s in soup.select('section.pagebar ul li a') if s.get('href') != None]
[menu_url.append(other_page_url) for other_page_url in other_page if other_page_url not in set(menu_url)]
# print(menu_url) # 預計是三個url

# 抓 所有上映中電影的 中文名 & 英文名 & 對應網址
all_movie_ch_name = []
all_movie_en_name = []
all_movie_url = []
for url in menu_url:
    res = requests.get(url)
    name_soup = BeautifulSoup(res.text, 'html.parser')
    all_movie_ch_name += [h2.text.lower() for h2 in name_soup.select('h2')]
    all_movie_en_name += [h3.text.lower() for h3 in name_soup.select('section.infoArea h3')]
    pre_url = 'https://www.vscinemas.com.tw/vsweb/film/'
    all_movie_url += [pre_url + a.get('href') for a in name_soup.select('h2 a')]

# 確認使用者欲觀看的電影是否上映中
movie_is_on = 0
all_movie_url = all_movie_url * 2
for i, name in enumerate(all_movie_ch_name + all_movie_en_name):
    if movie_name in name:
        the_movie_url = all_movie_url[i]
        movie_name = name
        movie_is_on = 1
        break 

# 若所查電影不在上映中列表內的話，讓使用者重新輸入，意即重跑程式
if movie_is_on == 0:
    print('很抱歉，您所輸入的電影目前沒有在任何威秀影城上映，麻煩請再輸入一次。\n或是輸入"Exit"以終止程式。')
    import movit
else:
    movie_res = requests.get(the_movie_url)
    movie_soup = BeautifulSoup(movie_res.text, 'html.parser')
    
    # 分別抓兩影院 哪些天有上映該電影；
    # 以下的far是指大遠百
    # 以下的big是指巨城
    far_have_available_date = movie_soup.select('article#movieTime1_9_7 div.movieDay h4')
    big_have_available_date = movie_soup.select('article#movieTime1_9_9 div.movieDay h4')

    # 確認大遠百欲觀影日期有上映 & 那時候剩餘座位(圖)的連結
    far_the_date_have_the_movie = 0
    if far_have_available_date:
        for j, date in enumerate(far_have_available_date):
            if date.text.strip().startswith(movie_date):
                far_all_available_time = movie_soup.select('article#movieTime1_9_7 div.movieDay')[j].select('ul li')
                far_all_available_time = [time.text for time in far_all_available_time]
                far_all_available_seat_url = movie_soup.select('article#movieTime1_9_7 div.movieDay')[j].select('ul a[target="_blank"]')
                far_all_available_seat_url = [seat_url.get('href') for seat_url in far_all_available_seat_url]
                far_the_date_have_the_movie = 1
                break

        # 紀錄剩餘座位數-大遠百
        if far_the_date_have_the_movie:
            far_leave_seats = []
            for seat_url in far_all_available_seat_url:
                # 修改header以避免轉址
                seat_res = requests.get(seat_url, headers={'Sec-Fetch-Site': 'same-site', 'Cache-Control': 'max-age=0', 'Referer': 'https://www.vscinemas.com.tw/'})
                seat_soup = BeautifulSoup(seat_res.text, 'html.parser')
                far_leave_seats.append(len(seat_soup.select('div.label-info')))

    # 印出結果-大遠百
    print(movie_name.title(), movie_date, sep='  ')
    print('新竹大遠百：')
    if far_the_date_have_the_movie:
        newline = ['\n' if i % 4 == 0 else '' for i, seat in enumerate(far_leave_seats, 1)]
        space = [''  if i % 4 == 0 else '  ' for i, seat in enumerate(far_leave_seats)]
        print(''.join([space[i] + far_all_available_time[i] + f'【剩餘：{far_leave_seats[i]}個座位】' + newline[i] for i in range(len(far_leave_seats))]))
        # print(far_all_available_seat_url)
    else:
        print('可惜了，這天新竹大遠百沒《' + movie_name + '》')

    # 確認巨城欲觀影日期有上映 & 那時候剩餘座位(圖)的連結
    big_the_date_have_the_movie = 0
    if big_have_available_date:
        for k, date in enumerate(big_have_available_date):
            if date.text.strip().startswith(movie_date):
                big_all_available_time = movie_soup.select('article#movieTime1_9_9 div.movieDay')[k].select('ul li')
                big_all_available_time = [time.text for time in big_all_available_time]
                big_all_available_seat_url = movie_soup.select('article#movieTime1_9_9 div.movieDay')[k].select('ul a[target="_blank"]')
                big_all_available_seat_url = [seat_url.get('href') for seat_url in big_all_available_seat_url]
                big_the_date_have_the_movie = 1
                break

        # 紀錄剩餘座位數-大遠百
        if big_the_date_have_the_movie:
            big_leave_seats = []
            for seat_url in big_all_available_seat_url:
                # 修改header以避免轉址
                seat_res = requests.get(seat_url, headers={'Sec-Fetch-Site': 'same-site', 'Cache-Control': 'max-age=0', 'Referer': 'https://www.vscinemas.com.tw/'})
                seat_soup = BeautifulSoup(seat_res.text, 'html.parser')
                big_leave_seats.append(len(seat_soup.select('div.label-info')))

    # 印出結果-巨城
    print('新竹巨城：')
    if big_the_date_have_the_movie:
        newline = ['\n' if i % 4 == 0 else '' for i, seat in enumerate(big_leave_seats, 1)]
        space = [''  if i % 4 == 0 else '  ' for i, seat in enumerate(big_leave_seats)]
        print(''.join([space[i] + big_all_available_time[i] + f'【剩餘：{big_leave_seats[i]}個座位】' + newline[i] for i in range(len(big_leave_seats))]))
        # print(big_all_available_seat_url)
    else:
        print('可惜了，這天新竹巨城沒《' + movie_name + '》。')
    
    print()

    # 確認使用者預計前往大遠百還是巨城，並控制input內容，以保程式正常運行
    while True:
        movie_city = input('您預計前往 新竹大遠百[F] 或 新竹巨城[B]： ').strip().lower()
        if movie_city in ('f', 'far', '大遠百', '新竹大遠百', '遠百'):
            print()
            movie_city = '新竹大遠百威秀影城'
            print(movie_city, movie_date, sep='\t')
            print('  '.join(far_all_available_time))
            movie_time_list = far_all_available_time
            movie_seat_list = far_leave_seats
            break
        elif movie_city in ('b', 'big', 'big city', '巨城', '新竹巨城', '巨'):
            print()
            movie_city = '新竹巨城威秀影城'
            print(movie_city, movie_date, sep='\t')
            print('  '.join(big_all_available_time))
            movie_time_list = big_all_available_time
            movie_seat_list = big_leave_seats
            break
        else:
            print('請輸入 [F](表大遠百) 或 [B](表巨城)。')

    # 確認使用者的觀影時間，同時確認在對應的影城中是否有這個時段
    movie_time = input('請輸入您預計的觀影時間。輸入格式：09:15\n觀影時間：').strip().lower()
    while movie_time not in set(movie_time_list):
        print(f'請輸入所選影城當日有播映 {movie_name} 的時段！')
        movie_time = input('請輸入您預計的觀影時間。輸入格式：09:15\n觀影時間：').strip().lower()

    print()

    # 確認購票張數是否多於剩餘座位
    # leave_seat = movie_seat_list[movie_time_list.index(movie_time)]
    # while True:
    #     movie_peo_num = input('請問預計要購買幾張票呢？ ').strip()
    #     if int(movie_peo_num) > leave_seat:
    #         print('不好意思！剩餘座位不足，請減少同行友人再重新輸入訂購張數。')
    #     elif movie_peo_num.isdigit() == False:
    #         print('請輸入預計買票張數！請以半形數字回答。')
    #     else:
    #         break
    
    print()

    # 最後呈現並整理要交由QRcode呈現的內容
    output = [movie_name, movie_city, movie_date, movie_time]
    print('最後確認：')
    print('此次觀看電影為：' + movie_name)
    print('此次前往影城為：' + movie_city)
    print('此次觀影時間為：' + movie_date + movie_time)
    # print('此次訂購票數為：' + movie_peo_num + '張')