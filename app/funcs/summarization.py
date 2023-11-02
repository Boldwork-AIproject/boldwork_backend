# Load model directly
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer = AutoTokenizer.from_pretrained("alaggung/bart-r3f")
model = AutoModelForSeq2SeqLM.from_pretrained("alaggung/bart-r3f")

def summarize(input_text):
    try_num = 0
    max_tries = len(input_text) // 100
    while try_num < max_tries:
        try:
            if try_num != 0:
                num = (len(input_text) // 100 - 1) * 100
            else:
                num = len(input_text)
            try_num += 1
            print('###########','try_num','num')
            input_text = input_text[:num]
            input_ids = tokenizer.encode(input_text, return_tensors="pt")
            # Generate Summary Text Ids
            summary_text_ids = model.generate(
                input_ids=input_ids,
                bos_token_id=model.config.bos_token_id,
                eos_token_id=model.config.eos_token_id,
                length_penalty=2.0,
                max_length=142,
                min_length=56,
                num_beams=4,
            )
            # Decoding Text
            result = tokenizer.decode(summary_text_ids[0], skip_special_tokens=True)
            return result
        except Exception as e:
            print(f"Attempt {try_num} failed with error: {e}")

    # If all attempts fail, return None
    return None