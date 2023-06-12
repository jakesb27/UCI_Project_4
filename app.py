from flask import Flask, render_template, request
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, normalize
from sklearn.neighbors import NearestNeighbors
from fuzzywuzzy import process


###########################
##    Flask Functions    ##
###########################

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        movie = request.form['movie']
        data = get_movie(movie)
        return render_template('index.html', data=data)
    else:
        return render_template('index.html')


###########################################
##    Scikit Learn Function Functions    ##
###########################################

# Global variables
url = 'https://movie-recommender-2023.s3.us-west-2.amazonaws.com/titles.csv'
titles = pd.read_csv(url)
netflix_titles, knn, norm_data_df, title_names = None, None, None, None


# Function used to preprocess data and create dataframe
def prepare_df():
    global netflix_titles, knn, norm_data_df, title_names

    genres_list = titles.genres.to_list()

    # Finding all the unique genres
    unique_genres = unique(genres_list)

    for genre in unique_genres:
        titles[genre] = titles['genres'].str.contains(genre).astype('int')

    # dropping unneeded columns
    titles_clean = titles.drop(columns=['title', 'description', 'genres', 'imdb_id', 'production_countries'])

    # Define categorical variables
    cat_variables = titles_clean.dtypes[titles_clean.dtypes == "object"].index.tolist()[-2:]

    # Create a OneHotEncoder instance
    enc = OneHotEncoder(sparse=False)

    # Fit and transform the OneHotEncoder using the categorical variable list
    encode_df = pd.DataFrame(enc.fit_transform(titles_clean[cat_variables]))

    # Add the encoded variable names to the dataframe
    encode_df.columns = enc.get_feature_names_out(cat_variables)

    # Merge one-hot encoded features and drop the originals
    titles_clean = titles_clean.merge(encode_df, left_index=True, right_index=True)
    titles_clean = titles_clean.drop(cat_variables, axis=1)
    titles_clean = titles_clean.fillna(0).drop(columns='id')

    # Normalizing data
    norm_data = normalize(titles_clean)
    norm_data_df = pd.DataFrame(norm_data, columns=titles_clean.columns)

    knn = NearestNeighbors(metric='cosine', algorithm='brute')
    knn.fit(norm_data_df.values)  # Pass norm_data_df.values instead of norm_data_df

    # creating df of title names
    title_names = titles.loc[:, ['title']]
    title_names['title'] = title_names['title'].str.lower()
    netflix_titles = list(title_names.loc[:, 'title'])


# Get the unique genres
def unique(list_data):
    """Function used to get unique genres"""

    # Strip unwanted characters
    data_stripped = [data.strip("[]") for data in list_data]

    # Split string of genres into list of genres
    new_list = []
    for i in range(len(data_stripped)):
        new_list.append(data_stripped[i].split(','))
    temp_data = list({x for l in new_list for x in l})

    # Insert the list to the set
    list_set = set([s.strip("' ") for s in temp_data])

    # Convert the set to the list and filter blank values
    unique_list = (list(list_set))
    final_list = []
    for item in unique_list:
        if item == '':
            pass
        else:
            final_list.append(item)

    # Return list data
    return final_list


# Find matching title name in dataframe
def get_movie(title):
    """Function used to find matching titles in DataFrame"""

    title = title.lower()
    results = process.extract(title, netflix_titles, limit=5)

    if results[0][1] == 100:
        index = netflix_titles.index(title)
        return recommendations(index, title)
    elif results[0][1] >= 80:
        similar = [movie[0].title() for movie in results]
        return [1, similar, title.title()]
    else:
        no_match = [movie[0].title() for movie in results]
        return [2, no_match, title.title()]


# get the ten nearest neighbors
def recommendations(index, title):
    """Function used for finding the nearest neighbors"""

    neighbor_index = knn.kneighbors([norm_data_df.loc[index].values], return_distance=False, n_neighbors=11)
    neighbor_index = list(neighbor_index[0])
    neighbor_index = neighbor_index[1:11]
    recs = title_names.loc[neighbor_index]
    recs_list = recs.values.tolist()
    data = [item[0].title() for item in recs_list]
    return [0, data, title.title()]


if __name__ == '__main__':
    prepare_df()
    app.run(port=5001, debug=True)
