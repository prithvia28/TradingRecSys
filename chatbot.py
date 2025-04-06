from openai import OpenAI
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def validate_api_key():
    """
    Validate the OpenAI API key from environment variables or user input.
    """
    # Try to get API key from environment variables
    api_key = os.environ.get('OPENAI_API_KEY')
    
    # If no key in env, ask user to input
    if not api_key:
        st.warning("No API key found in environment variables.")
        api_key = st.text_input(
            "Enter your OpenAI API Key:", 
            type="password", 
            help="You can get your API key from https://platform.openai.com/account/api-keys"
        )
        
        # Validate user-provided key
        if api_key:
            try:
                client = OpenAI(api_key=api_key)
                # Test the API key with a simple request
                client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10
                )
                st.success("API Key validated successfully!")
                return api_key
            except Exception as e:
                st.error(f"Invalid API Key: {str(e)}")
                return None
    
    # Validate environment variable key
    try:
        client = OpenAI(api_key=api_key)
        # Test the API key with a simple request
        client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        return api_key
    except Exception as e:
        st.error(f"API Key validation failed: {str(e)}")
        return None

def get_belfort_response(prompt, client):
    """
    Generate a response in the style of Jordan Belfort using OpenAI's API.
    """
    try:
        # Make the request to OpenAI's chat completion endpoint
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": """You are Jordan Belfort, the Wolf of Wall Street. 
                    You have comprehensive trading knowledge and explain complex financial 
                    concepts in an energetic, motivational, and simple way. 
                    Your responses are clear, high-energy, and persuasive. 
                    Use motivational language, real-world examples, and actionable insights."""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300,
            top_p=0.9,
            frequency_penalty=0.5,
            presence_penalty=0.6
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Oops! Error: {str(e)}"

def jordan_belfort_chatbot():
    """
    Render the Jordan Belfort chatbot as a Streamlit component
    """
    # Validate API Key
    api_key = validate_api_key()
    
    # Only proceed if API key is valid
    if api_key:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)

        # Check if a message has been sent
        chatbot_input = st.session_state.get('chatbot_input', '')
        
        if chatbot_input:
            # Generate response
            response = get_belfort_response(chatbot_input, client)
            
            # Clear the input
            st.session_state.chatbot_input = ''
            
            # Send response back to the component
            components.html(f"""
            <script>
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue', 
                key: 'chatbot_response', 
                value: `{response}`
            }}, '*');
            </script>
            """, height=0)

        # Render the chatbot HTML component directly
        components.html("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <style>
                #chatbot-container {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    width: 350px;
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    transition: all 0.3s ease;
                    border: 1px solid #e0e0e0;
                    z-index: 1000;
                }

                #chatbot-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    background-color: #4a4a4a;
                    color: white;
                    padding: 10px 15px;
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                    cursor: pointer;
                }

                #chatbot-messages {
                    height: 400px;
                    overflow-y: auto;
                    padding: 15px;
                    background-color: #f9f9f9;
                }

                #chatbot-input-area {
                    display: flex;
                    padding: 10px;
                    background-color: white;
                    border-bottom-left-radius: 10px;
                    border-bottom-right-radius: 10px;
                }

                #chatbot-input {
                    flex-grow: 1;
                    padding: 10px;
                    border: 1px solid #e0e0e0;
                    border-radius: 5px;
                    margin-right: 10px;
                }

                #chatbot-send {
                    background-color: #4a4a4a;
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    border-radius: 5px;
                    cursor: pointer;
                }

                .minimized {
                    height: 50px !important;
                    overflow: hidden;
                }

                .user-message {
                    background-color: #e0e0e0;
                    border-radius: 10px;
                    padding: 10px;
                    margin-bottom: 10px;
                    max-width: 80%;
                    align-self: flex-end;
                }

                .assistant-message {
                    background-color: #f0f0f0;
                    border-radius: 10px;
                    padding: 10px;
                    margin-bottom: 10px;
                    max-width: 80%;
                    align-self: flex-start;
                }

                #chatbot-messages {
                    display: flex;
                    flex-direction: column;
                }
            </style>
        </head>
        <body>
            <div id="chatbot-container">
                <div id="chatbot-header" onclick="toggleChatbot()">
                    <span>🤖 Jordan Belfort Trading Chatbot</span>
                    <span id="minimize-btn">-</span>
                </div>
                <div id="chatbot-messages"></div>
                <div id="chatbot-input-area">
                    <input type="text" id="chatbot-input" placeholder="Ask a trading question...">
                    <button id="chatbot-send" onclick="sendMessage()">Send</button>
                </div>
            </div>

            <script>
                let isMinimized = false;

                function toggleChatbot() {
                    const container = document.getElementById('chatbot-container');
                    const minimizeBtn = document.getElementById('minimize-btn');
                    
                    isMinimized = !isMinimized;
                    
                    if (isMinimized) {
                        container.classList.add('minimized');
                        minimizeBtn.textContent = '+';
                    } else {
                        container.classList.remove('minimized');
                        minimizeBtn.textContent = '-';
                    }
                }

                function sendMessage() {
                    const input = document.getElementById('chatbot-input');
                    const messagesContainer = document.getElementById('chatbot-messages');
                    const message = input.value.trim();

                    if (message) {
                        // Add user message
                        const userMessageEl = document.createElement('div');
                        userMessageEl.classList.add('user-message');
                        userMessageEl.textContent = message;
                        messagesContainer.appendChild(userMessageEl);

                        // Clear input
                        input.value = '';

                        // Scroll to bottom
                        messagesContainer.scrollTop = messagesContainer.scrollHeight;

                        // Send message to Streamlit
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue', 
                            key: 'chatbot_input', 
                            value: message
                        }, '*');
                    }
                }

                // Listen for messages from Streamlit
                window.addEventListener('message', (event) => {
                    if (event.data.type === 'streamlit:setComponentValue' && event.data.key === 'chatbot_response') {
                        const messagesContainer = document.getElementById('chatbot-messages');
                        const assistantMessageEl = document.createElement('div');
                        assistantMessageEl.classList.add('assistant-message');
                        assistantMessageEl.textContent = event.data.value;
                        messagesContainer.appendChild(assistantMessageEl);

                        // Scroll to bottom
                        messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    }
                });

                // Allow sending message with Enter key
                document.getElementById('chatbot-input').addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });
            </script>
        </body>
        </html>
        """, height=500, scrolling=False)