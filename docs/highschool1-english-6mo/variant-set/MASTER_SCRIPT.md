# 2026 고1 영어 변형 문제집 — 마스터 제작 스크립트

## 목적
2026년 6월 고1 전국연합학력평가 영어 18~45번 지문을 **한 글자도 바꾸지 않고** 유지하되,
문제(발문·선지·서술형)를 더 어렵고 다양하게 변형한 내신 대비 문제집을 제작한다.

---

## 절대 원칙 (Anti-Leakage Rules)

1. **지문 단일 버전**: 공통 지문 박스 하나만 인쇄. 절대 같은 지문을 문항 아래 다시 인쇄하지 않는다.
2. **빈칸**: 빈칸(\_\_\_\_)은 반드시 공통 지문 안에 직접 삽입. 별도 패시지 없음.
3. **어법 네모**: `\nemo{A / B}` 형태를 공통 지문 안에 직접 삽입. 문항에 별도 지문 없음.
4. **선지 패러프레이즈**: 불일치·일치 문항의 모든 선지는 본문을 그대로 복사하지 않고 동의어·구조 변환으로 패러프레이즈. "단어 찾기"로 풀 수 없게.
5. **서술형**: 정답이 본문에 그대로 존재하는 영작 절대 금지. 반드시 **태변환·해석(영→한)·단답(문맥추론)** 형태로만 출제.
6. **함의추론 선지**: 밑줄 구절의 의미를 묻는 문항은 선지를 영어로 작성, 본문 어휘 재활용하되 논리적으로 부분만 맞는 매력적 오답 구성.

---

## LaTeX 템플릿 (완전 검증본 — xelatex으로 컴파일)

```latex
\documentclass[11pt,a4paper]{article}

\usepackage{kotex}
\usepackage{fontspec}
\setmainfont{Times New Roman}
\setmainhangulfont{AppleMyungjo}
\setsanshangulfont{Apple SD Gothic Neo}

\usepackage[a4paper,top=18mm,bottom=18mm,left=20mm,right=20mm]{geometry}
\usepackage{fancyhdr}
\setlength{\headheight}{24pt}
\usepackage{enumitem}
\usepackage{mdframed}
\usepackage{array}
\usepackage{booktabs}

\setlength{\parindent}{1em}
\linespread{1.18}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.6pt}
\fancyhead[L]{\sffamily\bfseries 2026 고1 영어 변형 — 지문 XX}
\fancyhead[R]{\sffamily [소재 키워드]}
\renewcommand{\footrulewidth}{0pt}
\fancyfoot[C]{\framebox[16mm][c]{\thepage}}

\newcommand{\qno}[1]{\par\vspace{8pt}\noindent{\sffamily\bfseries #1.}\ }
\newcommand{\instr}[1]{{\sffamily #1}\par\vspace{3pt}}
\newlist{choices}{enumerate}{1}
\setlist[choices]{label=,leftmargin=1.5em,itemsep=2pt,topsep=3pt,parsep=0pt}
\newmdenv[linewidth=0.6pt,roundcorner=3pt,innertopmargin=7pt,innerbottommargin=7pt,
          innerleftmargin=9pt,innerrightmargin=9pt,skipabove=5pt,skipbelow=5pt]{pbox}
\newcommand{\nemo}[1]{\fbox{\,#1\,}}

\begin{document}

\begin{center}
{\fontsize{15}{17}\selectfont\sffamily\bfseries [지문 XX] 다음 글을 읽고 물음에 답하시오.}
\end{center}
\vspace{4pt}

% 공통 지문 박스 (수정 가능: 빈칸 \rule{Xcm}{0.4pt} 또는 \nemo{A/B} 삽입)
\begin{pbox}
[지문 내용]
\end{pbox}

% Q1
\qno{1}\instr{[발문]}
\begin{choices}
\item ① ...
...
\end{choices}

\end{document}
```

---

## 문항 유형별 LaTeX 패턴

### 빈칸추론
- 지문 내 해당 어구를 `\rule{3.5cm}{0.4pt}` 로 교체 (선지 없이 지문만 수정)
- 발문: `다음 빈칸에 들어갈 말로 가장 적절한 것은?` (3점이면 `[3점]` 추가)
- 선지: ①②③④⑤, 영어 어구 혹은 절

### 어법(네모)
- 지문 내 해당 위치에 `\nemo{형태A / 형태B}` 삽입
- 발문: `(A), (B), (C)의 각 네모 안에서 어법에 맞는 표현으로 가장 적절한 것은?`
- 선지: tabular 형태 ①~⑤, 각 행이 (A)(B)(C) 조합

### 어휘(문맥상 부적절)
- 지문 내 5개 단어에 `\underline{단어}` 삽입
- 발문: `밑줄 친 (①)~(⑤) 중에서 문맥상 낱말의 쓰임이 적절하지 않은 것은?`
- 선지: `① (①) ② (②) ③ (③) ④ (④) ⑤ (⑤)` 형태

### 내용 일치/불일치
- 발문: `윗글의 내용과 일치하지 않는 것은?` 또는 `일치하는 것은?`
- **모든 선지 반드시 패러프레이즈** (본문 어휘 직접 인용 금지)
- 선지: 영어 또는 한글 가능

### 영어 제목/주제
- 발문: `윗글의 제목으로 가장 적절한 것은?` / `주제로 가장 적절한 것은?`
- 선지: 영어 5개, 주제와 한두 단어 차이의 매력적 오답 포함

### 요약문 (A)(B)
- 발문: `다음은 윗글을 요약한 것이다. 빈칸 (A), (B)에 들어갈 말로 가장 적절한 것은?`
- 요약문(이탤릭): 2~3문장, (A)와 (B) 각각 핵심어 1개 blank
- 선지: tabular ①~⑤, 각 행 (A) / (B) 단어 쌍

### 서술형 — 해석 (영→한)
- 발문: `[서술형] 다음 문장을 우리말로 해석하시오.`
- 대상 문장: 가정법·복합 관계사·분사구문 등 구문 복잡한 문장
- 답란: `$\Rightarrow$ \rule{\linewidth}{0.4pt}`

### 서술형 — 태변환
- 발문: `[서술형] 밑줄 친 문장을 [조건]으로 바꿔 쓰시오.`
- 조건 예: "We를 주어로 하는 능동태", "It ~ that 강조구문으로"
- 답란: `$\Rightarrow$ \rule{\linewidth}{0.4pt}`

### 서술형 — 단답(한글)
- 발문: `[서술형] [질문]을 우리말로 간단히 쓰시오.` (조건: ~자 이내 등)
- 답란: `$\Rightarrow$ \rule{10cm}{0.4pt}`

### 함의추론 (밑줄)
- 지문 내 해당 어구에 `\underline{어구}` 삽입
- 발문: `밑줄 친 '[어구]'가 윗글에서 의미하는 바로 가장 적절한 것은?`
- 선지: 영어 5개, 본문 어휘 재활용하되 논리적으로 미묘하게 다른 오답

### 무관 문장
- 발문: `다음 글에서 전체 흐름과 관계 없는 문장은?`
- 지문에 ①②③④⑤ 표시 (`( ① )` 형태, 각 문장 앞)
- 선지: `① ② ③ ④ ⑤` (번호만)

### 글 순서 배열
- 지문: 주어진 첫 문단 박스 + (A)(B)(C) 섹션
- 발문: `주어진 글 다음에 이어질 글의 순서로 가장 적절한 것은?`
- 선지: 5가지 순서 조합

### 문장 삽입
- 지문에 `( ① )` ~ `( ⑤ )` 번호 삽입
- 삽입할 문장 박스 위에 표시
- 발문: `글의 흐름으로 보아, 주어진 문장이 들어가기에 가장 적절한 곳을 고르시오.`

---

## 컴파일 명령
```bash
xelatex -interaction=nonstopmode -halt-on-error 문제XX.tex
xelatex -interaction=nonstopmode -halt-on-error 정답XX.tex
```

## 출력 경로
- 문제지: `docs/highschool1-english-6mo/variant-set/문제{N}.tex` / `.pdf`
- 정답지: `docs/highschool1-english-6mo/variant-set/정답{N}.tex` / `.pdf`
- 작업 디렉토리: `docs/highschool1-english-6mo/variant-set/`

## 정답지 구성
1. 정답 표 (문항번호 / 유형 / 정답 / 배점)
2. 문항별 해설: 정답 근거 문장 인용 + 오답 소거 이유
3. 서술형 모범답안 + 채점 포인트
