from db import db

# Recommendation Engine
# Rule No. 1: Recommend movies watched by friends that share the same genre (prioritizing the highest ranks first)
def recommend_movies_1(username):
    query = """
    MATCH (user:Person {name: $username})-[:WATCHED]->(m:Movie)
    WITH user, collect(DISTINCT m.genre) AS user_genres

    MATCH (user)-[:FRIENDS_WITH]-(friend:Person)-[r:WATCHED]->(rec_movie:Movie)
    WHERE rec_movie.genre IN user_genres 
          AND NOT (user)-[:WATCHED]->(rec_movie)
    RETURN rec_movie.title AS movie, rec_movie.genre AS genre, 
           COALESCE(r.weight, 0) AS weight
    ORDER BY weight DESC  
    """

    with db._driver.session() as session:
        result = session.run(query, {"username": username})
        recommendations = [{"title": record["movie"], "genre": record["genre"], "rate": record["weight"]} for record
                           in result]

    return recommendations


# Rule No. 2: Recommend movies watched by users who have watched at least 50% of the same movies as you,
# ignoring genre (prioritizing the highest ranks first)
def recommend_movies_2(username):
    query = """
        MATCH (user:Person {name: $username})-[:WATCHED]->(myMovie:Movie)
        WITH user, COLLECT(myMovie) AS myMovies, COUNT(myMovie) AS myCount  

        MATCH (otherUser:Person)-[:WATCHED]->(commonMovie:Movie)
        WHERE otherUser <> user AND commonMovie IN myMovies  
        WITH user, otherUser, myMovies, myCount, 
             COLLECT(commonMovie) AS commonMovies, COUNT(commonMovie) AS commonCount  

        WHERE commonCount * 1.0 / myCount >= 0.5  

        MATCH (otherUser)-[r:WATCHED]->(recMovie:Movie)
        WHERE NOT (user)-[:WATCHED]->(recMovie)  

        RETURN recMovie.title AS movie, recMovie.genre AS genre, 
               COLLECT(otherUser.name) AS recommendedBy, 
               COALESCE(AVG(r.weight), 0) AS weight  
        ORDER BY weight DESC  
        """

    with db._driver.session() as session:
        result = session.run(query, {"username": username})
        recommendations = [
            {"title": record["movie"], "genre": record["genre"], "recommended_by": record["recommendedBy"], "rate": record["weight"]}
            for record in result
        ]

    return recommendations


# Rule No. 3: Recommend up to 3 movies that belong to the same genres as the user's watched movies
# These movies must have the highest average rating (weight) given by other users
def recommend_movies_3(username):
    query = """
    MATCH (user:Person {name: $username})-[:WATCHED]->(watchedMovie:Movie)
    WITH user, COLLECT(DISTINCT watchedMovie.genre) AS userGenres

    MATCH (otherUser:Person)-[r:WATCHED]->(recMovie:Movie)
    WHERE recMovie.genre IN userGenres 
          AND NOT (user)-[:WATCHED]->(recMovie)

    WITH recMovie, recMovie.genre AS genre, 
         AVG(r.weight) AS avg_weight  
    ORDER BY avg_weight DESC  
    LIMIT 3  

    RETURN recMovie.title AS movie, genre, avg_weight
    """

    with db._driver.session() as session:
        result = session.run(query, {"username": username})
        recommendations = [
            {"title": record["movie"], "genre": record["genre"], "average_rate": record["avg_weight"]}
            for record in result
        ]

    return recommendations


def get_combined_recommendations(username):
    # Get recommendations from all three rules
    recommendations_1 = recommend_movies_1(username)
    recommendations_2 = recommend_movies_2(username)
    recommendations_3 = recommend_movies_3(username)

    combined_recommendations = {}

    # Process Rule 1 recommendations
    for rec in recommendations_1:
        title = rec["title"]
        if title not in combined_recommendations:
            combined_recommendations[title] = {"title": title, "genre": rec["genre"]}

    # Process Rule 2 recommendations
    for rec in recommendations_2:
        title = rec["title"]
        if title not in combined_recommendations:
            combined_recommendations[title] = {"title": title, "genre": rec["genre"]}

    # Process Rule 3 recommendations
    for rec in recommendations_3:
        title = rec["title"]
        if title not in combined_recommendations:
            combined_recommendations[title] = {"title": title, "genre": rec["genre"]}

    # Convert dictionary values to a list
    final_recommendations = list(combined_recommendations.values())

    return final_recommendations


# Close the database connection
db.close()