from pydantic import BaseModel, Field
from typing import Literal, Optional, List

pyschoactive_state_literal = Literal["drunk", "sober", "high"]
mood_literal = Literal["happy", "sad", "neutral"]
genre_literal = Literal["romance", "horror", "comedy", "thriller", "drama"]

class Payload(BaseModel):
    psychoactive_state: pyschoactive_state_literal = Field(
        description="""all the psychoactive states are: drunk, sober, high
                      - recommend movies based on this"""
    )
    
    mood: mood_literal = Field(
        description="""this is the mood of the user,
                      what the user is currently feeling right now"""
    )
    
    # Fix the genre field:
    genre: genre_literal = Field(
        default="comedy",  # or use a valid default from your literal
        description="Genre preference"
    )
    
    # Fix the list type annotation:
    already_watched: Optional[List[str]] = Field(
        default=None,
        description="List of movies already watched, Don't recommend movies present on this list"
    )# all the movies already watched will be added to this list variable



class Movie_Response(BaseModel):
    movie_name: str = Field(description="Name of the movie")