#!/usr/bin/env python3
"""Simple Perplexity search via OpenRouter API."""

import os
import json
import sys

# Set API key
os.environ["OPENROUTER_API_KEY"] = "REMOVED_OPENROUTER_KEY"

from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

def search(query: str, model: str = "perplexity/sonar-pro"):
    """Search using Perplexity Sonar via OpenRouter."""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": query
                }
            ],
            extra_headers={
                "HTTP-Referer": "https://siso.ai",
                "X-Title": "SISO Research"
            }
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "test"
    result = search(query)
    print(result)
