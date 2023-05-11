import pandas as pd
import string
import seaborn as sns
import matplotlib.pyplot as plt
import sys

# Get a string of all punctuation characters
punctuations = string.punctuation

# command line argument for rolling window size
window_size = int(sys.argv[1])


# read script data from /data
script_data = pd.read_csv('../data/breaking-bad-words.csv')
# make all words in text lower case

# line number by season and episode


script_data['text'] = script_data['text'].str.lower()
# Remove punctuation from the 'text' column
script_data['text'] = script_data['text'].str.translate(str.maketrans('', '', punctuations))
# extract season and episode from episode column
script_data['season'] = script_data['episode'].str.extract('(\d+)').astype(int)
script_data['episode'] = script_data['episode'].str.extract('(\d+$)').astype(int)

# remove empty rows
script_data = script_data.dropna(subset=['text'])

script_data['line_number'] = script_data.groupby(["season", "episode"]).cumcount() + 1




# count unique words in the script data
print("unique words in script data:")
unique_script_words = len(script_data['text'].unique())
print(unique_script_words)
# read ousiometry tsv data 
ousiometry_data = pd.read_csv('../data/ousiometry_data_augmented.tsv', sep='\t')

# proportion of unique words in ousiometry data that are in script data
print(len(ousiometry_data[ousiometry_data['word'].isin(script_data['text'].unique())]['word'].unique()) / len(ousiometry_data['word'].unique()))


# merge script data with ousiometry data on text = word
merged_data = pd.merge(script_data, ousiometry_data, left_on='text', right_on='word', how='left')


# create key of distinct season and episodes, ordered and indexed in a new df with the index named key
seasons = merged_data[['season', 'episode']].drop_duplicates().sort_values(['season', 'episode']).reset_index(drop=True).reset_index().rename(columns={'index': 'key'})
seasons["key"] = seasons["key"] + 1

# merge seasons with merged_data on season and episode
merged_data = pd.merge(merged_data, seasons, on=['season', 'episode'], how='left')
merged_data = merged_data.sort_values(by=["season", "episode", "line_number"]).reset_index()
merged_data["overall_line_number"] = merged_data.reset_index().index + 1

# write merged data to csv
merged_data.to_csv('../data/ousiometer_breaking_bad.csv', index=False)

# calculate rolling average of power, danger, energy, structure, goodness by a window of 100 overall_line_number, ignoring NaN values
merged_data["power_rolling_avg"] = merged_data["power"].rolling(window_size, min_periods=1).mean()
merged_data["danger_rolling_avg"] = merged_data["danger"].rolling(window_size, min_periods=1).mean()
merged_data["energy_rolling_avg"] = merged_data["energy"].rolling(window_size, min_periods=1).mean()
merged_data["structure_rolling_avg"] = merged_data["structure"].rolling(window_size, min_periods=1).mean()
merged_data["goodness_rolling_avg"] = merged_data["goodness"].rolling(window_size, min_periods=1).mean()
# number of unique words in rolling window
def unique_word_count(text_list):
    words = set()
    for text in text_list:
        words.update(set(text.split()))
    return len(words)

merged_data['unique_words_rolling_window'] = merged_data['text'].rolling(window=window_size).apply(lambda x: unique_word_count(x), raw=False)


merged_data['rolling_average_unique_words'] = merged_data['unique_word_count'].rolling(window=window_size).mean()



# filter out first 100 lines
merged_data = merged_data[merged_data["overall_line_number"] > window_size]

## pivot table so that all rolling avg columns are in one column
merged_data_melted = merged_data.melt(id_vars=['season', 'episode', 'line_number', 'text', 'word', 'key', 'overall_line_number'], value_vars=['power_rolling_avg', 'danger_rolling_avg', 'energy_rolling_avg', 'structure_rolling_avg', 'goodness_rolling_avg'], var_name='metric', value_name='rolling_avg')

# visualize rolling averages in seaborn, faceted by metric
g = sns.FacetGrid(merged_data_melted, col="metric", col_wrap=3, hue="metric", sharey=False, sharex=True)
g.map(plt.plot, "overall_line_number", "rolling_avg", alpha=.7)
g.set_axis_labels("Line Number", "Rolling Average")
g.set_titles("{col_name}")
g.tight_layout()
# save plot in plots folder one level up
plt.savefig(f'../plots/rolling-averages_{window_size}.png')

print("Bottom 10 lines by danger")
print(merged_data.sort_values(by=["danger_rolling_avg"], ascending=True).head(10))


print("Bottom 10 lines by ernergy")
print(merged_data.sort_values(by=["energy_rolling_avg"], ascending=True).head(10))