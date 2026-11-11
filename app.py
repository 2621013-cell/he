import streamlit as st
import requests
from kiwipiepy import Kiwi
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# Page 기본 설정
st.set_page_config(
    page_title="YouTube 데이터 분석기",
    page_icon="🎬",
    layout="wide"
)

# Kiwi 형태소 분석기 캐싱 로드
@st.cache_resource
def load_kiwi():
    return Kiwi()

kiwi = load_kiwi()

# YouTube Video ID 추출 함수
def extract_video_id(url):
    pattern = r'(?:v=|\/live\/|\/shorts\/|youtu\.be\/|\/embed\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

# YouTube 댓글 수집 함수 (YouTube Data API v3)
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
        st.error(f"댓글을 불러오는데 실패했습니다. (코드: {response.status_code})")
        return []

# 명사 추출 및 데이터 정제 함수
def extract_nouns(comments):
    full_text = " ".join(comments)
    clean_text = re.sub(r'[^가-힣a-zA-Z\s]', '', full_text)
    tokens = kiwi.tokenize(clean_text)
    nouns = [token.form for token in tokens if token.tag.startswith('NN') and len(token.form) > 1]
    return " ".join(nouns)


# 메인 헤더
st.title("🎬 YouTube 멀티 데이터 분석기")
st.write("YouTube 링크를 활용해 썸네일을 추출하고 댓글 키워드를 분석해 보세요.")

# 탭 메뉴 구성
tab1, tab2 = st.tabs(["🖼️ 썸네일 추출기", "💬 댓글 분석 & 워드클라우드"])

# [탭 1] 썸네일 추출 기능
with tab1:
    st.header("YouTube 썸네일 추출")
    video_url_thumb = st.text_input("YouTube 영상 링크를 입력하세요:", key="thumb_url", placeholder="https://www.youtube.com/watch?v=...")
    
    if video_url_thumb:
        video_id = extract_video_id(video_url_thumb)
        if video_id:
            maxres_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            
            st.image(maxres_url, caption="최고화질 썸네일", use_container_width=True)
            st.markdown(f"👉 **[원본 이미지 고화질 링크 다운로드]({maxres_url})**")
        else:
            st.warning("올바른 YouTube URL 형식이 아닙니다.")

# [탭 2] 댓글 분석 및 워드클라우드 기능
with tab2:
    st.header("YouTube 댓글 분석 & 워드클라우드")
    
    api_key = st.sidebar.text_input("YouTube Data API Key 입력", type="password")
    font_path = st.sidebar.text_input("한글 폰트 경로", value="malgun.ttf")
    
    video_url_comment = st.text_input("댓글을 분석할 YouTube 영상 링크를 입력하세요:", key="comment_url", placeholder="https://www.youtube.com/watch?v=...")
    
    if st.button("댓글 분석 시작"):
        if not api_key:
            st.warning("사이드바에 YouTube Data API Key를 입력해야 수집이 가능합니다.")
        elif not video_url_comment:
            st.warning("분석할 YouTube 영상 링크를 입력해주세요.")
        else:
            video_id = extract
