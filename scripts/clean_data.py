import os
import csv
import pandas as pd
import string

def save_words_to_csv():
    # List all .txt files in the episodes directory
    episodes_directory = 'episodes'
    txt_files = [f for f in os.listdir(episodes_directory) if f.endswith('.txt')]

    # Initialize the CSV file
    with open('data/breaking-bad-words.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['episode', 'text'])  # Write the header

        # Iterate through each .txt file
        for txt_file in txt_files:
            episode_name = os.path.splitext(txt_file)[0]  # Remove the file extension
            with open(os.path.join(episodes_directory, txt_file), 'r') as file:
                content = file.read()
                words = content.split()

                # Write each word as a separate row in the CSV, along with the episode name
                for word in words:
                    csv_writer.writerow([episode_name, word])

def word_counts_csv(file_path): 
    raw_csv = pd.read_csv(file_path)
    #raw_csv['text'] = raw_csv['text'].str.replace('.',' ')
    # remove punctuation (including periods), make all words lower case, resplit rows
    raw_csv['text'] = raw_csv['text'].str.lower().apply(lambda x: str(x).translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))).str.split()
    # explode rows so that each word is in its own row
    raw_csv = raw_csv.explode('text')
    word_counts = raw_csv['text'].value_counts().reset_index()
    # make text str type
    word_counts['text'] = word_counts['text'].astype(str)
    word_counts.columns = ['ngram', 'count']
    word_counts = word_counts.reset_index()
    word_counts.to_csv('data/corpus_data.csv', index=True)
    # flat count
    word_counts["count"] = 1
    word_counts.to_csv('data/corpus_data_flat.csv', index=False)
    

if __name__ == '__main__':
    #save_words_to_csv()
    word_counts_csv('data/breaking-bad-words.csv')