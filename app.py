import streamlit as st
from pytube import YouTube
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def download_media(yt, download_type='video'):
    try:
        if download_type == 'video':
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        else:
            stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        
        if stream:
            download_path = stream.download()
            base, ext = os.path.splitext(download_path)
            if download_type == 'audio':
                new_file = base + '.mp3'
                os.rename(download_path, new_file)
                return new_file
            return download_path
        return None
    except Exception as e:
        st.error(f"Download Error: {e}")
        logging.error(f"Download failed: {str(e)}")
        return None

# Streamlit UI
st.title("YouTube Downloader 🎥➡️📥")
st.write("Paste a YouTube URL below to download video or audio")

url = st.text_input("YouTube URL:")

if url:
    try:
        if 'yt' not in st.session_state or st.session_state.current_url != url:
            with st.spinner('Initializing connection...'):
                st.session_state.yt = YouTube(
                    url,
                    use_oauth=True,
                    allow_oauth_cache=True
                )
                
                if st.session_state.yt.age_restricted:
                    st.info("Age-restricted content detected, attempting bypass...")
                    st.session_state.yt.bypass_age_gate()
                
                st.session_state.current_url = url
                st.rerun()

        if 'yt' in st.session_state:
            yt = st.session_state.yt
            st.image(yt.thumbnail_url, width=300)
            st.subheader(yt.title)
            st.write(f"Channel: {yt.author}")
            st.write(f"Length: {yt.length // 60} minutes {yt.length % 60} seconds")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Video Download")
                if st.button("Download MP4"):
                    with st.spinner('Downloading video...'):
                        video_path = download_media(yt, 'video')
                        if video_path:
                            with open(video_path, 'rb') as f:
                                st.download_button(
                                    label="Save Video",
                                    data=f,
                                    file_name=os.path.basename(video_path),
                                    mime='video/mp4'
                                )
                            os.remove(video_path)
            
            with col2:
                st.subheader("Audio Download")
                if st.button("Extract MP3"):
                    with st.spinner('Extracting audio...'):
                        audio_path = download_media(yt, 'audio')
                        if audio_path:
                            with open(audio_path, 'rb') as f:
                                st.download_button(
                                    label="Save Audio",
                                    data=f,
                                    file_name=os.path.basename(audio_path),
                                    mime='audio/mpeg'
                                )
                            os.remove(audio_path)

    except Exception as e:
        st.error(f"Error: {str(e)}")
        logging.error(f"Main error: {str(e)}")


