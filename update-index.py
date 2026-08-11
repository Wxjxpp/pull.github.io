#!/usr/bin/env python3
"""扫描 vulkans/、about.md、news.md，生成嵌入数据，更新 index.html"""
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
VULKANS_DIR = os.path.join(ROOT, 'vulkans')
INDEX_FILE = os.path.join(ROOT, 'index.html')
ABOUT_FILE = os.path.join(ROOT, 'about.md')
NEWS_FILE = os.path.join(ROOT, 'news.md')

CDN_BASE = 'https://cdn.jsdelivr.net/gh/Wxjxpp/pull.github.io@main'
RAW_BASE = 'https://raw.githubusercontent.com/Wxjxpp/pull.github.io/main'
LARGE_FILE_THRESHOLD = 50 * 1024 * 1024
CATEGORIES = [
    'snapdragon', 'mediatek', 'exynos', 'tensor', 'mali',
    'powervr', 'xuanjie', 'other', '待验证'
]


def format_bytes(size):
    for unit in ['Bytes', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f'{size:.1f} {unit}' if unit != 'Bytes' else f'{size} Bytes'
        size /= 1024
    return f'{size:.1f} TB'


def build_files_data():
    data = {}
    for cat in CATEGORIES:
        cat_dir = os.path.join(VULKANS_DIR, cat)
        if not os.path.isdir(cat_dir):
            continue
        files = []
        for fname in sorted(os.listdir(cat_dir)):
            fpath = os.path.join(cat_dir, fname)
            if not os.path.isfile(fpath) or not fname.endswith('.so'):
                continue
            size = os.path.getsize(fpath)
            files.append({
                'name': fname,
                'size': size,
                'sizeHuman': format_bytes(size),
            })
        if files:
            data[cat] = files
    return data


def load_meta():
    meta_path = os.path.join(VULKANS_DIR, 'drivers.json')
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def _parse_simple_yaml_value(raw):
    raw = raw.strip()
    if not raw:
        return ''
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    if raw.lower() in ('true', 'false'):
        return raw.lower() == 'true'
    try:
        if raw.isdigit() or (raw.startswith('-') and raw[1:].isdigit()):
            return int(raw)
    except Exception:
        pass
    return raw


def parse_front_matter(text):
    text = text.lstrip('\ufeff')
    if not text.startswith('---'):
        return {}, text
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        return {}, text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end = i
            break
    if end is None:
        return {}, text

    meta = {}
    current_list_key = None
    current_item = None
    for line in lines[1:end]:
        if not line.strip():
            continue
        m_item = re.match(r'^(\s*)-\s+(.*)$', line)
        if m_item:
            rest = m_item.group(2)
            if current_list_key is None:
                continue
            if current_item is not None:
                meta.setdefault(current_list_key, []).append(current_item)
            kv = re.match(r'^([\w\-]+)\s*:\s*(.*)$', rest)
            if kv:
                current_item = {kv.group(1): _parse_simple_yaml_value(kv.group(2))}
            else:
                current_item = {'value': _parse_simple_yaml_value(rest)}
            continue

        m_nested = re.match(r'^(\s{2,})([\w\-]+)\s*:\s*(.*)$', line)
        if m_nested and current_item is not None and current_list_key is not None:
            current_item[m_nested.group(2)] = _parse_simple_yaml_value(m_nested.group(3))
            continue

        m_key = re.match(r'^([\w\-]+)\s*:\s*(.*)$', line)
        if m_key:
            if current_item is not None and current_list_key is not None:
                meta.setdefault(current_list_key, []).append(current_item)
                current_item = None
            key = m_key.group(1)
            val = m_key.group(2).strip()
            if val == '' or val == '|' or val == '>':
                current_list_key = key
                meta[key] = meta.get(key, [])
                current_item = None
            else:
                current_list_key = None
                current_item = None
                meta[key] = _parse_simple_yaml_value(val)
            continue

    if current_item is not None and current_list_key is not None:
        meta.setdefault(current_list_key, []).append(current_item)

    body = '\n'.join(lines[end + 1:]).lstrip('\n')
    return meta, body


def load_about():
    if not os.path.exists(ABOUT_FILE):
        return {'body': '', 'friend_address': []}
    with open(ABOUT_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    meta, body = parse_front_matter(text)
    friends = meta.get('friend_address') or []
    normalized = []
    for item in friends:
        if not isinstance(item, dict):
            continue
        name = str(item.get('name') or item.get('title') or '').strip()
        url = str(item.get('url') or item.get('link') or item.get('href') or '').strip()
        desc = str(item.get('desc') or item.get('description') or '').strip()
        if name and url:
            normalized.append({'name': name, 'url': url, 'desc': desc})
    return {'body': body.strip(), 'friend_address': normalized}


def load_news():
    if not os.path.exists(NEWS_FILE):
        return []
    with open(NEWS_FILE, 'r', encoding='utf-8') as f:
        text = f.read().lstrip('\ufeff').strip()
    if not text:
        return []

    # Split on --- lines, then pair consecutive blocks: (front_matter, body)
    raw_blocks = re.split(r'(?m)^---\s*$', text)
    blocks = [b.strip() for b in raw_blocks if b.strip()]
    items = []
    for i in range(0, len(blocks), 2):
        meta_text = blocks[i]
        body = blocks[i + 1] if i + 1 < len(blocks) else ''
        meta = {}
        for line in meta_text.splitlines():
            m = re.match(r'^([\w\-]+)\s*:\s*(.*)$', line)
            if m:
                key = m.group(1).lower()
                if key in ('title', 'date', 'tag', 'link', 'url', 'summary'):
                    meta[key if key != 'url' else 'link'] = _parse_simple_yaml_value(m.group(2))
        title = str(meta.get('title') or '').strip()
        if not title:
            first = body.splitlines()[0].strip() if body else ''
            first_clean = re.sub(r'^#+\s*', '', first)
            title = first_clean[:40] + ('…' if len(first_clean) > 40 else '') if first_clean else '公告'
            if body.startswith(first) and first.startswith('#'):
                body = '\n'.join(body.splitlines()[1:]).strip()
        items.append({
            'title': title,
            'date': str(meta.get('date') or '').strip(),
            'tag': str(meta.get('tag') or '公告').strip(),
            'link': str(meta.get('link') or '').strip(),
            'body': body,
        })
    return items


def replace_js_const(html, const_name, value_js):
    placeholder = f'/* AUTO_GENERATED_{const_name} */'
    full_line = f'const {const_name} = {value_js};'
    if placeholder in html:
        return html.replace(placeholder, value_js, 1)

    pattern = rf'const {re.escape(const_name)} = (?:\{{[\s\S]*?\n\}}|\[[\s\S]*?\n\]|"(?:\\.|[^"\\])*\ ");'
    # fixed below
    return None


def replace_js_const_fixed(html, const_name, value_js):
    placeholder = f'/* AUTO_GENERATED_{const_name} */'
    full_line = f'const {const_name} = {value_js};'
    if placeholder in html:
        return html.replace(placeholder, value_js, 1)

    # Match pretty-printed object/array ending with newline before closing + semicolon
    pattern = rf'const {re.escape(const_name)} = (?:\{{[\s\S]*?\n\}}|\[[\s\S]*?\n\]);'
    if re.search(pattern, html):
        return re.sub(pattern, full_line, html, count=1)

    pattern2 = rf'const {re.escape(const_name)} = (?:\{{[\s\S]*?\}}|\[[\s\S]*?\]);'
    if re.search(pattern2, html):
        return re.sub(pattern2, full_line, html, count=1)

    print(f'ERROR: 未找到 {const_name} 数据块')
    return None


def main():
    files_data = build_files_data()
    meta = load_meta()
    for cat, files in files_data.items():
        for f in files:
            cat_meta = meta.get(cat, [])
            match = next((m for m in cat_meta if m.get('name') == f['name']), None)
            if match:
                f['meta'] = match

    about = load_about()
    news = load_news()

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    original = html
    embedded_files = json.dumps(files_data, ensure_ascii=False, indent=2)
    embedded_about = json.dumps(about, ensure_ascii=False, indent=2)
    embedded_news = json.dumps(news, ensure_ascii=False, indent=2)

    for name, value in [
        ('EMBEDDED_FILES', embedded_files),
        ('EMBEDDED_ABOUT', embedded_about),
        ('EMBEDDED_NEWS', embedded_news),
    ]:
        html2 = replace_js_const_fixed(html, name, value)
        if html2 is None:
            return 1
        html = html2

    if html == original:
        total = sum(len(v) for v in files_data.values())
        print(
            f'OK: 数据已是最新 '
            f'(files={total}, news={len(news)}, friends={len(about.get("friend_address", []))})'
        )
        return 0

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    total = sum(len(v) for v in files_data.values())
    print(
        f'OK: 已嵌入 files={total} '
        f'({ ", ".join(f"{k}:{len(v)}个" for k, v in files_data.items()) }), '
        f'news={len(news)}, friends={len(about.get("friend_address", []))}, '
        f'about_body={len(about.get("body", ""))} chars'
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
