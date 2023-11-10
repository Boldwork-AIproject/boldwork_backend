import os
import json
import ast
from typing import List, Tuple
import pandas as pd
import re
import nltk
from collections import Counter
from konlpy.tag import Kkma


# 현재 스크립트 파일의 디렉토리에서 'badwords.json' 파일을 읽기
current_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(current_dir, 'badwords.json')

# 욕 사전 가져오기(리스트)
with open(json_file_path, 'r', encoding="UTF-8") as fp:
  after = json.load(fp)
badwords = json.dumps(after, ensure_ascii=False)
badwords = ast.literal_eval(badwords)
badwords = badwords['badwords']

kkma = Kkma()

class GetWords:
  def __init__(self, input_text: str):
    self.input_text = input_text
    self.input_noun = kkma.nouns(input_text)

  # 욕설 빈도 백분율 구하기
  def get_badword_percentage(self) -> float:
    # 욕설 개수 세기
    bad_cnt = 0
    for i in self.input_noun:
      if i in badwords:
        bad_cnt += 1

    # 욕설 빈도 -> 백분율로 return
    return bad_cnt/len(self.input_noun)*100

  # 상담 내용 키워드 구하기
  def get_keywords(self) -> List[Tuple[str, int]]:
    ko = nltk.Text(self.input_noun, name = "상담 내용 키워드")
    stop_words = ['안녕', '무엇', '시리얼', '선생님', '마죠', '하세', '기사', '기사원사', '원사', '로그', '은', '예']
    ko = [each_word for each_word in ko if each_word not in stop_words]
    ko = [each_word for each_word in ko if len(each_word) != 1]
    ko = [each_word for each_word in ko if each_word not in badwords]
    data = Counter(ko).most_common(150)
    return data
  
  # 상담 필터링 키워드 확인
  def get_filter_keywords(self) -> str:
    result = ''
    flag = False
    if ('배송' in self.input_noun) or ('택배' in self.input_noun):
      flag = True
      if flag and (('위치' in self.input_noun) or ('어디' in self.input_noun)):
        result += '배송위치'
      if flag and (('언제' in self.input_noun) or ('언제쯤' in self.input_noun) or ('지연' in self.input_noun)):
        if result == '': result += '배송지연'
        else: result += ';배송지연'
    if '환불' in self.input_noun:
      if result == '': result += '환불문의'
      else: result += ';환불문의'
    if '반품' in self.input_noun:
      if result == '': result += '반품문의'
      else: result += ';반품문의'
    if ('교환' in self.input_noun) or ('교체' in self.input_noun):
      if result == '': result += '교환문의'
      else: result += ';교환문의'
    
    return result