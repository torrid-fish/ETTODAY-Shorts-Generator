from script import script_generator
from image import get_img
from audio import audio_generator, bgm_generator
from pathlib import Path
import cv2
import numpy as np
from moviepy.editor import *
from PIL import Image, ImageFont, ImageDraw
import random
import glob
import re
import os

def generate_requirements(length, text, imgs, imgsDescription, gerne):
    # Generate scipt to read
        print("Generating script ... ", flush=True, end='')
        sentences = script_generator(text, length, imgsDescription)

        print("Complete!", flush=True)

        print(sentences)

        print("Generating audio and images ... ", flush=True)

        # Create folder if not exist
        if not Path('./audio_result').exists():
            os.mkdir(Path('./audio_result'))
        else:
            os.system("rm audio_result/*")
        # Parallelly create audios
        ListOfAudio, ListOfLength, ListOfTimeStampes, ListOfText, ListOfKeywords = audio_generator(sentences, gerne)

        # Create images
        ListOfImage = []
        ListOfImageReal = []
        i = 0
        print(" - Generating Images ... ", flush=True, end='\n')
        for s in sentences:
            if s["imageDescription"]:
                img, r = get_img(s["imageDescription"], imgs)
                ListOfImage.append(img)
                ListOfImageReal.append(r)
                print(f"{int(100 * i / (len(sentences)-2))}% done")
                i += 1
        
        assert len(ListOfImage) == len(ListOfAudio) - 2, "The number of images and sentences are not matched"
        print("Done!", flush=True)

        # Create data
        print(" - Generating Data Lists ... ", flush=True, end='')
        data = []
        for i in range(len(ListOfAudio)):
            if i < 2: 
                image, imageReal = ListOfImage[0], ListOfImageReal[0]
            elif i == len(ListOfAudio)-1:
                image, imageReal = ListOfImage[-1], ListOfImageReal[-1]
            else:
                image, imageReal = ListOfImage[i-1], ListOfImageReal[-1]
            data.append({
                "text": ListOfText[i],
                "length": ListOfLength[i],
                "keywords": ListOfKeywords[i],
                "timeStamps": ListOfTimeStampes[i],
                # First sentence and second sentence is title and intro, they share the same image
                "image": image,
                "imageReal": imageReal 
            })
        print("Done!", flush=True)

        print(" - Merging audio with bgm ... ", flush=True, end='')
        # Merge audio
        audio = ListOfAudio[0]
        for a in ListOfAudio[1:]:
            audio += a
    
        # Generate bgm
        totalLength = len(audio)
        bgm = bgm_generator(gerne, totalLength)
        audio = audio.overlay(bgm, position=0)
        print("Done!", flush=True)
        print('\033[5A', end='') # cursor up 5 lines
        print('\033[32C', end='') # cursor right 32 char
        print("Complete!", flush=True)

        return data, audio

##############################################################################################################

def generate_video_picture_api(datas):
    secs = []
    imgs = []
    effects = []
    #random.randint(0, 6)
    for item in datas:
        secs.append(item['length']/1000)
        imgs.append(np.array(item['image']))
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

def caption_pic_generator(img,input_text,title,longest_string):

    font_size = min((970//len(longest_string)),100)
    font_size_title = min((970//len(title)),100)

    font = ImageFont.truetype('NotoSansTC-VariableFont_wght.ttf', font_size)    # 設定文字字體和大小
    font_title = ImageFont.truetype('NotoSansTC-VariableFont_wght.ttf', font_size_title)
    anchor = 'mm'
    img = Image.fromarray(img)
    draw = ImageDraw.Draw(img)
    # 计算文本的 x 坐标，使其水平居中
    background_rect = (0, 0, 1170, 250)
    draw.rectangle(background_rect, fill=(47, 40, 115))  # 背景矩形为蓝色
    draw.rectangle(background_rect, fill=(47, 40, 115))  # 背景矩形为蓝色
    background_rect = (0, 1950, 1170, 2050)
    draw.rectangle(background_rect, fill=(47, 40, 115))  # 背景矩形为蓝色
    x_text = 585 #- len(text)/2*font_size
    x_title = 585 #- len(title)/2*120
    draw.text((x_text,2000), input_text, fill=(255,255,255), font=font, stroke_width=1, stroke_fill='white',anchor = anchor)
    draw.text((x_title,120), title, fill=(255,255,255), font=font_title, stroke_width=3, stroke_fill='white',anchor = anchor)
    return np.array(img)

def add_caption(input_text, title, video_list,generated_frames, FPS):
    #need  to count longeat  string
    #text_list = text_list_generator(input_text, x_caption, y_caption)
    #print(text_list)
    longest = max(input_text,key = lambda x: len(x))
    # 使用 for 迴圈，合併字卡和影片
    for i in range(len(video_list)):
        FROM =  int(round(video_list[i][0]*FPS))
        TO   = int(round(video_list[i][1]*FPS)) if i < len(video_list) else len(generated_frames)
        temp  =  generated_frames[FROM:TO]
        for j in range(len(temp)):
            temp[j] = caption_pic_generator(temp[j],input_text[i],title,longest)
        generated_frames[FROM:TO]  = temp
    return generated_frames        

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

def punch_pic_generator(img,punch):
    font = ImageFont.truetype('NotoSansTC-VariableFont_wght.ttf', 150)
    anchor = 'mm'
    img = Image.fromarray(img)
    draw = ImageDraw.Draw(img)
    x_text = 585 #- len(text)/2*font_size
    draw.text((x_text,650), punch, fill=(239,198,27), font=font, stroke_width=3, stroke_fill='white',anchor = anchor)
    return np.array(img)

def add_punch(generated_frames, data,FPS):
    time_split,punch_set,length_list = set_punchcard_time(data)
    for i in range(len(punch_set)):
        if(i+1!=len(punch_set)):
            duration = min(time_split[i+1]-time_split[i],1)
        else:
            duration = 1
        start_time =  int(round(time_split[i]*FPS))
        duration = int(round(duration*FPS))
        temp  = generated_frames[start_time:start_time+duration]
        for j in range(len(temp)):
            temp[j] = punch_pic_generator(temp[j],punch_set[i])
        generated_frames[start_time:start_time+duration] =  temp
    return generated_frames

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
    for i in  range(int(round(secs*FPS))):

        temp_crop = crop[int(round(crop_center[1]-500)):int(round(crop_center[0]+500)),:]
        temp_BG = BG[int(round(BG_center[1]-1260)):int(round(BG_center[0]+1260)),:]
        temp_BG = cv2.GaussianBlur(temp_BG, (5, 5), 0)
        temp_BG = cv2.add(temp_BG, np.array([-100.0]))  # subtract 50 from every pixel value
        print('check')
        print(img)
        print(temp_crop.shape)
        temp_crop = cv2.resize(temp_crop, (1000,1000))
        temp_BG = cv2.resize(temp_BG, video_size)

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
    BG_step =  ((BG_w-600)-600)/(secs*FPS)

    outputs  =[]
    if(effects==3):#right_to_left
        crop_center = [crop_w-550,499]
        BG_center  =  [BG_w-600,1265]
        dr =  -1
    else:#left_to_right
        crop_center = [550,550]
        BG_center  =  [600,1300]
        dr =  1
    for i in  range(int(round(secs*FPS))):

        temp_crop = crop[:,int(round(crop_center[0]-500)):int(round(crop_center[0]+500))]
        temp_BG = BG[:,int(round(BG_center[0]-585)):int(round(BG_center[0]+585))]
        temp_BG = cv2.GaussianBlur(temp_BG, (5, 5), 0)
        temp_BG = cv2.add(temp_BG, np.array([-100.0]))  # subtract 50 from every pixel value
        print('check')
        print(img)
        print(temp_crop.shape)
        temp_crop =   cv2.resize(temp_crop, (1000,1000))
        temp_BG = cv2.resize(temp_BG, video_size)

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
    center = [w//2,h//2]
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

    for i in  range(int(round(secs*FPS))):


        temp_crop = crop[int(round(center[1]-start)):int(round(center[1]+start)),int(round(center[0]-start)):int(round(center[0]+start))]
        temp_BG = BG[int(round(center[1]-start_BG[1]/2)):int(round(center[1]+start_BG[1]/2)),int(round(center[0]-start_BG[0]/2)):int(round(center[0]+start_BG[0]/2))]
        print('check')
        print(img)
        print(temp_crop.shape)

        temp_crop = cv2.resize(temp_crop, (1000,1000))
        temp_BG = cv2.resize(temp_BG, video_size)
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
    video_size = (1170, 2532)
    def resize(img,fac):
        h, w = img.shape[:2]
        scale_factor =max((1000) / w, (1000) / h)
        new_w = int(w * scale_factor)*fac
        new_h = int(h * scale_factor)*fac
        return cv2.resize(img, (new_w, new_h))
    crop = resize(img,1)
    BG = resize(img,3)
    BG = cv2.GaussianBlur(BG, (5, 5), 0)
    BG = cv2.add(BG, np.array([-100.0]))  # subtract 50 from every pixel value

    h, w = crop.shape[:2]
    center_h = h//2
    center_w = w//2
    print('crop')
    print(h,w)
    crop = crop[center_h-500:center_h+500,center_w-500:center_w+500]

    h, w = BG.shape[:2]
    print('BG')
    print(h,w)
    center_h = h//2
    center_w = w//2
    BG = BG[center_h-1266:center_h+1266,center_w-585:center_w+585]
    BG[1266-500:1266+500,585-500:585+500] = crop




    return [BG]*int(round(secs*FPS))

def generate_video_picture(imgs,secs,effects,FPS):
    #imgs input images
    #sec seconds of each images
    #effect 0:None,1:right,2:up,3:left,4:down,5,zoom_in,zoom out
    image_lists=  []
    for i,image in enumerate(imgs):
        temp = []
        # if(effects[i] in [1,2]):
        #     temp = up_down(image,secs[i],effects[i],FPS)
        # elif(effects[i] in [3,4]):
        #     temp = left_right(image,secs[i],effects[i],FPS)
        # elif(effects[i] in [5,6]):
        #     temp = in_out(image,secs[i],effects[i],FPS)
        # else:
        temp = no_effect(image,secs[i],effects[i],FPS)
        image_lists += temp

    return  image_lists

def combine_audio_video(audio_path, input_video, output_video, FPS):
    audio = AudioFileClip(audio_path)
    video = VideoFileClip(input_video)

    final_clip = video.set_audio(audio)
    final_clip.write_videofile(output_video,fps=FPS)

def increment_path(folder, exist_ok=True, sep=''):
    # Increment path, with a filename extension at the end.
    path = Path(folder) # Without filename extension
    if (path.exists() and exist_ok) or (not path.exists()):
        return str(path)
    else:
        dirs = glob.glob(f"{path}{sep}*")  # similar paths
        matches = [re.search(rf"%s{sep}(\d+)" % path.stem, d) for d in dirs] 
        i = [int(m.groups()[0]) for m in matches if m]  # indices
        n = max(i) + 1 if i else 2  # increment number
        return f"{path}{sep}{n}"  # update path

def video_generator(data, dest, audio):
    # Settings of the video
    FPS = 10

    # prcess data
    print("Generating caption and preprocess received data ... ", flush=True, end='')
    input_text, video_list, title = generate_caption_api(data)
    imgs, secs, effects = generate_video_picture_api(data)
    print("Complete!")

    print(input_text, video_list, title)
    print(imgs,secs,effects)
    # Raw video
    print("Generating raw video frames ... ", flush=True, end='')
    generated_frames = generate_video_picture(imgs, secs, effects,FPS)
    print("Complete!")

    # Add caption
    print("Adding caption on top of each frame ... ", flush=True, end='')
    generated_frames = add_caption(input_text, title, video_list,generated_frames, FPS)
    print("Complete!")

    # Add punch
    print("Add punch on top of each frame ... ", flush = True, end='')
    generated_frames = add_punch(generated_frames, data, FPS)
    print("Complete!")

    # Merge with audio
    print("Start combine video and audio ... ", flush = True, end='')
    videoPath = 'video.mp4'
    for i in range(len(generated_frames)): 
        generated_frames[i] = cv2.cvtColor(generated_frames[i], cv2.COLOR_BGR2RGB)
    frame_size = (generated_frames[0].shape[1], generated_frames[0].shape[0])
    out = cv2.VideoWriter(videoPath, cv2.VideoWriter_fourcc(*'mp4v'), FPS, frame_size)
    for img in generated_frames:
        out.write(img)
    out.release()

    audioPath = 'audio.wav'
    audio.export(audioPath, format='wav')
    
    combine_audio_video(audioPath, videoPath, dest, FPS)
