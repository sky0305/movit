import tkinter as tk #導入Tkinter模組
from tkinter import messagebox

import requests #pip install requests
from bs4 import BeautifulSoup #pip install beautifulsoup4

import qrcode #pip install qrcode

class basedesk():
    
    def __init__(self,master):
        self.root = master
        self.root.config(bg='skyblue')
        self.root.title('Movit')
        self.root.geometry('800x350')
        self.root.resizable(0,0)
        #透明度
        self.root.attributes("-alpha", 1)   #1~0,  1=100%  0=0%

        #置頂
        self.root.attributes("-topmost", 1) # 1 = True, 0 = False

        page0(self.root)
         


class page0():

    def __init__(self,master):
        self._master = master
        self._page0 = tk.Frame(self._master,bg='#b3d9ff')
        self._page0.pack()

        wel_label=tk.Label(self._page0,text="Welcome to Movit!", fg="white", bg="#323232",font=('Arial',25))
        wel_label.pack(pady=30)

        data_label = tk.Label(self._page0,text="您想看的電影是？ (請勿輸入錯誤名稱/縮寫，可僅輸入關鍵字)", fg="white", bg="#323232")
        data_label.pack()
        self.data_entry = tk.Entry(self._page0)
        self.data_entry.pack()

        
        time_data_label = tk.Label(self._page0,text="您想哪一天看呢？ 輸入格式：2022/05/20", fg="white", bg="#323232")
        time_data_label.pack()
        self.time_data_entry = tk.Entry(self._page0)
        self.time_data_entry.pack()


        btn=tk.Button(self._page0,text="run program",command=self.Go_page1)
        btn.pack()


    @property
    def movie_name(self):
        return self.data_entry.get()

    @property
    def time(self):
        return self.time_data_entry.get()

    
    def Go_page1(self):
        movie_name=self.movie_name

        movie_date=self.time

        movie_name=movie_name.strip().lower()
        Error=None
        if movie_date == '':
            messagebox.showerror('Error','請輸入欲觀影日期！輸入格式：2022/05/20：')
            Error=True
        elif movie_date.count('/') != 2:
            messagebox.showerror('Error','請依格式輸入觀影日期！輸入格式：2022/05/20：')
            Error=True
        elif movie_date.replace('/','').isdigit() == False:
            messagebox.showerror('Error','請年/月/日請以半形數字填寫！輸入格式：2022/05/20')
            Error=True


        if not Error:
            self._page0.destroy()
            page1(self._master,movie_name,movie_date)    

        
class page1():

    def __init__(self,master,movie_name,time):
        #捍衛戰士：獨行俠

        self._master = master
        self._page1 = tk.Frame(self._master,bg='skyblue')
        self._page1.pack()
        
        self.showbox=tk.Listbox(self._page1,width=100,bg='#34ebba')
        self.showbox.pack()


        self.back_btn=tk.Button(self._page1,text="Back to start",command=self.Go_page0)
        self.back_btn.pack()


        self.time_data_label = tk.Label(self._page1,text="請輸入您預計的觀影時間。輸入格式：09:15", fg="white", bg="#323232")
        self.time_data_label.pack()

        self.time_entry=tk.Entry(self._page1)
        self.time_entry.pack()

        self.theater_name_data_label = tk.Label(self._page1,text="您預計前往 新竹大遠百[F] 或 新竹巨城[B]", fg="white", bg="#323232")
        self.theater_name_data_label.pack()

        self.theater_name_entry=tk.Entry(self._page1)
        self.theater_name_entry.pack()

        self.query_btn=tk.Button(self._page1,text="前往產生QRcode",command=lambda:self.finalpart(movie_name,movie_date,far_all_available_time,far_leave_seats,big_all_available_time,big_leave_seats))
        self.query_btn.pack()

        #####
        movie_date=time.strip('/').split('/')
        movie_date = movie_date[0] + ' 年 ' + movie_date[1] + ' 月 ' + movie_date[2] + ' 日 '
        #####
        # 抓電影目錄(共三頁)
        menu_url = ['https://www.vscinemas.com.tw/vsweb/film/index.aspx?p=1']
        res = requests.get(menu_url[0])
        soup = BeautifulSoup(res.text, 'html.parser')
        base_url = 'https://www.vscinemas.com.tw/vsweb/film/index.aspx'
        other_page = [base_url + s.get('href') for s in soup.select('section.pagebar ul li a') if s.get('href') != None]
        [menu_url.append(other_page_url) for other_page_url in other_page if other_page_url not in set(menu_url)]
        # print(menu_url) # 三個url

        # 抓 所有電影的 中文名 & 英文名 & 對應網址
        all_movie_ch_name = []
        all_movie_en_name = []
        all_movie_url = []
        for url in menu_url:
            res = requests.get(url)
            name_soup = BeautifulSoup(res.text, 'html.parser')
            all_movie_ch_name += [h2.text.lower() for h2 in name_soup.select('h2')]
            all_movie_en_name += [h3.text.lower() for h3 in name_soup.select('section.infoArea h3')]
            all_movie_url += ['https://www.vscinemas.com.tw/vsweb/film/' + a.get('href') for a in name_soup.select('h2 a')]

        # 只有第一頁

        # 確認是哪一部電影
        movie_is_on = 0
        all_movie_url = all_movie_url * 2
        for i, name in enumerate(all_movie_ch_name + all_movie_en_name):
            if movie_name in name:
                the_movie_url = all_movie_url[i]
                movie_name = name
                movie_is_on = 1
                break  # 視情況可不用



        if movie_is_on == 0:
            messagebox.showerror('Error',"很抱歉，您所輸入的電影目前沒有在任何威秀影城上映，麻煩請Back to start再輸入一次。")
            #print('很抱歉，您所輸入的電影目前沒有在任何威秀影城上映，麻煩請再輸入一次。\n或是輸入"Exit"以終止程式。')
            #import vieshow
        else:
            movie_res = requests.get(the_movie_url)
            movie_soup = BeautifulSoup(movie_res.text, 'html.parser')
            
            # 分別抓兩影院 哪些天有上映該電影
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
                        seat_res = requests.get(seat_url, headers={'Sec-Fetch-Site': 'same-site', 'Cache-Control': 'max-age=0', 'Referer': 'https://www.vscinemas.com.tw/'})
                        seat_soup = BeautifulSoup(seat_res.text, 'html.parser')
                        far_leave_seats.append(len(seat_soup.select('div.label-info')))

            # 印出結果-大遠百
            print(movie_name.title(), movie_date, sep='  ')
            print('新竹大遠百：')
            ###
            far_time_seat=[]
            ###
            if far_the_date_have_the_movie:
                newline = ['\n' if i % 4 == 0 else '' for i, seat in enumerate(far_leave_seats, 1)]
                space = [''  if i % 4 == 0 else '  ' for i, seat in enumerate(far_leave_seats)]
                print(''.join([space[i] + far_all_available_time[i] + f'【剩餘：{far_leave_seats[i]}個座位】' + newline[i] for i in range(len(far_leave_seats))]))
                ###
                for i in range(len(far_leave_seats)):
                    far_time_seat.append((far_all_available_time[i]+ f'【剩餘：{far_leave_seats[i]}個座位】'))
                ###

            else:
                ###
                far_time_seat=['可惜了，這天新竹大遠百沒《' + movie_name + '》']
                ###
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
                        seat_res = requests.get(seat_url, headers={'Sec-Fetch-Site': 'same-site', 'Cache-Control': 'max-age=0', 'Referer': 'https://www.vscinemas.com.tw/'})
                        seat_soup = BeautifulSoup(seat_res.text, 'html.parser')
                        big_leave_seats.append(len(seat_soup.select('div.label-info')))

            # 印出結果-巨城
            print('新竹巨城：')
            ###
            big_time_seat=[]
            ###
            if big_the_date_have_the_movie:
                newline = ['\n' if i % 4 == 0 else '' for i, seat in enumerate(big_leave_seats, 1)]
                space = [''  if i % 4 == 0 else '  ' for i, seat in enumerate(big_leave_seats)]
                print(''.join([space[i] + big_all_available_time[i] + f'【剩餘：{big_leave_seats[i]}個座位】' + newline[i] for i in range(len(big_leave_seats))]))
                ###
                for i in range(len(big_leave_seats)):
                    big_time_seat.append((big_all_available_time[i]+ f'【剩餘：{big_leave_seats[i]}個座位】'))
                ###

            else:
                ###
                big_time_seat=['可惜了，這天新竹大遠百沒《' + movie_name + '》']
                ### 
                print('可惜了，這天新竹巨城沒《' + movie_name + '》。')
            
            print()

        ######UI加入結果#################################################################
        self.showbox.insert(tk.END,movie_date,'新竹大遠百：')

        try:
            for i in range(len(far_all_available_time)):
                if i%3==0:
                    try:
                        self.showbox.insert(tk.END,far_time_seat[i:i+3])
                    except IndexError:
                        self.showbox.insert(tk.END,far_time_seat[i:])
                        break
        except NameError:
            self.showbox.insert(tk.END,far_time_seat)
            far_all_available_time=None
            far_leave_seats=None
                    
        self.showbox.insert(tk.END,'新竹巨城：')

        try:
            for j in range(len(big_all_available_time)):
                if j%3==0:
                    try:
                        self.showbox.insert(tk.END,big_time_seat[j:j+3])
                    except IndexError:
                        self.showbox.insert(tk.END,big_time_seat[j:])
                        break
        except NameError:
            self.showbox.insert(tk.END,big_time_seat)
            big_all_available_time=None
            big_leave_seats =None

    def finalpart(self,movie_name,movie_date,far_all_available_time,far_leave_seats,big_all_available_time,big_leave_seats):
        movie_city =self.theater_name_entry.get().strip().lower()
        print(movie_city)
        if movie_city in ('f', 'far', '大遠百', '新竹大遠百', '遠百'):
                print()
                movie_city = '新竹大遠百威秀影城'
                print(movie_city, movie_date, sep='\t')
                print('  '.join(far_all_available_time))
                movie_time_list = far_all_available_time
                movie_seat_list = far_leave_seats
                #break
        elif movie_city in ('b', 'big', 'big city', '巨城', '新竹巨城', '巨'):
                print()
                movie_city = '新竹巨城威秀影城'
                print(movie_city, movie_date, sep='\t')
                print('  '.join(big_all_available_time))
                movie_time_list = big_all_available_time
                movie_seat_list = big_leave_seats
                #break
        else:
                print('請輸入 [F](表大遠百) 或 [B](表巨城)。')

        #movie_time = input('請輸入您預計的觀影時間。輸入格式：09:15\n觀影時間：').strip().lower()
        movie_time = self.time_entry.get().strip().lower()
        while movie_time not in set(movie_time_list):
            print(f'請輸入所選影城當日有播映 {movie_name} 的時段！')
            movie_time = input('請輸入您預計的觀影時間。輸入格式：09:15\n觀影時間：').strip().lower()
        #print()
        leave_seat = movie_seat_list[movie_time_list.index(movie_time)]

        #print()
        op = [movie_name, movie_city, movie_date, movie_time]


        ######UI端#################################################################
        self.showbox.delete(0,tk.END)
        self.showbox.insert(tk.END,'最後確認：','此次觀看電影為：' +movie_name, '此次前往影城為：' +movie_city, '此次觀影時間為：' +movie_date+movie_time)

        self.time_data_label.destroy()

        self.time_entry.destroy()

        self.theater_name_data_label.destroy()

        self.theater_name_entry.destroy()

        self.query_btn.destroy()


        qr_name_data_label = tk.Label(self._page1,text="Enter Your's QRcode name", fg="white", bg="#323232")
        qr_name_data_label.pack()

        self.qr_name_entry=tk.Entry(self._page1)
        self.qr_name_entry.pack()

        
        qr_btn=tk.Button(self._page1,text="Generate QRcode!",command=self.makeqrcode)
        qr_btn.pack()
            





    def Go_page0(self):
        self._page1.destroy()
        page0(self._master)

    def makeqrcode(self):
        data=self.showbox.get(0,tk.END)
        data=list(map(str,data))
        data_str=''
        for i in range(1,len(data)):
            data_str+=data[i]
            data_str+='\n'

        img_name=self.qr_name_entry.get()
        qr_img=qrcode.make(data_str)
        qr_img.save(f'{img_name}.png')

        
if __name__ == '__main__':
    #循環常駐主視窗
    root = tk.Tk()
    basedesk(root)
    root.mainloop()


