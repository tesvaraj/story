import os
import json
import base64
import requests
import subprocess
import tempfile
from together import Together
from PIL import Image
import io
import webbrowser
from dotenv import load_dotenv
import argparse
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__, static_folder='generated_images')
CORS(app)  # Enable CORS for all routes

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
        self.image_files = []  # To track saved image files
        
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
    
    def save_all_images(self):
        """
        Save all generated images to disk
        
        Returns:
            list: Paths of saved images
        """
        if not self.generated_images:
            print("No images to save")
            return []
            
        image_paths = []
        
        # Create directory for saved images if it doesn't exist
        os.makedirs("generated_images", exist_ok=True)
        
        for i, (img_data, prompt) in enumerate(zip(self.generated_images, self.prompts_used)):
            # Generate a unique filename based on timestamp and index
            import time
            timestamp = int(time.time())
            filename = f"generated_images/image_{timestamp}_{i}.png"
            
            try:
                # Convert base64 to image and save
                image_data = base64.b64decode(img_data)
                image = Image.open(io.BytesIO(image_data))
                image.save(filename)
                print(f"Image {i+1} saved to {filename}")
                image_paths.append((filename, prompt))
            except Exception as e:
                print(f"Error saving image {i+1}: {e}")
                
        self.image_files = image_paths
        return image_paths
    
    def upload_to_story_protocol(self, image_index=None):
        """
        Upload a specific image or all images to Story Protocol
        
        Args:
            image_index (int, optional): Index of the image to upload. If None, uploads all images.
            
        Returns:
            list: List of upload results
        """
        if not self.image_files:
            # Save images first if they haven't been saved
            self.save_all_images()
            
        if not self.image_files:
            print("No images available to upload")
            return []
            
        results = []
        
        # Determine which images to upload
        images_to_upload = [self.image_files[image_index]] if image_index is not None else self.image_files
        
        for image_path, prompt in images_to_upload:
            try:
                print("")
                print("=" * 70)
                print(f"Uploading image '{image_path}' to Story Protocol")
                print(f"Prompt: '{prompt}'")
                print("=" * 70)
                
                # Call the Node.js script to upload the image
                script_path = os.path.join("story-integration", "storyUploader.js")
                
                # Run the script and show real-time output
                process = subprocess.Popen(
                    ["node", script_path, image_path, prompt],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                
                # Print output in real-time
                for line in process.stdout:
                    print(line.strip())
                
                # Wait for the process to complete
                exit_code = process.wait()
                
                # Check if upload was successful
                if exit_code == 0:
                    # Try to read the result from the JSON file
                    try:
                        result_file = os.path.join("story-integration", "upload_result.json")
                        with open(result_file, "r") as f:
                            upload_result = json.load(f)
                            
                        # Try to also load the debug file if it exists
                        debug_file = os.path.join("story-integration", "upload_result_debug.txt")
                        debug_content = ""
                        if os.path.exists(debug_file):
                            with open(debug_file, "r") as f:
                                debug_content = f.read()
                            print("\nDEBUG INFO:")
                            print(debug_content)
                        
                        # Print transaction summary
                        print("")
                        print("=" * 70)
                        print("TRANSACTION SUMMARY")
                        print("=" * 70)
                        print(f"Transaction Hash: {upload_result.get('txHash', 'N/A')}")
                        print(f"Transaction Hash Length: {len(str(upload_result.get('txHash', '')))}")
                        print(f"IPFS Hash: {upload_result.get('ipfsCid', 'N/A')}")
                        print(f"IPFS Hash Length: {len(str(upload_result.get('ipfsCid', '')))}")
                        print(f"IP Asset ID: {upload_result.get('ipId', 'N/A')}")
                        print(f"IP Asset URL: {upload_result.get('ipAssetUrl', 'N/A')}")
                        print(f"Explorer: {upload_result.get('explorerUrl', 'N/A')}")
                        print(f"Image IPFS: {upload_result.get('viewUrl', 'N/A')}")
                        print("=" * 70)
                        
                        results.append(upload_result)
                    except Exception as e:
                        print(f"Error reading upload result: {e}")
                else:
                    # Read error output
                    stderr = process.stderr.read()
                    print(f"Error uploading to Story Protocol (exit code {exit_code}):")
                    print(stderr)
                    
            except Exception as e:
                print(f"Error in upload process: {e}")
                
        return results
    
    def display_images_for_selection(self, provider="", enable_story_upload=True):
        """
        Display the generated images in a simple HTML page for selection
        
        Args:
            provider (str): Name of the provider used to generate images
            enable_story_upload (bool): Whether to enable uploading to Story Protocol
        
        Returns:
            str: Path to the HTML file
        """
        if not self.generated_images:
            print("No images to display")
            return None
            
        # Save images first
        self.save_all_images()
            
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
                .button-group { display: flex; gap: 10px; }
                .select-btn { background: #4CAF50; color: white; border: none; padding: 10px; flex-grow: 1; cursor: pointer; font-size: 16px; }
                .select-btn:hover { background: #45a049; }
                .upload-btn { background: #2196F3; color: white; border: none; padding: 10px; flex-grow: 1; cursor: pointer; font-size: 16px; }
                .upload-btn:hover { background: #0b7dda; }
                .image-info { padding: 10px; background: #f9f9f9; }
                .prompt-text { font-size: 12px; color: #666; margin: 5px 0; }
                .provider-badge { display: inline-block; background: #e0e0e0; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin-left: 8px; }
                .status-message { margin-top: 10px; padding: 10px; border-radius: 4px; display: none; }
                .success { background-color: #dff0d8; color: #3c763d; }
                .error { background-color: #f2dede; color: #a94442; }
                .transaction-details { background-color: #f9f9f9; padding: 10px; margin-top: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; }
                .transaction-details p { margin: 5px 0; }
                .transaction-details a { color: #2196F3; text-decoration: none; }
                .transaction-details a:hover { text-decoration: underline; }
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
            
            # Create a div for the status message
            status_div_id = f"status-{i}"
            transaction_div_id = f"transaction-{i}"
            
            html_content += f"""
                <div class="image-option" id="option-{i+1}">
                    <img src="{img_src}" alt="Generated image {i+1}">
                    <div class="image-info">
                        <h3>Option {i+1}</h3>
                        <div class="prompt-text">Prompt: {prompt}</div>
                        <div class="button-group">
                            <button class="select-btn" onclick="selectImage({i})">Save Image</button>
            """
            
            if enable_story_upload:
                html_content += f"""
                            <button class="upload-btn" onclick="uploadToStory({i})">Upload to Story Protocol</button>
                """
                
            html_content += f"""
                        </div>
                        <div id="{status_div_id}" class="status-message"></div>
                        <div id="{transaction_div_id}" class="transaction-details" style="display: none; word-wrap: break-word; white-space: pre-wrap;"></div>
                    </div>
                </div>
            """
            
        html_content += """
            </div>
            <script>
                async function selectImage(index) {
                    const statusDiv = document.getElementById(`status-${index}`);
                    statusDiv.textContent = "Saving image...";
                    statusDiv.className = "status-message";
                    statusDiv.style.display = "block";
                    
                    try {
                        const response = await fetch('/save-image', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ imageIndex: index })
                        });
                        
                        const result = await response.json();
                        
                        if (result.success) {
                            statusDiv.textContent = `Image saved as ${result.filename}`;
                            statusDiv.className = "status-message success";
                        } else {
                            statusDiv.textContent = `Error: ${result.error}`;
                            statusDiv.className = "status-message error";
                        }
                    } catch (error) {
                        console.error("Error:", error);
                        statusDiv.textContent = "Error saving image. See console for details.";
                        statusDiv.className = "status-message error";
                    }
                }
                
                async function uploadToStory(index) {
                    const statusDiv = document.getElementById(`status-${index}`);
                    const transactionDiv = document.getElementById(`transaction-${index}`);
                    statusDiv.textContent = "Uploading to Story Protocol...";
                    statusDiv.className = "status-message";
                    statusDiv.style.display = "block";
                    transactionDiv.style.display = "none";
                    
                    try {
                        const response = await fetch('/upload-to-story', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ imageIndex: index })
                        });
                        
                        const result = await response.json();
                        
                        if (result.success) {
                            statusDiv.textContent = `Successfully uploaded to Story Protocol!`;
                            statusDiv.className = "status-message success";
                            
                            // Display transaction details
                            transactionDiv.innerHTML = `
                                <p><strong>Transaction Hash:</strong> <code style="word-break: break-all; display: block; background: #f5f5f5; padding: 8px; overflow: auto;">${result.txHash}</code></p>
                                <p><strong>IPFS Hash:</strong> <code style="word-break: break-all; display: block; background: #f5f5f5; padding: 8px; overflow: auto;">${result.ipfsCid || 'N/A'}</code></p>
                                <p><strong>IP Asset ID:</strong> <code style="word-break: break-all; display: block; background: #f5f5f5; padding: 8px; overflow: auto;">${result.ipId || 'N/A'}</code></p>
                                <p><strong>IP Asset URL:</strong> <a href="${result.ipAssetUrl || 'N/A'}" target="_blank">View IP Asset</a></p>
                                <p><strong>Explorer:</strong> <a href="${result.explorerUrl}" target="_blank">View on Explorer</a></p>
                                <p><strong>IPFS:</strong> <a href="${result.viewUrl}" target="_blank">View Image</a></p>
                            `;
                            transactionDiv.style.display = "block";
                        } else {
                            statusDiv.textContent = `Error: ${result.error}`;
                            statusDiv.className = "status-message error";
                        }
                    } catch (error) {
                        console.error("Error:", error);
                        statusDiv.textContent = "Error uploading to Story Protocol. See console for details.";
                        statusDiv.className = "status-message error";
                    }
                }
                
                // Since we're using a static HTML file, simulate API functionality
                // In a real app, you'd have an actual server handling these requests
                const originalFetch = window.fetch;
                window.fetch = function(url, options) {
                    if (url === '/save-image' && options.method === 'POST') {
                        return new Promise(resolve => {
                            setTimeout(() => {
                                const body = JSON.parse(options.body);
                                console.log("Saving image with index:", body.imageIndex);
                                // Simulate successful image save
                                resolve({
                                    json: () => Promise.resolve({
                                        success: true,
                                        filename: `generated_image_${body.imageIndex}.png`
                                    })
                                });
                            }, 500);
                        });
                    }
                    
                    if (url === '/upload-to-story' && options.method === 'POST') {
                        return new Promise(resolve => {
                            setTimeout(() => {
                                const body = JSON.parse(options.body);
                                console.log("Uploading to Story Protocol, image index:", body.imageIndex);
                                // Simulate image upload to Story Protocol
                                // In a real app, this would make a server request to trigger the Node.js script
                                resolve({
                                    json: () => Promise.resolve({
                                        success: true,
                                        txHash: "0x" + Math.random().toString(16).substring(2, 66),
                                        ipfsCid: "Qm" + Math.random().toString(16).substring(2, 46),
                                        ipId: "Qm" + Math.random().toString(16).substring(2, 46),
                                        ipAssetUrl: "https://ipfs.io/ipfs/" + Math.random().toString(16).substring(2, 46),
                                        explorerUrl: "https://explorer.aeneid.storyrpc.io/tx/0x" + Math.random().toString(16).substring(2, 66),
                                        viewUrl: "https://ipfs.io/ipfs/Qm" + Math.random().toString(16).substring(2, 46)
                                    })
                                });
                            }, 1500);
                        });
                    }
                    
                    return originalFetch(url, options);
                };
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
        
        print(f"To upload images to Story Protocol, please select the 'Upload to Story Protocol' button in the browser.")
        print(f"Note: The button in the browser will simulate the upload. To actually upload, use the save_image() and upload_to_story_protocol() methods.")
        
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
            # Create directory for saved images if it doesn't exist
            os.makedirs("generated_images", exist_ok=True)
            # Generate a unique filename based on timestamp and index
            import time
            timestamp = int(time.time())
            filename = f"generated_images/image_{timestamp}_{index}.png"
            
        try:
            # Convert base64 to image and save
            image_data = base64.b64decode(self.generated_images[index])
            image = Image.open(io.BytesIO(image_data))
            image.save(filename)
            print(f"Image saved to {filename}")
            
            # Store the file path and prompt for later use
            prompt = self.prompts_used[index] if index < len(self.prompts_used) else f"Generated image {index}"
            if not hasattr(self, 'image_files'):
                self.image_files = []
            self.image_files.append((filename, prompt))
            
            return filename
        except Exception as e:
            print(f"Error saving image: {e}")
            return None


def create_images_from_concept(concept, num_variations=3, provider="together", upload_to_story=False):
    """
    Main function to generate images from a simple concept
    
    1. Convert concept to detailed prompts using LLM
    2. Generate an image for each prompt using the selected provider
    3. Display images for selection
    4. Optionally upload to Story Protocol
    
    Args:
        concept (str): Simple concept like "on beach"
        num_variations (int): Number of image variations to generate
        provider (str): Image generation provider ("together" or "ablo")
        upload_to_story (bool): Whether to automatically upload all images to Story Protocol
        
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
        
        # Step 3: Save all generated images
        if images:
            generator.save_all_images()
            
            # Step 4: Upload to Story Protocol if requested
            if upload_to_story:
                print("")
                print("=" * 70)
                print("UPLOADING IMAGES TO STORY PROTOCOL")
                print("=" * 70)
                
                upload_results = generator.upload_to_story_protocol()
                
                if upload_results:
                    print("")
                    print("=" * 70)
                    print(f"SUCCESSFULLY UPLOADED {len(upload_results)} IMAGES TO STORY PROTOCOL")
                    print("=" * 70)
                    
                    for i, result in enumerate(upload_results):
                        print(f"Image {i+1}:")
                        print(f"  Transaction: {result.get('txHash', 'N/A')}")
                        print(f"  IPFS Hash: {result.get('ipfsCid', 'N/A')}")
                        print(f"  IP Asset ID: {result.get('ipId', 'N/A')}")
                        print(f"  IP Asset URL: {result.get('ipAssetUrl', 'N/A')}")
                        print(f"  Explorer: {result.get('explorerUrl', 'N/A')}")
                        print(f"  View Image: {result.get('viewUrl', 'N/A')}")
                        print("")
            
            # Step 5: Display images for selection
            generator.display_images_for_selection(provider, enable_story_upload=True)
            
            return images, generator.prompts_used
        else:
            print("No images were generated")
            return [], []
            
    except Exception as e:
        print(f"Error in image generation process: {e}")
        return [], []


# API Endpoints
@app.route('/api/generate-image', methods=['POST'])
def api_generate_image():
    """API endpoint to generate an image based on a prompt"""
    data = request.json
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Prompt is required'}), 400
    
    prompt = data['prompt']
    provider = data.get('provider', 'together')
    
    try:
        print(f"API received prompt: '{prompt}' with provider '{provider}'")
        
        # Create generator instance
        generator = ImageGenerator()
        
        # Determine if we need to add n3lson prefix based on provider
        include_nelson = provider.lower() == "together"
        
        # Generate detailed prompts from the concept
        prompts = generate_image_prompts(prompt, 1, include_nelson)
        if not prompts:
            return jsonify({'error': 'Failed to generate prompts'}), 500
        
        # Use the first generated prompt to create an image
        if provider.lower() == "ablo":
            images = generator.generate_images_with_ablo(prompts)
        else:  # Default to Together
            images = generator.generate_images_with_together(prompts)
        
        if not images:
            return jsonify({'error': 'Failed to generate image'}), 500
        
        # Save the image
        filepath = generator.save_image(0)
        if not filepath:
            return jsonify({'error': 'Failed to save image'}), 500
        
        # Get the full image URL for the frontend including host and port
        image_name = os.path.basename(filepath)
        image_url = f"http://{request.host}/api/images/{image_name}"
        
        # Return response
        return jsonify({
            'imageUrl': image_url,
            'prompt': prompts[0],
            'generatedAt': int(os.path.basename(filepath).split('_')[1]),
            'provider': provider
        })
        
    except Exception as e:
        print(f"Error generating image via API: {e}")
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/api/images/<image_name>', methods=['GET'])
def get_image(image_name):
    """Serve generated images"""
    return send_from_directory('generated_images', image_name)

# Run the Flask app when called with --serve flag
def run_flask_server(host='0.0.0.0', port=5001):
    """Run the Flask server"""
    print(f"Starting API server at http://{host}:{port}")
    print(f"API endpoint available at http://{host}:{port}/api/generate-image")
    app.run(host=host, port=port, debug=True)

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
    parser.add_argument("--upload", "-u", action="store_true",
                       help="Automatically upload all generated images to Story Protocol")
    parser.add_argument("--serve", "-s", action="store_true",
                       help="Start the API server")
    parser.add_argument("--port", type=int, default=5001,
                       help="Port to run the API server on (default: 5001)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # If --serve flag is provided, start the Flask server
    if args.serve:
        return run_flask_server(port=args.port)
    
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
        
    # If uploading to Story Protocol, verify those API keys
    if args.upload:
        if not os.environ.get("PINATA_JWT") or not os.environ.get("WALLET_PRIVATE_KEY"):
            print("Error: Story Protocol configuration missing from environment variables.")
            print("Please add PINATA_JWT, WALLET_PRIVATE_KEY, and RPC_PROVIDER_URL to your .env file.")
            sys.exit(1)
            
    print(f"Generating {args.variations} images for concept: '{user_concept}' using {args.provider}")
    if args.upload:
        print("Images will be automatically uploaded to Story Protocol")
    
    # Generate images from concept
    images, prompts = create_images_from_concept(user_concept, args.variations, args.provider, args.upload)
    
    print(f"Generated {len(images)} images")
    
    # Return success or failure
    return 0 if images else 1


# Entry point
if __name__ == "__main__":
    sys.exit(main())