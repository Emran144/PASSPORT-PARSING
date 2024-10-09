import os, time
from flask import Flask, request, jsonify

from resources import passport_output_processing

app = Flask(__name__)

# Define the upload folder
UPLOAD_FOLDER = 'UploadedFile'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/passport-parsing', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    print("Extraction PASSPORT...!!!", flush=True)
    passport_output_processing.clean_upload_directory(UPLOAD_FOLDER)
    # Save the file with a new name "file_1" in the "stored-file" folder
    file_dir = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_dir)

    file_name = os.listdir(UPLOAD_FOLDER)[0]
    if file_name.endswith('.pdf'):
        # print(f"Type of file: {type(file)}", flush=True)
        passport_output_processing.convert_pdf_to_img(file_name, UPLOAD_FOLDER)

    new_img_dir = os.path.join(UPLOAD_FOLDER, os.listdir(UPLOAD_FOLDER)[0])     # new_img_dir = UploadedFile/image.jpg
    
    final_result = passport_output_processing.start_passport_extraction(new_img_dir)    

    return jsonify(error=False, message="Request Response", data=final_result)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', threaded=True, port = 5052)

# start_time = time.time()
# file_dir = os.path.join(UPLOAD_FOLDER, os.listdir(UPLOAD_FOLDER)[0])
# final_result = passport_output_processing.start_passport_extraction(file_dir)
# passport_output_processing.print_data(final_result)
# print(f"Total Passport processing time: {time.time() - start_time} sec...", flush=True)