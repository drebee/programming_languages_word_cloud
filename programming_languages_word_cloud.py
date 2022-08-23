import pandas as pd
import re
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
from time import sleep
from random import random
import os
import glob
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import matplotlib.colors as clr

width = 24
height = 36
scale1 = 50
scale2 = 1

def get_pl_from_li(li):
    pl = re.sub(" ?/.*", "", li.text)
    pl = re.sub(" ?\(.*", "", pl)
    return pl
    
def get_pl_from_kw(kw):
    return kw.replace(" programming language", "")

def get_programming_languages():
    filename = "list_of_pl.html"
    # html = open("/Users/erinbennett/programming_languages_word_cloud/list_of_programming_languages.html")
    html = open(f"/Users/erinbennett/programming_languages_word_cloud/{filename}")
    page = BeautifulSoup(html)
    list_items = [get_pl_from_li(li) for li in page.find_all("li")]
    first_pl_index = list_items.index("4th Dimension")
    last_pl_index = list_items.index("Z shell")
    return list_items[first_pl_index:last_pl_index+1]

def get_trends_specific():
    # C++ programming language,21549,C++
    programming_languages = ["'c++' programming language"]

    pytrends = TrendReq(retries=2, backoff_factor=0.1)

    subset_dfs = []

    i = 50
    kw_list = [f"{pl} programming language" for pl in programming_languages]
    pytrends.build_payload(kw_list, cat=31, timeframe='today 5-y', geo='', gprop='')
    df = pytrends.interest_over_time()
    popularity_series = df.sum(axis=0)
    popularity_df = pd.DataFrame(popularity_series, columns = ["popularity"])
    popularity_df = popularity_df.loc[popularity_df.index != "isPartial"]
    popularity_df["programming_language"] = [get_pl_from_kw(pl) for pl in kw_list]
    popularity_df.to_csv(f"plpop{i}.csv")

def get_trends_data():

    programming_languages = get_programming_languages()

    pytrends = TrendReq(retries=2, backoff_factor=0.1)

    subset_dfs = []

    alread_visited = []
    subset_length = 5
    n_subsets = len(programming_languages)//subset_length
    for i in range(n_subsets):
        start_index = i*subset_length
        end_index = (i+1)*subset_length
        pl_subset = programming_languages[start_index:end_index]
        kw_list = pl_subset
        kw_list = [f"{pl} programming language" for pl in pl_subset]
        kw_list = [kw for kw in kw_list if kw not in alread_visited]
        kw_list = list(set(kw_list))
        alread_visited += kw_list
        if i > -1:
            pytrends.build_payload(kw_list, cat=31, timeframe='today 5-y', geo='', gprop='')
            df = pytrends.interest_over_time()
            if len(df) > 0:
                popularity_series = df.sum(axis=0)
                popularity_df = pd.DataFrame(popularity_series, columns = ["popularity"])
                popularity_df = popularity_df.loc[popularity_df.index != "isPartial"]
                popularity_df["programming_language"] = [get_pl_from_kw(pl) for pl in kw_list]
                subset_dfs.append(popularity_df)
                popularity_df.to_csv(f"plpop{i}.csv")
                sleep(random()*5 + 1)

def combine_dfs():
    # use glob to get all the csv files 
    # in the folder
    path = os.getcwd()
    csv_files = glob.glob(os.path.join(path, "*.csv"))
    
    subset_dfs = []
    # loop over the list of csv files
    for f in csv_files:
        
        # read the csv file
        df = pd.read_csv(f)
        
        subset_dfs.append(df)

    df = pd.concat(subset_dfs)
    df.to_csv("programming_language_popularity.csv")

# get_trends_specific()

# # get_trends_data()
# # pls = get_programming_languages()
# # print(pls)
combine_dfs()

df = pd.read_csv("programming_language_popularity.csv")
df = df.loc[df["popularity"] > 0]
text = df["popularity"]
text.index = df["programming_language"]
text = text.to_dict()
print(text)
# wordcloud = WordCloud(
#     max_words=200,
#     width = 1100,
#     height = 1700
# ).generate_from_frequencies(text)

# # Display the generated image:
# plt.imshow(wordcloud, interpolation='bilinear')
# plt.axis("off")
# plt.show()

# Generate a word cloud image
image_mask_file = "rect.png"
# image_mask_file = "flourish_square.png"
# image_mask_file = "kehillah_logo.png"
# image_mask_file = "flourish circle blue.png"
# image_mask_file = "flourish only.png"
mask = np.array(Image.open(image_mask_file))

# wordcloud = WordCloud(
#     max_words=200,
#     width = 1100,
#     height = 1700
# ).generate_from_frequencies(text)

# def get_color(word, font_size, position, orientation, font_path, random_state):
    

font_path = "brandon-grotesque-black-58a8a3e824392.otf"

# cmap = plt.colors.LinearSegmentedColormap('my_colormap2',cdict2,256)
cmap = clr.LinearSegmentedColormap.from_list('custom blue', ['#404154','#79B8D2'], N=10)


# generating word cloud
wordcloud = WordCloud(
    background_color="white", 
    mode="RGBA", 
    max_words=300, 
    width = width*scale1,
    height = height*scale1,
    # scale = 10,
    relative_scaling = 0.5,
    font_path = font_path,
    # color_func = get_color
    colormap = cmap
    #mask=mask
    ).generate_from_frequencies(text)

# # create coloring from image
# # image_colors = ImageColorGenerator(mask)
# plt.figure(figsize=[24,36])
# # plt.imshow(wordcloud.recolor(color_func=image_colors), interpolation="bilinear")
# plt.imshow(wordcloud, interpolation='bilinear')
# plt.axis("off")
# plt.show()

# # store to file
# plt.savefig("kehillah_programming_languages_word_cloud.png", format="png")

# plt.show()

# Display the generated image:
scale_factor = scale2
plt.figure(figsize=[width*scale_factor,height*scale_factor])
plt.imshow(wordcloud, interpolation='bilinear')
plt.tight_layout(pad=3)
plt.axis("off")
plt.savefig("kehillah_programming_languages_word_cloud.png", format="png")
plt.show()