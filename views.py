import os
import markdown
import PIL.Image
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
try:
    from google import genai
except ImportError:
    # Fallback if genai is not installed
    pass

def setup_api():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it before running the server to avoid hardcoding secrets.")
    return api_key

def index(request):
    return render(request, 'detector/index.html')

def analyze(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        
        # Save temp file
        path = default_storage.save('temp.jpg', ContentFile(image_file.read()))
        full_path = os.path.join(settings.MEDIA_ROOT, path) if hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT else path
        
        try:
            img = PIL.Image.open(full_path)
            
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
            
            # Convert markdown to HTML
            html_result = markdown.markdown(response.text)
            
            # Clean up temp file
            if os.path.exists(full_path):
                os.remove(full_path)
                
            return render(request, 'detector/index.html', {'result': html_result})
            
        except Exception as e:
            if os.path.exists(full_path):
                os.remove(full_path)
            
            error_message = str(e)
            if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
                error_message = "API Rate Limit Exceeded. Please wait a minute and try again."
                
            return render(request, 'detector/index.html', {'error': error_message})

    return render(request, 'detector/index.html')
