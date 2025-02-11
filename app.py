# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
import user_management
import recommendation

app = Flask(__name__)
DEFAULT_USER = user_management.DEFAULT_USER  # "Amir" per your module

@app.route('/')
def index():
    # Redirect to the Friends page by default
    return redirect(url_for('friends'))

@app.route('/friends')
def friends():
    # Get the friend list using the provided user_management module
    friends_list = user_management.get_friends(DEFAULT_USER)
    return render_template('friends.html', friends=friends_list)

@app.route('/watched_movies')
def watched_movies():
    query = "MATCH (p:Person {name: $username})-[:WATCHED]->(m:Movie) RETURN m.title AS title"
    # Convert the result to a list immediately
    result = list(user_management.db.query(query, {"username": DEFAULT_USER}))
    watched = [record["title"] for record in result]
    movies = [{'title': title, 'watched': True} for title in watched]
    return render_template('watched.html', movies=movies)


@app.route('/search', methods=['GET', 'POST'])
def search():
    movies = None
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        # Search for movies using the updated function
        movie_results = user_management.search_movies(search_term)  # Fetch title + genre

        # Build a list of movies with watched status for the current user
        movies = []
        for movie in movie_results:
            watched = user_management.has_watched_movie(DEFAULT_USER, movie["title"])
            movies.append({'title': movie["title"], 'genre': movie["genre"], 'watched': watched})

    return render_template('search.html', movies=movies)


@app.route('/recommendations')
def recommendations():
    # Get combined recommendations from the recommendation module
    rec_movies = recommendation.get_combined_recommendations(DEFAULT_USER)
    # Add watched status to each recommended movie
    for movie in rec_movies:
        movie['watched'] = user_management.has_watched_movie(DEFAULT_USER, movie['title'])
    return render_template('recommendations.html', movies=rec_movies)

@app.route('/toggle_movie_status', methods=['POST'])
def toggle_movie_status():
    # This endpoint toggles the watched status of a movie.
    movie_title = request.form.get('movie_title')
    if user_management.has_watched_movie(DEFAULT_USER, movie_title):
        # If movie is watched, remove the relationship
        user_management.remove_movie(DEFAULT_USER, movie_title)
        new_status = False
    else:
        # If movie is not watched, add the relationship
        user_management.add_movie(DEFAULT_USER, movie_title)
        new_status = True
    # Return the new status as JSON (to update the button via JavaScript)
    return jsonify({'watched': new_status})


if __name__ == '__main__':
    app.run(debug=True, port=5001)
