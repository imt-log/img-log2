# -*- coding: utf-8 -*-
"""
기술사 토픽 한장정리 자동 생성기
- 입력: 토픽명, 태그, 키워드, 설명
- 출력: index.html (기술사 답안형식), diagram.svg, diagram.png(옵션), meta.json
"""

import os, re, json, argparse
from datetime import date

try:
    import cairosvg
    HAS_CAIRO = True
except ImportError:
    HAS_CAIRO = False

# ---------- 유틸 ----------
def slugify(s: str) -> str:
    """한글 포함 슬러그 생성"""
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s\-]+", "-", s)
    return s[:80] or "topic"

def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

def html_escape(s: str) -> str:
    return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

# ---------- SVG 생성 ----------
def make_svg(topic: str):
    """토픽명 박스 + 하위 3박스 구성도"""
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="600">
  <style>text {{ font-family: 'Noto Sans KR', sans-serif; }}</style>
  <rect width="100%" height="100%" fill="#fff"/>
  <rect x="300" y="50" width="400" height="100" rx="12" fill="#2563eb" stroke="#111"/>
  <text x="500" y="110" font-size="26" text-anchor="middle" fill="#fff">{html_escape(topic)}</text>

  <polyline points="500,150 500,250" stroke="#555" stroke-width="2" fill="none" marker-end="url(#arrow)"/>

  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="6" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#555"/>
    </marker>
  </defs>

  <rect x="150" y="250" width="200" height="100" rx="10" fill="#10b981" stroke="#111"/>
  <text x="250" y="310" font-size="20" text-anchor="middle" fill="#fff">특징</text>

  <rect x="400" y="250" width="200" height="100" rx="10" fill="#10b981" stroke="#111"/>
  <text x="500" y="310" font-size="20" text-anchor="middle" fill="#fff">구성요소</text>

  <rect x="650" y="250" width="200" height="100" rx="10" fill="#10b981" stroke="#111"/>
  <text x="750" y="310" font-size="20" text-anchor="middle" fill="#fff">절차</text>
</svg>
"""

# ---------- HTML 템플릿 ----------
def build_html(topic, desc, tags, keywords, pub_date):
    tag_str = ", ".join(tags)
    kw_str = ", ".join(keywords)

    body = f"""
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{html_escape(topic)} | 기술사 토픽 한장정리</title>
<meta name="description" content="{html_escape(desc)}">
<meta name="keywords" content="{html_escape(tag_str)}, {html_escape(kw_str)}">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
  <article>
    <h1>{html_escape(topic)} | 기술사 토픽 한장정리</h1>
    <p><em>최신화: {pub_date}</em></p>

    <h2 id="sec1">1. 개요</h2>
    <p>{html_escape(desc or topic + " 개요 요약.")}</p>

    <h2 id="sec2">2. 특징</h2>
    <ul>
      <li>특징 1</li>
      <li>특징 2</li>
    </ul>

    <h2 id="sec3">3. 구성도</h2>
    <img src="diagram.svg" alt="{html_escape(topic)} 구성도">

    <h2 id="sec4">4. 구성요소</h2>
    <ul>
      <li>구성요소 A</li>
      <li>구성요소 B</li>
      <li>구성요소 C</li>
    </ul>

    <h2 id="sec5">5. 절차</h2>
    <ol>
      <li>단계 1</li>
      <li>단계 2</li>
      <li>단계 3</li>
    </ol>

    <h2 id="sec6">6. 결론</h2>
    <p>
      {html_escape(topic)}는 <strong>{html_escape(", ".join(keywords))}</strong> 관점에서
      핵심적인 의의를 가진다.
    </p>

    <footer>
      <p>태그: {html_escape(tag_str)}</p>
      <p>키워드: {html_escape(kw_str)}</p>
    </footer>
  </article>
</body>
</html>
"""
    return body

# ---------- 생성기 ----------
def generate(topic, desc="", tags=None, keywords=None):
    tags = tags or []
    keywords = keywords or []
    slug = slugify(topic)
    out_dir = os.path.join("topics", slug)
    ensure_dir(out_dir)

    # 1. SVG 저장
    svg_code = make_svg(topic)
    with open(os.path.join(out_dir, "diagram.svg"), "w", encoding="utf-8") as f:
        f.write(svg_code)

    # 2. PNG 변환
    if HAS_CAIRO:
        cairosvg.svg2png(bytestring=svg_code.encode("utf-8"),
                         write_to=os.path.join(out_dir, "diagram.png"))

    # 3. HTML 저장
    pub_date = date.today().isoformat()
    html = build_html(topic, desc, tags, keywords, pub_date)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    # 4. 메타 저장
    meta = {
        "topic": topic,
        "slug": slug,
        "date": pub_date,
        "tags": tags,
        "keywords": keywords
    }
    with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"✅ 생성 완료: {out_dir}/index.html, diagram.svg, meta.json")

# ---------- CLI ----------
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--topic", required=True, help="토픽명 (예: ISO 21500 프로젝트 관리)")
    p.add_argument("--desc", default="", help="개요/설명문")
    p.add_argument("--tags", default="", help="쉼표 구분 태그")
    p.add_argument("--keywords", default="", help="쉼표 구분 키워드")
    args = p.parse_args()

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]

    generate(args.topic, args.desc, tags, keywords)
