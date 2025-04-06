import streamlit as st
from openai import OpenAI
import os

def add_chat_css():
    """
    Add custom CSS to position the chat container in the right corner.
    """
    st.markdown("""
    <style>
    .right-corner-chat {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 300px;
        max-height: 500px;
        z-index: 1000;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    .stApp {
        max-width: 100%;
        padding-right: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def minimizable_trading_chatbot():
    """
    Create a trading chatbot interface in the right corner of the screen.
    """
    # Add custom positioning CSS
    add_chat_css()

    # Initialize session state for chat messages
    if 'trading_chat_messages' not in st.session_state:
        st.session_state.trading_chat_messages = []

    # Create OpenAI client using environment variable
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # Create a container for the right corner chat
    chat_container = st.container()
    
    with chat_container:
        # Use an expander for collapsible functionality
        with st.expander("🐺 Wolf of Wall Street Chat", expanded=False):
            # Display chat messages
            for message in st.session_state.trading_chat_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # User input
            if prompt := st.chat_input("What trading question do you have?"):
                # Add user message to chat history
                st.session_state.trading_chat_messages.append(
                    {"role": "user", "content": prompt}
                )
                
                # Display user message
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Generate AI response
                with st.chat_message("assistant"):
                    with st.spinner("The Wolf is hunting for insights..."):
                        response = get_belfort_response(prompt, client)
                        st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.trading_chat_messages.append(
                    {"role": "assistant", "content": response}
                )

    # Apply right corner positioning via JavaScript
    st.markdown("""
    <script>
    // Select the last expander (our chat)
    const expanders = document.querySelectorAll('.stExpander');
    const chatExpander = expanders[expanders.length - 1];
    
    // Add custom class for positioning
    if (chatExpander) {
        chatExpander.classList.add('right-corner-chat');
    }
    </script>
    """, unsafe_allow_html=True)

def get_belfort_response(prompt, client):
    """
    Generate a response in the style of Jordan Belfort using OpenAI's API.
    
    :param prompt: User's input message
    :param client: OpenAI client
    :return: AI-generated response
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
            temperature=0.7,  # Adjust creativity
            max_tokens=300,   # Increased response length
            top_p=0.9,        # Diversity of response
            frequency_penalty=0.5,  # Reduce repetition
            presence_penalty=0.6    # Encourage novel content
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"OpenAI API Error: {str(e)}")
        return "Oops! Looks like we hit a Wall Street roadblock. Try again in a moment."