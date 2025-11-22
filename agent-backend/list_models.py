"""
List all available OpenAI models for your API key.
"""
import os
import json
import httpx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

http_client = httpx.Client(
    timeout=30.0,
    limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
)

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    http_client=http_client
)

print("=" * 80)
print("Fetching Available OpenAI Models")
print("=" * 80)
print()

try:
    # Fetch all models
    models = client.models.list()
    
    print(f"Total models available: {len(models.data)}\n")
    print("-" * 80)
    
    # Group models by type
    chat_models = []
    embedding_models = []
    image_models = []
    audio_models = []
    other_models = []
    
    for model in models.data:
        model_id = model.id
        if 'gpt' in model_id.lower() or 'chat' in model_id.lower():
            chat_models.append(model)
        elif 'embedding' in model_id.lower() or 'text-embedding' in model_id.lower():
            embedding_models.append(model)
        elif 'dall-e' in model_id.lower() or 'image' in model_id.lower():
            image_models.append(model)
        elif 'whisper' in model_id.lower() or 'audio' in model_id.lower() or 'tts' in model_id.lower():
            audio_models.append(model)
        else:
            other_models.append(model)
    
    # Display chat models (most relevant for assistants)
    if chat_models:
        print("\n🤖 CHAT MODELS (for Assistants):")
        print("-" * 80)
        for model in sorted(chat_models, key=lambda x: x.id):
            print(f"  • {model.id}")
            if hasattr(model, 'created') and model.created:
                print(f"    Created: {model.created}")
            print()
    
    # Display embedding models
    if embedding_models:
        print("\n📊 EMBEDDING MODELS:")
        print("-" * 80)
        for model in sorted(embedding_models, key=lambda x: x.id):
            print(f"  • {model.id}")
            if hasattr(model, 'created') and model.created:
                print(f"    Created: {model.created}")
            print()
    
    # Display image models
    if image_models:
        print("\n🎨 IMAGE MODELS:")
        print("-" * 80)
        for model in sorted(image_models, key=lambda x: x.id):
            print(f"  • {model.id}")
            if hasattr(model, 'created') and model.created:
                print(f"    Created: {model.created}")
            print()
    
    # Display audio models
    if audio_models:
        print("\n🎵 AUDIO MODELS:")
        print("-" * 80)
        for model in sorted(audio_models, key=lambda x: x.id):
            print(f"  • {model.id}")
            if hasattr(model, 'created') and model.created:
                print(f"    Created: {model.created}")
            print()
    
    # Display other models
    if other_models:
        print("\n📦 OTHER MODELS:")
        print("-" * 80)
        for model in sorted(other_models, key=lambda x: x.id):
            print(f"  • {model.id}")
            if hasattr(model, 'created') and model.created:
                print(f"    Created: {model.created}")
            print()
    
    # Show recommended models for assistants
    print("\n" + "=" * 80)
    print("RECOMMENDED MODELS FOR ASSISTANTS:")
    print("=" * 80)
    recommended = [m.id for m in chat_models if any(x in m.id.lower() for x in ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'])]
    if recommended:
        for model_id in sorted(recommended):
            print(f"  ✓ {model_id}")
    else:
        print("  (No standard GPT models found)")
    
    print("\n" + "=" * 80)
    print("✅ Successfully fetched model list!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ Error fetching models: {str(e)}")
    print("\nMake sure:")
    print("  1. Your OPENAI_API_KEY is set in the .env file")
    print("  2. Your API key is valid and has access to the models endpoint")
    print("  3. You have an active internet connection")