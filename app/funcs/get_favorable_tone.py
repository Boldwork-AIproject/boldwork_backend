import librosa

def favorable_tone(file_path: str) -> float:
    # 음성 파일 불러오기
    audio, sr = librosa.load(file_path, sr=16000)

    # RMS (Root Mean Square) Mean 및 Variance
    rms = librosa.feature.rms(y=audio)
    rms_mean = rms.mean()
    rms_var = rms.var()

    mean_Q1 = 0.0235419245
    mean_Q3 = 0.044102674499999994
    var_Q1 = 0.000690981175
    var_Q3 = 0.0021330691
    mean_IQR = mean_Q3 - mean_Q1
    var_IQR = var_Q3 - var_Q1
    threshold = 1.5

    if rms_mean >= mean_Q3 + threshold * mean_IQR:
        rms_mean_value = 1
    elif rms_mean <= mean_Q1 - threshold * mean_IQR:
        rms_mean_value = 0
    else:
        rms_mean_value = rms_mean / (mean_Q3 - mean_Q1 + 2 * threshold * mean_IQR)
    
    if rms_var >= var_Q3 + threshold * var_IQR:
        rms_var_value = 1
    elif rms_var <= var_Q1 - threshold * var_IQR:
        rms_var_value = 0
    else:
        rms_var_value = rms_var / (var_Q3 - var_Q1 + 2 * threshold * var_IQR)
    
    return 1 - rms_mean_value * rms_var_value