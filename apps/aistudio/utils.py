import base64
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def generate(ingredient_list):
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"""{ingredient_list}"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type = genai.types.Type.OBJECT,
            properties = {
                "response": genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    required = ["RecipeTitle", "Ingredients", "Category", "Instructions", "CookingTime"],
                    properties = {
                        "RecipeTitle": genai.types.Schema(
                            type = genai.types.Type.STRING,
                        ),
                        "Ingredients": genai.types.Schema(
                            type = genai.types.Type.ARRAY,
                            items = genai.types.Schema(
                                type = genai.types.Type.OBJECT,
                                required = ["name", "quantity"],
                                properties = {
                                    "name": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                    ),
                                    "quantity": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                        description = "Strictly use quantity in terms of grams",
                                    ),
                                },
                            ),
                        ),
                        "Category": genai.types.Schema(
                            type = genai.types.Type.STRING,
                            enum = ["veg", "nonveg"],
                        ),
                        "Instructions": genai.types.Schema(
                            type = genai.types.Type.ARRAY,
                            items = genai.types.Schema(
                                type = genai.types.Type.OBJECT,
                                required = ["step_number", "content"],
                                properties = {
                                    "step_number": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                    ),
                                    "content": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                    ),
                                },
                            ),
                        ),
                        "CookingTime": genai.types.Schema(
                            type = genai.types.Type.INTEGER,
                            description = "Time in minutes",
                        ),
                    },
                ),
            },
        ),
        system_instruction=[
            types.Part.from_text
            (
                text="""
                generate recipe  base on the input ingredients provided. 
                Use only provided ingredients. 
                If you are not familiar with ingredients, Reply (Invalid Ingredients).
                """
            ),
        ],
    )

    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        response_text += chunk.text

    # Convert response text to JSON and return
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response"}
