from script import script_generator
from image import get_img
from audio import audio_generator, bgm_generator
from pathlib import Path
import sys
import os

import sys

def move_cursor(row, col):
    sys.stdout.write("\x1b[{};{}H".format(row, col))
    sys.stdout.flush()

def main(length: int, text: str, imgs: list, imgsDescription: list[str], gerne: str, dest: str) -> bool:
    """
    ## Args
    - length: The length of the video.
    - text: The text of the news.
    - imgs: The list of string represents path to those images that are used in the news.
    - imgsDescription: The list of string that describe the images.
    - gerne: What type of the news it is.
    - dest: The destination path of the output videos.
    ## Return
    - (bool): Whether the video is successfully generated.
    """
    os.system('')  # start VT-100 in windows console
    try:
        # Generate scipt to read
        print("Generating script ... ", flush=True, end='')
        sentences = script_generator(text, length, imgsDescription)

        print("Complete!", flush=True)

        print("Generating audio and images ... ", flush=True)

        # Create folder if not exist
        if not Path('./audio_result').exists():
            os.mkdir(Path('./audio_result'))
        # Parallelly create audios
        ListOfAudio, ListOfLength, ListOfTimeStampes, ListOfText, ListOfKeywords = audio_generator(sentences, gerne)

        # Create images
        ListOfImage = []
        ListOfImageReal = []
        print(" - Generating Images ... ", flush=True, end='')
        for s in sentences:
            if s["imageDescription"]:
                img, r = get_img(s["imageDescription"], imgs)
                ListOfImage.append(img)
                ListOfImageReal.append(r)
        
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

        # Start producing video
        print("Generating video ... ", flush=True)
        '''
        # Start to apply video editing here: 
        - audio: Final audio data
        - totalLength: The length of this audio data
        - data: Data of each sentence, which contains 
            - "text"
            - "length"
            - "keywords"
            - "timeStamps"
            - "image"
            - "imageReal"
        '''

        print("Complete!", flush=True)
        return True
    except ...:
        return False
    

# length = 20
# text = "國立清華大學本月9日迄今校園多次無預警停電，學生會不滿校方昨天片面宣布下周23到26日部分宿舍區白天停止供電，今天發文批評是枉顧學生權益，也傳出有學生要發起抗議行動。台電新竹區營業處獲悉校園停電狀況主動出手，今天到校會勘，允諾協助清大將於明後天先協助布設臨時電纜，校方傍晚證實下周一23日起恢復正常供電。\
# 清大從9日起短短10天內停電6次，3次為無預警停電，學生哀鴻遍野抱怨電器受損、實驗中斷等，更不滿宿舍區還要限電。校方說明，是因供應全校約一半電力的第二高壓站電纜因老舊及受潮突然故障，緊急修復又有另處電纜故障，預計29日全面修復。\
# 對此，清華大學學生會今天在臉書發文，表示停電已影響教職員工生，且至今仍處限電狀態，尤其不滿校方昨晚在未與學生討論的情況下，擅自發布未來一周，也就是23日到26日的部分宿舍區白天早上11至傍晚5點停止供電，此舉嚴重罔顧住宿生權益。\
# 據了解，清大校園內部電力向來由校方負責，校方因為仍正在等候新電纜到料，所以修復完成時間壓在29日。台電新竹區營業處處長胡忠興、電務副處長陳煥文等人今天早上主動到清大拜訪總務長、營繕組長，認為等候到料緩不濟急，決定協助處理。\
# 陳煥文說，經與學校會勘診斷，台電新竹營業處決定會同學校營繕組明、後天，趁假日的學校用電離峰時段，在校園共同管路系統，先緊急舖設1.2公里長的臨時高壓電纜、並做好設備銜接，待學校到料著手修復，且測試穩定後，就會收回臨時電纜。\
# 陳煥文表示，因應相關工程預定23日凌晨2到5時停電改接送電，並說明清大校區廣大，電纜線路也相當長，台電在電力修復方面經驗充足，且有現成的電纜線料可以先協助清大，後續也將協助清大協助申請緊急提升契約容量，讓校園用電更穩定安全。"
# imgsDescription = ["學生沒有電在對電腦生氣的圖"]
# gerne="大學"

# main(length=length, text=text, imgsDescription=imgsDescription, gerne=gerne, imgs=["./temp.png"], dest="none")
