import os
import sys
import chromedriver_autoinstaller
import requests
import urllib.request
import tkinter.messagebox as msgbox
import threading
import tkinter as tk
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from tkinter import *
from tkinter import filedialog
import re


# 디렉토리 설정
def ask_directory():
    global dirName
    dirName = filedialog.askdirectory()


# 파일 이름 특수문자 제거
def clean_filename(filename):
    valid_chars = r"[^<>|:\\/\?*\"\/]"
    new_filename = "".join(re.findall(valid_chars, filename))
    return new_filename


# 전체 구현 프로세스
def run():
    global dirName
    runBtn.config(state="disabled")
    prefs = {
        "profile.managed_default_content_settings.stylesheets": 2,
    }

    os.environ['WDM_RUNTIME'] = os.path.dirname(sys.executable) + os.pathsep + os.environ['PATH']
    if hasattr(sys, '_MEIPASS'):
        os.environ['WDM_LOCAL'] = sys._MEIPASS
    else:
        os.environ['WDM_LOCAL'] = os.path.dirname(os.path.abspath(__file__))

    chromedriver_autoinstaller.install()

    options = Options()
    options.add_argument('--headless')
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    driver.implicitly_wait(10)

    search = searchEntry.get()
    num = 1
    startPage = int(startEntry.get())
    endPage = int(endEntry.get())

    if not os.path.exists(search):
        if dirName:
            os.mkdir(dirName + '/' + search)
        else:
            os.mkdir(search)

    while startPage <= endPage:
        page_directory = os.path.join(search, str(startPage))
        if not os.path.exists(page_directory):
            if dirName:
                os.mkdir(os.path.join(dirName, page_directory))
            else:
                os.mkdir(page_directory)
        url = "https://www.fmkorea.com/search.php?mid=humor&search_keyword=" + search + "&search_target=title_content&page=" + str(startPage)

        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        items = soup.select(".hx")
        for item in items:

            href = item.get('href')
            php_index = href.index('.php')
            href_php = href[php_index:]
            fmLink = 'https://www.fmkorea.com/search' + href_php
            driver.get(fmLink)

            currentPage = driver.page_source
            soup2 = BeautifulSoup(currentPage, "html.parser")

            textarea = soup2.find('textarea', {'name': 'title'})
            fn, file_extension = os.path.splitext(textarea.text)
            safe_fn = clean_filename(fn)  # 폴더 구분자가 파일 이름에 포함된 경우, 대시(-)로 변경
            # print(safe_fn)
            video_tags = soup2.find_all('video')

            if video_tags and len(video_tags) <= 70:
                for video in video_tags:
                    source_tag = video.find('source')
                    if source_tag:
                        src = source_tag.get('src')
                        if src is not None:
                            src = "https:" + src
                            # 파일명은 글 제목으로 가져와야함.
                            filename = str(num) + "_" + safe_fn + ".mp4"
                            if dirName == None:
                                filepath = os.path.join(search, str(startPage), filename)
                            else:
                                filepath = os.path.join(dirName, search, str(startPage), filename)
                            try:
                                urllib.request.urlretrieve(src, filepath)
                            except urllib.error.HTTPError as e:
                                if e.code == 404:
                                    print(f"Error 404: Resource not found at {src}")
                                elif e.code == 403:
                                    print(f"Error 403: Forbidden, access denied at {src}")
                                elif e.code == 429:
                                    print(f"Error 429: Too many requests at {src}")
                                elif e.code == 503:
                                    print(f"Error 503: Service unavailable at {src}")
                                else:
                                    print(f"HTTPError downloading {src}: {e}")
                            except Exception as e:
                                print(f"Error downloading {src}: {e}")
                            else:
                                num += 1

            fmImgs = soup2.select(".highslide.highslide-move")
            if fmImgs and len(fmImgs) <= 70:
                for fmImg in fmImgs:
                    imgUrl = "https:" + fmImg.get("href")
                    filename = str(num) + "_" + safe_fn + ".jpg"
                    if dirName == None:
                        filepath = os.path.join(search, str(startPage), filename)
                    else:
                        filepath = os.path.join(dirName, search, str(startPage), filename)
                    try:
                        urllib.request.urlretrieve(imgUrl, filepath)
                    except urllib.error.HTTPError as e:
                        if e.code == 404:
                            print(f"Error 404: Resource not found at {src}")
                        elif e.code == 403:
                            print(f"Error 403: Forbidden, access denied at {src}")
                        elif e.code == 429:
                            print(f"Error 429: Too many requests at {src}")
                        elif e.code == 503:
                            print(f"Error 503: Service unavailable at {src}")
                        else:
                            print(f"HTTPError downloading {src}: {e}")
                    except Exception as e:
                        print(f"Error downloading {src}: {e}")
                    else:
                        num += 1
            else:
                pass

        startPage += 1
    runBtn.config(state="normal")
    msgbox.showinfo("Info", "작업이 완료되었습니다.")


# 값 비어있으면 에러메세지
def validate_and_run():
    searchText = searchEntry.get()
    startText = startEntry.get()
    endText = endEntry.get()

    if not searchText:
        msgbox.showerror("Error", "검색어를 입력하세요.")
        return
    if not startText:
        msgbox.showerror("Error", "시작 페이지를 입력하세요.")
        return
    if not endText:
        msgbox.showerror("Error", "종료 페이지를 입력하세요.")
        return

    # 검색어와 파일 개수가 모두 입력되면 run 함수 실행
    t = threading.Thread(target=run, daemon=True)
    t.start()


# 키 이벤트를 처리하는 함수
def on_key(event):
    if event.keysym == 'grave' and event.state & 0x00044:  # 컨트롤 + `
        searchEntry.delete(0, tk.END)  # Entry의 내용물을 삭제합니다.
        return "break"
# 메인
if __name__ == "__main__":
    dirName = None
    shift_pressed = False

    fonts = ('맑은고딕', 13, 'bold')
    window = Tk()
    window.title("Tottoria")
    window.geometry("640x360")
    window.resizable(height=False, width=False)

    searchLabel = Label(window, text="검색어", font=fonts)  # 검색어
    searchLabel.place(x=100, y=10)
    searchEntry = Entry(width=30)  # 검색어 입력창
    searchEntry.place(x=250, y=10)
    searchEntry.bind('<Key>', on_key)

    startLabel = Label(window, text="시작 페이지", font=fonts)  # 시작 페이지
    startLabel.place(x=100, y=40)
    startEntry = Entry(width=10)
    startEntry.place(x=250, y=40)

    endLabel = Label(window, text="종료 페이지", font=fonts)  # 종료 페이지
    endLabel.place(x=100, y=70)
    endEntry = Entry(width=10)
    endEntry.place(x=250, y=70)

    runBtn = Button(window, text="실행", height=3, width=20, relief="ridge", command=validate_and_run)  # 실행 버튼
    runBtn.place(x=240, y=250)

    dirBtn = Button(window, text="폴더 선택", relief="ridge", command=ask_directory)
    dirBtn.place(x=400, y=250)

    window.mainloop()
