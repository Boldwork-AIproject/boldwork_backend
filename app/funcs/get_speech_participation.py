import datetime

def get_speech_participation_score(segments):
    # data_list에서 생성된 리스트에서 Speaker 유형에 따라
    # 'speech_duration' 가져와서 새로운 리스트 생성
    def time(secs):
        return datetime.timedelta(seconds=round(secs))

    data_list = []
    for (i, segment) in enumerate(segments):
        data = {}
        data["role"] = segment["speaker"]
        data["text"] = segment["text"]
        data["timestamp"] = str(time(segment["start"])) 
        data["speech_duration"] = str(time(segment["end"]-segment["start"]))
        data_list.append(data)

    speaker1_speech_durations = [obj['speech_duration'] for obj in data_list if obj['role'] == 'SPEAKER 1']
    speaker2_speech_durations = [obj['speech_duration'] for obj in data_list if obj['role'] == 'SPEAKER 2']

    ## 출력예시
    ## print(speaker1_speech_durations)
    ## ['0:00:05', '0:00:01', '0:00:02', '0:00:01', '0:00:07', '0:00:07', '0:00:01', '0:00:01', '0:00:01', '0:00:08', '0:00:01', '0:00:02', '0:00:01', '0:00:03', '0:00:01', '0:00:06', '0:00:01', '0:00:01', '0:00:01', '0:00:01', '0:00:01', '0:00:01', '0:00:03', '0:00:05', '0:00:01', '0:00:05', '0:00:01', '0:00:13', '0:00:04', '0:00:01', '0:00:05', '0:00:09', '0:00:11', '0:00:08', '0:00:05', '0:00:02']
    ## print(speaker2_speech_durations)
    ## ['0:00:12', '0:00:11', '0:00:05', '0:00:04', '0:00:05', '0:00:08', '0:00:03', '0:00:06', '0:00:09', '0:00:10', '0:00:04', '0:00:09', '0:00:08']

    def time_to_seconds(time_str):
        hours, minutes, seconds = time_str.split(':')
        total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        return total_seconds

    # 각 시간을 초로 변환하여 리스트 생성
    speaker1_speech = [time_to_seconds(time) for time in speaker1_speech_durations]
    speaker2_speech = [time_to_seconds(time) for time in speaker2_speech_durations]

    # 초로 변환된 시간의 총합 계산
    speaker1_total_speech = sum(speaker1_speech)
    speaker2_total_speech = sum(speaker2_speech)

    ## print("상담원 발화 시간:", speaker1_total_speech, "초") 
    ## 상담원 발화 시간: 127초
    ## print("고객 발화 시간:", speaker2_total_speech, "초")
    ## 고객 발화 시간: 94초
    ## print("전체 상담 시간:", int(duration), "초")
    ## 전체 상담 시간: 311초

    speech_participation_score1 = speaker2_total_speech/speaker1_total_speech*100

    # segment에서 start, end 시간 튜플 형식으로 가져오기
    # 발화자 대화간 간격(이전 대화의 end - 다음 대화의 start) 추출

    start_end_values = [(entry['start'], entry['end']) for entry in segments]
    result_list = [start_end_values[i][0] - start_end_values[i - 1][1] for i in range(1, len(start_end_values))]

    ## 출력 예시
    ## print(result_list)
    ## [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 13.0, 29.0, 30.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    # 10 이상의 값 제거
    result_list = [value for value in result_list if value < 10]  

    average_speech_blank = sum(result_list) / len(result_list)  
    speech_participation_score2 = average_speech_blank**2

    speech_participation_score = speech_participation_score1 + speech_participation_score2

    return speech_participation_score