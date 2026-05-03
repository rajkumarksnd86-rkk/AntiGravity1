#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.theme import Theme
from google import genai
import PIL.Image

# Setup custom green theme
custom_theme = Theme({
    "info": "dim green",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "title": "bold dark_green",
})

console = Console(theme=custom_theme)

def setup_api():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        console.print("[error]Error: GEMINI_API_KEY environment variable is not set. Please set it before running the script.[/error]")
        sys.exit(1)
    return api_key

def analyze_image(image_path: str):
    if not os.path.exists(image_path):
        console.print(f"[error]Error: Image file '{image_path}' not found.[/error]")
        sys.exit(1)
        
    try:
        img = PIL.Image.open(image_path)
    except Exception as e:
        console.print(f"[error]Error opening image: {e}[/error]")
        sys.exit(1)

    console.print(Panel("[title]Plant Doctor[/title]\n[success]Analyzing your plant image... Please wait.[/success]", border_style="green"))

    try:
        api_key = setup_api()
        client = genai.Client(api_key=api_key)
        
        prompt = (
            "You are an expert botanist and plant pathologist. "
            "Please analyze this image of a plant. "
            "1. Identify the plant if possible. "
            "2. Identify any visible diseases, pests, or nutrient deficiencies. "
            "3. If a disease is found, provide a brief summary of the cause and recommended treatments. "
            "4. If the plant looks healthy, state that it appears healthy. "
            "Please keep the response concise and informative."
        )
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[prompt, img]
        )
        
        console.print("\n[bold green]Diagnosis Results:[/bold green]")
        md = Markdown(response.text)
        console.print(Panel(md, title="Plant Health Report", border_style="bold green"))
        
    except Exception as e:
         console.print(f"[error]An error occurred during analysis: {e}[/error]")

def main():
    parser = argparse.ArgumentParser(description="Identify plant diseases from an image.")
    parser.add_argument("image_path", type=str, help="Path to the plant image file.")
    
    args = parser.parse_args()
    
    analyze_image(args.image_path)

if __name__ == "__main__":
    main()
