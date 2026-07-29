#!/usr/bin/env python3
"""Simple Perplexity search via the OpenRouter API."""

import os
import sys


def client():
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is required")

    from openai import OpenAI

    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)


def search(query: str, model: str = "perplexity/sonar-pro"):
    """Search using Perplexity Sonar through OpenRouter."""
    try:
        response = client().chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": query}],
            extra_headers={
                "HTTP-Referer": "https://siso.ai",
                "X-Title": "SISO Research",
            },
        )
        return response.choices[0].message.content
    except SystemExit:
        raise
    except Exception as error:
        return f"Error: {error}"


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "test"
    print(search(query))
