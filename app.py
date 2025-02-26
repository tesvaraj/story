import os
import json
import base64
import requests
from together import Together
from PIL import Image
import io
import tempfile
import webbrowser
from dotenv import load_dotenv
import argparse
import sys

# Load environment variables
load_dotenv()

def generate_image_prompts(concept, num_prompts=3, include_nelson=True):
    """
    Use the Nillion API to generate detailed image prompts from a simple concept
    
    Args:
        concept (str): Simple concept like "on beach"
        num_prompts (int): Number of different prompts to generate
        include_nelson (bool): Whether to include n3lson in the prompts
        
    Returns:
        list: List of generated detailed prompts
    """
    try:
        # Get environment variables for Nillion API
        api_url = os.environ.get("NILAI_API_URL", "https://nilai-a779.nillion.network")
        api_key = os.environ.get("NILAI_API_KEY", "Nillion2025")
        
        # Prepare system message to instruct LLM to generate image prompts
        if include_nelson:
            system_message = """
            You are a specialized image prompt generator. 
            Create detailed, high-quality image prompts for the concept provided.
            Each prompt should be different but related to the same concept. Max of 10 words.
            Make the prompts specific, visual, and detailed enough for an image generation model.
            Prompt MUST start with 'n3lson man', eg: 'n3lson man on beach' since 'n3lson' is the keyword for the image fine tuned model.
            ONLY return the prompts, one per line, with no additional explanation or commentary.
            """
        else:
            system_message = """
            You are a specialized image prompt generator. 
            Create detailed, high-quality image prompts for the concept provided.
            Each prompt should be different but related to the same concept. Max of 10 words.
            Make the prompts specific, visual, and detailed enough for an image generation model.
            ONLY return the prompts, one per line, with no additional explanation or commentary.
            """
        
        # Prepare the request
        url = f"{api_url}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": "meta-llama/Llama-3.1-8B-Instruct",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Generate {num_prompts} different detailed image prompts for the concept: '{concept}'"}
            ],
            "temperature": 0.7,  # Slightly higher temperature for creativity
        }
        
        # Make the API call
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        generated_text = result['choices'][0]['message']['content']
        
        # Split text into individual prompts (one per line)
        prompts = [p.strip() for p in generated_text.strip().split('\n') if p.strip()]
        
        # Limit to requested number of prompts
        prompts = prompts[:num_prompts]
        
        print(f"Generated {len(prompts)} image prompts:")
        for i, prompt in enumerate(prompts):
            print(f"{i+1}. {prompt}")
            
        return prompts
        
    except Exception as error:
        print(f"Error generating prompts: {error}")
        # Fallback prompts if API call fails
        if include_nelson:
            return [f"n3lson {concept} realistic photo high definition" for _ in range(num_prompts)]
        else:
            return [f"{concept} realistic photo high definition" for _ in range(num_prompts)]


class ImageGenerator:
    def __init__(self):
        # Load environment variables if not already loaded
        load_dotenv()
        
        # Get API keys from environment
        self.together_api_key = os.environ.get("TOGETHER_API_KEY")
        self.ablo_api_key = os.environ.get("ABLO_KEY")
        
        # Initialize Together client if available
        if self.together_api_key:
            self.together_client = Together(api_key=self.together_api_key)
        else:
            self.together_client = None
            
        self.generated_images = []
        self.prompts_used = []
        
    def generate_images_with_together(self, prompts, 
                               model="black-forest-labs/FLUX.1-dev-lora",
                               width=1024, 
                               height=768, 
                               steps=28,
                               lora_path="http://hills.ccsf.edu/~clai74/nelson_unet.safetensors",
                               lora_scale=1.0):
        """
        Generate one image for each provided prompt using Together API
        
        Args:
            prompts (list): List of text prompts to generate images from
            model (str): Model name to use
            width (int): Image width
            height (int): Image height
            steps (int): Number of inference steps
            lora_path (str): Path to LoRA adapter
            lora_scale (float): Scale factor for LoRA adapter
            
        Returns:
            list: List of base64 encoded images
        """
        if not self.together_api_key:
            raise ValueError("TOGETHER_API_KEY is required for Together image generation. Add it to .env file.")
            
        images = []
        self.prompts_used = []
        
        for i, prompt in enumerate(prompts):
            try:
                print(f"Generating image {i+1}/{len(prompts)} with Together...")
                response = self.together_client.images.generate(
                    prompt=prompt,
                    model=model,
                    width=width,
                    height=height,
                    steps=steps,
                    n=1,
                    response_format="b64_json",
                    image_loras=[{"path": lora_path, "scale": lora_scale}]
                )
                
                # Store the generated image
                if response.data and len(response.data) > 0:
                    images.append(response.data[0].b64_json)
                    self.prompts_used.append(prompt)
                    print(f"Image {i+1} generated successfully")
                else:
                    print(f"No image data returned for prompt {i+1}")
                    
            except Exception as e:
                print(f"Error generating image {i+1}: {e}")
                
        # Store all generated images
        self.generated_images = images
        
        return images
            
    def generate_images_with_ablo(self, prompts, style_id="a58f5b3c-2263-4072-8242-f23c52315125"):
        """
        Generate images for each provided prompt using Ablo API
        
        Args:
            prompts (list): List of text prompts to generate images from
            style_id (str): Style ID for Ablo image generation
            
        Returns:
            list: List of base64 encoded images
        """
        if not self.ablo_api_key:
            raise ValueError("ABLO_KEY is required for Ablo image generation. Add it to .env file.")
            
        images = []
        self.prompts_used = []
        
        for i, prompt in enumerate(prompts):
            try:
                print(f"Generating image {i+1}/{len(prompts)} with Ablo...")
                
                # For Ablo, trim the first two words if they contain "n3lson"
                if prompt.lower().startswith("n3lson"):
                    words = prompt.split()
                    if len(words) > 2:
                        ablo_prompt = " ".join(words[2:])
                    else:
                        ablo_prompt = prompt
                else:
                    ablo_prompt = prompt
                
                # Make the API call to Ablo
                url = "https://api.ablo.ai/image-maker"
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": self.ablo_api_key
                }
                payload = {
                    "styleId": style_id,
                    "freeText": ablo_prompt
                }
                
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                # Parse the response
                result = response.json()
                
                # Extract image URLs from the response - Ablo returns multiple images
                if "images" in result and result["images"]:
                    for img_data in result["images"]:
                        if "url" in img_data:
                            # Fetch the image from URL and convert to base64
                            image_url = img_data["url"]
                            image_response = requests.get(image_url)
                            image_response.raise_for_status()
                            image_bytes = image_response.content
                            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                            images.append(image_base64)
                            self.prompts_used.append(f"{prompt} (variant {len(images)})")
                            print(f"Image variant {len(images)} for prompt {i+1} generated successfully")
                else:
                    print(f"No image data returned from Ablo for prompt {i+1}")
                    
            except Exception as e:
                print(f"Error generating image {i+1} with Ablo: {e}")
                
        # Store all generated images
        self.generated_images = images
        
        return images

    
    def display_images_for_selection(self, provider=""):
        """
        Display the generated images in a simple HTML page for selection
        
        Args:
            provider (str): Name of the provider used to generate images
            
        Returns:
            str: Path to the HTML file
        """
        if not self.generated_images:
            print("No images to display")
            return None
            
        # Create HTML page with images
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Select an Image</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
                h1 { text-align: center; }
                .image-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-top: 30px; }
                .image-option { border: 1px solid #ddd; border-radius: 8px; overflow: hidden; width: 45%; max-width: 600px; margin-bottom: 20px; }
                .image-option img { width: 100%; height: auto; display: block; }
                .image-option .select-btn { background: #4CAF50; color: white; border: none; padding: 10px; width: 100%; cursor: pointer; font-size: 16px; }
                .image-option .select-btn:hover { background: #45a049; }
                .image-info { padding: 10px; background: #f9f9f9; }
                .prompt-text { font-size: 12px; color: #666; margin: 5px 0; }
                .provider-badge { display: inline-block; background: #e0e0e0; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin-left: 8px; }
            </style>
        </head>
        <body>
        """
        
        if provider:
            html_content += f"""
            <h1>Select an Image <span class="provider-badge">Generated with {provider}</span></h1>
            """
        else:
            html_content += """
            <h1>Select an Image</h1>
            """
            
        html_content += """
            <div class="image-container">
        """
        
        for i, (img_data, prompt) in enumerate(zip(self.generated_images, self.prompts_used)):
            img_src = f"data:image/png;base64,{img_data}"
            html_content += f"""
                <div class="image-option" id="option-{i+1}">
                    <img src="{img_src}" alt="Generated image {i+1}">
                    <div class="image-info">
                        <h3>Option {i+1}</h3>
                        <div class="prompt-text">Prompt: {prompt}</div>
                        <button class="select-btn" onclick="selectImage({i})">Select This Image</button>
                    </div>
                </div>
            """
            
        html_content += """
            </div>
            <script>
                function selectImage(index) {
                    const selectedFile = `selected_image_${index}.png`;
                    console.log("Selected image:", index);
                    alert(`You selected image ${index + 1}! In a complete application, this would be saved as ${selectedFile}`);
                    // Here you would typically communicate back to Python
                }
            </script>
        </body>
        </html>
        """
        
        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            f.write(html_content.encode('utf-8'))
            html_path = f.name
            
        # Open in browser
        webbrowser.open('file://' + html_path)
        
        return html_path
    
    def save_image(self, index=0, filename=None):
        """
        Save a specific image to disk
        
        Args:
            index (int): Index of the image to save
            filename (str, optional): Filename to save to. If None, generates one.
            
        Returns:
            str: Path to the saved image
        """
        if not self.generated_images or index >= len(self.generated_images):
            print("Invalid image index")
            return None
            
        if filename is None:
            filename = f"generated_image_{index}.png"
            
        try:
            # Convert base64 to image and save
            image_data = base64.b64decode(self.generated_images[index])
            image = Image.open(io.BytesIO(image_data))
            image.save(filename)
            print(f"Image saved to {filename}")
            return filename
        except Exception as e:
            print(f"Error saving image: {e}")
            return None


def create_images_from_concept(concept, num_variations=3, provider="together"):
    """
    Main function to generate images from a simple concept
    
    1. Convert concept to detailed prompts using LLM
    2. Generate an image for each prompt using the selected provider
    3. Display images for selection
    
    Args:
        concept (str): Simple concept like "on beach"
        num_variations (int): Number of image variations to generate
        provider (str): Image generation provider ("together" or "ablo")
        
    Returns:
        tuple: (list of generated images, list of prompts used)
    """
    # Determine if we need to include n3lson in prompts based on provider
    include_nelson = provider.lower() == "together"
    
    # For Ablo, we only need 1 prompt since it generates multiple variations per prompt
    num_prompts = 1 if provider.lower() == "ablo" else num_variations
    
    # Step 1: Generate detailed prompts from the concept
    prompts = generate_image_prompts(concept, num_prompts, include_nelson)
    
    # Step 2: Generate images from the prompts using the selected provider
    try:
        generator = ImageGenerator()
        
        if provider.lower() == "ablo":
            images = generator.generate_images_with_ablo(prompts)
        else:  # Default to Together
            images = generator.generate_images_with_together(prompts)
        
        # Step 3: Display images for selection
        if images:
            generator.display_images_for_selection(provider)
            return images, generator.prompts_used
        else:
            print("No images were generated")
            return [], []
            
    except Exception as e:
        print(f"Error in image generation process: {e}")
        return [], []


def main():
    """
    Main entry point with argument parsing
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate images from a simple concept using AI")
    parser.add_argument("concept", nargs="*", help="Concept to generate images for (e.g., 'on beach')")
    parser.add_argument("--provider", "-p", choices=["together", "ablo"], default="together", 
                       help="Image generation provider to use (together or ablo)")
    parser.add_argument("--variations", "-n", type=int, default=3,
                       help="Number of image variations to generate")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Get concept from arguments or use default
    user_concept = " ".join(args.concept) if args.concept else "on beach with sunglasses"
    
    # Verify required API keys are available
    if args.provider.lower() == "together" and not os.environ.get("TOGETHER_API_KEY"):
        print("Error: TOGETHER_API_KEY not found in environment variables.")
        print("Please add it to your .env file in the format: TOGETHER_API_KEY=your_api_key_here")
        sys.exit(1)
    elif args.provider.lower() == "ablo" and not os.environ.get("ABLO_KEY"):
        print("Error: ABLO_KEY not found in environment variables.")
        print("Please add it to your .env file in the format: ABLO_KEY=your_api_key_here")
        sys.exit(1)
        
    print(f"Generating {args.variations} images for concept: '{user_concept}' using {args.provider}")
    
    # Generate images from concept
    images, prompts = create_images_from_concept(user_concept, args.variations, args.provider)
    
    print(f"Generated {len(images)} images")
    
    # Return success or failure
    return 0 if images else 1


# Entry point
if __name__ == "__main__":
    sys.exit(main())