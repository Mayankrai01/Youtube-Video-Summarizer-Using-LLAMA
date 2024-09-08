from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import streamlit as st
from langchain_groq import ChatGroq
import os
from youtube_transcript_api import YouTubeTranscriptApi ## For Public Videos Only
from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    groq_api_key=os.getenv("groq_api_key")
)

prompt="""You are an Youtube video summarizer. Take the transcript, 
summarize the video and also return important pointer"""


def extract_transcript_details(youtube_video_url):
    try:

        # Extract the video ID from the URL

        # Find the starting index of the value (after "v=")
        start_index = youtube_video_url.find("v=") + 2  # Add 2 to skip "v="

        # Find the ending index of the value (before "&")
        end_index = youtube_video_url.find("&")

        # Extract the value between start and end indices
        video_id = youtube_video_url[start_index:end_index]

        # List all available transcripts for the video
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try to get the manually created transcript first
        transcript = ""
        languages = ['en', 'hi', 'ta', 'te', 'bn', 'gu', 'fr', 'de', 'es']
        try:
            transcript_obj = transcript_list.find_manually_created_transcript(languages)
            transcript_text = transcript_obj.fetch()
            for item in transcript_text:
                transcript += " " + item["text"]

        # If no manually created transcript is available, fallback to auto-generated
        except NoTranscriptFound:
            transcript_obj = transcript_list.find_generated_transcript(languages)
            transcript_text = transcript_obj.fetch()
            for item in transcript_text:
                transcript += " " + item["text"]

        return transcript

    except TranscriptsDisabled:
        raise Exception("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise Exception("No transcripts were found for this video.")
    except Exception as e:
        raise e



def generate_content(transcript_text, prompt):
    model = llm
    response = model.invoke(prompt+transcript_text)
    return response


st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    # Find the starting index of the value (after "v=")
    start_index = youtube_link.find("v=") + 2  # Add 2 to skip "v="

    # Find the ending index of the value (before "&")
    end_index = youtube_link.find("&")

    # Extract the value between start and end indices
    video_id = youtube_link[start_index:end_index]
    st.image(
        f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    video_transcript = extract_transcript_details(youtube_link)

    if video_transcript:
        summary = generate_content(transcript_text=video_transcript, prompt=prompt)
        st.markdown("## Detailed Notes:")
        st.write(summary.content)
