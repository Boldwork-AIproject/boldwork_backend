# Load model directly
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer = AutoTokenizer.from_pretrained("alaggung/bart-r3f")
model = AutoModelForSeq2SeqLM.from_pretrained("alaggung/bart-r3f")

def summarize(input_text):
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