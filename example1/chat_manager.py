import anthropic
import logging
from PIL import Image
import io
import base64
import os
from dotenv import load_dotenv

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ChatManager:
    def __init__(self):
        self.client = None
        self.messages = []
        logging.debug("Initializing ChatManager")
        self._initialize_from_env()
        
    def _initialize_from_env(self):
        """Initialize client from environment variable"""
        try:
            print("\n=== Environment Initialization ===")
            # Load environment variables
            load_dotenv()
            api_key = os.getenv('ANTHROPIC_API_KEY')
            print(f"API Key found: {'Yes' if api_key else 'No'}")
            print(f"API Key length: {len(api_key) if api_key else 0}")
            print(f"API Key starts with: {api_key[:10] + '...' if api_key else 'None'}")
            
            if not api_key:
                print("No API key found in environment")
                return False
            
            print("\nTrying to initialize Anthropic client...")
            print(f"Anthropic version: {anthropic.__version__}")
            
            # Initialize client according to latest SDK docs
            self.client = anthropic.Anthropic(
                api_key=api_key,
            )
            print("Client initialized successfully!")
            return True
            
        except Exception as e:
            print(f"\nERROR during initialization: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print("Traceback:")
            traceback.print_exc()
            return False
    
    def initialize(self, api_key):
        """Initialize the Anthropic client with explicit API key"""
        try:
            print("\n=== Manual Initialization ===")
            print(f"Received API key length: {len(api_key)}")
            print(f"API key starts with: {api_key[:10]}...")
            
            # Initialize client
            self.client = anthropic.Anthropic(
                api_key=api_key,
            )
            print("Client initialized successfully!")
            return True
        except Exception as e:
            print(f"\nERROR during manual initialization: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print("Traceback:")
            traceback.print_exc()
            return False
    
    def is_initialized(self):
        """Check if client is initialized"""
        # Check both client existence and API key
        if not self.client:
            return False
        try:
            # Verify we can access the client's api_key
            _ = self.client.api_key
            return True
        except:
            return False
    
    def analyze_image(self, image, prompt=None):
        """Analyze image with Claude"""
        if not self.client:
            logging.error("Client not initialized. Please provide API key first.")
            return "Error: Please configure API key first"
            
        try:
            logging.debug("Converting image to base64")
            # Convert PIL Image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Prepare the message
            default_prompt = "What can you see in this screenshot? Please describe its content."
            message = prompt if prompt else default_prompt
            logging.debug(f"Using prompt: {message}")
            
            # Create the message with image using Claude 3
            logging.debug("Sending request to Claude")
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": message},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_str
                            }
                        }
                    ]
                }]
            )
            logging.debug("Successfully received response from Claude")
            
            # Store the conversation
            self.messages.append({
                "role": "user",
                "content": message
            })
            self.messages.append({
                "role": "assistant",
                "content": response.content[0].text
            })
            
            return response.content[0].text
            
        except Exception as e:
            logging.error(f"Error analyzing image: {str(e)}", exc_info=True)
            return f"Error analyzing image: {str(e)}"
    
    def get_chat_history(self):
        """Return the chat history"""
        return self.messages 