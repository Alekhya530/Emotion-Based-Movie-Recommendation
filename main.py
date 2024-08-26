from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
import webbrowser

# Replace with your own Spotify API credentials
SPOTIPY_CLIENT_ID = '7e197dd4ccfb4e8ab8ef7d6decc77ffe'
SPOTIPY_CLIENT_SECRET = '9e8bce6b3d4545f6988ba69af1cd0a44'

app = Flask(__name__)

def get_spotify_client():
    return spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

def get_track_details(query):
    sp = get_spotify_client()
    results = sp.search(q=query, type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        return track['external_urls']['spotify']
    return None

def get_book_details(emotion):
    emotion = emotion.lower()
    emotion_genres = {
        "sad": "drama",
        "disgust": "musical",
        "anger": "action",
        "anticipation": "thriller",
        "fear": "horror",
        "enjoyment": "comedy",
        "trust": "family",
        "surprise": "mystery"
    }
    if emotion not in emotion_genres:
        return []
    genre = emotion_genres[emotion]
    search_url = f"https://www.goodreads.com/search?q={requests.utils.quote(genre)}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return []
    soup = BeautifulSoup(response.content, 'html.parser')
    book_elements = soup.find_all('a', class_='bookTitle')
    if not book_elements:
        return []
    titles = [book_element.get_text(strip=True) for book_element in book_elements[:10]]
    return titles

def get_movie_recommendations(emotion):
    emotion = emotion.lower()
    emotion_genres = {
        "sad": "drama",
        "disgust": "musical",
        "anger": "action",
        "anticipation": "thriller",
        "fear": "horror",
        "enjoyment": "comedy",
        "trust": "family",
        "surprise": "mystery"
    }
    if emotion not in emotion_genres:
        return []
    genre = emotion_genres[emotion]
    api_key = "59cd77c5"  # Replace with your actual OMDb API key
    url = "http://www.omdbapi.com/"
    params = {"apikey": api_key, "type": "movie", "s": genre}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to retrieve data from OMDb: {e}")
        return []
    data = response.json()
    if "Search" not in data:
        return []
    return [movie["Title"] for movie in data["Search"]]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    choice = request.form.get('choice')
    query = request.form.get('query')
    emotion = request.form.get('emotion')
    result = None

    if choice == '1':
        track_url = get_track_details(query)
        result = {'track_url': track_url} if track_url else {'error': 'No track found'}

    elif choice == '2':
        movie_titles = get_movie_recommendations(emotion)
        result = {'movies': movie_titles} if movie_titles else {'error': 'No movies found'}

    elif choice == '3':
        book_titles = get_book_details(emotion)
        result = {'books': book_titles} if book_titles else {'error': 'No books found'}

    return render_template('result.html', result=result, choice=choice)

if __name__ == '__main__':
    app.run(debug=True)
