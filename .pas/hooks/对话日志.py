"""
Stop Hook: 从 transcript JSONL 提取对话正文，写入日志记录。

触发时机：每次对话停止时自动执行。
输入：stdin 传入 JSON payload，含 transcript_path 字段。
输出：<output_dir>\<hash>.md
"""
import sys
import json
import os
import hashlib
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# ── 读 payload ──────────────────────────────────────────────
try:
    payload = json.loads(sys.stdin.read())
except (json.JSONDecodeError, ValueError):
    sys.exit(0)

transcript_path = payload.get('transcript_path', '')

if not transcript_path or not os.path.isfile(transcript_path):
    sys.exit(0)

# ── 读 JSONL ────────────────────────────────────────────────
events = []
with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue

# ── 过滤 + 提取 ─────────────────────────────────────────────
SKIP_EVENT_TYPES = {
    'queue-operation',
    'attachment',
    'file-history-snapshot',
    'system',
    'last-prompt',
}

turns = []
current_role = None
current_texts = []

for event in events:
    if event.get('type') in SKIP_EVENT_TYPES:
        continue

    msg = event.get('message')
    if not isinstance(msg, dict):
        continue

    role = msg.get('role')
    content = msg.get('content')

    if role == 'user':
        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            parts = [b.get('text', '') for b in content if b.get('type') == 'text']
            text = '\n'.join(parts) if parts else ''
        else:
            text = ''

        # 跳过系统注入的伪 user 消息（技能注入、本地命令、command 输出）
        injected_markers = (
            'Base directory for this skill:',
            '<command-name>',
            '<command-message>',
            '<local-command-stdout>',
            '<local-command-caveat>',
        )
        if any(marker in text for marker in injected_markers):
            continue

        if text.strip():
            if current_role == 'user':
                current_texts.append(text)
            else:
                if current_texts:
                    turns.append((current_role, '\n\n'.join(current_texts)))
                current_role = 'user'
                current_texts = [text]

    elif role == 'assistant':
        if isinstance(content, list):
            text_parts = []
            for block in content:
                if block.get('type') == 'text':
                    t = block.get('text', '')
                    if t:
                        text_parts.append(t)
            if text_parts:
                combined = '\n'.join(text_parts)
                if current_role == 'assistant':
                    current_texts.append(combined)
                else:
                    if current_texts:
                        turns.append((current_role, '\n\n'.join(current_texts)))
                    current_role = 'assistant'
                    current_texts = [combined]

if current_texts:
    turns.append((current_role, '\n\n'.join(current_texts)))

if not turns:
    sys.exit(0)

# ── 构建输出 ────────────────────────────────────────────────
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
lines = [
    f'date: {now}',
    f'transcript: {transcript_path}',
    '',
]

for role, text in turns:
    if role == 'user':
        lines.append('## User')
    else:
        lines.append('## Assistant')
    lines.append(text)
    lines.append('')

# ── 写入文件 ────────────────────────────────────────────────
output_dir = str(Path(__file__).resolve().parent.parent.parent / '日志记录')
os.makedirs(output_dir, exist_ok=True)
path_hash = hashlib.md5(transcript_path.encode('utf-8')).hexdigest()[:8]
filename = path_hash + '.md'
output_path = os.path.join(output_dir, filename)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
