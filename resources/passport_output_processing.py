import os, shutil, json, warnings, easyocr, cv2
from dateutil import parser
import matplotlib.image as mpimg
from passporteye import read_mrz
from PIL import Image, ImageOps
from resources import got_ocr, donutVQA, donut_tuned, helper_function
import string as st
import pytesseract
import fitz  # PyMuPDF
from paddleocr import PaddleOCR

reader = easyocr.Reader(['en'], gpu=False, download_enabled=False, model_storage_directory="models/easyocr-models")

warnings.filterwarnings('ignore')

# Clear all the files inside the output folder
def clean_upload_directory(output_path):
    for root, dirs, files in os.walk(output_path):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

def convert_pdf_to_img(pdf_file, output_dir):

    pdf_file_dir = os.path.join(output_dir, pdf_file)
    pdf_document = fitz.open(pdf_file_dir)

    # Iterate through all the pages in the PDF
    for page_num in range(pdf_document.page_count):
        # Get each page
        page = pdf_document.load_page(page_num)
        
        # Define zoom and rotation if needed (optional)
        zoom = 1.0  # Adjust zoom (1.0 means no zoom, 2.0 means zoomed in by 2 times)
        mat = fitz.Matrix(zoom, zoom)
        
        # Render page to an image (pixmap object)
        pix = page.get_pixmap(matrix=mat)
        
        # Save the image
        image_file_path = os.path.join(output_dir, f"{pdf_file.split('.')[0]}.png")
        pix.save(image_file_path)
        print(f"Saved page {page_num + 1} as {image_file_path}")

    # Close the PDF file
    pdf_document.close()
    os.remove(pdf_file_dir)

def copy_cropped_mrz(mrz_region_path, renamed_file_name):
    new_location = os.path.join("outputs", "cropped_mrz", renamed_file_name)
    shutil.copy2(mrz_region_path, new_location)
    os.remove(mrz_region_path)

def parse_date(string, iob=True):
    # print(f"DOB: {string}", flush=True)
    date = parser.parse(string, yearfirst=True).date() 
    return date.strftime('%d/%m/%Y')

def clean(string):
    return ''.join(i for i in string if i.isalnum()).upper()

def get_country_name(country_code):
    with open('static-files/country-codes/countries.json') as f:
        country_codes = json.load(f)
        
    country_name = ''
    for country in country_codes:
        if country['alpha_3_code'] == country_code:
            country_name = country['en_short_name']
            return country_name.upper()
    return country_code

def get_nationality(nationality_code):
    with open('static-files/country-codes/countries.json') as f:
        country_codes = json.load(f)
        
    nationality = ''
    for country in country_codes:
        if country['alpha_3_code'] == nationality_code:
            nationality = country['nationality']
            return nationality.upper()
    return nationality_code

def get_sex(code):
    if code in ['M', 'm', 'F', 'f']:
        sex = code.upper() 
    elif code == '0':
        sex = 'M'
    else:
        sex = 'F'
    return sex

def print_data(data):
    for key in data.keys():
        info = key.replace('_', ' ').capitalize()
        print(f'{info}\t:\t{data[key]}')
    return

def make_image_black_white(path):
    print(path)
    image = Image.open(path)
    # image = ImageOps.expand(image, border=(100, 500, 100, 500), fill=(255, 255, 255))  # Fill with white color, you can change this
    image = image.convert("L")
    image = image.point(lambda x: 255 if x > 160 else 0, mode='1')
    new_im_path = os.path.join('/'.join(path.split('/')[:-1]), f"b&w_{path.split('/')[-1]}")
    print(new_im_path)
    image.save(new_im_path)

def perform_paddleOCR(img_path):
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    result = ocr.ocr(img_path, cls=True)
    paddle_ocr_text = ''
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            print(line)
            paddle_ocr_text += line[1][0] + "\n"
    return paddle_ocr_text
    

def start_passport_extraction(img_name):    # img_name = UploadedFile/image.jpg

    # all_txt = reader.readtext(Image.open(img_name), paragraph=False, detail=0)
    # all_txt = got_ocr.perform_GOTOCR(img_name).split('\n')
    # print(f"Passport OCR: \n{all_txt}\n", flush=True)

    user_info = {}    
    new_im_path = os.path.join("UploadedFile", 'tmp.png')   # new_im_path = UploadedFile/tmp.png
    im_path = img_name
    # Crop image to Machine Readable Zone(MRZ)
    mrz = read_mrz(im_path, save_roi=True)
    print(mrz, flush=True)
    if mrz:
        mpimg.imsave(new_im_path, mrz.aux['roi'], cmap='gray')
        
        img = cv2.imread(new_im_path)
        img = cv2.resize(img, (1110, 140))
        
        allowlist = st.ascii_letters+st.digits+'< '
        encoded_text = reader.readtext(img, paragraph=False, detail=0, allowlist=allowlist)

        encoded_text = helper_function.process_easyocr_output_for_mrz(encoded_text)
        
        donutVQA_result = donutVQA.perform_donutvqa(new_im_path)        # new_im_path = UploadedFile/tmp.png
        print(f"\nDonutVQA Result: {donutVQA_result}", flush=True)
        # donut_tuned_result = donut_tuned.perform_donut_tuned(new_im_path)   # new_im_path = UploadedFile/tmp.png
        # print(f"Donut Tune Extractior Result: {donut_tuned_result}\n", flush=True)
        # encoded_text = got_ocr.perform_GOTOCR(new_im_path).split('\n')
        # encoded_text = perform_paddleOCR(new_im_path).split('\n')
        # encoded_text = pytesseract.image_to_string(Image.open(new_im_path), config='--psm 6').split('\n')
        print(f"Code---->{encoded_text}", flush=True)
        a = encoded_text[0].upper().replace(" ", "")
        b = encoded_text[1].upper().replace(" ", "")
        
        if len(a) < 44:
            a = a + '<'*(44 - len(a))
        if len(b) < 44:
            b = b + '<'*(44 - len(b))

        print(f"\na----->{a}\nb----->{b}\n", flush=True)

        surname_names = a[5:44].split('<<', 1)
        if len(surname_names) < 2:
            surname_names += ['']
        surname, names = surname_names
        
        # print(f"Name:\t\t ----->\t {names.replace('<', ' ').strip().upper()}")
        # print(f"SurName:\t\t ----->\t {surname.replace('<', ' ').strip().upper()}")
        # print(f"Sex:\t\t ----->\t {clean(b[20])}")
        # print(f"date_of_birth:\t ----->\t {b[13:19]}")
        # print(f"nationality:\t ----->\t {clean(b[10:13])}")
        # print(f"passport_type:\t ----->\t {clean(a[0:2])}")
        # print(f"passport_number:\t ----->\t {clean(b[0:9])}")
        # print(f"issuing_country:\t ----->\t {clean(a[2:5])}")
        # print(f"expiration_date:\t ----->\t {b[21:27]}")
        # print(f"personal_number:\t ----->\t {b[28:42]}")
        
        
        user_info['name'] = names.replace('<', ' ').strip().upper()
        user_info['surname'] = surname.replace('<', ' ').strip().upper()
        user_info['sex'] = get_sex(clean(b[20]))
        user_info['date_of_birth'] = parse_date(b[13:19])
        user_info['nationality'] = get_nationality(clean(b[10:13]))
        user_info['passport_type'] = clean(a[0:2])
        user_info['passport_number']  = clean(b[0:9])
        user_info['issuing_country'] = get_country_name(clean(a[2:5]))
        user_info['expiration_date'] = parse_date(b[21:27])
        user_info['personal_number'] = clean(b[28:42])

    else:
        return print(f'Machine cannot read image {img_name}.')
    
    renamed_file_name = f"{img_name.split('/')[-1].split('.')[0]}_{new_im_path.split('/')[-1]}"
    copy_cropped_mrz(new_im_path, renamed_file_name)
    # os.remove(new_im_path)
    
    return user_info