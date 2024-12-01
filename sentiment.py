from bs4 import BeautifulSoup
import re
import pandas as pd
import torch
from transformers import pipeline
import mwparserfromhell

grammar_model = pipeline("text-classification", model="textattack/distilbert-base-uncased-CoLA", device="mps")
sentiment_model = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", device="mps")

print("reading file...")
# Load the XML file
with open('extracted.xml', 'r') as file:
    xml_data = file.read()

print("parsing file...")
# Parse the XML using BeautifulSoup
soup = BeautifulSoup(xml_data, 'lxml')

data = []

# Patterns
image_pattern = r'\.(jpg|jpeg|png|gif)\b'
video_pattern = r'\.(mp4|mov|avi|mkv)\b'
media_pattern = r'\[\[.*?\]\]'

count = 0
pages = soup.find_all('page')
# Iterate through <page> elements
for page in pages:
    count += 1
    title = page.find('title').text if page.find('title') else 'No title'
    print(f"{count}/{len(pages)} ({title})", end='                                                                                                     \r')

    # Extract text content and its 'bytes' attribute
    text_element = page.find('text')
    text_content = text_element.text if text_element else ''
    bytes_value = text_element.get('bytes', 'Not Found') if text_element else 'Not Found'

    clean_text = text_content

    # Count occurrences
    images = len(re.findall(image_pattern, clean_text, re.IGNORECASE))
    videos = len(re.findall(video_pattern, clean_text, re.IGNORECASE))
    media_links = len(re.findall(media_pattern, clean_text))

    # gramatical correctness
    clean_text = re.sub(r'(=+)see also\1.*', '', clean_text, flags=re.IGNORECASE + re.DOTALL) # remove everything after "== see also =="
    clean_text = re.sub(r'\n(=+).*?\1\n', '', clean_text, flags=re.DOTALL) # remove headers
    clean_text = re.sub(r'<ref.*?>.*?</ref>', '', clean_text, flags=re.DOTALL) # remove anything inside html tags
    clean_text = re.sub(r'<imagemap.*?>.*?</imagemap>', '', clean_text, flags=re.DOTALL) # remove <imagemap></imagemap>
    clean_text = re.sub(r'<gallery.*?>.*?</gallery>', '', clean_text, flags=re.DOTALL) # remove <gallery></gallery>
    clean_text = re.sub(r'\[\[File:.*?\]\]', '', clean_text) # remove anything in [[File:]]
    clean_text = re.sub(r'\{\{infobox.*?\n\n\}\}', '', clean_text, flags=re.DOTALL + re.IGNORECASE) # remove {{Infobox}}
    clean_text = re.sub(r'\{\|.*?\|\}', '', clean_text, flags=re.DOTALL) # remove anyting in {||}
    clean_text = re.sub(r'\[\[([^\[\]]*?\|)?([^\[\]]*?)\]\]', lambda match : match.group(2), clean_text) # replace "[[a|b]]" with "b"
    # delete all the templates
    clean_text = mwparserfromhell.parse(clean_text).strip_code()
    # split text into sentences
    sentences = clean_text.split('. ')

    # check if the text is gramatically correct
    acceptable = 0
    unnacceptable = 0
    positive = 0
    negative = 0
    for sentence in sentences:
        if 512 > len(sentence) > 0:
            grammar = grammar_model(sentence)
            if grammar[0]['label'] == 'LABEL_1':
                acceptable += 1
            else:
                unnacceptable += 1
            sentiment = sentiment_model(sentence)
            if sentiment[0]['label'] == 'POSITIVE':
                positive += 1
            else:
                negative += 1

    # Append the data as a dictionary
    data.append({
        'Title': title,
        'Bytes': bytes_value,
        'Media Count': images + videos + media_links,
        'n_acceptable': acceptable,
        'n_unnacceptable': unnacceptable,
        'n_positive': positive,
        'n_negative': negative
    })

# Create a DataFrame for easier analysis
df = pd.DataFrame(data)

# Display the DataFrame
print(df)

# Save the DataFrame to a CSV file
df.to_csv('output.csv', index=False)