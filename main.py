import os
from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Together
from langchain_core.callbacks import CallbackManagerForToolInvocation
from langchain.tools import BaseTool
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain.tools.render import format_tool_to_openai_function
import requests
import json
import base64
from io import BytesIO
from PIL import Image
import streamlit as st

# Environment variables for API keys
# Make sure to set these in your environment
# export TOGETHER_API_KEY="your_together_api_key"
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")

# LLM Setup
llm = Together(
    model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    temperature=0.7,
    max_tokens=1024,
    together_api_key=TOGETHER_API_KEY
)

# Image Generation Tool
class ImageGenerationTool(BaseTool):
    name = "image_generator"
    description = """
    Generate an image using the FLUX.1-dev-lora model on TogetherAI. 
    This tool is useful when you need to create a high-quality image based on a detailed prompt.
    Input should be a detailed description of the image to generate.
    """
    
    def _run(self, prompt: str, run_manager: CallbackManagerForToolInvocation = None) -> str:
        """Run the image generation based on the prompt."""
        try:
            headers = {
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "black-forest-labs/FLUX.1-dev-lora",
                "prompt": prompt,
                "negative_prompt": "low quality, blurry, distorted features, unrealistic, bad anatomy, multiple limbs, excessive limbs",
                "height": 1024,
                "width": 768,
                "steps": 30,
                "seed": 42,
                "num_images": 1
            }
            
            response = requests.post(
                "https://api.together.xyz/v1/image/generation",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                image_b64 = result["output"]["images"][0]
                
                # For Streamlit, we'll return the base64 string to display
                return f"Image generated successfully! Base64: {image_b64[:20]}..."
            else:
                return f"Error generating image: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _arun(self, prompt: str):
        """Async version (not implemented)"""
        raise NotImplementedError("Async version not implemented")

# Create the image generation tool
image_tool = ImageGenerationTool()

# Format the tool for the agent
tools = [image_tool]
llm_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])

# Prompt Template for the agent
prompt = ChatPromptTemplate.from_template("""
You are an AI assistant helping an Instagram influencer create content based on simple keyword ideas.
Your job is to take simple keywords and convert them into detailed, visually appealing prompts for image generation.

The influencer's content style is trendy, modern, and aesthetically pleasing with high-quality composition.
Always ensure the prompts are tasteful and appropriate for Instagram.

For each keyword input, create a detailed prompt that includes:
1. The main subject (the influencer - a woman)
2. The setting and environment in detail
3. Lighting conditions and time of day
4. Outfit details (keeping it appropriate and fashionable)
5. Pose suggestions
6. Overall mood and aesthetic
7. Photographic style (e.g., "portrait photography", "candid shot", etc.)

KEYWORD INPUT: {keyword}

Remember to keep the content tasteful and appropriate for a mainstream audience.
After generating the prompt, use the image_generator tool to create the image.
""")

# Create the agent
agent = create_structured_chat_agent(llm_with_tools, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Streamlit UI
def main():
    st.title("Instagram Content Generator")
    st.write("Generate content ideas for your Instagram based on simple keywords")
    
    # Example keyword ideas
    st.subheader("Example Keywords:")
    example_keywords = [
        "woman on beach wearing yoga pants",
        "woman in park wearing hoodie",
        "woman at cafe with laptop",
        "woman hiking in mountains",
        "woman at sunset on rooftop"
    ]
    
    st.write(", ".join(example_keywords))
    
    # Input for keyword
    keyword = st.text_input("Enter your keyword idea:")
    
    if st.button("Generate Content"):
        if keyword:
            with st.spinner("Generating content..."):
                # Run the agent
                result = agent_executor.invoke({"keyword": keyword})
                
                # Display results
                st.subheader("Generated Content")
                st.write(result["output"])
                
                # Check if there's a base64 image in the output
                if "Base64:" in result["output"]:
                    try:
                        base64_start = result["output"].find("Base64:") + 7
                        base64_end = result["output"].find("...", base64_start)
                        
                        # This is just to show that we found the base64 string
                        # In a real implementation, you'd have the full base64 string
                        st.write("Image generated! (Base64 data found)")
                        
                        # In a real implementation with the full base64:
                        # image_data = base64.b64decode(base64_string)
                        # image = Image.open(BytesIO(image_data))
                        # st.image(image, caption="Generated Image")
                    except Exception as e:
                        st.error(f"Error processing image: {str(e)}")
        else:
            st.warning("Please enter a keyword idea")

# Entry point for the application
if __name__ == "__main__":
    main()