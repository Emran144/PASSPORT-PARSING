import re
from PIL import Image

import torch
from transformers import DonutProcessor, VisionEncoderDecoderModel

donut_vqa_model_dir = "models/donutVQA-base-model"
processor = DonutProcessor.from_pretrained(donut_vqa_model_dir)
model = VisionEncoderDecoderModel.from_pretrained(donut_vqa_model_dir)

# Choose the appropriate device (GPU if available, otherwise CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Move the model to the chosen device
model.to(device)

def get_outputs(image, questions):
    pixel_values = processor(image, return_tensors="pt").pixel_values
    # print(pixel_values.shape)

    prompts = []
    for q in questions:
        prompts.append(f"<s_docvqa><s_question>{q}</s_question><s_answer>")
    # print(prompts)

    decoder_input_ids = processor.tokenizer(prompts, add_special_tokens=False, padding=True, return_tensors="pt")["input_ids"]

    outputs = model.generate(pixel_values.to(device),
                                   decoder_input_ids=decoder_input_ids.to(device),
                                   max_length=model.decoder.config.max_position_embeddings,
                                   early_stopping=True,
                                   pad_token_id=processor.tokenizer.pad_token_id,
                                   eos_token_id=processor.tokenizer.eos_token_id,
                                   use_cache=True,
                                   num_beams=1,
                                   bad_words_ids=[[processor.tokenizer.unk_token_id]],
                                   return_dict_in_generate=True,
                                   output_scores=True)

    return processor.batch_decode(outputs.sequences)

def preprocess_outputs(outputs):
    l = []
    for o in outputs:
        seq = o.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "")
        seq = re.sub(r"<.*?>", "", seq, count=1).strip()  # remove first task start token
        l.append(processor.token2json(seq))
    return l


def donut_output_json_convert(donut_output, path):
    json_output = {}
    for ques in donut_output:
        if ques == 'What is the first line?':
            json_output['line_1'] = donut_output[ques].replace(" ", "").upper()
        elif ques == 'What is the last line?':
            json_output['line_2'] = donut_output[ques].replace(" ", "").upper()

    return json_output
          
def perform_donutvqa(img_file):
        
    donut_image = Image.open(img_file).convert("RGB")

    question = []
    question.append("What is the first line?")
    question.append("What is the last line?")

    temp_list = {}
    for ques in question:
        o = get_outputs(donut_image, [ques])
        output = preprocess_outputs(o)
        # print(output, flush=True)
        temp_list[output[0]['question']] = output[0]['answer']

    donutVQA_output = donut_output_json_convert(temp_list, img_file)

    return donutVQA_output