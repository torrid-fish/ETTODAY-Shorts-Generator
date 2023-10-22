from tempfile import tempdir
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
    threshold = 1.4
    secs = []
    imgs = []
    effects = []
    #random.randint(0, 6)
    for item in datas:
        secs.append(item['length']/1000)
        imgs.append(item['image'])
        h, w = item['image'].shape[:2]
        effect_id= 0
        if(h/w >= 1.4):
            effect_id = random.randint(1, 2) #  up down
        elif(h/w <=  1/1.4):
            effect_id = random.randint(3, 4) #   leftright
        else:
            effect_id = random.randint(5, 6)#   inout
        effects.append(effect_id)
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


#modified#########################################################3
def punch_pic_generator(img,punch):
    font = ImageFont.truetype('NotoSansTC-VariableFont_wght.ttf', 150)
    anchor = 'mm'
    draw = ImageDraw.Draw(img)
    x_text = 585 #- len(text)/2*font_size
    draw.text((x_text,650), punch, fill=(239,198,27), font=font, stroke_width=3, stroke_fill='white',anchor = anchor)
    return img

def add_punch(generated_frames, data,FPS):
    time_split,punch_set,length_list = set_punchcard_time(data)
    for i in range(len(punch_set)):
        if(i+1!=len(punch_set)):
            duration = min(time_split[i+1]-time_split[i],1)
        else:
            duration = 1
        start_time =  time_split[i]*FPS
        duration = duration*FPS
        temp  = generated_frames[start_time:start_time+duration]
        for item  in temp:
            item = punch_pic_generator(item,punch_set[i])
        generated_frames[start_time:start_time+duration] =  temp
    return generated_frames

def from_frames_to_video():
    pass
def caption_pic_generator(img,input_text,title,longest_string):

    font_size = min((970//len(longest_string)),100)
    font_size_title = min((970//len(title)),100)

    font = ImageFont.truetype('NotoSansTC-VariableFont_wght.ttf', font_size)    # 設定文字字體和大小
    font_title = ImageFont.truetype('NotoSansTC-VariableFont_wght.ttf', font_size_title)
    anchor = 'mm'
    draw = ImageDraw.Draw(img)
    # 计算文本的 x 坐标，使其水平居中
    background_rect = (0, 0, 1170, 250)
    draw.rectangle(background_rect, fill=(47, 40, 115))  # 背景矩形为蓝色
    background_rect = (0, 1950, 1170, 2050)
    draw.rectangle(background_rect, fill=(47, 40, 115))  # 背景矩形为蓝色
    text = input_text
    text_width, text_height = draw.textsize(text, font=font)
    x_text = 585 #- len(text)/2*font_size
    x_title = 585 #- len(title)/2*120
    draw.text((x_text,2000), input_text, fill=(255,255,255), font=font, stroke_width=1, stroke_fill='white',anchor = anchor)
    draw.text((x_title,120), title, fill=(255,255,255), font=font_title, stroke_width=3, stroke_fill='white',anchor = anchor)
    
    return img
def add_caption(input_text, title, video_list,generated_frames, FPS):
    #need  to count longeat  string
    #text_list = text_list_generator(input_text, x_caption, y_caption)
    #print(text_list)
    
    

    # 使用 for 迴圈，合併字卡和影片
    for i in range(len(video_list)):
        FROM =  video_list[i][0]*FPS
        TO   =  video_list[i][1]*FPS
        temp  =  generated_frames[FROM:TO]
        for item in temp:
            item = caption_pic_generator(item,input_text,title)
        generated_frames[FROM:TO]  = temp
    return generated_frames        

# 轉換成 gif 動畫

def up_down(img,secs,effects,FPS):
    video_size = (1170, 2532)
    def resize(img,width):
        h, w = img.shape[:2]
        scale_factor =(width) / w
        new_w = int(w * scale_factor)
        new_h = int(h * scale_factor)
        return cv2.resize(img, (new_w, new_h))
    crop = resize(img,1000)
    BG  = resize(img,2532)

    crop_h, crop_w = crop.shape[:2]
    BG_h , BG_w = BG.shape[:2]

    crop_step =  ((crop_h-550)-550)/(secs*FPS)
    BG_step =  ((BG_h-1300)-1300)/(secs*FPS)

    outputs  =[]
    if(effects==1):
        crop_center = [499,crop_h-550]
        BG_center  =  [584,BG_h-1300]
        dr =  -1
    else:
        crop_center = [499,550]
        BG_center  =  [584,1300]
        dr =  1
    for i in  range(secs*FPS):

        temp_crop = crop[crop_center[1]-500:crop_center[1]+500,:]
        temp_BG = BG[BG_center[1]-1260:BG_center[1]+1260,:]
        temp_BG = cv2.GaussianBlur(temp_BG, (5, 5), 0)
        temp_BG = cv2.add(temp_BG, np.array([-100.0]))  # subtract 50 from every pixel value

        temp_crop.resize(temp_crop, (1000,1000))
        temp_BG.resize(temp_BG, video_size)

        start_x = (1170 - 1000) // 2
        start_y = (2532 - 1000) // 2

        # Determine the ending point of the smaller image
        end_x = start_x + 1000
        end_y = start_y + 1000

        temp_BG[start_y:end_y, start_x:end_x] = temp_crop
        outputs.append(temp_BG)
        crop_center[1] += i*crop_step*dr
        BG_center[1]  += i*BG_step*dr

    return outputs

def left_right(img,secs,effects,FPS):
    video_size = (1170, 2532)
    def resize(img,width):
        h, w = img.shape[:2]
        scale_factor =(width) / h
        new_w = int(w * scale_factor)
        new_h = int(h * scale_factor)
        return cv2.resize(img, (new_w, new_h))
    crop = resize(img,1000)
    BG  = resize(img,2532)

    crop_h, crop_w = crop.shape[:2]
    BG_h , BG_w = BG.shape[:2]

    crop_step =  ((crop_w-550)-550)/(secs*FPS)
    BG_step =  ((BG_w-550)-550)/(secs*FPS)

    outputs  =[]
    if(effects==3):#right_to_left
        crop_center = [crop_w-550,499]
        BG_center  =  [BG_w-550,1265]
        dr =  -1
    else:#left_to_right
        crop_center = [550,550]
        BG_center  =  [550,1300]
        dr =  1
    for i in  range(secs*FPS):

        temp_crop = crop[:,crop_center[0]-500:crop_center[0]+500]
        temp_BG = BG[:,BG_center[0]-585:BG_center[0]+585]
        temp_BG = cv2.GaussianBlur(temp_BG, (5, 5), 0)
        temp_BG = cv2.add(temp_BG, np.array([-100.0]))  # subtract 50 from every pixel value

        temp_crop.resize(temp_crop, (1000,1000))
        temp_BG.resize(temp_BG, video_size)

        start_x = (1170 - 1000) // 2
        start_y = (2532 - 1000) // 2

        # Determine the ending point of the smaller image
        end_x = start_x + 1000
        end_y = start_y + 1000

        temp_BG[start_y:end_y, start_x:end_x] = temp_crop
        outputs.append(temp_BG)
        crop_center[0] += i*crop_step*dr
        BG_center[0]  += i*BG_step*dr

    return outputs
def in_out(img,secs,effects,FPS):
    outputs=[]
    video_size = (1170, 2532)
    crop = img
    BG  = img
    h, w = img.shape[:2]
    center = [w//2,h//w]
    shorter = min(h,w)
    outbound = shorter*9/10 / 2 
    inbound = shorter*4/5 / 2

    BG_outbound = [h/2,h]
    BG_inbound  = [h/2*4/5,h*4/5]

    step  =   (outbound  -   inbound)/(secs*FPS)

    BG_step  =   [(BG_outbound[0]  -   BG_inbound[0])/(secs*FPS),(BG_outbound[1]  -   BG_inbound[1])/(secs*FPS)]

    if(effects == 5):
        dr  = 1
        start =  inbound
        start_BG =  BG_outbound
    else:
        dr = -1
        start =  outbound
        start_BG =  BG_inbound

    for i in  range(secs*FPS):


        temp_crop = crop[center[1]-start:center[1]+start,center[0]-start:center[0]+start]
        temp_BG = BG[center[1]-start_BG[1]/2:center[1]+start_BG[1]/2,center[0]-start_BG[0]/2:center[0]+start_BG[0]/2]


        temp_crop.resize(temp_crop, (1000,1000))
        temp_BG.resize(temp_BG, video_size)
        temp_BG = cv2.GaussianBlur(temp_BG, (5, 5), 0)
        temp_BG = cv2.add(temp_BG, np.array([-100.0]))  # subtract 50 from every pixel value

        start_x = (1170 - 1000) // 2
        start_y = (2532 - 1000) // 2

        # Determine the ending point of the smaller image
        end_x = start_x + 1000
        end_y = start_y + 1000

        temp_BG[start_y:end_y, start_x:end_x] = temp_crop
        outputs.append(temp_BG)
        start_BG[0] += i* BG_step[0]*dr
        start_BG[1] += i* BG_step[1]*dr
        start += i* step*dr

    return outputs
def no_effect(img,secs,effects,FPS):
    return [img]*secs*FPS
def generate_video_picture(imgs,secs,effects):
    #imgs input images
    #sec seconds of each images
    #effect 0:None,1:right,2:up,3:left,4:down,5,zoom_in,zoom out
    FPS = 60
    image_lists=  []
    for i,image in enumerate(imgs):
        temp = []
        if(effects[i] in [1,2]):
            temp = up_down(image,secs,effects,FPS)
        elif(effects[i] in [3,4]):
            temp = left_right(image,secs,effects,FPS)
        elif(effects[i] in [5,6]):
            temp = in_out(image,secs,effects,FPS)
        else:
            temp = no_effect(image,secs,FPS)
    image_lists += temp

    return  image_lists
#modified#########################################################3



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
    generated_frames  = generate_video_picture(imgs,secs,effects)
    print("video picture generated")
    print("raw video get")
    x_caption = 300
    y_caption = 2000

    x_title = 400
    y_title = 120

    # Generated the video
    caption_input = "output.mp4"
    caption_output = "addAll.mp4"
    # Add caption
    add_caption(input_text, title, video_list,generated_frames, caption_input, x_caption, y_caption, x_title, y_title, caption_output)
    print("cpation added")
    # Add punch
    add_punch('addAll.mp4', data)
    print("punch added")
    # Merge with audio
    input_video = "addPunch.mp4"
    print("start combine video and audio")
    combine_audio_video(audioPath, input_video, dest)
