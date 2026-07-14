import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'movies_db.json')

# Load dataset
if os.path.exists(db_path):
    with open(db_path, 'r', encoding='utf-8') as f:
        movies_db = json.load(f)
else:
    movies_db = []

def recommend_movies(genres, language, decade, min_rating, duration, actor_director, mood, content_pref, liked_movies=None):
    scored_movies = []
    
    # Extract liked movies profiles (genres, directors, cast) to build user profile
    liked_genres = set()
    liked_directors = set()
    liked_cast = set()
    
    if liked_movies:
        for title in liked_movies:
            # Find the movie in our db
            for m in movies_db:
                if m["title"].lower() == title.lower():
                    liked_genres.update(m["genres"])
                    liked_directors.add(m["director"].lower())
                    liked_cast.update(c.lower() for c in m["cast"])
                    break
    
    for movie in movies_db:
        # Skip if already liked (no need to recommend a movie they already like!)
        if liked_movies and movie["title"].lower() in [t.lower() for t in liked_movies]:
            continue
            
        # 1. Hard filters first (if applicable)
        
        # Content rating filter (Family-friendly excludes Adult movies)
        if content_pref == "Family-friendly" and movie["content_rating"] == "Adult":
            continue
            
        # Language filter (if specific language selected)
        if language != "All" and movie["language"].lower() != language.lower():
            continue
            
        # Minimum IMDb rating filter
        try:
            rating_clean = min_rating.replace("+", "").strip() if min_rating else "0.0"
            min_r = float(rating_clean)
            if movie["imdb_rating"] < min_r:
                continue
        except ValueError:
            pass

        # 2. Score calculation
        score = 0
        match_reasons = []

        # Genre matching (+4 for each match)
        if genres:
            matching_genres = [g for g in movie["genres"] if g in genres]
            if matching_genres:
                score += len(matching_genres) * 4
                match_reasons.append(f"Matches favorite genres: {', '.join(matching_genres)}")
        
        # Liked movies profile boost (+3 points per matching genre, +6 points if same director, +4 points if same cast)
        if liked_genres:
            matching_liked_genres = [g for g in movie["genres"] if g in liked_genres]
            if matching_liked_genres:
                score += len(matching_liked_genres) * 3
                if not any("Matches favorite genres" in r for r in match_reasons):
                    match_reasons.append(f"Similar genre to movies you liked")
                    
        if liked_directors and movie["director"].lower() in liked_directors:
            score += 6
            match_reasons.append(f"Directed by {movie['director']} (director of a movie you liked)")
            
        if liked_cast:
            matching_liked_cast = [c for c in movie["cast"] if c.lower() in liked_cast]
            if matching_liked_cast:
                score += 4
                match_reasons.append(f"Stars {', '.join(matching_liked_cast)} (from movies you liked)")

        # Mood matching (+5 points)
        if mood != "All":
            if mood in movie["moods"]:
                score += 5
                match_reasons.append(f"Great for your '{mood}' mood")
        
        # Decade matching (+3 points)
        if decade != "All":
            year = movie["release_year"]
            is_decade_match = False
            if decade == "2020s" and year >= 2020:
                is_decade_match = True
            elif decade == "2010s" and 2010 <= year <= 2019:
                is_decade_match = True
            elif decade == "2000s" and 2000 <= year <= 2009:
                is_decade_match = True
            elif decade == "1990s" and 1990 <= year <= 1999:
                is_decade_match = True
            elif decade == "1980s_older" and year < 1990:
                is_decade_match = True
                
            if is_decade_match:
                score += 3
                match_reasons.append(f"Released in the {decade}")
        
        # Duration matching (+3 points)
        if duration != "All":
            m_duration = movie["duration"]
            is_duration_match = False
            if duration == "Short" and m_duration < 90:
                is_duration_match = True
            elif duration == "Medium" and 90 <= m_duration <= 150:
                is_duration_match = True
            elif duration == "Long" and m_duration > 150:
                is_duration_match = True
                
            if is_duration_match:
                score += 3
                match_reasons.append(f"Fits preferred '{duration}' runtime")
        
        # Actor/Director matching (+10 points if search query matches)
        if actor_director.strip():
            query = actor_director.lower().strip()
            cast_match = any(query in actor.lower() for actor in movie["cast"])
            director_match = query in movie["director"].lower()
            if cast_match or director_match:
                score += 10
                match_reasons.append(f"Features cast/director: '{actor_director.strip()}'")

        # IMDb rating score boost (adds rating points to score)
        score += movie["imdb_rating"]
        
        # Format movie duration into hours/mins for display
        hours = movie["duration"] // 60
        mins = movie["duration"] % 60
        duration_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"

        scored_movies.append({
            "title": movie["title"],
            "language": movie["language"],
            "release_year": movie["release_year"],
            "genres": movie["genres"],
            "imdb_rating": movie["imdb_rating"],
            "duration_str": duration_str,
            "director": movie["director"],
            "cast": movie["cast"],
            "moods": movie["moods"],
            "content_rating": movie["content_rating"],
            "url": movie["url"],
            "poster_url": movie.get("poster_url", ""),
            "score": round(score, 1),
            "match_reasons": match_reasons
        })
        
    # Sort movies: highest score first
    scored_movies.sort(key=lambda x: x["score"], reverse=True)
    return scored_movies[:10]

@app.route('/', methods=['GET'])
def index():
    # Pass movie catalog sorted alphabetically by title for Step 2
    sorted_catalog = sorted(movies_db, key=lambda x: x["title"])
    return render_template('index.html', movies_catalog=sorted_catalog)

@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    data = request.get_json() or {}
    genres = data.get('genres', [])
    language = data.get('language', 'All')
    decade = data.get('decade', 'All')
    min_rating = data.get('min_rating', '6.0')
    duration = data.get('duration', 'All')
    actor_director = data.get('actor_director', '')
    mood = data.get('mood', 'All')
    content_pref = data.get('content_pref', 'Family-friendly')
    liked_movies = data.get('liked_movies', [])
    
    recommendations = recommend_movies(
        genres=genres,
        language=language,
        decade=decade,
        min_rating=min_rating,
        duration=duration,
        actor_director=actor_director,
        mood=mood,
        content_pref=content_pref,
        liked_movies=liked_movies
    )
    
    return jsonify({
        "success": True,
        "recommendations": recommendations
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)