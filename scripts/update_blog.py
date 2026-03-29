from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

import feedparser

# 벨로그 RSS 피드 URL
# example : rss_url = 'https://api.velog.io/rss/@soozi'
rss_url = 'https://api.velog.io/rss/@gyeongyeonk'

# 레포지토리 루트 기준 경로
repo_path = Path(__file__).resolve().parents[1]

# 'posts' 폴더 경로
posts_dir = repo_path / 'posts'

# 'posts' 폴더가 없다면 생성
posts_dir.mkdir(exist_ok=True)


def build_file_name(title: str) -> str:
    sanitized = title.replace('/', '-')
    sanitized = sanitized.replace('\\', '-')
    return f'{sanitized}.md'


def get_entry_year(entry) -> str:
    parsed = entry.get('published_parsed') or entry.get('updated_parsed')
    if parsed:
        return str(parsed.tm_year)

    raw_date = entry.get('published') or entry.get('updated')
    if raw_date:
        try:
            return str(parsedate_to_datetime(raw_date).year)
        except (TypeError, ValueError, IndexError, OverflowError):
            pass

    return str(datetime.now().year)

# RSS 피드 파싱
feed = feedparser.parse(rss_url)

if getattr(feed, 'bozo', False):
    print(f'RSS parse warning: {feed.bozo_exception}')

print(f'Fetched {len(feed.entries)} entries from {rss_url}')

# 각 글을 파일로 저장
created_count = 0
updated_count = 0
expected_files = set()
for entry in feed.entries:
    file_name = build_file_name(entry.get('title', 'untitled'))
    year_dir = posts_dir / get_entry_year(entry)
    year_dir.mkdir(exist_ok=True)
    file_path = year_dir / file_name
    expected_files.add(file_path)
    content = entry.get('description', '')

    if not file_path.exists():
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        created_count += 1
        continue

    current_content = file_path.read_text(encoding='utf-8')
    if current_content != content:
        file_path.write_text(content, encoding='utf-8')
        updated_count += 1

deleted_count = 0
for existing_file in posts_dir.rglob('*.md'):
    if existing_file not in expected_files:
        existing_file.unlink()
        deleted_count += 1

for year_dir in posts_dir.iterdir():
    if year_dir.is_dir() and not any(year_dir.iterdir()):
        year_dir.rmdir()

print(f'Created {created_count} new post files')
print(f'Updated {updated_count} existing post files')
print(f'Deleted {deleted_count} removed post files')
