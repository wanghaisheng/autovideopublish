#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import threading
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import AudioClip
from moviepy.editor import concatenate_videoclips,concatenate_audioclips,TextClip,CompositeVideoClip
from moviepy.video.fx.accel_decel import accel_decel
from moviepy.video.fx.blackwhite import blackwhite
from moviepy.video.fx.blink import blink
from moviepy.video.fx.colorx import colorx
from moviepy.video.fx.crop import crop
from moviepy.video.fx.even_size import even_size
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.fx.freeze import freeze
from moviepy.video.fx.freeze_region import freeze_region
from moviepy.video.fx.gamma_corr import gamma_corr
from moviepy.video.fx.headblur import headblur
from moviepy.video.fx.invert_colors import invert_colors
from moviepy.video.fx.loop import loop
from moviepy.video.fx.lum_contrast import lum_contrast
from moviepy.video.fx.make_loopable import make_loopable
from moviepy.video.fx.margin import margin
from moviepy.video.fx.mask_and import mask_and
from moviepy.video.fx.mask_color import mask_color
from moviepy.video.fx.mask_or import mask_or
from moviepy.video.fx.mirror_x import mirror_x
from moviepy.video.fx.mirror_y import mirror_y
from moviepy.video.fx.painting import painting
from moviepy.video.fx.resize import resize
from moviepy.video.fx.rotate import rotate
from moviepy.video.fx.scroll import scroll
from moviepy.video.fx.speedx import speedx
from moviepy.video.fx.supersample import supersample
from moviepy.video.fx.time_mirror import time_mirror
from moviepy.video.fx.time_symmetrize import time_symmetrize

from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_left_right import audio_left_right
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
from moviepy.audio.fx.volumex import volumex
import moviepy.audio.fx.all  as afx
import moviepy.video.fx.all as vfx
# here put the import lib
import json
import tkinter as tk

from tkinter import OptionMenu, filedialog,ttk

import os
import base64
import subprocess
import sys
import random
import os
import time
from datetime import timedelta, date,datetime
# import multiprocessing.dummy as mp
import concurrent
from glob import glob
from src.dbmanipulation import *
from src.UploadSession import *
from PIL import Image,ImageTk
import multiprocessing as mp
from src.upload import *
from src.ai_detector import AiThumbnailGenerator
from datetime import datetime,date,timedelta
import asyncio
import requests
import re
import calendar
from tsup.utils.webdriver.setupPL import checkRequirments

from easy_i18n.t import Ai18n
config = {
    "load_path": "./locales", # 指定在 /locales 下找对应的翻译 json文件
    "default_module": "global", # 指定默认的全局模块，你可以为比如用户模块，订单模块单独设置翻译，如果不指定 module 则会去全局模块查找。
}
a_i18n = Ai18n(locales=["en", "zh"], config=config)

i18labels= a_i18n.translate
window_size='1024x720'
height=720
width=1024
# after import or define a_i18n and t
# add translation dictionary manually.
# dbname = "reddit_popular"
# Open the database and make sure there is a table with appopriate indices


def url_ok(url,proxy_option=''):


    try:
        if not proxy_option=='':
            

            # proxies = {
            #    'http': 'http://proxy.example.com:8080',
            #    'https': 'http://secureproxy.example.com:8090',
            # }
            if 'http:' in proxy_option:

                proxies = {
                'http': proxy_option
                }                
            elif 'https:' in proxy_option:

                proxies = {
                'https': proxy_option,
                }                
            elif 'socks' in proxy_option:
                proxies = {
                'http': proxy_option,
                'https': proxy_option,
                }
            else:
                proxy_option='http://'
                proxies = {
                'http': proxy_option,
                'https': proxy_option,
                }            
            print('use proxy',proxy_option)
            response = requests.head(url,proxies=proxies)
            print('google access is ok use {proxy_option}')
        else:
            response = requests.head(url)
            print('we cant  access google without proxy')

    except Exception as e:
        # print(f"NOT OK: {str(e)}")
        print('we cant  access google')
        
        return False
    else:
        print('status code',response.status_code)
        if response.status_code == 200:
            print('we cant  access google')
            return True
        else:
            print(f"NOT OK: HTTP response code {response.status_code}")

            return False


def isfilenamevalid(filename):
    # print(imagename)
    invalid = '…,<>:."/\|?*!$\'\"#'

    for char in invalid:

        filename = filename.replace(char, '')
    if len(filename) > 260:
        filename = filename[:259]
    return filename


def fix_size(old_image_path, new_image_path, canvas_width=1080, canvas_height=720):
    """Edited from https://stackoverflow.com/questions/44231209/resize-rectangular-image-to-square-keeping-ratio-and-fill-background-with-black"""
    im = Image.open(old_image_path)
    x, y = im.size

    ratio = x / y
    desired_ratio = canvas_width / canvas_height

    w = max(canvas_width, x)
    h = int(w / desired_ratio)
    if h < y:
        h = y
        w = int(h * desired_ratio)

    mode = im.mode
    print(mode)
    if len(mode) == 1:  # L, 1
        new_background = (0)
    if len(mode) == 3:  # RGB
        new_background = (0, 0, 0)
    if len(mode) == 4:  # RGBA, CMYK
        new_background = (0, 0, 0, 0)
    new_im = Image.new(mode, (w, h), new_background)
    new_im.paste(im, ((w - x) // 2, (h - y) // 2))
    img = new_im.resize((canvas_width, canvas_height))
    if mode == 'RGBA':
        img = img.convert('RGB')
    img.save(new_image_path)


def load_setting():

    global setting

    if os.path.exists('latest-used-setting.txt') :
        try:
            fp = open('latest-used-setting.txt', 'r', encoding='utf-8')
            settingfile=fp.readlines()[0]
            print(i18labels("start-loading-setting", locale='en', module="g"),settingfile)

            fp = open(settingfile, 'r', encoding='utf-8')
            setting_json = fp.read()
            fp.close()
        except:
            print(i18labels("loading-default-setting", locale='en', module="g"))
            fp = open("./assets/config/demo.json", 'r', encoding='utf-8')
            setting_json = fp.read()
            fp.close()
    else:
        print(i18labels("loading-default-setting", locale='en', module="g"))
        fp = open("./assets/config/demo.json", 'r', encoding='utf-8')
        setting_json = fp.read()
        fp.close()        
    setting = json.loads(setting_json)
    return setting

def reset_gui():

    load_setting()

    # 清空表格
    # 写入数据

    prefertags.set(setting['prefertags'])
    preferdessuffix.set(setting['preferdessuffix'])
    preferdesprefix.set(setting['preferdesprefix'])

def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj
# 加载剧本

settingid=0
# 保存配置

def save_setting(dbm):
    global settingid

    try:
        proxy_option_value = proxy_option.get()
        # print(' proxy_option setting',proxy_option.get())
    except NameError:
        print('no  proxy_option,using existing setting',
              setting['proxy_option'])
        proxy_option_value = setting['proxy_option']
    try:
        firefox_profile_folder_path = firefox_profile_folder.get()
        print('firefox_profile_folder is ',firefox_profile_folder_path)
        setting['firefox_profile_folder'] = firefox_profile_folder_path

    except NameError:
        print('no new  firefox_profile_folder,using existing setting',
              setting['firefox_profile_folder'])
        setting['firefox_profile_folder'] = ''

    try:
        video_folder_path=video_folder.get()
    except NameError:
        print('no new  video_folder_path,using existing setting',
              setting['video_folder'])
        video_folder_path = setting['video_folder']
        print(video_folder_path)
    else:
        if video_folder_path:
            if os.path.exists(video_folder_path):
                setting['video_folder'] = video_folder_path
            else:
                print('we can not find this video foler',video_folder_path)
    try:
        channel_cookie_path=channel_cookie.get()
    except NameError:
        print('no new  channel_cookie_path,using existing setting',
              setting['channelcookiepath'])
        channel_cookie_path = setting['channelcookiepath']
        print(channel_cookie_path)
    else:
        if channel_cookie_path:
            if os.path.exists(channel_cookie_path):
                setting['channelcookiepath'] = channel_cookie_path
            else:
                print('we cannot find cookie file',channel_cookie_path)
    try:
        music_folder_path=music_folder.get()
    except NameError:
        # print('no new  music_folder,using existing setting',
            #   setting['music_folder'])
        music_folder = setting['music_folder']
        # print(music_folder)
    else:
        if music_folder_path:
            setting['music_folder'] = music_folder_path

    setting['is_record_video'] = is_record_video.get()
    setting['is_open_browser'] = is_open_browser.get()    
    setting['ratio'] = ratio.get()
    setting['debug'] = is_debug.get()

    setting['dailycount'] = dailycount.get()
    setting['channelname'] = channelname.get()
    setting['start_publish_date'] = start_publish_date.get()

    setting['preferdesprefix'] = preferdesprefix.get()
    setting['preferdessuffix'] = preferdessuffix.get()
    setting['proxy_option']=proxy_option_value
    setting['prefertags'] = prefertags.get()
    setting['publishpolicy']=publishpolicy.get()    
    if setting['publishpolicy']=='': 
        setting['publishpolicy']=1
    if setting['start_publish_date']=='': 
        setting['start_publish_date']='1'
    if setting['channelname'] is None or setting['channelname']=='' :
        print('before save setting,you need input channelname')
    else:
        if setting['video_folder'] is None or setting['video_folder']=='' :
            print('before save setting,you need input video_folder')
        else:
            if os.path.exists(channel_cookie_path):

                
                newsetting=json.dumps(setting, indent=4, separators=(',', ': '))
                if os.path.exists('./assets/config/'+setting['channelname']+".json"):
                    with open('./assets/config/'+setting['channelname']+".json", 'r') as fr:
                        exitingsetting=json.loads(fr.read())

                        if ordered(setting)==ordered(exitingsetting):
                            print('no change at all')
                        else:
                            print('new change will be saved')
                        with open('./assets/config/'+setting['channelname']+".json", 'w') as f:
                            f.write(json.dumps(setting, indent=4, separators=(',', ': ')))
                        settingid=dbm.Add_New_UploadSetting_In_Db(setting)
                        print("配置保存成功",settingid)
                        with open('latest-used-setting.txt','w+') as fw:
                            fw.write('./assets/config/'+setting['channelname']+".json")                        
                else:
                    with open('./assets/config/'+setting['channelname']+".json", 'w') as f:
 
                        f.write(json.dumps(setting, indent=4, separators=(',', ': ')))                                     
                # print('当前使用的配置为：', setting)
                
                    settingid=dbm.Add_New_UploadSetting_In_Db(setting)
                    print("配置保存成功",settingid)
                    with open('latest-used-setting.txt','w+') as fw:
                        fw.write('./assets/config/'+setting['channelname']+".json")
            else:
                print('请检查cookie文件是否存在 是否损坏',channel_cookie_path)

def select_profile_folder():
    global firefox_profile_folder_path
    try:
        firefox_profile_folder_path = filedialog.askdirectory(
        parent=root, initialdir="/", title='Please select a directory')

        if os.path.exists(firefox_profile_folder_path):
            firefox_profile_folder_path = str(firefox_profile_folder_path)
            print("You chose %s" % firefox_profile_folder_path)
            firefox_profile_folder.set(firefox_profile_folder_path)
        else:
            print('please choose a valid profile folder')

            # setting['firefox_profile_folder'] = firefox_profile_folder
    except:
        print('please choose a valid profile folder')

def select_videos_folder():
    global video_folder_path
    try:
        video_folder_path = filedialog.askdirectory(
        parent=root, initialdir="/", title='Please select a directory')
        if os.path.exists(video_folder_path):
            print("You chose %s" % video_folder_path)
            video_folder.set(video_folder_path)
            setting['video_folder'] = video_folder_path
        else:
            print('please choose a valid video folder')

    except:
        print('please choose a valid video folder')
def select_musics_folder():
    global music_folder_path
    try:
        music_folder_path = filedialog.askdirectory(
        parent=root, initialdir="/", title='Please select a directory')


        if os.path.exists(music_folder_path):
            print("You chose %s" % music_folder_path)
            music_folder.set(music_folder_path)
            setting['music_folder'] = music_folder_path
        else:
            print('please choose a valid music folder')
    except:
        print('please choose a valid music folder')

docsopen=False
def docs():
    newWindow = tk.Toplevel(root)
    newWindow.geometry(window_size)

    label_helptext_setting = tk.Label(newWindow, text = i18labels("docs_str", locale='en', module="g").replace('\\n','\n'),justify='left', wraplength=450)
    label_helptext_setting.pack()
def version():
    newWindow = tk.Toplevel(root)
    newWindow.geometry(window_size)
    # print(type(i18labels("version_str", locale='en', module="g")))
    # print(str(i18labels("version_str", locale='en', module="g")))
    # if '\\n' in i18labels("version_str", locale='en', module="g"):
    #     print('111111111111')
    # print(type("First line\n and this is the second"))
    # print("First line\n and this is the second")
    # if '\n' in "First line\n and this is the second":
    #     print('22222222222')    
    label_helptext_setting = tk.Label(newWindow, 
                                      text = i18labels("version_str", locale='en', module="g").replace('\\n','\n'),
                                    #   text = "First line\n and this is the second",
                                      justify='left')
    label_helptext_setting.pack()


def contact():
    newWindow = tk.Toplevel(root)
    newWindow.geometry(window_size)
    # due to \n in json string should in \\n, so read it from json  need to convert to original 
    label_helptext_setting = tk.Label(newWindow, text = i18labels("contact_str", locale=lang, module="g").replace('\\n','\n'),anchor='e',justify='left', wraplength=450)
    label_helptext_setting.pack()

    group = tk.Label(newWindow, text =i18labels("contact_str_group", locale=lang, module="g"),anchor='e',justify='left')
    group.pack()
    path_group = './assets/feishu-chatgroup.jpg'
    img_group = Image.open(path_group)
    photo_group = ImageTk.PhotoImage(img_group)
    
    label_group = tk.Label(newWindow,image=photo_group,height=400, width=256)
    label_group.pack()

    personal = tk.Label(newWindow, text = i18labels("contact_str_personal", locale=lang, module="g").replace('\\n','\n'),anchor='e',justify='left')
    personal.pack()
    path_personal = './assets/wechat.jpg'
    img_personal = Image.open(path_personal)
    photo_personal = ImageTk.PhotoImage(img_personal)#在root实例化创建，否则会报错
    
    label_personal = tk.Label(newWindow,image=photo_personal,height=400, width=256)
    label_personal.pack()

    newWindow.mainloop()

def get_record_video():
    is_record_video=record_video.get()
def get_is_open_browser():
    is_open_browser=open_browser.get()

def install():
    # subprocess.check_call([sys.executable, "-m", "playwright ", "install"])
    subprocess.check_call(["playwright ", "install"])

def testInstallRequirements():
    print('check install requirments')
    checkRequirments()
def testNetwork():
    print('start to test network and proxy setting')
    if proxy_option.get() is None:
        url_ok('www.youtube.com')
        print('you can access google without proxy setting')
    else:
        # print('please check your proxy setting\nsocks5://127.0.0.1:1080\nhttp://proxy.example.com:8080\n222.165.235.2:80\n')
    
        print('your proxy setting is ',proxy_option.get())
        if  proxy_option.get()=='':

            print('you should provide valid your proxy setting,format as follows \nsocks5://127.0.0.1:1080\nhttp://proxy.example.com:8080\n222.165.235.2:80\n')
        else:
            if url_ok('www.youtube.com',proxy_option=proxy_option.get()):        
                print('your  proxy is running ok')
            else:
                print('you should provide valid your proxy setting,format as follows \nsocks5://127.0.0.1:1080\nhttp://proxy.example.com:8080\n222.165.235.2:80\n')
    print('netwrork and proxy test is done')
def proxyManage():
    print('import proxy list file')
    print('copy proxy list and parse')
    print('validate proxy list and save')
def accountManage():
    print('import account list file')
    print('copy account list and parse')
    print('validate account list and save')
    print('set account password choose platform')

    

def ValidateSetting():
    print('start to validate your upload settings')
    time.sleep(4)
    print('end to validate your upload settings')



def create_setting_file():
    ROOT_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )

    print('使用默认模版新建配置文件')
    default_setting_path ="./assets/config/template.json"

    global setting_file
    if os.path.exists(ROOT_DIR+os.path.sep+default_setting_path):
        print('default template exists')
        fp = open(ROOT_DIR+os.path.sep+default_setting_path, 'r', encoding='utf-8')
        setting_json = fp.read()
        fp.close()        
        setting = json.loads(setting_json)
    else:
        setting={}
    firefox_profile_folder_path = setting['firefox_profile_folder']
    firefox_profile_folder.set(firefox_profile_folder_path)

    proxy_option.set(setting['proxy_option'])
    # firefox_profile_folder.set(setting['firefox_profile_folder'])
    channel_cookie.set(setting['channelcookiepath'])
    video_folder.set(setting['video_folder'])

    prefertags.set(setting['prefertags'])
    preferdessuffix.set(setting['preferdessuffix'])
    preferdesprefix.set(setting['preferdesprefix'])
    
    dailycount.set(setting['dailycount'])
    channelname.set('hints-we use this as setting file name,you should change it')
    music_folder_path= setting['music_folder']
    publishpolicy.set(setting['publishpolicy'])
    music_folder.set(music_folder_path)
    ratio.set(setting['ratio'])    
    with open(ROOT_DIR+os.path.sep+'./assets/config/'+channelname.get()+".json", 'w') as f:

        f.write(json.dumps(setting, indent=4, separators=(',', ': ')))      

    if os.path.exists(ROOT_DIR+os.path.sep+'./assets/config/'+channelname.get()+".json"):
        print('setting file create done')

def load_setting_file():
    ROOT_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )
    default_setting_path=''
    if os.path.exists('latest-used-setting.txt') :
        try:
            fp = open('latest-used-setting.txt', 'r', encoding='utf-8')
            default_setting_path=fp.readlines()[0]
            print('读取最近保存的配置文件',default_setting_path)


        except:
            print('读取配置文件失败 加载默认模版')
            default_setting_path ="./assets/config/demo.json"

    else:
        print('读取配置文件失败 加载默认模版')
        default_setting_path ="./assets/config/demo.json"



    print('======',ROOT_DIR+os.path.sep+default_setting_path)

    global setting_file
    setting_file = filedialog.askopenfilenames(initialdir=ROOT_DIR,initialfile=ROOT_DIR+os.path.sep+default_setting_path,title="请选择该频道配置文件", filetypes=[
        ("Json", "*.json"), ("All Files", "*")])[0]
    load_setting()
    firefox_profile_folder_path = setting['firefox_profile_folder']
    firefox_profile_folder.set(firefox_profile_folder_path)

    proxy_option.set(setting['proxy_option'])
    # firefox_profile_folder.set(setting['firefox_profile_folder'])
    channel_cookie.set(setting['channelcookiepath'])
    video_folder.set(setting['video_folder'])

    prefertags.set(setting['prefertags'])
    preferdessuffix.set(setting['preferdessuffix'])
    preferdesprefix.set(setting['preferdesprefix'])
    
    dailycount.set(setting['dailycount'])
    channelname.set(setting['channelname'])
    music_folder_path= setting['music_folder']
    publishpolicy.set(setting['publishpolicy'])
    music_folder.set(music_folder_path)
    ratio.set(setting['ratio'])



def auto_gen_cookie_file():
    
    print('call tsup gen cookie api')
    
def select_cookie_file():

    global channel_cookie_path
    try:
        channel_cookie_path = filedialog.askopenfilenames(title="请选择该频道对应cookie文件", filetypes=[
            ("Json", "*.json"), ("All Files", "*")])[0]

        channel_cookie.set(channel_cookie_path)
        setting['channelcookiepath'] = channel_cookie_path
    except:
        print('please select a valid cookie json file')


# 清理残留文件

def threadusing_free_musichelper(numbers):

    using_free_music(numbers[0],numbers[1])

def using_free_music(setting,inputmp4):

    if os.path.exists(inputmp4):

        print('video exists', inputmp4)
    else:
        print('video not found')
    try:
        music_folder =setting['music_folder']
    except:
        music_folder='assets/freemusic'

    else:

        music_folder = setting['music_folder']
    if os.path.exists(music_folder):
        print('there are free music folder',music_folder)
    else:
        print('choose valid free music folder',music_folder)

    freemusic = []

    for ext in ('*.mp3', '*.wav','*.wma','*.ogg','*.aac'):
        freemusic.extend(glob(os.path.join(music_folder, ext)))
        
    if len(freemusic) > 0:    
        soundeffect = random.choice(freemusic)
        print('randomly choose a background music',soundeffect)
        ext = os.path.splitext(soundeffect)[1]
        videoext= os.path.splitext(inputmp4)[1]
        videofilename= os.path.splitext(inputmp4)[0]

        print('videoext',videoext)
        print('videofilename',videofilename)
        oldvideofiles=[]

        audioclip = AudioFileClip(soundeffect)
        if not os.path.exists(videofilename+'-old'+videoext):
            os.rename(inputmp4, videofilename+'-old'+videoext)
        videoclip = VideoFileClip(videofilename+'-old'+videoext)
        if audioclip.duration>videoclip.duration:
            audioclip =audioclip.subclip(0,videoclip.duration)
        else:
            audioclip = vfx.loop( audioclip, duration=videoclip.duration)
        if setting['ratio']:
            pass
        else:
            setting['ratio']=1
        # audioclip = audioclip.fx( afx.volumex, float(setting['ratio']))
        # audioclip.write_audiofile(videofilename+'.mp3')

        # audioclip = volumex(audioclip,setting['ratio'])          
        videoclip = videoclip.set_audio(audioclip)

        videoclip.write_videofile(videofilename+'.mp4', threads=0, audio=True)
        if not videoclip == None:
            print('force close clip')
            audioclip.close()

            videoclip.close()

            del audioclip 
            del videoclip 
 
            import gc 
            gc.collect()

           
        # time.sleep(2) 
        print('start cleaning old video file')
        if os.path.exists(videofilename+'-old'+videoext):
            os.remove(videofilename+'-old'+videoext)
def init_worker(mps, fps, cut):
    global memorizedPaths, filepaths, cutoff
    global DG

    print("process initializing", mp.current_process())
    memorizedPaths, filepaths, cutoff = mps, fps, cut
    DG = 1##nx.read_gml("KeggComplete.gml", relabel = True)

def changeDisplayLang(event):
    # if langchoosen.get()=='':
    
    #     langchoosen.set('zh')     
    
    # langchoosen.set(langchoosen.get())
    global lang
    lang=langchoosen.get()

    frame.destroy()
    root.title(i18labels("title", locale=lang, module="g"))        

    render(root,lang)
    print(f'switch lang to locale:{lang}')

def hiddenwatermark():
    print('add hiddenwatermark to each video for  copyright theft')
def batchchangebgmusic():

    # use all available CPUs
    # p = mp.Pool(initializer=init_worker, initargs=(memorizedPaths,
    #                                                filepaths,
    #                                                cutoff))
    folder =setting['video_folder']    
    oldvideofiles=[]
    videofiles = []

    if os.path.isdir(folder):
        print('this is a directory',folder)

        for ext in ('*.flv', '*.mp4', '*.avi'):
            videofiles.extend(glob(os.path.join(folder, ext)))
        print('detecting videos in folder',folder,videofiles)
        if len(videofiles) > 0:
            arguments=[]
            for i,f in enumerate(videofiles):
                videofilename= os.path.splitext(f)[0]
                videoext= os.path.splitext(f)[1]
                if not videofilename.endswith('-old'):
                    using_free_music(setting,f)
                    # arguments.append((setting,f)) 

            print('awaiting convert files',videofiles)                                                   
            # degreelist = range(100000) ##
    #         for _ in p.imap_unordered(threadusing_free_musichelper, arguments, chunksize=500):
    #             pass
    # p.close()
    # p.join()


    # print('start cleaning old video files')
    # oldvideofiles=[]

    # if os.path.isdir(folder):

    #     for ext in ('*.flv', '*.mp4', '*.avi'):
    #         oldvideofiles.extend(glob(os.path.join(folder, ext)))
    #     # print('this is a directory',folder)
  
    # for f in oldvideofiles:   
    #     videofilename= os.path.splitext(f)[0]

    #     if  videofilename.endswith('-old'):
    #         print('start cleaning old video file',f)
    #         if os.path.exists(f.replace('-old','')):
    #             os.remove( f)
    print('finish cleaning old video files')
def changebgmusic():
    folder =setting['video_folder']    
    if os.path.isdir(folder):
        print('this is a directory',folder)

        videofiles = []
        for ext in ('*.flv', '*.mp4', '*.avi'):
            videofiles.extend(glob(os.path.join(folder, ext)))
        print('detecting videos in folder',folder,videofiles)
        if len(videofiles) > 0:
            # for i,f in enumerate(videofiles):

            #     videofiles.append(f)    
            print('awaiting convert files',videofiles)
            start = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                # while True:
                tasks = [using_free_music(x) for x in videofiles]
                for task, future in [(i, executor.submit(i)) for i in tasks]:
                    try:
                        # print(future.result(timeout=1))
                        print('ok')
                    except concurrent.futures.TimeoutError:
                        print("this took too long...")
            #             # task.interrupt()
            end = time.time()
            print("批量替换took {} seconds\n".format(end-start))



def b64e(s):
    return base64.b64encode(s.encode()).decode()


def autothumb():

    save_setting()
# 文件夹下是否有视频文件

# 视频文件是否有同名的图片

    try:
        video_folder_path = setting['video_folder']

    except NameError:
        print('not found fastlane folder  file')
    else:
        if video_folder_path:
            print("sure, it was defined dir.",video_folder_path)

            check_video_thumb_pair(video_folder_path,False)
        else:
            print("pls choose file or folder")
def editVideoMetas():
    print('go to web json editor to edit prepared video metas in json format')


def importVideoMetas():
    print('import prepared video metas in json format')
    global video_meta_json_path
    video_meta_json_path = filedialog.askopenfilenames(title="choose video meta json file", filetypes=[
        ("Json", "*.json"), ("All Files", "*")])[0]

    # channel_cookie.set(channel_cookie_path)
    # setting['channelcookiepath'] = channel_cookie_path

def downVideoMetas():
    print('start to down video metas json template')
    time.sleep(3)
    print('finish to down video metas json template')
    
def genVideoMetas():
    dbm=DBM('prod')
    save_setting(dbm)
# 文件夹下是否有视频文件

# 视频文件是否有同名的图片

    try:
        video_folder_path = setting['video_folder']

    except NameError:
        print('not found fastlane folder  file')
    else:
        if video_folder_path:
            if os.path.exists(video_folder_path):
                check_video_thumb_pair(dbm,video_folder_path,False)
            else:
                print("there is no defined video dir.")
        else:
            print("pls choose file or folder")
    print('save metas to json /csv excel format for later processing')
def createuploadsession(dbm):
    save_setting(dbm)
    print('load video metas to database .create upload task for each video')
# 文件夹下是否有视频文件

# 视频文件是否有同名的图片

    try:
        video_folder_path = setting['video_folder']

    except NameError:
        print('not found fastlane folder  file')
    else:
        if video_folder_path:
            if os.path.exists(video_folder_path):
                check_video_thumb_pair(dbm,video_folder_path,True)
            else:
                print("there is no defined video dir.")
        else:
            print("pls choose file or folder")

def check_video_thumb_pair(dbm,folder,session):
    # print('detecting----------',folder)

    for r, d, f in os.walk(folder):
        with os.scandir(r) as i:
            print('detecting----------',r)
            videopair=0

            for entry in i:
                if entry.is_file():
                    filename = os.path.splitext(entry.name)[0]
                    ext = os.path.splitext(entry.name)[1]
                    # print(filename,'==',ext) 

                    start_index=1
                    if ext in ('.flv', '.mp4', '.avi'):
                        videopath = os.path.join(r, entry.name)
                        count=0
                        exist_image_ext=''
                        for image_ext in ['.jpeg', '.png', '.jpg','webp']:
                            thumbpath = os.path.join(r, filename+image_ext)

                            if not os.path.exists(thumbpath):     
                                count+=1
                            else:
                                exist_image_ext=image_ext  
                        if count==len(['.jpeg', '.png', '.jpg']):
                            no=random.choice(['001','002','003'])
                            if not os.path.exists(os.path.join(r, filename+'-'+no+'.jpg')):   
                                generator = AiThumbnailGenerator(videopath)

                                thumbpath=os.path.join(r, filename+'-'+no+'.jpg')                                
                                print('generated thumbnail is',thumbpath)
                        else:
                            thubmpath=os.path.join(r,filename+exist_image_ext)
                            print('thumbnail is there.if you need create,pls delete the old one')
                        if session:
                            print( videopath,thumbpath,filename,start_index,setting['channelname'],settingid)

                            prepareuploadsession( dbm,videopath,thumbpath,filename,start_index,setting['channelname'],settingid)
                            print('all video added to task list,you should start uploading next ')
                        else:
                            print('save video meta json to local disk')
                        start_index=start_index+1
                        videopair+=1

                if videopair==0:
                    print('we could not find any video,prefer format mp4,mkv,flv,mov')



def prepareuploadsession(dbm,videopath,thumbpath,filename,start_index,channelname,settingid):
    global uploadsessionid
    isadded,isuploaded=dbm.Query_video_status_in_channel(videopath,channelname,settingid)
              
    # filename = os.path.splitext(f)[0]
    if isadded:

        if isuploaded:
            print('task completed', isuploaded, videopath)
        else:

            print('task added but not uploaded')

    else:
        print('task not added before')
        
        tags = setting['prefertags']
        
        
        preferdesprefix = setting['preferdesprefix']
        preferdessuffix = setting['preferdessuffix']
        filename=filename.split(os.sep)[-1]
        des =filename
        if preferdesprefix:

            des=preferdesprefix+'========\n'+des
        if preferdessuffix:
            des=des+'=========\n'+preferdessuffix
        des=des[:4900]
        title = isfilenamevalid(filename)
        if len(filename) > 100:
            title = filename[:90]
        nowtime = time.time()
        videoid = b64e(filename)

        olddata = UploadSession()
        olddata.uploadSettingid=settingid
        olddata.videoid = videoid
        olddata.channelname=setting['channelname']
        publishpolicy=setting['publishpolicy']
        start_publish_date=setting['start_publish_date']
        olddata.publishpolicy=publishpolicy
        today = date.today()
        publish_date =datetime(today.year, today.month, today.day, 20, 15)

        if publishpolicy == 0:
            olddata.publish_date = publish_date
        elif publishpolicy == 1:
            olddata.publish_date = publish_date
        else:
            # Oct 19, 2021
            start_index = int(start_publish_date)+start_index
            maxdays=calendar._monthlen(today.year, today.month)

            monthoffset=int(int(start_index)/maxdays)
            startingday=today.day
            dayoffset=int(int(start_index)/int(setting['dailycount']))
            if today.day+1>maxdays:
                monthoffset=1
                startingday=today.day+1-maxdays
            publish_date =datetime(today.year, today.month+monthoffset, startingday+1+dayoffset, 20, 15)



            olddata.publish_date = publish_date
        olddata.thumbpath = thumbpath
        olddata.title= title
        olddata.des= des
        olddata.videopath = videopath
        olddata.tags= tags
        olddata.status = False
        uploadsessionid=dbm.Add_New_UploadSession_In_Db(olddata)
        print('add 1 new videos ',filename,'for upload session',uploadsessionid)



def exportcsv(dbm):
    videos=dbm.Query_undone_videos_in_channel()


def importundonefromcsv(dbm):
    videos=dbm.Query_undone_videos_in_channel()



def testupload():
    print('we got setting proxy ,',setting['proxy_option'])
    dbm=DBM('test')
    try:
        uploadsessionid
        if uploadsessionid is None:
            print('weir error',uploadsessionid)
            createuploadsession(dbm)
    except:

        print('before upload,you need create upload session first')
        createuploadsession(dbm)

    videos=dbm.Query_undone_videos_in_channel()
    print('there is ',len(videos),' video need to uploading for task ')

    if len(videos)>0:
        publicvideos=[]
        privatevideos=[]
        othervideos=[]
        if url_ok('http://www.google.com'):
            print('network is fine,there is no need for proxy ')
            setting['proxy_option']=""
            print('start browser in headless mode',is_open_browser)

        else:
            print('google can not be access ')

            print('we need for proxy ',setting['proxy_option'])   
            print('start browser in headless mode',is_open_browser,setting['proxy_option'])
        upload =  YoutubeUpload(
                root_profile_directory=setting['firefox_profile_folder'],
                proxy_option=setting['proxy_option'],
                is_open_browser=is_open_browser,
                debug=True,
                use_stealth_js=False,
                # if you want to silent background running, set watcheveryuploadstep false
                channel_cookie_path=setting['channelcookiepath'],
                username=setting['username'],
                browser_type='firefox',
                wait_policy="go next after copyright check success",
                password=setting['password'],
                is_record_video=setting['is_record_video']

                # for test purpose we need to check the video step by step ,
            )

        for video in videos:
            
            if int(video.publishpolicy)==1:
                print('add public uploading task video',video.videopath)
                
                publicvideos.append(video)
            elif int(video.publishpolicy)==0:
                print('add private uploading task video',video.videopath)

                privatevideos.append(video)
            else:
                print('add schedule uploading task video',video.videopath)

                othervideos.append(video)
        if len(publicvideos)>0:
            print('start public uploading task')
            asyncio.run(bulk_instantpublish(videos=publicvideos,upload=upload))
        if len(privatevideos)>0:
            print('start private uploading task')

            asyncio.run(bulk_privatedraft(videos=privatevideos,upload=upload))
        if len(othervideos)>0:
            print('start schedule uploading task')

            asyncio.run(bulk_scheduletopublish_specific_date(videos=othervideos,upload=upload))


def upload(mode='prod'):
    print('we got setting proxy ,',setting['proxy_option'])
    dbm=DBM('prod')
    
    try:
        uploadsessionid
        if uploadsessionid is None:
            print('weir error',uploadsessionid)
            # createuploadsession()
    except:

        print('before upload,you need create upload session first')
        # createuploadsession()

    videos=dbm.Query_undone_videos_in_channel()
    print('there is ',len(videos),' video need to uploading for task ')

    if len(videos)>0:
        publicvideos=[]
        privatevideos=[]
        othervideos=[]
        if url_ok('http://www.google.com'):
            print('network is fine,there is no need for proxy ')
            setting['proxy_option']=""
            print('start browser in headless mode',is_open_browser)

        else:
            print('google can not be access ')

            print('we need for proxy ',setting['proxy_option'])   
            print('start browser in headless mode',is_open_browser,setting['proxy_option'])
        upload =  YoutubeUpload(
                root_profile_directory=setting['firefox_profile_folder'],
                proxy_option=setting['proxy_option'],
                is_open_browser=is_open_browser,
                debug=True,
                use_stealth_js=False,
                # if you want to silent background running, set watcheveryuploadstep false
                channel_cookie_path=setting['channelcookiepath'],
                username=setting['username'],
                browser_type='firefox',
                wait_policy="go next after copyright check success",
                password=setting['password'],
                is_record_video=setting['is_record_video']

                # for test purpose we need to check the video step by step ,
            )

        for video in videos:
            
            if int(video.publishpolicy)==1:
                print('add public uploading task video',video.videopath)
                
                publicvideos.append(video)
            elif int(video.publishpolicy)==0:
                print('add private uploading task video',video.videopath)

                privatevideos.append(video)
            else:
                print('add schedule uploading task video',video.videopath)

                othervideos.append(video)
        if len(publicvideos)>0:
            print('start public uploading task')
            asyncio.run(bulk_instantpublish(videos=publicvideos,upload=upload))
        if len(privatevideos)>0:
            print('start private uploading task')

            asyncio.run(bulk_privatedraft(videos=privatevideos,upload=upload))
        if len(othervideos)>0:
            print('start schedule uploading task')

            asyncio.run(bulk_scheduletopublish_specific_date(videos=othervideos,upload=upload))


def render(root,lang):
    global frame
    frame=tk.Frame(root,width=str(width),  height=str(height),  )
    frame.pack()
    # frame.pack()  
    # 
    global is_debug,is_open_browser,is_record_video,start_publish_date,channelname,ratio,publishpolicy,prefertags,preferdesprefix,preferdessuffix,channel_cookie,proxy_option,firefox_profile_folder,video_folder,dailycount,music_folder
    is_debug = tk.BooleanVar()
    is_debug.set(setting['is_debug']) 

    is_open_browser = tk.BooleanVar()
    is_open_browser.set(setting['is_open_browser']) 
    is_record_video = tk.BooleanVar()
    is_record_video.set(setting['is_record_video'])

    prefertags = tk.StringVar()
    prefertags.set(setting['prefertags'])
    preferdesprefix = tk.StringVar()
    preferdesprefix.set(setting['preferdesprefix'])
    preferdessuffix = tk.StringVar()
    preferdessuffix.set(setting['preferdessuffix'])
    dailycount = tk.StringVar()
    dailycount.set(setting['dailycount'])
    music_folder = tk.StringVar()
    music_folder.set(setting['music_folder'])

    ratio = tk.StringVar()
    ratio.set(setting['ratio'])        
    video_folder = tk.StringVar()
    video_folder.set(setting['video_folder'])
    firefox_profile_folder = tk.StringVar()
    firefox_profile_folder.set(setting['firefox_profile_folder'])
    proxy_option = tk.StringVar()
    proxy_option.set(setting['proxy_option'])
    channelname = tk.StringVar()
    channelname.set(setting['channelname'])
    channel_cookie = tk.StringVar()
    channel_cookie.set(setting['channelcookiepath'])
    publishpolicy = tk.StringVar()
    publishpolicy.set(setting['publishpolicy'])
    start_publish_date = tk.StringVar()
    start_publish_date.set(setting['start_publish_date'])
    username = tk.StringVar()
    username.set(setting['username'])

    password = tk.StringVar()
    password.set(setting['password'])    
    

    
    
    

    l_prefertags = tk.Label(frame, text=i18labels("preferTags", locale=lang, module="g"))
    l_prefertags.place(x=10, y=50)
    el_prefertags = tk.Entry(frame, width=55, textvariable=prefertags)
    el_prefertags.place(x=150, y=50)

    l_preferdesprefix = tk.Label(frame, text=i18labels("descriptionPrefix", locale=lang, module="g"))
    l_preferdesprefix.place(x=10, y=70)
    e_preferdesprefix = tk.Entry(frame, width=55, textvariable=preferdesprefix)
    e_preferdesprefix.place(x=150, y=70)


    l_preferdessuffix = tk.Label(frame, text=i18labels("descriptionSuffix", locale=lang, module="g"))
    l_preferdessuffix.place(x=10, y=100)
    e_preferdessuffix = tk.Entry(frame, width=55, textvariable=preferdessuffix)
    e_preferdessuffix.place(x=150, y=100)


    l_music_folder = tk.Label(frame, text=i18labels("bgVideoFolder", locale=lang, module="g"))
    l_music_folder.place(in_=frame, x=10, y=130)
    
    el_music_folder = tk.Entry(frame, width=45, textvariable=music_folder)
    el_music_folder.place(x=150, y=130)
    
    b_music_folder=tk.Button(frame,text="Select",command=select_musics_folder)
    b_music_folder.place(x=580, y=130)        
    
    

    l_bgMucisVolume = tk.Label(frame, text=i18labels("bgMucisVolume", locale=lang, module="g"))
    l_bgMucisVolume.place(x=10, y=160)
    e_bgMucisVolume = tk.Entry(frame, width=55, textvariable=ratio)
    e_bgMucisVolume.place(x=150, y=160)
    
    l_publishpolicy = tk.Label(frame, text=i18labels("publishPolicy", locale=lang, module="g"))
    l_publishpolicy.place(x=10, y=180)
    e_publishpolicy = tk.Entry(frame, width=55, textvariable=publishpolicy)
    e_publishpolicy.place(x=150, y=180)


    l_dailycount = tk.Label(frame, text=i18labels("dailyVideoLimit", locale=lang, module="g"))
    l_dailycount.place(x=10, y=200)



    e_dailycount = tk.Entry(frame, width=55, textvariable=dailycount)
    e_dailycount.place(x=150, y=200)

    l_start_publish_date=tk.Label(frame, text=i18labels("offsetDays", locale=lang, module="g"))
    l_start_publish_date.place(x=10, y=220)
    e_start_publish_date = tk.Entry(frame, width=55, textvariable=start_publish_date)
    e_start_publish_date.place(x=150, y=220)

    


    l_channelname = tk.Label(frame, text=i18labels("channelName", locale=lang, module="g"))
    l_channelname.place(x=10, y=240)
    e_channelname = tk.Entry(frame, width=55, textvariable=channelname)
    e_channelname.place(x=150, y=240)

    l_video_folder = tk.Label(frame, text=i18labels("videoFolder", locale=lang, module="g"))
    l_video_folder.place(x=10, y=270)
    e_video_folder = tk.Entry(frame, width=45, textvariable=video_folder)
    e_video_folder.place(x=150, y=270)
    
    b_video_folder=tk.Button(frame,text="Select",command=lambda: threading.Thread(target=select_videos_folder).start() )
    b_video_folder.place(x=580, y=270)    
    

    l_firefox_profile_folder = tk.Label(frame, text=i18labels("profileFolder", locale=lang, module="g"))
    l_firefox_profile_folder.place(x=10, y=300)
    e_firefox_profile_folder = tk.Entry(frame, width=45, textvariable=firefox_profile_folder)
    e_firefox_profile_folder.place(x=150, y=300)


    b_firefox_profile_folder=tk.Button(frame,text="Select",command=lambda: threading.Thread(target=select_profile_folder).start() )
    b_firefox_profile_folder.place(x=580, y=300)


    l_proxy_option = tk.Label(frame, text=i18labels("proxySetting", locale=lang, module="g"))
    l_proxy_option.place(x=10, y=330)
    e_proxy_option = tk.Entry(frame, width=55, textvariable=proxy_option)
    e_proxy_option.place(x=150, y=330)

    l_channel_cookie = tk.Label(frame, text=i18labels("cookiejson", locale=lang, module="g"))
    l_channel_cookie.place(x=10, y=360)
    e_channel_cookie = tk.Entry(frame, width=35, textvariable=channel_cookie)
    e_channel_cookie.place(x=150, y=360)

    b_channel_cookie=tk.Button(frame,text="Select",command=lambda: threading.Thread(target=select_cookie_file).start() )
    b_channel_cookie.place(x=480, y=360)    
    
    
    b_channel_cookie_gen=tk.Button(frame,text="gen",command=auto_gen_cookie_file)
    b_channel_cookie_gen.place(x=550, y=360)    

    l_username = tk.Label(frame, text=i18labels("username", locale=lang, module="g"))
    l_username.place(x=10, y=390)
    e_username = tk.Entry(frame, width=55, textvariable=username)
    e_username.place(x=150, y=390)

    l_password = tk.Label(frame, text=i18labels("password", locale=lang, module="g"))
    l_password.place(x=10, y=420)
    e_password = tk.Entry(frame, width=55, textvariable=password)
    e_password.place(x=150, y=420)



    
    # b_readfist = tk.Button(frame, text="Read First", command=docs)
    # b_readfist.place(x=10, y=10)




    

    b_is_open_browser = tk.Checkbutton(frame, text=i18labels("is_open_browser", locale=lang, module="g"), variable=is_open_browser)
    b_is_open_browser.place(x=280, y=10)


    b_recordvideo = tk.Checkbutton(frame, text=i18labels("is_record_video", locale=lang, module="g"), variable=is_record_video)
    b_recordvideo.place(x=200, y=10)


    b_debug = tk.Checkbutton(frame, text=i18labels("debug", locale=lang, module="g"), variable=is_debug)
    b_debug.place(x=120, y=10)

    
    
    l_mode_1 = tk.Label(frame, text=i18labels("toolkits", locale=lang, module="g"))
    l_mode_1.place(x=10, y=int(height-250))
    
    
    b_autothumb = tk.Button(frame, text=i18labels("autothumb", locale=lang, module="g"), command=lambda: threading.Thread(target=autothumb).start())
    b_autothumb.place(x=150, y=int(height-250))
    b_batchchangebgmusic = tk.Button(frame, text=i18labels("batchchangebgmusic", locale=lang, module="g"), command=lambda: threading.Thread(target=batchchangebgmusic).start())
    b_batchchangebgmusic.place(x=350,y=int(height-250))
    
    
    b_hiddenwatermark = tk.Button(frame, text=i18labels("hiddenwatermark", locale=lang, module="g"), command=lambda: threading.Thread(target=hiddenwatermark))
    b_hiddenwatermark.place(x=500,y=int(height-250))

    
    l_mode_1 = tk.Label(frame, text=i18labels("mode1", locale=lang, module="g"))
    l_mode_1.place(x=10, y=int(height-200))

    b_editVideoMetas = tk.Button(frame, text=i18labels("editVideoMetas", locale=lang, module="g"), command=lambda: threading.Thread(target=editVideoMetas).start())
    b_editVideoMetas.place(x=150, y=int(height-200))
    
    
    
        
    l_mode_2 = tk.Label(frame, text=i18labels("mode2", locale=lang, module="g"))
    l_mode_2.place(x=10, y=int(height-150))
    
    
    
    b_gen_video_metas = tk.Button(frame, text=i18labels("genVideoMetas", locale=lang, module="g"), command=lambda: threading.Thread(target=genVideoMetas).start())
    b_gen_video_metas.place(x=150, y=int(height-150))





        
    l_mode_3 = tk.Label(frame, text=i18labels("mode3", locale=lang, module="g"))
    l_mode_3.place(x=10, y=int(height-100))
    

    b_import_video_metas = tk.Button(frame, text=i18labels("importVideoMetas", locale=lang, module="g"), command=lambda: threading.Thread(target=importVideoMetas).start())
    b_import_video_metas.place(x=150, y=int(height-100))
    
    b_down_video_metas_temp = tk.Button(frame, text=i18labels("downVideoMetas", locale=lang, module="g"), command=lambda: threading.Thread(target=downVideoMetas).start())
    b_down_video_metas_temp.place(x=350, y=int(height-100))    
    

    b_createuploadsession = tk.Button(frame, text=i18labels("createuploadsession", locale=lang, module="g"), command=lambda: threading.Thread(target=createuploadsession).start())
    b_createuploadsession.place(x=150, y=int(height-50))



    b_upload = tk.Button(frame, text=i18labels("testupload", locale=lang, module="g"), command=lambda: threading.Thread(target=testupload).start())
    b_upload.place(x=350, y=int(height-50))

    b_upload = tk.Button(frame, text=i18labels("upload", locale=lang, module="g"), command=lambda: threading.Thread(target=upload).start())
    b_upload.place(x=550, y=int(height-50))

    menubar = tk.Menu(root)
    settings = tk.Menu(menubar, tearoff=False)
    menubar.add_cascade(label=i18labels("settings", locale=lang, module="g"), menu=settings)
    # filemenu.add_command(label="选择geckodriver文件",
                        #  command=select_driver_file)
    settings.add_command(label=i18labels("load_setting_file", locale=lang, module="g"),
                            command=load_setting_file)
    settings.add_command(label=i18labels("save_setting", locale=lang, module="g"),
                            command=save_setting)
    settings.add_command(label=i18labels("create_setting_file", locale=lang, module="g"),
                            command=create_setting_file)
    
    setups = tk.Menu(menubar, tearoff=False)

    menubar.add_cascade(label=i18labels("setups", locale=lang, module="g"), menu=setups)
    setups.add_command(label=i18labels("testnetwork", locale=lang, module="g"),
                            command=lambda: threading.Thread(target=testNetwork).start())
    setups.add_command(label=i18labels("testinstall", locale=lang, module="g"),
                            command=lambda: threading.Thread(target=testInstallRequirements).start())
    
    setups.add_command(label=i18labels("testsettingok", locale=lang, module="g"),
                            command=lambda: threading.Thread(target=ValidateSetting).start())
        
    proxymanage = tk.Menu(menubar, tearoff=False)

    menubar.add_cascade(label=i18labels("proxymanage", locale=lang, module="g"), menu=proxymanage)
    proxymanage.add_command(label=i18labels("addproxy", locale=lang, module="g"),
                            command=proxyManage)


    accountmanage = tk.Menu(menubar, tearoff=False)

    menubar.add_cascade(label=i18labels("accountmanage", locale=lang, module="g"), menu=accountmanage)
    accountmanage.add_command(label=i18labels("addaccount", locale=lang, module="g"),
                            command=accountManage)
        

    # autoThumbPage = tk.Menu(menubar, tearoff=False)

    # menubar.add_cascade(label=i18labels("metamanage", locale=lang, module="g"), menu=metamanage)
    # metamanage.add_command(label=i18labels("autothumb", locale=lang, module="g"),
    #                         command=autoThumbPage)
    # metamanage.add_command(label=i18labels("autothumb", locale=lang, module="g"),
    #                         command=autoThumb)
        
        
    helpcenter = tk.Menu(menubar, tearoff=False)

    menubar.add_cascade(label=i18labels("helpcenter", locale=lang, module="g"), menu=helpcenter)
    helpcenter.add_command(label=i18labels("docs", locale=lang, module="g"),
                            command=docs)
    helpcenter.add_command(label=i18labels("contact", locale=lang, module="g"),
                            command=contact)
    helpcenter.add_command(label=i18labels("version", locale=lang, module="g"),
                            command=version)    
        

    l_chooseLang = tk.Label(frame, text=i18labels("chooseLang", locale=lang, module="g"))
    l_chooseLang.place(x=440, y=10)

    langlabel = tk.StringVar()
    global langchoosen 

    langchoosen = ttk.Combobox(root, width = 5, 
                                textvariable = langlabel)
    
    # Adding combobox drop down list
    langchoosen['values'] = ('zh', 'en')
    
    # langchoosen.place(in_=frame,  relx=0.5,  anchor=tk.E)
    langchoosen.place(in_=frame, y=10,x=480)
    langchoosen.set(lang)    
    langchoosen.bind("<<ComboboxSelected>>", changeDisplayLang)
    root.config(menu=menubar)
    return langchoosen.get()
if __name__ == '__main__':

    gui_flag = 1

    # log_file = "log.txt"


    load_setting()

    if gui_flag:
        root = tk.Tk()
        # root.geometry('1280x720')
        root.geometry(window_size)

        root.resizable(width=False, height=False)
        root.iconbitmap("assets/icon.ico")

        lang =render(root,'zh')
        root.title(i18labels("title", locale=lang, module="g"))        

        root.mainloop()
