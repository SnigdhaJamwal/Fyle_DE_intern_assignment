# Your imports go here
import logging
import json
import re
logger = logging.getLogger(__name__)

'''
    Given a directory with receipt file and OCR output, this function should extract the amount

    Parameters:
    dirpath (str): directory path containing receipt and ocr output

    Returns:
    float: returns the extracted amount

'''

def extract_amount(dirpath: str) -> float:

    logger.info('extract_amount called for dir %s', dirpath)
    path = dirpath+"/ocr.json"
    with open(path, mode='r', encoding="utf-8") as f:
        expected_data = json.load(f).get("Blocks")

    top = left = ""
    expected_amt = 0.0
# to check if the total amount is given in a line
    for text in expected_data:
        if text.get("BlockType") == "LINE":
            text_data = text.get("Text")
            if top != "" and abs(text.get("Geometry").get('BoundingBox').get('Top') - top) < 0.015:
                expected_amt = convert_amount(text_data)
                if expected_amt != -1:
                    return expected_amt

            if check_total(text_data):
                top = text.get("Geometry").get('BoundingBox').get('Top')
                # to check if the amount is in the same line
                amt_pattern = re.compile(r'\d*\.{1}\d*')
                expected_amt= amt_pattern.search(text_data)
                if expected_amt:
                    return float(expected_amt.group())

# to check if the total amount is given in a column
    for text in expected_data:
        if text.get("BlockType") == "LINE":
            text_data = text.get("Text")
            if left != "" and abs(text.get("Geometry").get('BoundingBox').get('Left') - left) < 0.03:
                expected_amt = convert_amount(text_data)
                if expected_amt != -1:
                    return expected_amt
            if check_total(text_data):
                left = text.get("Geometry").get('BoundingBox').get('Left')
    return expected_amt

# convert the expected amount to float
def convert_amount(amt: str) -> float:

    amt = amt.replace("$","").replace(",","").replace("USD","").strip()
    try:
        return float(amt)
    except ValueError:
        return -1

# function to check if the if the line refers to the total amount that needs to be extracted
def check_total(data):
    data = data.lower()
    total_words = ["due", "cost", "total", "sale", "debit", "payment", "price", "paid"]
    non_total_words = ["subtotal", "sub total", "promo","/","tax","vat"]

    total = any(total_word in data for total_word in total_words) and not any(total_word in data for total_word in non_total_words)
    return total