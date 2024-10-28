import streamlit as st
import pickle
import pandas as pd
import requests

# Load movie data and similarity matrix
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity', 'rb'))


# Function to fetch movie poster and details from TMDB
def fetch_poster(movie_id):
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=69b75c63148341b985cc4b23aa819ff4&language=en-US')
        response.raise_for_status()
        data = response.json()
        genres = ', '.join([genre['name'] for genre in data['genres']])  # Extract genres
        runtime = data['runtime']  # Extract runtime
        return "https://image.tmdb.org/t/p/w500/" + data['poster_path'], genres, runtime, data['release_date'], data[
            'vote_average']
    except Exception as e:
        st.error(f"Failed to fetch poster: {e}")
        return None, None, None, None, None


# Recommend movies based on similarity
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommend_movies = []
    recommend_movies_posters = []
    movie_details = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        movie_title = movies.iloc[i[0]].title
        poster, genres, runtime, release_date, rating = fetch_poster(movie_id)
        recommend_movies.append(movie_title)
        recommend_movies_posters.append(poster)
        movie_details.append((genres, runtime, release_date, rating))
    return recommend_movies, recommend_movies_posters, movie_details

# Set page configuration
st.set_page_config(
    page_title="Movie Recommender",  # Title of the page
    page_icon="🎬",                   # Icon displayed in the browser tab
    layout="wide",                    # Layout style
    initial_sidebar_state="expanded"  # Sidebar state
)

# Streamlit App Layout
st.markdown("<h1 style='text-align: center; color: #FF6347;'>🎬 Movie Recommender System 🍿</h1>",
            unsafe_allow_html=True)

# Movie select box
selected_movie_name = st.selectbox(
    "Search and select a movie:",
    movies['title'].values
)

# When the 'Recommend' button is clicked
if st.button("Recommend"):
    with st.spinner("Fetching recommendations..."):
        names, posters, details = recommend(selected_movie_name)

    # Display recommendations in columns with additional info
    col1, col2, col3, col4, col5 = st.columns(5)

    columns = [col1, col2, col3, col4, col5]

    for i in range(5):
        with columns[i]:
            st.text(names[i])
            st.image(posters[i], use_column_width=True)
            st.markdown(f"**Genres:** {details[i][0]}")
            st.markdown(f"**Runtime:** {details[i][1]} min")
            st.markdown(f"**Release Date:** {details[i][2]}")
            st.markdown(f"**Rating:** {details[i][3]} ⭐")

