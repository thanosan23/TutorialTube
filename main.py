import requests
import json
import urllib

import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer

import argparse

parser = argparse.ArgumentParser(prog='TutorialTube', description='Search for the best video',)

def add_video():
    input_url = input("Enter url: ")
    params = {"format": "json", "url": input_url}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string
    response = json.loads(requests.get(url).text)
    title = response['title']

    with open('videos.json', 'r') as f:
        data = json.loads(f.read())
    
    data["videos"].append({"title" : title, "url": input_url})

    with open('videos.json', 'w') as f:
        f.write(json.dumps(data))

def find_similar():
    input_query = input("Enter query: ")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    with open('videos.json', 'r') as f:
        data = json.loads(f.read())

    database = []
    for video in data["videos"]:
        database.append([video["title"], video["url"]])

    embeddings = model.encode(sentences=database)

    cos = nn.CosineSimilarity(dim=0)

    best = []

    input_query = torch.from_numpy(model.encode(input_query))

    for i, embedding in enumerate(embeddings):
        result = cos(input_query, torch.from_numpy(embedding))
        if(result > 0.5):
            best.append((result, database[i][0], database[i][1]))

    best.sort(key=lambda x:x[0])
    best.reverse()

    if len(best) == 0:
        print("No results!")
    else:
        print("Search results: ")
        out = []
        for i, e in enumerate(best):
            print(f"{i+1}. {e[1]} - {e[2]}")
            out.append([e[1], e[2]])

functions = {'add' : add_video,
             'find' : find_similar}

parser.add_argument('function', choices=functions.keys())
args = parser.parse_args()

func = functions[args.function]
func()