# Pixiv搜索界面
import os
import re
import sys
import time
import random
import urllib
import urllib3
import requests
import concurrent.futures
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class Thumbnail_Download_Thread(QThread):
    numsig = pyqtSignal(int)
    img_download_url = pyqtSignal(str)
    textsig = pyqtSignal(str)

    def __init__(self, thumbnail_urls):
        super().__init__()
        self.thumbnail_urls = thumbnail_urls
        self.num = 0

    def thumbnail_download(self, thumbnail_url):
        id = thumbnail_url.split("/")[-1].split("_")[0]  # 获取图片id
        file = path_t + id + ".jpg"  # 拼接文件路径
        img_url = "https://www.pixiv.net/artworks/" + id
        resp = requests.get(img_url, headers=headers)
        viewcount = re.search('"viewCount":(.*?),', resp.text).group(1)
        self.num += 1
        self.numsig.emit(int(self.num))
        if int(viewcount) > view:
            img_download_url = re.search('"original":"(.+?)"', resp.text).group(1)
            if os.path.isfile(file) == True:
                self.textsig.emit(f"{id}已存在,{viewcount}")
            else:
                thumbnail_src = requests.get(thumbnail_url, headers=headers)
                with open(file, "wb") as f:
                    f.write(thumbnail_src.content)
                self.textsig.emit(f"{id}已下载,{viewcount}")
            self.img_download_url.emit(str(img_download_url))
            time.sleep(random.random() + 0.5)

    def run(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            [executor.submit(self.thumbnail_download, url) for url in self.thumbnail_urls]


class Image_Download_Thread(QThread):
    textsig = pyqtSignal(str)

    def __init__(self, img_download_url):
        super().__init__()
        self.url = img_download_url
        self.id = img_download_url.split("/")[-1].split("_")[0]

    def run(self):
        file = path_i + self.id + ".jpg"
        if os.path.isfile(file) == True:
            self.textsig.emit(f"{self.id}已存在{path_i}")
        else:
            headers["referer"] = self.url
            s = requests.get(self.url, headers=headers, verify=False)
            with open(file, "wb") as f:
                f.write(s.content)
            self.textsig.emit(f"{self.id}下载至{path_i}")


class Pixiv(QDialog):
    def __init__(self):
        super().__init__()
        self.img_d_url_dict = dict()
        self.button_num = 0
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle("Pixiv_搜索")
        self.resize(1600, 1200)
        self.layout1 = QVBoxLayout()
        self.layout2 = QHBoxLayout()
        self.layout3 = QHBoxLayout()
        self.layout4 = QVBoxLayout()
        self.label1 = QLabel("搜索内容")
        self.label2 = QLabel("最低浏览量")
        self.label3 = QLabel("页码")
        self.lineedit1 = QLineEdit(target)
        self.lineedit2 = QLineEdit(str(view))
        self.spinbox1 = QSpinBox()
        self.spinbox1.setValue(page)
        self.scrollarea = QScrollArea(self)
        self.win = QWidget()
        self.grid = QGridLayout()
        self.textbrowser1 = QTextBrowser()
        self.textbrowser1.setFixedSize(1000, 200)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedSize(300, 30)
        self.button2 = QPushButton("搜索")
        self.button2.setFixedSize(150, 50)
        self.button2.clicked.connect(self.start)
        self.button3 = QPushButton("清空")
        self.button3.setFixedSize(150, 50)
        self.button3.clicked.connect(self.clear)
        self.win.setLayout(self.grid)
        self.scrollarea.setWidget(self.win)
        self.layout1.addLayout(self.layout2)
        self.layout1.addWidget(self.scrollarea)
        self.layout1.addLayout(self.layout3)
        self.layout2.addWidget(self.label1)
        self.layout2.addWidget(self.lineedit1)
        self.layout2.addWidget(self.label2)
        self.layout2.addWidget(self.lineedit2)
        self.layout2.addWidget(self.label3)
        self.layout2.addWidget(self.spinbox1)
        self.layout3.addWidget(self.textbrowser1)
        self.layout3.addLayout(self.layout4)
        self.layout4.addWidget(self.progress_bar)
        self.layout4.addWidget(self.button2)
        self.layout4.addWidget(self.button3)
        self.layout4.setAlignment(self.progress_bar, Qt.AlignCenter)
        self.layout4.setAlignment(self.button2, Qt.AlignCenter)
        self.layout4.setAlignment(self.button3, Qt.AlignCenter)
        self.setLayout(self.layout1)

    def start(self):
        global target, target_encoded, view, page, path_t, path_i
        self.scrollarea.setWidgetResizable(True)
        target = self.lineedit1.text()
        target_encoded = urllib.parse.quote(target)
        view = int(self.lineedit2.text())
        page = self.spinbox1.value()
        path_t = "D:/Pixiv_picture/" + target + "/thumbnail/"
        path_i = "D:/Pixiv_picture/" + target + "/"
        if os.path.isdir(path_t) == False:
            os.makedirs(path_t)
        if os.path.isdir(path_i) == False:
            os.mkdir(path_i)
        self.thumbnail_urls = self.get_thumbnail_urls(headers, page)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(self.thumbnail_urls))
        self.thumbnail_download_thread = Thumbnail_Download_Thread(self.thumbnail_urls)
        self.thumbnail_download_thread.numsig.connect(self.refresh_progress_bar)
        self.thumbnail_download_thread.img_download_url.connect(self.addimgbutton)
        self.thumbnail_download_thread.textsig.connect(self.append_text)
        self.thumbnail_download_thread.start()

    def get_thumbnail_urls(self, headers, page):  # 获取搜索页缩略图的url,返回url列表
        search_url = f"https://www.pixiv.net/ajax/search/artworks/{target_encoded}"
        headers["referer"] = search_url
        resp = requests.get(search_url, headers=headers, verify=False)
        thumbnail_urls = re.findall(',"url":"(.*?)",', resp.text)
        thumbnail_urls = [thumbnail_urls[i].replace("\\", "") for i in range(len(thumbnail_urls))]
        return thumbnail_urls

    def addimgbutton(self, img_download_url):
        id = img_download_url.split("/")[-1].split("_")[0]
        thumbnail = path_t + id
        self.button1 = QPushButton()
        self.button1.setIcon(QIcon(thumbnail))
        self.button1.setIconSize(QSize(250, 250))
        self.img_d_url_dict[thumbnail] = img_download_url
        self.button1.clicked.connect(lambda: self.img_download(self.img_d_url_dict[thumbnail]))
        self.grid.addWidget(self.button1, self.button_num // 5, self.button_num % 5)
        self.win.resize(1500, 250 * (self.button_num // 5 + 1))
        self.button_num += 1

    def img_download(self, img_download_url):
        self.image_download_thread = Image_Download_Thread(img_download_url)
        self.image_download_thread.textsig.connect(self.append_text)
        self.image_download_thread.start()

    def append_text(self, text):
        self.textbrowser1.append(text)

    def refresh_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def clear(self):
        self.button_num = 0
        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


if __name__ == "__main__":
    urllib3.disable_warnings()
    target = "原神"
    target_encoded = urllib.parse.quote(target)
    view = 100
    page = 1
    path_t = "D:/Pixiv_picture/" + target + "/thumbnail/"
    path_i = "D:/Pixiv_picture/" + target + "/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Cookie": "first_visit_datetime_pc=2024-06-13%2022%3A24%3A08; p_ab_id=5; p_ab_id_2=6; p_ab_d_id=1010867200; yuid_b=I2CBYEA; c_type=33; privacy_policy_notification=0; a_type=1; b_type=1; privacy_policy_agreement=7; login_ever=yes; __utmz=235335808.1726565461.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); _im_vid=01J7ZN4DCFAX51K7Y5RQ7F37AF; cc1=2024-09-22%2010%3A09%3A12; __utma=235335808.1942916407.1718285054.1726565461.1726967355.3; __utmc=235335808; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^5=gender=male=1^6=user_id=25093650=1^9=p_ab_id=5=1^10=p_ab_id_2=6=1^11=lang=zh=1; _gid=GA1.2.2097095115.1726967355; PHPSESSID=25093650_wF9x6AREHFmGhZd4dFhfrf5XrOU0KQyp; device_token=9720544955f010b03927486ef3b25b6d; _ga_MZ1NL4PHH0=GS1.1.1726967359.3.0.1726967382.0.0.0; _im_uid.3929=i.4H2kV0AuQ3WlCG2iVZDhsQ; __gads=ID=387f70eafb566c25:T=1726967405:RT=1726967405:S=ALNI_MZ21dpQjs_VVaaflpsS6D_iWHCOgA; __eoi=ID=aa4033b4e8c3122e:T=1726967405:RT=1726967405:S=AA-AfjZKgScLmAO5QywBf-ktXrDV; __bnc_pfpuid__=16vr-FbZUP3rGe8; first_visit_datetime=2024-09-22%2011%3A58%3A35; webp_available=1; _fbp=fb.1.1726973919423.49934962844327013; _lr_geo_location_state=NWT; _lr_geo_location=TW; AMZN-Token=v2FweIB6RThDVDhYUU8zNC9pdGtMQllHMDhjNUN5SXhKaEp4WGtiTm05TkQyVVF5aXRORnZsWmFSZU1TYWNmbG5pOFBFSGhVeEV4ckkxMkZsWGNDR1ZsbnVidG1XaFRYb2p2LzIyS3RCbjh4VDJVM1VtK2tYSzNDdlFjVGpKY0VXaG00a2JrdgFiaXZ4IDc3Kzk3Nys5TlNaZzc3KzlOdSsvdmUrL3ZWVWY3Nys5/w==; _im_vid=01J7ZN4DCFAX51K7Y5RQ7F37AF; _pubcid=7a1c66bd-1437-4de7-a7cd-3ea8297342b0; _pubcid_cst=zix7LPQsHA%3D%3D; _ga_3WKBFJLFCP=GS1.1.1726973918.1.0.1726974079.0.0.0; cf_clearance=dKgdWF_pQ1LTT_CKwM7WrzZR9AZjXyDHnpqCQvzT1DI-1726983729-1.2.1.1-si50A2quumlhatdowEvVkkMlY8PvkRmsdHQFjAqER8h2WsAg76OasSAFhbNCeue31P9rB3lSHmMSUwusxF2XheqMJJAaccpW2.VrMLA2mFoix3jvSr2_79Q08tBtMj8QZkQ2Xy20JTt0.eP_qxJ2XyhCEWJYiRxKTDD3YcXFYop4lVbELIIBNPgzi.uG2vdezG6dsgVsRTEkiSa_PtlG974zFlHVqe2RRAycDBFAwO48.mRtm_hVzv3I1rts4V.h22Pk6TOTHk_tW_1Ar_9D9Ibw8bjLBrCTdCRhU1HRjntOK89SswT5_gbfOjJ1hjnIA5_5yYpr.IcY_oXzIhC53.ENK.bD6Qusc6ljm400Ke0yBL8F6nm_yfZehUU6y7kr_lvZWjsg6sJ6NRuNgZjwVw; _ga_75BBYNYN9J=GS1.1.1726983730.6.0.1726983778.0.0.0; _ga=GA1.2.1784312852.1718285056; __cf_bm=m8o5BNRhfDhNPK5f..Z6fi1fw1gGb0BzAmb4WNxmV9Y-1726984680-1.0.1.1-ED4..DTN2uqP9XyAx9F5rgUvqhNAvFuFKaqKtyW6xjq4R.iXNGeoblTak1pANVrQg_M0BSnsaIu92xuye3zj9hhjOJbyQ9o12rFfxy8kkJQ",
    }
    app = QApplication(sys.argv)
    w = Pixiv()
    w.show()
    app.exec()
