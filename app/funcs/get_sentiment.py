import os
import pandas as pd
import re
from konlpy.tag import Kkma

kkma = Kkma()

# 현재 스크립트 파일의 디렉토리에서 'polarity.csv' 파일을 읽기
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.join(current_dir, 'polarity.csv')
polarity = pd.read_csv(csv_file_path)

def speaker_seperation(data_list):
    whole_text = ''
    speaker1_text = ''
    speaker2_text = ''

    for data in data_list:
        whole_text += data['text']
        if data['role'] == 'SPEAKER 1':
            speaker1_text += data['text']
        elif data['role'] == 'SPEAKER 2':
            speaker2_text += data['text']
    
    return whole_text, speaker1_text, speaker2_text

def get_score(text: str) -> (str, int, float):
    token_pos_data = kkma.pos(text)

    POS_score, NEG_score = 0, 0

    for d in token_pos_data:
        word, pos = d
        # 이스케이프 처리한 정규 표현식 패턴
        i = re.escape(f'{word}/{pos}')

        pattern = re.compile(i)
        filtered_data = polarity[polarity['ngram'].apply(lambda x: bool(pattern.search(x)))]

        # 데이터 없으면 다음으로 넘어가기
        if len(filtered_data) == 0:
            continue

        # max.value == POS면 POS 구하기
        if filtered_data.iloc[0]['max.value'] == 'POS':
            POS_score += 1

        # max.value == NEG면 NEG 구하기
        elif filtered_data.iloc[0]['max.value'] == 'NEG':
            NEG_score += 1

    score = abs(POS_score - NEG_score)
    if POS_score > NEG_score:
        sentiment = '긍정'
    elif POS_score < NEG_score:
        sentiment = '부정'
    else:
        sentiment = '중립'

    return (sentiment, score)

# z 스코어 계산
def calculate_z_score(score, mean, std):
  return (score-mean) / std

# 점수 매핑
def map_to_range(z_score):
  return 8*(z_score+9)

# 결과 산출
def get_sentiment_score(speaker1_text:str, speaker2_text:str) -> (int, int, int, str):
    speaker1_score = get_score(speaker1_text)
    speaker2_score = get_score(speaker2_text)

    # speaker1_score의 부정 여부 확인 후 값 조정
    if speaker1_score[0] == '부정':
        speaker1_score = (speaker1_score[0], speaker1_score[1] * -1)

    # speaker2_score의 부정 여부 확인 후 값 조정
    if speaker2_score[0] == '부정':
        speaker2_score = (speaker2_score[0], speaker2_score[1] * -1)

    # speaker1_score와 speaker2_score의 1번째 인덱스 값의 합 계산
    total_score = speaker1_score[1] + speaker2_score[1]

    # 점수 분포로 구간 설정
    if total_score < -51:
        conversation_sentiment ='주의'
    elif total_score < -18:
        conversation_sentiment = '보통'
    else:
        conversation_sentiment = '양호'
    
    z_score = calculate_z_score(total_score,-35.510373,23.999153)
    sentiment_score = int(map_to_range(z_score))

    return (speaker1_score[1], speaker2_score[1], sentiment_score, conversation_sentiment)