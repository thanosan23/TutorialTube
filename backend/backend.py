from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import os   
import requests
import json
import urllib
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
import whisper
import pytube
from transformers import pipeline

app = Flask(__name__)

app.config['CORS_ORIGINS'] = '*'
app.config['CORS_SEND_WILDCARD'] = False
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'

CORS(app, resources={r"/*": {"origins": "*"}})

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

@app.route('/add_video', methods=['POST'])
def add_video_route():
    data = request.get_json()
    input_url = data.get("url")

    params = {"format": "json", "url": input_url}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string
    response = json.loads(requests.get(url).text)
    title = response['title']

    model = whisper.load_model("base")

    yt = pytube.YouTube(url=input_url)
    output = yt.streams.filter(only_audio=True).first().download()
    base, _ = os.path.splitext(output)
    filename = base + '.mp3'
    os.rename(output, filename)

    result = model.transcribe(filename)

    text = result["text"]
    segments = result["segments"]

    final_segments = []

    for seg in segments:
        s = {}
        s["start"] = seg["start"]
        s["end"] = seg["end"]
        s["text"] = seg["text"]
        final_segments.append(s)

    with open(os.path.join(SITE_ROOT, 'static', 'videos.json'), 'r') as f:
        data = json.loads(f.read())
    
    data["videos"].append({"title" : title, "url": input_url, "transcript": text, "segments": final_segments})

    with open(os.path.join(SITE_ROOT, 'static', 'videos.json'), 'w') as f:
        f.write(json.dumps(data))

    os.remove(filename)

    return jsonify({"status": "success"})

@app.route('/find_similar', methods=['GET'])
def find_similar_route():
    args = request.args
    input_query = args.get("query")

    model = SentenceTransformer('all-MiniLM-L6-v2')

    with open(os.path.join(SITE_ROOT, 'static', 'videos.json'), 'r') as f:
        data = json.loads(f.read())

    database = []
    
    transcripts = []
    segments = []

    for video in data["videos"]:
        database.append([video["title"], video["url"], video["transcript"]])
        transcripts.append(video["transcript"])
        segments.append(video["segments"])

    embeddings = model.encode(sentences=database)

    cos = nn.CosineSimilarity(dim=0)

    best = []

    input_query_embedding = torch.from_numpy(model.encode(input_query))

    nlp = pipeline('question-answering', 
                   model='deepset/roberta-base-squad2',
                   tokenizer='deepset/roberta-base-squad2')

    for i, embedding in enumerate(embeddings):
        result = cos(input_query_embedding, torch.from_numpy(embedding))
        if(result > 0.3):
            qa_input = {
                'context': transcripts[i],
                'question': input_query
            }
            response = nlp(qa_input)
            answer = response['answer']

            # get the timestamp
            cnt = 0
            segment = None
            for seg_num, seg in enumerate(segments[i]):
                for _ in seg["text"]:
                    if cnt != response["start"]:
                        cnt += 1
                    else:
                        segment = seg_num
                        break
                if segment != None:
                    break
            timestamp = int(segments[i][seg_num]["start"])

            best.append((result, database[i][0], database[i][1]+f"&t={timestamp}", answer))

    best.sort(key=lambda x:x[0])
    best.reverse()

    if len(best) == 0:
        return jsonify({"status": "No results!"})
    else:
        results = []
        for i, e in enumerate(best):
            results.append({"video": e[1], "url": e[2], "answer": e[3]})
        return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)