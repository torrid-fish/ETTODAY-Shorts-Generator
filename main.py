import os
from script import script_generator
from image import get_img
from audio import audio_generator, bgm_generator
from pathlib import Path
import cv2
import numpy as np
from moviepy.editor import *
from video import text_to_video

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

        print(sentences)

        print("Generating audio and images ... ", flush=True)

        # Create folder if not exist
        if not Path('./audio_result').exists():
            os.mkdir(Path('./audio_result'))
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

        print(data)

        idx = 0
        for d in data:
            img = d["image"]
            p = f'imgs/photo{idx}.jpg'
            img.save(p)
            d["image"] = p
            idx += 1

        audio.export('audio.wav', format="wav")

        # Start producing video
        text_to_video(data, dest, 'audio.wav')
        print("Complete!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"Stored at {dest}")

        return True
    except ...:
        return False
    
from PIL import Image
length = 15
text = "2022 新竹 X 梅竹黑客松在 10 月 22 日及 23 日 於國立清華大學新體育館登場，本次競賽吸引近 250 位臺清交和各大專院校生、社會人士及高中生等參賽者，總與 會人數超過 450 人。梅竹黑客松現為全臺最大的校園黑客松，定期於每年 10 月底舉行大型黑客松年會，由企業提 供資源，供參賽者在兩天一夜中開發出別具創新力的實作品。\\r\\n\\r\\n今年的競賽組別為「黑客組」與「創客 交流組」，「黑客組」由七家合作企業分別帶領，包含台積電、ASML、意法半導體、中國信託、恩智浦半導體、原相科技以及 Kronos Research；「創客交流組」則攜手新竹市政府，透過融入新竹居民真實生活情境，讓參賽者在實作過程中，思索社會議題不同的可行解。\\r\\n\\r\\n緊迫的兩天時間內，許多參賽者以日常經驗出發，契合主題同時解決生活中的難題。如意法半導體組的「黑客松後黑顆肝」，以自種的繡球花為靈感，打造出可自動澆水及除蟲的溫室；首度參與便奪得梅竹大獎第三名的「吳星瀚粉絲後援會」也提及在學習交易的過程中屢受挫折的經歷，因此希望設計出 User-Friendly 的操作介面，更加貼近使用者的需求，降低耗費的時間成本。\\r\\n\\r\\n中國信託在接受 採訪時給予參賽 者兩點建議 : 首先，不論競賽規模大小，良好的溝通是幫助團隊完成終極目標的重要基石，保持正面態度並避免帶 入負面情緒，積極克服困難，才是梅竹黑客松的精神。另外，許多參賽者為了讓作品呈現更豐富， 傾向常見的「加法思考」，在實作的過程中塞入大量功能與特色，卻往往落入華而不實的窠臼；運用務實的「減法思考」，聚焦於做出自身特色的服務，亦不失為比賽中脫穎而出的好方法。\\r\\n\\r\\n而同為黑客組企業的 ASML 則以本身「3C」的企業文化鼓勵參賽者，透過勇於表達與思辨的「Challenge」與「Care」的傾聽與包容，才能打造出 「Collaborate」的團隊共贏。參與企業都希冀透過開放、創新的活動氛圍，在共同解題與合作的過程中，縮短產學 間的角色差距。"
imgsDescription = ['梅竹黑客松攜手七家業界巨頭及新竹市政府，實現產官學合作願景。', '2022新竹X梅竹黑客松 圓滿落幕，超過450人報名參賽共襄盛舉。']
gerne="生活"
imga = Image.open('uploaded_images/d6703317.jpg')
imgb = Image.open('uploaded_images/d6703316.jpg')

main(length=length, text=text, imgsDescription=imgsDescription, gerne=gerne, imgs=[imga, imgb], dest="final.mp4")
