# TMDB Tools Documentation

## Overview

The TMDB (The Movie Database) tools provide movie discovery capabilities through integration with the TMDB API. These tools allow users to search for movies and retrieve detailed information about specific titles.

## Architecture

### Integration Pattern

The TMDB tools follow the established architectural patterns:

1. **RunnableConfig Pattern**: User context is passed via `RunnableConfig` for logging and future permission extensions
2. **Client Abstraction**: Uses the existing `clients.tmdb_client` for API communication
3. **Modular Structure**: Located in `ai/tools/tmdb_tools.py` following the project's modular tool organization
4. **Official Agent Pattern**: Integrated via `create_agent` from LangChain

### File Structure

```
ai/
├── tools/
│   ├── tmdb_tools.py      # TMDB tool implementations
│   └── __init__.py         # Exports tmdb_tools
├── agents.py               # create_movie_agent()
└── utils.py                # Includes tmdb_tools in get_all_available_tools()
```

## Available Tools

### 1. search_movies

Search for movies by title in The Movie Database.

**Function Signature:**
```python
@tool
def search_movies(query: str, limit: int = 5, config: RunnableConfig = None) -> list
```

**Parameters:**
- `query` (str): Search term to find movies by title
- `limit` (int): Number of results to return (default 5, max 25)
- `config` (RunnableConfig): Runtime configuration with user context (auto-injected by LangGraph)

**Returns:**
- List of movie dictionaries with:
  - `id`: TMDB movie ID
  - `title`: Movie title
  - `overview`: Movie synopsis
  - `release_date`: Release date
  - `vote_average`: Rating
  - `poster_path`: Poster image path
  - Additional metadata

**Example Usage:**
```python
# User asks: "Find movies about space exploration"
results = search_movies("space exploration", limit=10)
# Returns list of space-themed movies
```

**Error Handling:**
- Returns empty list `[]` if no results found
- Limits results to maximum 25 to prevent token overflow
- Handles malformed responses gracefully

### 2. movie_detail

Get detailed information about a specific movie.

**Function Signature:**
```python
@tool
def movie_detail(movie_id: int, config: RunnableConfig = None) -> dict
```

**Parameters:**
- `movie_id` (int): TMDB movie ID (obtained from search_movies)
- `config` (RunnableConfig): Runtime configuration with user context (auto-injected by LangGraph)

**Returns:**
- Dictionary with comprehensive movie details:
  - Basic info: title, overview, release_date
  - Financial: budget, revenue
  - Runtime and genres
  - Production companies and countries
  - Cast and crew (if available)
  - Additional metadata

**Example Usage:**
```python
# User asks: "Tell me more about The Matrix"
# First search for the movie
results = search_movies("The Matrix")
movie_id = results[0]["id"]  # Get ID from first result

# Then get details
details = movie_detail(movie_id)
# Returns full movie information
```

## Movie Agent

### Configuration

The `movie_agent` is configured in `ai/agents.py`:

```python
def create_movie_agent(checkpointer=None):
    """
    Creates a movie discovery agent using create_agent.
    
    Returns:
        CompiledStateGraph: A compiled agent ready to use
    """
    llm = get_llm("movie_agent")
    tools = load_tools_for_agent("movie_agent")
    
    if checkpointer is None:
        checkpointer = MemorySaver()
    
    agent = create_agent(
        model=llm,
        tools=tools,
        prompt="You are a movie discovery agent. Help users search for movies and get detailed information from The Movie Database (TMDB).",
        checkpointer=checkpointer,
        name="movie_agent",
    )
    
    return agent
```

### Database Configuration (seed_agents.py)

```python
{
    "key": "movie_agent",
    "name": "Movie Agent",
    "role": "Movie Discovery",
    "llm_provider": "openai",
    "llm_model": "gpt-4o",
    "temperature": 0.3,  # Slightly creative for recommendations
    "system_prompt": "You are a movie discovery agent. You help users search for movies and get detailed information from The Movie Database (TMDB).",
}
```

## User Context & Permissions

### Current Implementation

The tools extract user context from `RunnableConfig` for logging:

```python
user_id = None
if config:
    configurable = config.get('configurable') or config.get('metadata', {})
    user_id = configurable.get('user_id')

if user_id:
    print(f'[TMDB] User {user_id} searching for: {query}')
```

### Future Permissions

While currently all users have read access to TMDB data (it's public information), the infrastructure is in place for future extensions:

1. **Rate Limiting**: Track API usage per user
2. **Premium Features**: Restrict certain detailed queries to premium users
3. **Usage Analytics**: Track popular searches and recommendations

Add to `ai/permissions.py`:
```python
def check_permission(user_id: int, action: str, resource: str) -> bool:
    if resource == "tmdb":
        # All users can search/read public movie data
        return action in ["search", "read"]
    # ...
```

## Integration with Supervisor

The movie_agent is integrated into the supervisor system in `ai/graph.py`:

```python
from langgraph_supervisor import create_supervisor
from .agents import get_all_agents

# get_all_agents() now includes movie_agent
supervisor = create_supervisor(
    agents=get_all_agents(checkpointer),
    model=supervisor_llm,
    prompt=SUPERVISOR_PROMPT,
)
```

The supervisor will route movie-related queries to the movie_agent:

**User Query Examples:**
- "Find movies similar to Inception"
- "What are the top-rated sci-fi movies?"
- "Tell me about the latest Marvel movie"
- "Show me details for movie ID 550"

## Testing

### Manual Testing

```python
# Test search
from ai.tools.tmdb_tools import search_movies
results = search_movies("interstellar", limit=3)
print(results)

# Test detail
from ai.tools.tmdb_tools import movie_detail
details = movie_detail(157336)  # Interstellar's TMDB ID
print(details)
```

### Integration Testing

```python
# Test via agent
from ai.agents import create_movie_agent

agent = create_movie_agent()
response = agent.invoke({
    "messages": [("user", "Find sci-fi movies about time travel")]
})
print(response)
```

## Error Handling

### Network Errors
The underlying `tmdb_client` handles network errors. Tools return gracefully:
- `search_movies`: Returns `[]` on error
- `movie_detail`: Returns `{}` or error message

### Invalid Input
- Invalid movie_id: TMDB API returns 404, tool returns error message
- Empty query: Returns empty results
- Limit too high: Automatically capped at 25

### Logging
All tool calls are logged with user context:
```
[TMDB] User 42 searching for: blade runner
[TMDB] User 42 requesting movie details for ID: 78
```

## Best Practices

### 1. Search First, Then Get Details
```python
# Good: Two-step approach
results = search_movies("the matrix")
details = movie_detail(results[0]["id"])

# Avoid: Direct ID lookup without search context
details = movie_detail(603)  # How did we get this ID?
```

### 2. Reasonable Limits
```python
# Good: Reasonable limit for conversation
search_movies("action movies", limit=5)

# Avoid: Too many results
search_movies("action movies", limit=50)  # Will be capped at 25
```

### 3. Handle Empty Results
```python
results = search_movies("xyzabc123impossible")
if not results:
    # Inform user no results found
    return "No movies found matching your search."
```

## Configuration

### Required Environment Variables

The TMDB client requires configuration in Django settings:

```python
# settings.py
TMDB_API_KEY = env("TMDB_API_KEY")  # Required for API authentication
```

### Optional Configuration

Future enhancements could include:
```python
TMDB_LANGUAGE = "en-US"  # Default language for results
TMDB_INCLUDE_ADULT = False  # Filter adult content
TMDB_RATE_LIMIT = 40  # Requests per 10 seconds
```

## Future Enhancements

### 1. Additional Tools
```python
@tool
def get_movie_recommendations(movie_id: int) -> list:
    """Get similar movie recommendations based on a movie ID."""
    
@tool
def search_by_genre(genre: str, limit: int = 10) -> list:
    """Search movies by genre."""
    
@tool
def get_trending_movies(time_window: str = "week") -> list:
    """Get trending movies for the week or day."""
```

### 2. Caching
Implement caching for frequently requested movie details:
```python
from django.core.cache import cache

def movie_detail(movie_id: int, config: RunnableConfig = None) -> dict:
    cache_key = f"tmdb_movie_{movie_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    result = tmdb_client.movie_detail(movie_id)
    cache.set(cache_key, result, timeout=3600)  # 1 hour
    return result
```

### 3. User Preferences
Store user preferences for personalized recommendations:
```python
class UserMoviePreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    favorite_genres = models.JSONField(default=list)
    watched_movies = models.JSONField(default=list)
```

## Troubleshooting

### Tool Not Found Error
```
Error loading tool ai.tools.tmdb_tools.search_movies: No module named 'tmdb_tools'
```
**Solution**: Ensure `tmdb_tools` is exported in `ai/tools/__init__.py`

### API Key Error
```
401 Unauthorized: Invalid API key
```
**Solution**: Check `TMDB_API_KEY` in `.env` file

### Empty Results
```
User asks: "Find movies about xyz" → Returns []
```
**Solution**: This is expected behavior. TMDB API returned no results for that query.

## References

- [TMDB API Documentation](https://developers.themoviedb.org/3)
- [LangChain Tools Documentation](https://python.langchain.com/docs/modules/tools/)
- [RunnableConfig Pattern](./FINAL_ARCHITECTURE.md#user-context-propagation)
- [Supervisor Pattern](./SUPERVISOR_PATTERN.md)
