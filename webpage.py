from flask import Flask, render_template, request
from pathlib import Path
from PIL import Image
import os
from main import main

app = Flask(__name__)
# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    output = None
    if request.method == 'POST':
        input_title = request.form['shortsTitle']
        input_labels = request.form['shortsLabels']
        labels_array = input_labels.split(', ')
        image_path_array = request.files.getlist('uploaded_images')
        imgdes = request.form.getlist('descriptions')

        input_text = request.form['input_text']
        
        print(f'request form {request.form}')
        print(f'labels: {labels_array}')

        print(f'image: {image_path_array}')

        if not Path('./uploaded_images').exists(): 
            os.mkdir('./uploaded_images')
        
        os.system('rm uploaded_images/*')

        image_PIL_array = []
        file_to_img = []
        for img_path in image_path_array:
            # Check if the file is a valid image
            print(type(img_path))
            if img_path != '':
                # Save the file to a folder uploaded_images
                file_path = os.path.join('uploaded_images', img_path.filename)
                img_path.save(file_path)
                file_to_img.append(file_path)

        print(f'file to image: {file_to_img}')

        for img in file_to_img:
            image_PIL = Image.open(img)
            image_PIL_array.append(image_PIL)
            print(type(image_PIL))
        
        print(f'PIL images: {image_PIL_array}')

        imgsDescription = []
        for des in imgdes:
            imgsDescription.append(des)
        
        print(f'imgsDescription: {imgsDescription}')

        result = main(length=10, text=input_text, imgsDescription=imgdes, gerne=input_labels, imgs=image_PIL_array, dest=None)

        output = result
    return render_template('index.html', output=output)

if __name__ == '__main__':
    app.run(debug=True)