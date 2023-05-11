import nltk
from nltk.corpus import stopwords
import shifterator as sh
import pandas as pd
import matplotlib.pyplot as plt

nltk.download('stopwords')
stops = set(stopwords.words('english'))

bb_data = pd.read_csv("../data/ousiometer_breaking_bad.csv")


#cols = ["valence" , "arousal", "dominance", "goodness",  "energy",  "structure",  "power",  "danger"]

# get user input for which column to use
cols = input("Enter columns to use, separated by a space: ").split()

# get user input for two seasons to compare
seasons = input("Enter two seasons to compare, separated by a space: ").split()

# get user input for episode numbers
episodes = input("Enter two episodes to compare, separated by a space: ").split()

# two dataframes, one first season, one 5th seasno
# first half is first set of season/episode input, second half is second set of season/episode input
bb_first_half = bb_data[(bb_data["season"] == int(seasons[0])) & (bb_data["episode"] == int(episodes[0]))]
bb_second_half = bb_data[(bb_data["season"] == int(seasons[1])) & (bb_data["episode"] == int(episodes[1]))]

print(bb_first_half.head())

for col in cols:
    print(col)
    # get a dictionary of distinct words and their average danger score, dropped inf and nan values
    distinct_words_scores = bb_data[["text", col]].dropna().drop_duplicates().groupby("text").mean().to_dict()[col]

    sentiment_shift = sh.WeightedAvgShift(bb_first_half["text"].value_counts().to_dict(),
                                        bb_second_half["text"].value_counts().to_dict(),
                                            type2score_1=distinct_words_scores,
                                    reference_value = bb_first_half[col].mean(),
                                        stop_words = stops
                                        )

    shift_graph = sentiment_shift.get_shift_graph(system_names =  [f'Season {seasons[0]} Episode {episodes[0]} ', f'Season {seasons[1]} Episode {episodes[1]}'],
                                                show_plot=False)

    plt.savefig(f"../plots/bb_{col}shift.png")

