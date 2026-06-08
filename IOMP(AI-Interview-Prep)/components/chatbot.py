import streamlit as st
from utils.grok_api import call_grok_api

def render_chatbot():
    st.header("Chat with your AI Interview Coach 💬")
    st.markdown("Ask for clarifications, mock practice, or deep dive into your feedback.")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔙 Back to Feedback"):
            st.session_state.current_page = 'feedback'
            st.rerun()
        
    st.markdown("---")

    if "messages" not in st.session_state:
        system_context = "You are an AI Interview Coach."
        if 'feedback_report' in st.session_state:
             system_context += f" Here is the feedback you just gave the user:\\n{st.session_state.feedback_report}\\nHelp them understand it or practice more."
             
        st.session_state.messages = [
            {"role": "system", "content": system_context},
            {"role": "assistant", "content": "Hello! I'm your AI Coach. How can I help you improve today? Feel free to ask me to clarify any feedback or if you'd like another practice question."}
        ]

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("What would you like to ask?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = call_grok_api(st.session_state.messages)
            st.markdown(response)
            
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
