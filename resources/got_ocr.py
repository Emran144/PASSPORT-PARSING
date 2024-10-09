# import torch
# from transformers import AutoModel, AutoTokenizer

# model_dir = 'models/gotocr'
# tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
# model = AutoModel.from_pretrained(
#     model_dir,
#     trust_remote_code=True,
#     low_cpu_mem_usage=True,
#     device_map='auto',      # for CPU remove this line
#     use_safetensors=True,
#     torch_dtype=torch.float16,  # float16 for GPU | float32 for CPU
#     pad_token_id=tokenizer.eos_token_id
# )
# model = model.eval()  # Switch the model to evaluation mode
# model.to('cpu') 

# def perform_GOTOCR(image_path):
#     # res = model.chat(tokenizer, image_path, ocr_type='ocr')
#     res = model.chat(tokenizer, image_path, ocr_type='format')
#     # print(res)
#     return res.upper().replace(' ','')