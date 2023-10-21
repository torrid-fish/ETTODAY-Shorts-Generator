from flask import Flask, render_template, request
import cv2
from PIL import Image
import os


app = Flask(__name__)

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    output = None
    if request.method == 'POST':
        input_length = int(request.form['shortsLength'])
        input_labels = request.form['shortsLabels']
        labels_array = input_labels.split(', ')
        image_path_array = request.files.getlist('uploaded_images')

        input_text = request.form['input_text']
        
        print(f'request form {request.form}')
        print(f'labels: {labels_array}')

        print(f'image: {image_path_array}')
        print(f'length: {input_length}')

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
        
        print(f'PIL images: {image_PIL_array}')

        

        #input_labels = request.form['shortsLabels']
        # Call your Python program with input_text and get the output
        # For example: output = your_python_function(input_text)
        # For demonstration purposes, let's assume the output is generated as a string
        output = "Output: This is input text - " + input_text + " this is input labels - " + input_labels
    return render_template('index.html', output=output)

if __name__ == '__main__':
    app.run(debug=True)
