import whisper
import datetime

import torch
import pyannote.audio
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
from pyannote.audio import Audio
from pyannote.core import Segment
import wave
import contextlib
from sklearn.cluster import AgglomerativeClustering
import numpy as np

num_speakers = 2
language = 'any'
model_size = 'small' # large로 바꾸기
embedding_model = PretrainedSpeakerEmbedding("speechbrain/spkrec-ecapa-voxceleb", device=torch.device("cpu")) # gpu로 바꾸기
model = whisper.load_model(model_size)

def process_audio(path):
    result = model.transcribe(path)
    segments = result["segments"]

    audio = Audio()

    with contextlib.closing(wave.open(path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)

    def segment_embedding(segment):
        start = segment["start"]
        end = min(duration, segment["end"])
        clip = Segment(start, end)
        waveform, sample_rate = audio.crop(path, clip)
        return embedding_model(waveform[None])

    embeddings = np.zeros(shape=(len(segments), 192))
    for i, segment in enumerate(segments):
        embeddings[i] = segment_embedding(segment)

    embeddings = np.nan_to_num(embeddings)

    clustering = AgglomerativeClustering(num_speakers).fit(embeddings)
    labels = clustering.labels_
    for i in range(len(segments)):
        segments[i]["speaker"] = 'SPEAKER ' + str(labels[i] + 1)

    def time(secs):
        return datetime.timedelta(seconds=round(secs))

    data_list = []
    for (i, segment) in enumerate(segments):
        data = {}
        data["role"] = segment["speaker"]
        data["text"] = segment["text"]
        data["timestamp"] = str(time(segment["start"]))
        data_list.append(data)

    return data_list