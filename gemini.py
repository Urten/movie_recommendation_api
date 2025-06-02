from google import genai
import os
from schema import Movie_Response, Payload
import json
import logging
import asyncio
logging.basicConfig(level=logging.INFO)
from dotenv import load_dotenv
load_dotenv()


client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

async def get_movie_recommendation(payload: Payload, model_name="gemini-2.0-flash"):
    response = client.models.generate_content(
        model=model_name,
        contents="Give me a movie recommendation based on the following payload: " + str(payload),
        config={
            "response_mime_type": "application/json",
            "response_schema": Movie_Response,
        },
    )
    # Use the response as a JSON string.
    try:
        response = response.text
        print(response)
        return json.loads(response)
    except json.JSONDecodeError:
        logging.error("Error in get_movie_recommendation: Invalid JSON response")
        return False
    except genai.exceptions.UnavailableError as e:
        if e.error.code == 503 and e.error.message == "The model is overloaded. Please try again later.":
            logging.error(f"Error in get_movie_recommendation: {e}")
            try:
                asyncio.run(get_movie_recommendation(payload, model_name="gemini-2.0"))
            except Exception as e:
                logging.error(f"Error in get_movie_recommendation: {e}")
                return False
    except Exception as e:
        logging.error(f"Error in get_movie_recommendation: {e}")
        return False

# Use instantiated objects.


if __name__ == "__main__":
    payload = Payload(
        psychoactive_state="drunk",
        mood="happy",
        genre="comedy",
        already_watched=["The Matrix", "The Dark Knight"],
    )
    response = asyncio.run(get_movie_recommendation(payload))
    print(response)
