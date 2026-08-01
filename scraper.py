#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prestige-okayama.info の出勤表を取得して shifts.json を生成
サイト構造: 「週間出勤表 YYYY/M/D～YYYY/M/D」見出し + h3(名前) + h4(N日 （曜）シフト)
"""
import json
import re
import sys
import datetime
import requests
from bs4 import BeautifulSoup

URL = "https://www.prestige-okayama.info/%E5%87%BA%E5%8B%A4%E8%A1%A8/"
VALID = {"休", "早", "遅", "通"}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja-JP,ja;q=0.9",
}

WEEK_RE = re.compile(r"週間出勤表\s*(\d{4})/(\d{1,2})/(\d{1,2})\s*[～〜]\s*(\d{4})/(\d{1,2})/(\d{1,2})")
DAY_RE = re.compile(r"(\d{1,2})日\s*（(.)）\s*(.*)")


def main():
    resp = requests.get(URL, timeout=30, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # 本文の全要素を文書順に走査
    weeks = []
    current_week = None
    current_staff = None

    body_text_elements = soup.find_all(["h1", "h2", "h3", "h4", "p", "div", "strong"])
    seen_week_labels = set()

    for el in soup.find_all(string=WEEK_RE):
        pass  # 週見出しはテキスト検索で拾う

    # 文書順で処理するため、全要素を順に見る
    for el in soup.body.descendants if soup.body else []:
        if not hasattr(el, "name") or el.name is None:
            continue

        text = el.get_text(strip=True) if el.name in ("h1", "h2", "h3", "h4", "p", "strong", "div") else ""

        # 週見出し検出（子要素の重複検出を避けるため、直下テキストで判定）
        if el.name in ("h1", "h2", "p", "div", "strong"):
            m = WEEK_RE.search(text)
            if m and text not in seen_week_labels and len(text) < 60:
                seen_week_labels.add(text)
                y1, m1, d1 = int(m.group(1)), int(m.group(2)), int(m.group(3))
                y2, m2_, d2 = int(m.group(4)), int(m.group(5)), int(m.group(6))
                start = datetime.date(y1, m1, d1)
                end = datetime.date(y2, m2_, d2)
                dates = []
                d = start
                while d <= end and len(dates) < 7:
                    dates.append({"iso": d.isoformat(), "label": f"{d.month}/{d.day}",
                                  "dow": "日月火水木金土"[(d.weekday() + 1) % 7]})
                    d += datetime.timedelta(days=1)
                current_week = {"start": start.isoformat(), "dates": dates, "staff": []}
                weeks.append(current_week)
                current_staff = None
                continue

        if current_week is None:
            continue

        if el.name == "h3":
            name = text
            if name and len(name) <= 10:
                current_staff = {"name": name, "shifts": []}
                current_week["staff"].append(current_staff)
            continue

        if el.name == "h4" and current_staff is not None:
            m = DAY_RE.match(text)
            if m:
                val = m.group(3).strip()
                if val in VALID:
                    current_staff["shifts"].append(val)
                elif "作成中" in val or val == "":
                    current_staff["shifts"].append("未")
                else:
                    current_staff["shifts"].append("未")

    # シフトが7日分ない人は未で埋める
    for w in weeks:
        for s in w["staff"]:
            while len(s["shifts"]) < len(w["dates"]):
                s["shifts"].append("未")
        # シフトが1件もない週は除外対象
        w["staff"] = [s for s in w["staff"] if s["shifts"]]

    weeks = [w for w in weeks if w["staff"]]

    if not weeks:
        print("ERROR: no data parsed", file=sys.stderr)
        sys.exit(1)

    out = {
        "updated": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M"),
        "weeks": weeks[:2],
    }

    with open("shifts.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    total = sum(len(w["staff"]) for w in out["weeks"])
    print(f"OK: {len(out['weeks'])} weeks, {total} staff rows")


if __name__ == "__main__":
    main()
