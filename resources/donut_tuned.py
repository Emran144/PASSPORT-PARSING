import re
from PIL import Image
import torch

from transformers import DonutProcessor, VisionEncoderDecoderModel

donut_fine_tuned_model_dir = "synthetic-mrz/syn_mrz_donut_dataset/finetuned_files_weight"
processor = DonutProcessor.from_pretrained(donut_fine_tuned_model_dir, local_files_only=True)
model = VisionEncoderDecoderModel.from_pretrained(donut_fine_tuned_model_dir, local_files_only=True)

def perform_donut_tuned(img_path):

    image = Image.open(img_path).convert('RGB')

    # # Get image details
    # image_format = image.format          # Format (e.g., JPEG, PNG)
    # image_size = image.size              # Dimensions (width, height)
    # image_mode = image.mode              # Color mode (e.g., RGB, RGBA, L)
    # image_info = image.info              # Other metadata (e.g., EXIF data)

    # # Print the details
    # print(f'Format: {image_format}', flush=True)
    # print(f'Size: {image_size}', flush=True)         # Tuple (width, height)
    # print(f'Mode: {image_mode}', flush=True)
    # print(f'Info: {image_info}', flush=True)          # Dictionary of metadata

    pixel_values = processor(image, return_tensors="pt", do_align_long_axis=False).pixel_values
    task_prompt = "<s_cord-v2>"
    decoder_input_ids = processor.tokenizer(task_prompt, add_special_tokens=False, return_tensors="pt")["input_ids"]
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    
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

    sequence = processor.batch_decode(outputs.sequences)[0]
    sequence = sequence.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "")
    sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()

    result = processor.token2json(sequence)
    result = {k: v if v else "N/A" for k, v in result.items()}

    formatted_result = {
        "line_1": result.get("line_1", "N/A"),
        "line_2": result.get("line_2", "N/A")
    }

    return formatted_result
