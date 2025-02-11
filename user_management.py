from db import db

DEFAULT_USER = "Emil Eifrem"


def get_friends(username):
    query = "MATCH (:Person {name: $username})-[:FRIENDS_WITH]-(f:Person) RETURN f.name AS friend"

    with db._driver.session() as session:
        result = session.run(query, {"username": username})
        friends_list = [record["friend"] for record in result]  # Convert to list before consuming

    return friends_list


def add_friend(username, user):
    query = """MATCH (a:Person {name: $username}), (b:Person {name: $user}) 
                MERGE (a)-[:FRIENDS_WITH]-(b)"""

    with db._driver.session() as session:
        session.run(query, {"username": username, "user": user})


def remove_friend(username, user):
    query = """MATCH (a:Person {name: $username})-[r:FRIENDS_WITH]-(b:Person {name: $user}) 
                    DELETE r"""

    with db._driver.session() as session:
        session.run(query, {"username": username, "user": user})


def has_watched_movie(username, movie_title):
    query = """
    MATCH (p:Person {name: $username})-[:WATCHED]->(m:Movie {title: $movie_title})
    RETURN m LIMIT 1 """

    with db._driver.session() as session:
        result = session.run(query, {"username": username, "movie_title": movie_title})
        return result.single() is not None


def search_movies(search_term):
    query = """
    MATCH (m:Movie)
    WHERE m.title CONTAINS $search_term
    RETURN m.title AS title, m.genre AS genre
    """

    with db._driver.session() as session:
        result = session.run(query, {"search_term": search_term})
        movies = [{"title": record["title"], "genre": record["genre"]} for record in result]

    return movies


def add_movie(username, movie_name):
    query = """MATCH (a:Person {name: $username}), (m:Movie {title: $movie_name}) 
                MERGE (a)-[:WATCHED]->(m)"""

    with db._driver.session() as session:
        session.run(query, {"username": username, "movie_name": movie_name})


def remove_movie(username, movie_name):
    query = """MATCH (a:Person {name: $username})-[r:WATCHED]->(m:Movie {title: $movie_name}) 
                    DELETE r"""

    with db._driver.session() as session:
        session.run(query, {"username": username, "movie_name": movie_name})


def rate_movie(username, movie_name, rating):
    query = """
    MATCH (p:Person {name: $username}), (m:Movie {title: $movie_name})
    MERGE (p)-[r:WATCHED]->(m)
    SET r.weight = $rating
    RETURN r.weight AS weight
    """

    with db._driver.session() as session:
        session.run(query, {"username": username, "movie_name": movie_name, "rating": rating})
