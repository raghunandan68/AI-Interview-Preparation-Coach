import streamlit as st
import numpy as np
import cv2
from components.interview import count_faces

def render_verification():
    st.markdown("<h2 style='text-align: center;'>🛡️ Secure Verification</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Captured media will be verified locally to ensure interview integrity.</p>", unsafe_allow_html=True)
    
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📷 Step 1: Camera Check")
        cam_photo = st.camera_input("Take a photo to verify your identity", key="verif_cam")
        
        face_count = 0
        if cam_photo:
            with st.spinner("Checking for faces..."):
                face_count = count_faces(cam_photo)
                if face_count == 1:
                    st.success("✅ Identity Verified: 1 Face Detected")
                elif face_count == 0:
                    st.warning("⚠️ No face detected. Please ensure you are clearly visible.")
                else:
                    st.error(f"🚨 Access Blocked: {face_count} faces detected. Please ensure you are alone.")
                    st.info("For security and fairness, only one participant is allowed in the interview.")

    with col2:
        st.markdown("### 🎤 Step 2: Microphone Check")
        st.info("Record a short test (1-2 seconds) to confirm your microphone is working.")
        audio_test = st.audio_input("Test Microphone 🎤", key="verif_mic")
        
        mic_ok = False
        if audio_test:
            with st.spinner("Verifying audio..."):
                # Basic check: did we get data?
                if audio_test.size > 0:
                    st.success("✅ Microphone access confirmed!")
                    mic_ok = True
                else:
                    st.error("❌ Audio capture failed. Please try again.")

    st.markdown("---")

    # The "Manual" button enabled ONLY when logic passes
    is_ready = (face_count == 1 and mic_ok)

    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if is_ready:
            st.success("🎉 All checks passed! You are ready to begin.")
            if st.button("🚀 Enter Interview Room", type="primary", use_container_width=True):
                st.session_state.permissions_confirmed = True
                st.session_state.current_page = 'interview'
                st.rerun()
        else:
            st.button("🚀 Enter Interview Room", disabled=True, use_container_width=True)
            
        if st.button("⬅️ Cancel and Return to Dashboard", use_container_width=True):
            st.session_state.current_page = 'dashboard'
            st.rerun()
