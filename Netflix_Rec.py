import pandas as pd
import altair as alt
import numpy as np
from fuzzywuzzy import process

titles = pd.read_csv('https://movie-recommender-2023.s3.us-west-2.amazonaws.com/titles.csv')

# Checking data type of each column
titles.dtypes

# Preview of titles data
titles.head()

# looking what columns contain a lot of null values
Nullpercent = titles.isnull().sum().sort_values(ascending = False) / len(titles) * 100
null_df = pd.DataFrame({'Features': Nullpercent.index, 'Null_Value_Percentage': Nullpercent.values}).style.background_gradient(cmap='Blues')
null_df

# Finding all the unique genres
array = titles.genres.to_list()

array1 = [s.strip("[]") for s in array]

lst = []
for i in range(len(array1)):
    lst.append(array1[i].split(','))

result = list({x for l in lst for x in l})

result1 = [s.strip("' ") for s in result]

# function to get unique values
def unique(list1):
      
    # insert the list to the set
    list_set = set(list1)
    # convert the set to the list
    unique_list = (list(list_set))
    for x in unique_list:
        print(x),

results = unique(result1)

# Creating indictor columns for each genre
titles['horror'] = titles['genres'].str.contains('horror').astype('int')
titles['history'] = titles['genres'].str.contains('history').astype('int')
titles['european'] = titles['genres'].str.contains('european').astype('int')
titles['sport'] = titles['genres'].str.contains('sport').astype('int')
titles['family'] = titles['genres'].str.contains('family').astype('int')
titles['reality'] = titles['genres'].str.contains('reality').astype('int')
titles['drama'] = titles['genres'].str.contains('drama').astype('int')
titles['animation'] = titles['genres'].str.contains('animation').astype('int')
titles['comedy'] = titles['genres'].str.contains('comedy').astype('int')
titles['scifi'] = titles['genres'].str.contains('scifi').astype('int')
titles['music'] = titles['genres'].str.contains('music').astype('int')
titles['fantasy'] = titles['genres'].str.contains('fantasy').astype('int')
titles['western'] = titles['genres'].str.contains('western').astype('int')
titles['thriller'] = titles['genres'].str.contains('thriller').astype('int')
titles['documentation'] = titles['genres'].str.contains('documentation').astype('int')
titles['crime'] = titles['genres'].str.contains('crime').astype('int')
titles['action'] = titles['genres'].str.contains('action').astype('int')
titles['war'] = titles['genres'].str.contains('war').astype('int')
titles['romance'] =titles['genres'].str.contains('romance').astype('int')
titles.head()

# dropping unneeded columns
titles_mod1 = titles.drop(columns = ['title', 'description', 'genres', 'imdb_id', 'production_countries'])
titles_mod1

# creating indicator columns for show or movie
titles_mod1['movie'] = titles_mod1['type'].str.contains('MOVIE').astype('int')
titles_mod1['show'] = titles_mod1['type'].str.contains('SHOW').astype('int')
titles_mod1 = titles_mod1.drop(columns = 'type')

# creating indicator columns for age certification
unique(titles_mod1['age_certification'])

titles_mod1['not_rated'] = titles_mod1['age_certification'].isna().astype('int')
titles_mod1['TV-Y'] = titles_mod1['age_certification'].str.contains('TV-Y', na = False).astype('int')
titles_mod1['TV-PG'] = titles_mod1['age_certification'].str.contains('TV-PG', na = False).astype('int')
titles_mod1['PG'] = titles_mod1['age_certification'].str.contains('PG', na = False).astype('int')
titles_mod1['R'] = titles_mod1['age_certification'].str.contains('R', na = False).astype('int')
titles_mod1['TV-14'] = titles_mod1['age_certification'].str.contains('TV-14', na = False).astype('int')
titles_mod1['PG-13'] = titles_mod1['age_certification'].str.contains('PG-13', na = False).astype('int')
titles_mod1['TV-Y7'] = titles_mod1['age_certification'].str.contains('TV-Y7', na = False).astype('int')
titles_mod1['NC-17'] = titles_mod1['age_certification'].str.contains('NC-17', na = False).astype('int')
titles_mod1['G'] = titles_mod1['age_certification'].str.contains('G', na = False).astype('int')
titles_mod1['TV-G'] = titles_mod1['age_certification'].str.contains('TV-G', na = False).astype('int')
titles_mod1['TV-MA'] = titles_mod1['age_certification'].str.contains('TV-MA', na = False).astype('int')
titles_mod1 = titles_mod1.drop(columns = ['age_certification'])
titles_mod1.head()

# Changing NA's to zeros
titles_mod1 = titles_mod1.fillna(0).drop(columns='id')
titles_mod1.head()

# Normalizing data
normalized_data = (titles_mod1 - titles_mod1.min())/(titles_mod1.max() - titles_mod1.min())
normalized_data.head()

from sklearn.neighbors import NearestNeighbors

knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
knn.fit(normalized_data)

# creating df of title names
title_names = titles.loc[ : , ['title']]
title_names['title'] = title_names['title'].str.lower()
title_names.head()

#get the ten nearest neighbors
def recomendations(n):
    neighbor_index = knn.kneighbors([normalized_data.loc[n]], return_distance=False, n_neighbors=11)
    neighbor_index = list(neighbor_index[0])
    neighbor_index = neighbor_index[1:11]
    print("Recomendations for: " + title_names.loc[n, 'title'])
    print(title_names.loc[neighbor_index])

    netflix_titles = list(title_names.loc[:, 'title'])

def movie(title):
    title = title.lower()
    result = process.extract(title, netflix_titles, limit = 5)
    i = 1
    for mov in result:
        if (i == 1 and mov[1] <= 80):
            print('No close matches found. Try again.')
            break
        if mov[1] == 100:
            index = netflix_titles.index(title)
            recomendations(index)
            return
        if (mov[1] >= 80 and mov[1] != 100):
            if i == 1:
                print('Exact match not found for {}. Did you mean:'.format(title))
            print(str(i) + ') ' + mov[0])
            i = i+1

            
