import json
from django.conf import settings
from openai import OpenAI

GMS_BASE_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1"

client = OpenAI(
    api_key=settings.GMS_KEY,
    base_url=GMS_BASE_URL,
)

def _safe_json(text: str):
    try:
        # 마크다운 코드 펜스(```json ... ```)가 섞여 들어올 경우를 대비해 정제
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        return json.loads(text)
    except Exception:
        return None

def run_taste_ai(message: str, history: list | None = None):
    """
    사용자의 메시지를 분석하여 DB 검색을 위한 필터와 응답을 생성합니다.
    """
    # 우리 DB에서 사용하는 정확한 장르 목록
    GENRES = "드라마, SF, 판타지, 로맨스, 뮤지컬, 애니메이션, 전쟁, 가족, 다큐멘터리, 스릴러, 공포, 액션, 코미디, 범죄, 모험, 미스터리, 역사, 음악, 서부"

    system = (
        "너는 영화 추천 전문가야. 사용자의 요구사항을 분석해서 DB 검색용 필터와 친절한 답변을 JSON으로 반환해.\n"
        f"1. 장르(genre_names)는 반드시 다음 리스트 중에서만 골라: [{GENRES}]\n"
        "2. 언급된 특정 영화 제목이 있다면 'titles' 배열에 넣어줘.\n"
        "3. 결과는 반드시 마크다운 없이 순수 JSON만 출력해.\n\n"
        "형식:\n"
        "{\n"
        '  "answer": "사용자에게 줄 추천 이유 (2~3문장)",\n'
        '  "filters": {\n'
        '    "genre_names": ["장르1", "장르2"],\n'
        '    "keywords": ["키워드1", "키워드2"],\n'
        '    "titles": ["영화제목1", "영화제목2"],\n'
        '    "min_vote": 0\n'
        '  }\n'
        "}"
    )

    msgs = [{"role": "system", "content": system}]
    if isinstance(history, list) and history:
        msgs += history[-10:]
    msgs.append({"role": "user", "content": message})

    model = getattr(settings, "GMS_MODEL", "gpt-4o-mini")

    res = client.chat.completions.create(
        model=model,
        messages=msgs,
        temperature=0.7,
    )

    raw = res.choices[0].message.content or ""
    data = _safe_json(raw)
    
    # JSON 파싱 실패 시 기본 구조 반환
    if not data:
        data = {
            "answer": "죄송합니다. 추천을 생성하는 중에 문제가 발생했습니다.",
            "filters": {"genre_names": [], "keywords": [], "titles": [], "min_vote": 0}
        }
    
    return data, raw