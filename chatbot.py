import streamlit as st
from openai import OpenAI
import os

def minimizable_trading_chatbot():
    """
    Create a trading chatbot interface without page reload.
    """
    # Initialize session state for chat messages
    if 'trading_chat_messages' not in st.session_state:
        st.session_state.trading_chat_messages = []

    # Create OpenAI client using environment variable
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # Create a container for the chat in the sidebar
    with st.sidebar:
        # Use an expander with a default expanded state
        with st.expander("🐺 FinnXpert Chat", expanded=True):
            # Display chat messages
            message_placeholder = st.empty()  # Use `st.empty()` to dynamically update chat window
            
            # Display current chat history
            with message_placeholder.container():
                for message in st.session_state.trading_chat_messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            # User input for new message
            prompt = st.chat_input("Ask here..")

            if prompt:
                # Add user message to chat history
                st.session_state.trading_chat_messages.append(
                    {"role": "user", "content": prompt}
                )
                
                # Generate AI response and append it to the chat history
                try:
                    # Get AI response
                    response = get_belfort_response(prompt, client)
                    
                    # Add assistant response to chat history
                    st.session_state.trading_chat_messages.append(
                        {"role": "assistant", "content": response}
                    )

                    # Clear the existing messages and re-display
                    message_placeholder.empty()  # Clear the current chat
                    with message_placeholder.container():
                        for message in st.session_state.trading_chat_messages:
                            with st.chat_message(message["role"]):
                                st.markdown(message["content"])

                except Exception as e:
                    st.error(f"Error generating response: {e}")

def get_belfort_response(prompt, client):
    """
    Generate a response in the style of Jordan Belfort using OpenAI's API.
    """
    try:
        # Make the request to OpenAI's chat completion endpoint
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system", 
                "content": """You are Jordan Belfort, the Wolf of Wall Street. 
                You have comprehensive trading knowledge and explain complex financial 
                concepts in an energetic, motivational, and simple way. 
                Your responses are clear, high-energy, and persuasive. 
                Use motivational language, real-world examples, and actionable insights."""
            },
            {"role": "user", "content": prompt}],
            temperature=0.7,  # Adjust creativity
            max_tokens=300,   # Increased response length
            top_p=0.9,        # Diversity of response
            frequency_penalty=0.5,  # Reduce repetition
            presence_penalty=0.6    # Encourage novel content
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Oops! Error: {str(e)}"
