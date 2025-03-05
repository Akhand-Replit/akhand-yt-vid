import streamlit as st
from pytube import YouTube
import os

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
        return None

# Streamlit UI
st.title("YouTube Downloader 🎥➡️📥")
st.write("Paste a YouTube URL below to download video or audio")

url = st.text_input("YouTube URL:")

if url:
    if 'yt' not in st.session_state or st.session_state.current_url != url:
        try:
            # Initialize YouTube object with OAuth and caching
            st.session_state.yt = YouTube(
                url,
                use_oauth=True,
                allow_oauth_cache=True
            )
            
            # Bypass age restriction if needed
            if st.session_state.yt.age_restricted:
                st.session_state.yt.bypass_age_gate()
            
            st.session_state.current_url = url
            st.rerun()
        
        except Exception as e:
            st.error(f"Initialization Error: {str(e)}")
            st.stop()

    if 'yt' in st.session_state:
        yt = st.session_state.yt
        try:
            st.image(yt.thumbnail_url, width=300)
            st.subheader(yt.title)
            st.write(f"Channel: {yt.author}")
            st.write(f"Length: {yt.length // 60} minutes {yt.length % 60} seconds")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Video Download")
                st.write("Download highest quality video")
                if st.button("Download MP4"):
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
                st.write("Download MP3 audio only")
                if st.button("Extract MP3"):
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
            st.error(f"Processing Error: {str(e)}")

# Add informational notes
st.markdown("""
### Notes:
1. For age-restricted videos:
   - You'll need to authenticate with Google in the popup window
   - First download attempt might fail - try again after authentication
2. Private videos cannot be downloaded unless you have direct access
3. Downloads might be slower for large videos
4. Always respect copyright and privacy laws
""")
