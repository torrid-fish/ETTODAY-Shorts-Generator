from script import script_generator
from image import get_img
from audio import audio_generator, bgm_generator
from pathlib import Path
import cv2
import numpy as np
from moviepy.editor import *
from PIL import Image, ImageFont, ImageDraw
import random
import sys
import os

def generate_video_picture_api(datas):
    secs = []
    imgs = []
    effects = []
    #random.randint(0, 6)
    for item in datas:
        secs.append(item['length']/1000)
        imgs.append(item['image'])
        effects.append(random.randint(0, 6))
    effects[0] = 0
    effects[-1] = 0
    effects[1] = 0
    return imgs,secs,effects

def generate_caption_api(datas):
    captions = []
    secs = [] #[[s,e],[s,e],[s,e]]
    start_time = 0
    end_time = 0
    title = datas[0]['text']
    for item in datas:
        total_len = len(item['text'])
        temp_sentences = item['text'].split('，')  # 使用逗号分隔句子
        temp_secs = [len(i)/total_len*item['length']+0 for i in temp_sentences ]
        for temp_s in temp_secs:
            end_time = end_time + temp_s
        secs.append([round(start_time)/1000,round(end_time)/1000])
        start_time = end_time
        captions = captions + temp_sentences
    return captions, secs, title

def text_list_generator(text, x, y):
    text_list = []
    text_split = text.split("，")  # 用逗号分割文本
    base_position = (x, y)  # 初始坐标

    for i in range(len(text_split)):
        text_list.append([base_position, text_split[i]])

    return text_list

def add_caption(input_text, title, video_list, video, x_caption, y_caption, x_title, y_title, output_name):
    #text_list = text_list_generator(input_text, x_caption, y_caption)
    #print(text_list)
    text_list = input_text
    img_empty = Image.new('RGBA', (1170, 2532))                  # 產生 RGBA 空圖片
    longest_string = max(text_list, key=lambda x: len(x))
    print(longest_string)
    font_size = min((970//len(longest_string)),100)
    font_size_title = min((970//len(title)),100)
    print("check other len:",970//len(longest_string))
    print("font:",font_size)
    font = ImageFont.truetype('NotoSansTC-VariableFont_wght.ttf', font_size)    # 設定文字字體和大小
    font_title = ImageFont.truetype('NotoSansTC-VariableFont_wght.ttf', font_size_title)
    video = VideoFileClip(video).resize((1170,2532))  # 讀取影片，改變尺寸
    output_list = []      # 記錄最後要組合的影片片段
    anchor = 'mm'
    # 使用 for 迴圈，產生文字字卡
    for i in range(len(text_list)):
        img = img_empty.copy()
        draw = ImageDraw.Draw(img)
        # 计算文本的 x 坐标，使其水平居中
        background_rect = (0, 0, 1170, 250)
        draw.rectangle(background_rect, fill=(47, 40, 115))  # 背景矩形为蓝色
        background_rect = (0, 1950, 1170, 2050)
        draw.rectangle(background_rect, fill=(47, 40, 115))  # 背景矩形为蓝色
        text = text_list[i]
        text_width, text_height = draw.textsize(text, font=font)
        x_text = 585 #- len(text)/2*font_size
        x_title = 585 #- len(title)/2*120
        draw.text((x_text,y_caption), text_list[i], fill=(255,255,255), font=font, stroke_width=1, stroke_fill='white',anchor = anchor)
        draw.text((x_title,y_title), title, fill=(255,255,255), font=font_title, stroke_width=3, stroke_fill='white',anchor = anchor)
        img.save(f'text_{i}.png')
    print('1')
    # 使用 for 迴圈，合併字卡和影片
    for i in range(len(video_list)):
        clip = video.subclip(video_list[i][0], video_list[i][1])
        text = ImageClip(f'text_{i}.png', transparent=True).set_duration(video_list[i][1] - video_list[i][0])#.set_start(video_list[i][0])
        combine_clip = CompositeVideoClip([clip, text])
        output_list.append(combine_clip)
    output = concatenate_videoclips(output_list)      # 合併所有影片片段
    output.write_videofile(output_name, fps=60)  # 轉換成 gif 動畫

def merge_images(imgs,secs,effects):
    # 设置视频尺寸
    video_size = (1170, 2532)
    FPS = 60
    clips = []
    for i,image in enumerate(imgs):
        if(None):
            for i in range(int(secs[i]*FPS)):
                clips.append(ImageClip(image[:-4]+f'_{i:03d}'+'.jpg').set_duration(1/FPS))
        else:
            clips.append(ImageClip(image).set_duration(secs[i]))

    video = concatenate_videoclips(clips)
    video = video.on_color(size=video_size, color=(255, 255, 255), col_opacity=1)


    # 保存或预览视频
    video.preview()  # 这将打开一个预览窗口
    video.write_videofile("output.mp4", fps=60)  # 这将保存视频到文件

def set_punchcard_time(datas):
    time_split = []
    length_list = []
    timeStamp_list = []
    punch_set = []
    for i,item in enumerate(datas):
        length_list.append(item['length'])
    temp = [0]
    for i in range(len(length_list)):
        t = temp[i] + length_list[i]
        temp.append(t)
    length_list = temp

    for i,item in enumerate(datas):

        if (item['timeStamps']!=None):
            punch_set+=item["keywords"]
        #print(item['timeStamps'])
        temp = [(x + length_list[i])/1000 for x in item['timeStamps'] ]
        timeStamp_list+=temp

    #temp.insert(0,0)
    #length_list = list(zip(temp,length_list))
    #print(timeStamp_list)
    #print(length_list)
    return timeStamp_list,punch_set,length_list

def punch_pic_generator(punch_set):
    img_empty = Image.new('RGBA', (1170, 2532))
    font = ImageFont.truetype('NotoSansTC-VariableFont_wght.ttf', 150)
    anchor = 'mm'
    print('before iter')
    for i in range(len(punch_set)):
        img = img_empty.copy()
        draw = ImageDraw.Draw(img)
        # 计算文本的 x 坐标，使其水平居中

        file_path = f'{punch_set[i]}.png'
        file_exists = os.path.exists(file_path)
        if(file_exists):
            continue

        #text_width, text_height = draw.textsize(text, font=font)
        x_text = 585 #- len(text)/2*font_size
        draw.text((x_text,650), punch_set[i], fill=(239,198,27), font=font, stroke_width=3, stroke_fill='white',anchor = anchor)
        img.save(f'{punch_set[i]}.png')

def add_punch(video, data):
    video = VideoFileClip(video).resize((1170,2532))
    time_split,punch_set,length_list = set_punchcard_time(data)
    punch_pic_generator(punch_set)
    texts = []
    for i in range(len(punch_set)):
        if(i+1!=len(punch_set)):
            duration = min(time_split[i+1]-time_split[i],1)
        else:
            duration = 1
        texts.append(ImageClip(f'{punch_set[i]}.png', transparent=True).set_duration(duration).set_start(time_split[i]))
    output = CompositeVideoClip([video]+texts)
        # 合併所有影片片段
    output.write_videofile("addPunch.mp4", fps=60)  # 轉換成 gif 動畫

def bg_image_process(Image):

  Image = cv2.GaussianBlur(Image, (5, 5), 0)
  Image = cv2.add(Image, np.array([-100.0]))  # subtract 50 from every pixel value
  Image[:, :, 3] = 90
  # 獲取圖像的原始尺寸
  return Image

def crop_image(input_image,image_bias_x,image_bias_y,zoom,outputname):
    video_size = (1170, 2532)
    # 讀取圖像
    image = cv2.imread(input_image,cv2.IMREAD_UNCHANGED)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    bg_image = cv2.imread(input_image, cv2.IMREAD_UNCHANGED)
    bg_image = cv2.cvtColor(bg_image, cv2.COLOR_BGR2BGRA)
    #print(bg_image.shape)

    h, w = image.shape[:2]
    big_h, big_w = bg_image.shape[:2]
    #print(bg_image.shape)

    # 計算縮放因子，以確保新圖像的尺寸大於1000x1000
    scale_factor = max((1500) / w, (1500) / h)
    new_w = int(w * scale_factor)+ zoom
    new_h = int(h * scale_factor)+ zoom

    # 計算縮放因子，以確保新圖像的尺寸大於1000x1000
    scale_factor = max((3000) / big_w, (3000) / big_h)
    new_big_w = int(big_w * scale_factor)+ zoom//2
    new_big_h = int(big_h * scale_factor)+ zoom//2
    #print('new_big')
    #print(new_big_w ,new_big_h)
    #print(bg_image.shape)

    # 縮放圖像
    resized_image = cv2.resize(image, (new_w, new_h))
    #print(resized_image.shape[:2])
    resized_bg_image = cv2.resize(bg_image, (new_big_w, new_big_h))
    #print(resized_bg_image.shape)
    # 計算中心點坐標
    center_x, center_y = new_w // 2, new_h // 2
    center_x += image_bias_x
    center_y += image_bias_y
    # 計算擷取區域的坐標
    start_x, start_y = center_x -500 , center_y - 500
    end_x, end_y = center_x + 500, center_y + 500
    #print('startpoint',start_x, start_y,end_x, end_y)
    # 計算中心點坐標
    center_x, center_y = new_big_w // 2, new_big_h // 2
    center_x += image_bias_x//2
    center_y += image_bias_y//2
    # 計算擷取區域的坐標
    start_big_x, start_big_y = center_x - 1170//2, center_y - 2532//2
    end_big_x, end_big_y = center_x + 1170//2, center_y + 2532//2

    #print(bg_image.shape)

    # 擷取1000x1000的區域
    cropped_image = resized_image[start_y:end_y, start_x:end_x]
    bg_image = resized_bg_image[start_big_y:end_big_y, start_big_x:end_big_x]
    big_h, big_w = bg_image.shape[:2]
    #print(bg_image.shape)

    # Calculate the starting point of the smaller image
    start_x = (big_w - 1000) // 2
    start_y = (big_h - 1000) // 2

    # Determine the ending point of the smaller image
    end_x = start_x + 1000
    end_y = start_y + 1000

    # Overlay the smaller image onto the big image
    bg_image = bg_image_process(bg_image)
    #print(bg_image.shape)
    #print(cropped_image.shape)
    bg_image[start_y:end_y, start_x:end_x] = cropped_image
    #print("starts",start_y,end_y, start_x,end_x)
    # 保存或顯示擷取的區域
    cv2.imwrite(outputname, bg_image)


def generate_video_picture(imgs,secs,effects):
    #imgs input images
    #sec seconds of each images
    #effect 0:None,1:right,2:up,3:left,4:down,5,zoom_in,zoom out
    FPS = 60
    for i,image in enumerate(imgs):
        if(None):
            for j in range(int(secs[i]*FPS)):
                if(effects[i]==1):
                    crop_image(image,-2*j,0,0,image[:-4]+f'_{j:03d}'+'.jpg')
                elif(effects[i]==2):
                    crop_image(image,0,2*j,0,image[:-4]+f'_{j:03d}'+'.jpg')
                elif(effects[i]==3):
                    crop_image(image,2*j,0,0,image[:-4]+f'_{j:03d}'+'.jpg')
                elif(effects[i]==4):
                    crop_image(image,0,-2*j,0,image[:-4]+f'_{j:03d}'+'.jpg')
                elif(effects[i]==5):
                    crop_image(image,0,0,2*j,image[:-4]+f'_{j:03d}'+'.jpg')
                elif(effects[i]==6):
                    crop_image(image,0,0,-2*j,image[:-4]+f'_{j:03d}'+'.jpg')
        else:
            crop_image(image,0,0,0,image)

def combine_audio_video(audio_path, input_video, output_video):
    audio = AudioFileClip(audio_path)
    video = VideoFileClip(input_video)

    final_clip = video.set_audio(audio)
    final_clip.write_videofile(output_video,fps=60)

def text_to_video(data, dest, audioPath):
    input_text, video_list, title = generate_caption_api(data)
    imgs,secs,effects = generate_video_picture_api(data)
    print("input_transformed")
    print(input_text, video_list, title)
    print(imgs,secs,effects)
    generate_video_picture(imgs,secs,effects)
    print("video picture generated")
    merge_images(imgs,secs,effects)
    print("raw video get")
    x_caption = 300
    y_caption = 2000

    x_title = 400
    y_title = 120

    # Generated the video
    caption_input = "output.mp4"
    caption_output = "addAll.mp4"
    # Add caption
    add_caption(input_text, title, video_list, caption_input, x_caption, y_caption, x_title, y_title, caption_output)
    print("cpation added")
    # Add punch
    add_punch('addAll.mp4', data)
    print("punch added")
    # Merge with audio
    input_video = "addPunch.mp4"
    print("start combine video and audio")
    combine_audio_video(audioPath, input_video, dest)
