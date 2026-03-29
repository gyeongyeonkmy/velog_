import os
from pathlib import Path

import feedparser

# 벨로그 RSS 피드 URL
# example : rss_url = 'https://api.velog.io/rss/@soozi'
rss_url = 'https://api.velog.io/rss/@gyeongyeonk'

# 레포지토리 루트 기준 경로
repo_path = Path(__file__).resolve().parents[1]

# 'velog-posts' 폴더 경로
posts_dir = repo_path / 'velog-posts'

# 'velog-posts' 폴더가 없다면 생성
posts_dir.mkdir(exist_ok=True)

# RSS 피드 파싱
feed = feedparser.parse(rss_url)

if getattr(feed, 'bozo', False):
    print(f'RSS parse warning: {feed.bozo_exception}')

print(f'Fetched {len(feed.entries)} entries from {rss_url}')

# 각 글을 파일로 저장
created_count = 0
for entry in feed.entries:
    # 파일 이름에서 유효하지 않은 문자 제거 또는 대체
    file_name = entry.title
    file_name = file_name.replace('/', '-')  # 슬래시를 대시로 대체
    file_name = file_name.replace('\\', '-')  # 백슬래시를 대시로 대체
    # 필요에 따라 추가 문자 대체
    file_name += '.md'
    file_path = posts_dir / file_name

    # 파일이 이미 존재하지 않으면 생성
    if not file_path.exists():
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(entry.description)  # 글 내용을 파일에 작성
        created_count += 1

print(f'Created {created_count} new post files')
