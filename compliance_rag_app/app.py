import streamlit as st
from rag_core import query_compliance_logic

st.set_page_config(page_title="Compliance RAG Assistant", page_icon="🛡️", layout="wide")

st.title("🛡️ Multi-Framework Compliance RAG")
st.markdown("Ask questions about **NIST CSF v2.0**, **CIS Controls v8**, **HIPAA Security Rule**, and **PCI DSS v4.0**.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask me anything about NIST CSF, CIS Controls, HIPAA, or PCI DSS"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Consulting the regulations..."):
            try:
                response_data = query_compliance_logic(prompt)
                
                # Display Answer
                st.markdown(response_data["answer"])
                
                # Display Evidence in Expander
                with st.expander("📚 Evidence Snapshots"):
                    for item in response_data["evidence"]:
                        st.markdown(f"**{item['source']} - Page {item['page']}**")
                        st.caption(f"\"{item['content_snippet']}\"")
                        st.divider()

                # Add assistant response to chat history (store just the answer text for now)
                st.session_state.messages.append({"role": "assistant", "content": response_data["answer"]})
            except Exception as e:
                st.error(f"An error occurred: {e}")
