import streamlit as st
import requests
from kiwipiepy import Kiwi
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# 페이지 기본 설정
st.set_page_config(
    page_title="유튜브 데이터 분석기",
    page_icon="🎬",
    layout="wide"
)

# Kiwi 형태소 분석기 캐싱 로드
@st.cache_resource
def load_kiwi():
    return Kiwi()

kiwi = load_kiwi()

# 유튜브 동영상 ID 추출 함수
def extract_video_id(url):
    pattern = r'(?:v=|\/live\/|\/shorts\/|youtu\.be\/|\/embed\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

# 유튜브 댓글 수집 함수 (YouTube Data API v3)
def fetch_youtube_comments(video_id, api_key, max_results=100):
    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "key": api_key,
        "maxResults": max_results,
        "order": "relevance"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        comments = []
        for item in data.get("items", []):
            text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(text)
        return comments
    else:
        st.error(f"댓글을 불러오는 데 실패했습니다. (오류 코드: {response.status_code})")
        return []

# 명사 추출 및 데이터 정제 함수
def extract_nouns(comments):
    full_text = " ".join(comments)
    clean_text = re.sub(r'[^가-힣a-zA-Z\s]', '', full_text)
    tokens = kiwi.tokenize(clean_text)
    nouns = [token.form for token in tokens if token.tag.startswith('NN') and len(token.form)
