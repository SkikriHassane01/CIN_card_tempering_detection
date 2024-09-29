from flask import Blueprint, render_template, request, redirect, url_for, current_app
import cv2
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import os 
from skimage.metrics import structural_similarity as ssim
import imutils

bp = Blueprint('main', __name__, template_folder='templates')

def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # check if the post request has the file part, file part is the name of the input field in the form 
        if 'file' not in request.files:
            flask('No file part')
            return redirect(request.url) # redirect to the same page
        
        file = request.files['file']

        # check if the file is empty
        if file.filename == '':
            flask('No selected file')
            return redirect(request.url) 

        # check if the file is allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # process the upload file
            return process_file(filepath, filename)
    return render_template('index.html')


def process_file(filepath,filename):
    # load the images
    original_path = 'app/static/images/original.png'
    original = cv2.imread(original_path)
    uploaded = cv2.imread(filepath)

    if original is None or uploaded is None:
        return "Error loading images."

    # Resize the uploaded image to match the original image dimensions
    uploaded_resized = cv2.resize(uploaded, (original.shape[1], original.shape[0]))
    
    # convert the images to grayscale 
    original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    uploaded_gray = cv2.cvtColor(uploaded, cv2.COLOR_BGR2GRAY)

    # compute the structural similarity index 
    (score, diff) = ssim(original_gray, uploaded_gray, full=True)
    diff = (diff * 255).astype('uint8')

    # determine the result 
    if score >= 0.8:
        result = "the given PAN card is original"
    else:
        result = "the given PAN card is fake"

    # threshold the difference image, followed by finding contours
    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    
    # loop over the contours
    for c in contours:
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(original, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.rectangle(uploaded, (x, y), (x + w, y + h), (0, 0, 255), 2)


    # Get file extension
    _, ext = os.path.splitext(filename)
    if not ext:
        ext = '.jpg'  # Default extension if none is found

    original_output_path = os.path.join(current_app.static_folder, f'images/output.png')
    uploaded_output_path = os.path.join(current_app.static_folder, f'images/output2{ext}')

    # Save the output images
    cv2.imwrite(original_output_path, original)
    cv2.imwrite(uploaded_output_path, uploaded_resized)

    # Render the result template with images
    return render_template('result.html', 
                           result=result, 
                           score=score, 
                           original=url_for('static', filename='images/original.png'), 
                           uploaded=url_for('static', filename=f'uploads/{filename}'), 
                           output=url_for('static', filename=f'images/output.png'), 
                           output2=url_for('static', filename=f'images/output2{ext}'))
