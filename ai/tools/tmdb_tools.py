"""
TMDB (The Movie Database) tools for movie search and details.
"""

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from clients import tmdb_client


@tool
def search_movies(query: str, limit: int = 5, config: RunnableConfig = None) -> list:
    """
    Search for movies from The Movie Database (TMDB).

    Returns up to LIMIT movies matching the query (maximum 25).

    Args:
        query: Search term to find movies by title
        limit: Number of results to return (max 25)
        config: Runtime configuration (automatically injected by LangGraph)

    Returns:
        List of movie dictionaries with id, title, overview, release_date, etc.
    """
    # Extract user_id from config for logging/permissions
    user_id = None
    if config:
        configurable = config.get("configurable") or config.get("metadata", {})
        user_id = configurable.get("user_id")

    # Log the search (optional)
    if user_id:
        print(f"[TMDB] User {user_id} searching for: {query}")

    # Call TMDB API
    response = tmdb_client.search_movie(query, raw=False)

    # Handle empty results
    try:
        total_results = int(response.get("total_results", 0))
    except (ValueError, TypeError):
        total_results = 0

    if total_results == 0:
        return []

    # Limit results to max 25
    if limit > 25:
        limit = 25

    results = response.get("results", [])[:limit]
    return results


@tool
def movie_detail(movie_id: int, config: RunnableConfig = None) -> dict:
    """
    Get detailed information about a specific movie from TMDB.

    Args:
        movie_id: The TMDB movie ID (obtained from search_movies)
        config: Runtime configuration (automatically injected by LangGraph)

    Returns:
        Dictionary with full movie details including budget, revenue, runtime,
        genres, production companies, etc.
    """
    # Extract user_id from config for logging/permissions
    user_id = None
    if config:
        configurable = config.get("configurable") or config.get("metadata", {})
        user_id = configurable.get("user_id")

    # Log the request (optional)
    if user_id:
        print(f"[TMDB] User {user_id} requesting movie details for ID: {movie_id}")

    # Call TMDB API
    response = tmdb_client.movie_detail(movie_id, raw=False)
    return response


# Export tools list for easy registration
tmdb_tools = [search_movies, movie_detail]
