#!/usr/bin/env python
"""
Quick test script for TMDB tools integration.
Run with: python test_tmdb.py
"""

import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from ai.tools.tmdb_tools import search_movies, movie_detail

def test_tmdb_tools():
    print("=" * 60)
    print("TMDB Tools Integration Test")
    print("=" * 60)
    
    # Test 1: Search for movies
    print("\n1️⃣  Testing search_movies...")
    print("-" * 60)
    
    try:
        results = search_movies.invoke({"query": "inception", "limit": 3})
        print(f"✅ Found {len(results)} movies")
        
        if results:
            print("\nResults:")
            for i, movie in enumerate(results, 1):
                print(f"  {i}. {movie.get('title', 'N/A')} ({movie.get('release_date', 'N/A')[:4]})")
                print(f"     ID: {movie.get('id')}, Rating: {movie.get('vote_average', 'N/A')}/10")
            
            # Test 2: Get movie details
            movie_id = results[0].get('id')
            print(f"\n2️⃣  Testing movie_detail for ID {movie_id}...")
            print("-" * 60)
            
            details = movie_detail.invoke({"movie_id": movie_id})
            print(f"✅ Retrieved movie details")
            print(f"\nMovie: {details.get('title', 'N/A')}")
            print(f"Tagline: {details.get('tagline', 'N/A')}")
            print(f"Budget: ${details.get('budget', 0):,}")
            print(f"Revenue: ${details.get('revenue', 0):,}")
            print(f"Runtime: {details.get('runtime', 'N/A')} minutes")
            
            genres = details.get('genres', [])
            if genres:
                genre_names = [g.get('name') for g in genres]
                print(f"Genres: {', '.join(genre_names)}")
        else:
            print("⚠️  No results found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ All TMDB tools tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_tmdb_tools()
    exit(0 if success else 1)
