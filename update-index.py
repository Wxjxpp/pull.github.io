#!/usr/bin/env python3
"""扫描 vulkans/ 目录，生成嵌入数据，更新 index.html"""

import json, os, re

VULKANS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vulkans')
INDEX_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
CDN_BASE = 'https://cdn.jsdelivr.net/gh/Wxjxpp/pull.github.io@main'
RAW_BASE = 'https://raw.githubusercontent.com/Wxjxpp/pull.github.io/main'
LARGE_FILE_THRESHOLD = 50 * 1024 * 1024  # 50MB，超过此大小用 raw GitHub

CATEGORIES = ['snapdragon', 'mediatek', 'exynos', 'tensor', 'mali', 'powervr', 'other', '待验证']


def format_bytes(size):
    for unit in ['Bytes', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f'{size:.1f} {unit}' if unit != 'Bytes' else f'{size} Bytes'
        size /= 1024
    return f'{size:.1f} TB'


def build_files_data():
    """扫描所有 .so 文件，返回 {category: [{name, size, cdnUrl}]}"""
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
    """加载 drivers.json"""
    meta_path = os.path.join(VULKANS_DIR, 'drivers.json')
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def main():
    files_data = build_files_data()
    meta = load_meta()

    # 合并 meta 到 files_data
    for cat, files in files_data.items():
        for f in files:
            cat_meta = meta.get(cat, [])
            match = next((m for m in cat_meta if m['name'] == f['name']), None)
            if match:
                f['meta'] = match

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    # 生成嵌入的 JS 数据
    embedded = f'const EMBEDDED_FILES = {json.dumps(files_data, ensure_ascii=False, indent=2)};'
    embedded += f'\n        const CDN_BASE = "{CDN_BASE}";'
    embedded += f'\n        const RAW_BASE = "{RAW_BASE}";'
    embedded += f'\n        const LARGE_FILE_THRESHOLD = 50 * 1024 * 1024; // 50MB，超过此大小用 raw GitHub（jsDelivr 有 50MB 限制）'

    # 使用正则替换 EMBEDDED_FILES 数据块
    pattern = r'const EMBEDDED_FILES = \{[\s\S]*?const LARGE_FILE_THRESHOLD = \d+ \* \d+ \* \d+;[^\n]*\n'
    new_html = re.sub(pattern, embedded + '\n', html, count=1)

    if new_html == html:
        if re.search(pattern, html):
            total = sum(len(v) for v in files_data.values())
            print(f'OK: 数据已是最新 ({", ".join(f"{k}:{len(v)}个" for k,v in files_data.items())})')
            return 0
        print(f'ERROR: 未找到 EMBEDDED_FILES 数据块')
        return 1

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(new_html)

    total = sum(len(v) for v in files_data.values())
    print(f'OK: 已嵌入 {total} 个文件的数据 ({", ".join(f"{k}:{len(v)}个" for k,v in files_data.items())})')
    return 0


if __name__ == '__main__':
    exit(main())