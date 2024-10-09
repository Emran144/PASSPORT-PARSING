import re

def process_easyocr_output_for_mrz(encoded_text):

    def replace_line1_garbage_by_less_than(line_1):
        match = re.search(r'<<<', line_1)
        if match:
            first_index = match.start()
            # Pad with '<' to make the first line 44 characters long
            line_1 = (line_1[:first_index] + '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')[:44]
            return line_1

    if len(encoded_text) == 2:
        line_1 = encoded_text[0]
        line_2 = encoded_text[1]
        if len(line_1) == 44 and len(line_2) == 44:
            line_1 = replace_line1_garbage_by_less_than(line_1)
            return [line_1, line_2]
        elif (len(line_1) > 44 and len(line_2) < 44):
            new_line_1 = line_1[:44]
            new_line_2 = line_1[44:] + line_2
            new_line_1 = replace_line1_garbage_by_less_than(new_line_1)
            return [new_line_1, new_line_2]
        else:
            print(f"...........................................Not Processed: {[line_1, line_2]}")
            return [line_1, line_2]
    
    else:
        print(f"Before Formated: {encoded_text}")
        all_lines = ''.join(encoded_text)
        if len(all_lines) == 88:
            line_1 = all_lines[:44]
            line_2 = all_lines[44:]
            line_1 = replace_line1_garbage_by_less_than(line_1)
            print(f"After Formated-1: {[line_1, line_2]}")
            return [line_1, line_2]
        else:
            line_2 = all_lines[len(all_lines) - 44:]
            line_1 = all_lines[:len(all_lines) - 44]
            line_1 = replace_line1_garbage_by_less_than(line_1)
            print(f"After Formated-2: {[line_1, line_2]}")
            return [line_1, line_2]