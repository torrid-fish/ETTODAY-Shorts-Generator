from video import video_generator, generate_requirements
from pathlib import Path
import os
import sys
import json
from pydub import AudioSegment
from PIL import Image

def move_cursor(row, col):
    sys.stdout.write("\x1b[{};{}H".format(row, col))
    sys.stdout.flush()

def preserve(data, audio):
    # Preserve
    if not Path('./preserve').exists():
        os.mkdir('./preserve')
    else:
        os.system("rm preserve/*")

    audio.export("./preserve/audio.wav", format="wav")

    if not Path('./preserve/imgs').exists():
        os.mkdir('./preserve/imgs')
    else: 
        os.system("rm preserve/imgs/*")
    idx = 0
    for d in data:
        img = d["image"]
        p = f'./preserve/imgs/photo{idx}.jpg'
        img.save(p)
        d["image"] = p
        idx += 1

    with open("./preserve/data.txt", "w") as f:
        json.dump(data, f, indent=4)

def load():
    audio = AudioSegment.from_file('./preserve/audio.wav')
    with open("./preserve/data.txt", "r") as f:
        data = json.load(f)

    idx = 0
    for d in data:
        p = d["image"]
        d["image"] = Image.open(p)
        idx += 1

    return data, audio

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
        # Generate requirements
        #data, audio = generate_requirements(length, text, imgs, imgsDescription, gerne)
    
        # Preserve files
        #preserve(data, audio)

        data, audio = load()

        # Start to generate video
        video_generator(data, dest, audio)

        return True
    except ...:
        return False
    

length = 15
text = "2022 新竹 X 梅竹黑客松在 10 月 22 日及 23 日 於國立清華大學新體育館登場，本次競賽吸引近 250 位臺清交和各大專院校生、社會人士及高中生等參賽者，總與 會人數超過 450 人。梅竹黑客松現為全臺最大的校園黑客松，定期於每年 10 月底舉行大型黑客松年會，由企業提 供資源，供參賽者在兩天一夜中開發出別具創新力的實作品。\\r\\n\\r\\n今年的競賽組別為「黑客組」與「創客 交流組」，「黑客組」由七家合作企業分別帶領，包含台積電、ASML、意法半導體、中國信託、恩智浦半導體、原相科技以及 Kronos Research；「創客交流組」則攜手新竹市政府，透過融入新竹居民真實生活情境，讓參賽者在實作過程中，思索社會議題不同的可行解。\\r\\n\\r\\n緊迫的兩天時間內，許多參賽者以日常經驗出發，契合主題同時解決生活中的難題。如意法半導體組的「黑客松後黑顆肝」，以自種的繡球花為靈感，打造出可自動澆水及除蟲的溫室；首度參與便奪得梅竹大獎第三名的「吳星瀚粉絲後援會」也提及在學習交易的過程中屢受挫折的經歷，因此希望設計出 User-Friendly 的操作介面，更加貼近使用者的需求，降低耗費的時間成本。\\r\\n\\r\\n中國信託在接受 採訪時給予參賽 者兩點建議 : 首先，不論競賽規模大小，良好的溝通是幫助團隊完成終極目標的重要基石，保持正面態度並避免帶 入負面情緒，積極克服困難，才是梅竹黑客松的精神。另外，許多參賽者為了讓作品呈現更豐富， 傾向常見的「加法思考」，在實作的過程中塞入大量功能與特色，卻往往落入華而不實的窠臼；運用務實的「減法思考」，聚焦於做出自身特色的服務，亦不失為比賽中脫穎而出的好方法。\\r\\n\\r\\n而同為黑客組企業的 ASML 則以本身「3C」的企業文化鼓勵參賽者，透過勇於表達與思辨的「Challenge」與「Care」的傾聽與包容，才能打造出 「Collaborate」的團隊共贏。參與企業都希冀透過開放、創新的活動氛圍，在共同解題與合作的過程中，縮短產學 間的角色差距。"
imgsDescription = ['梅竹黑客松攜手七家業界巨頭及新竹市政府，實現產官學合作願景。', '2022新竹X梅竹黑客松 圓滿落幕，超過450人報名參賽共襄盛舉。']
gerne="生活"
imga = Image.open('uploaded_images/d6703317.jpg')
imgb = Image.open('uploaded_images/d6703316.jpg')

main(length=length, text=text, imgsDescription=imgsDescription, gerne=gerne, imgs=[imga, imgb], dest="final.mp4")
