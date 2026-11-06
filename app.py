import streamlit as st
import requests
from kiwipiepy import Kiwi
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# 1. Kiwi 형태소 분석기 초기화
@st.cache_resource
def load_kiwi():
    return Kiwi()

kiwi = load_kiwi()

# 2. GitHub 댓글 수집 함수
def fetch_github_comments(repo_owner, repo_name, token=None):
    # Issue 및 PR 댓글 조회 API Endpoint
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/comments"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    if token:
        headers["Authorization"] = f"token {token}"
        
    comments = []
    params = {"per_page": 100, "page": 1}
    
    # 최근 100개 댓글 수집
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        for item in data:
            comments.append(item.get("body", ""))
        return comments
    else:
        st.error(f"데이터를 가져오는데 실패했습니다. (상태 코드: {response.status_code})")
        return []

# 3. 텍스트 정제 및 명사 추출 함수
def extract_nouns(comments):
    full_text = " ".join(comments)
    # 한글, 영문, 공백을 제외한 특수문자 제거
    clean_text = re.sub(r'[^가-힣a-zA-Z\s]', '', full_text)
    
    tokens = kiwi.tokenize(clean_text)
    nouns = [token.form for token in tokens if token.tag.startswith('NN') and len(token.form) > 1]
    
    return " ".join(nouns)

# 4. Streamlit UI 구성
st.title("🐙 GitHub 댓글 키워드 분석기")
st.write("특정 GitHub 저장소의 Issue 및 PR 댓글을 수집하여 워드클라우드를 생성합니다.")

# 사용자 입력
col1, col2 = st.columns(2)
with col1:
    repo_owner = st.text_input("GitHub Owner (예: facebook)", value="")
with col2:
    repo_name = st.text_input("Repository Name (예: react)", value="")

github_token = st.sidebar.text_input("GitHub Personal Access Token (선택사항 - API 제한 완화용)", type="password")
font_path = st.sidebar.text_input("한글 폰트 경로", value="malgun.ttf")  # Windows: malgun.ttf, Mac: AppleGothic.ttf

if st.button("댓글 분석 및 워드클라우드 생성"):
    if not repo_owner or not repo_name:
        st.warning("Owner와 Repository 이름을 모두 입력해주세요.")
    else:
        with st.spinner("GitHub에서 댓글을 수집하는 중..."):
            comments = fetch_github_comments(repo_owner, repo_name, github_token)
            
        if comments:
            st.success(f"총 {len(comments)}개의 댓글을 성공적으로 수집했습니다!")
            
            with st.spinner("형태소 분석 및 워드클라우드 생성 중..."):
                processed_text = extract_nouns(comments)
                
                if processed_text.strip():
                    # 워드클라우드 생성
                    wc = WordCloud(
                        font_path=font_path,
                        background_color="white",
                        width=800,
                        height=400
                    ).generate(processed_text)
                    
                    # Matplotlib 시각화
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wc, interpolation='bilinear')
                    ax.axis('off')
                    
                    st.pyplot(fig)
                else:
                    st.warning("분석할 수 있는 의미 있는 단어가 부족합니다.")
