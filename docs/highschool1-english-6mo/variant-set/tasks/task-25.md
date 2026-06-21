# Task: Passage 25 — 도표 (자율주행차 신뢰도)

## Chart Data (exact from exam)
Title: The Extent of People's Trust in Self-Driving Cars, 2023
Note: Over 1,000 respondents surveyed per selected country

| Country | A great deal | A lot | A little | Not at all |
|---------|-------------|-------|----------|------------|
| U.K.    | 4%          | 10%   | 34%      | 52%        |
| U.S.    | 6%          | 13%   | 30%      | 51%        |
| China   | 8%          | 47%   | 35%      | 10%        |
| India   | 22%         | 29%   | 35%      | 14%        |

## Passage Text (exact description below chart)
```
The graph above shows the extent of people's trust in self-driving cars based on a survey in 2023. ① All countries except India had less than 10% of people who trusted self-driving cars a great deal. ② More than half of the people in the U.K. and the U.S. did not trust self-driving cars at all. ③ China was the only country where the percentage of people who trusted self-driving cars a lot was over 40%. ④ China and India had the same percentage of people who trusted self-driving cars a little. ⑤ In India, the percentage of people who did not trust self-driving cars at all was the lowest among the four countries.
```

## LaTeX Chart Rendering
Reproduce the chart as a tabular in LaTeX (horizontal bar chart can be simplified to a table):
```latex
\begin{center}
\small
\begin{tabular}{|l|c|c|c|c|}
\hline
 & \textbf{A great deal} & \textbf{A lot} & \textbf{A little} & \textbf{Not at all} \\\hline
U.K.   & 4\%  & 10\% & 34\% & 52\% \\\hline
U.S.   & 6\%  & 13\% & 30\% & 51\% \\\hline
China  & 8\%  & 47\% & 35\% & 10\% \\\hline
India  & 22\% & 29\% & 35\% & 14\% \\\hline
\end{tabular}
\end{center}
\par\noindent\small\textit{Note: Over 1,000 respondents surveyed per selected country}
```

## Passage Modifications
None — no blanks or markings needed. The description sentences ①~⑤ are shown as-is (these ARE the answer choices in the original format; see below).

## Questions

### Q1: 도표 불일치 (2점) — HARDER PARAPHRASE version
Present the chart (table) and 5 statements. Ask which does NOT match.
- **발문**: `다음 표의 내용과 일치하지 않는 것은?`
- **CORRECT answer (the false statement)**: ④
- **Final 5 choices** (all paraphrased, not copy-pasted from original):
  - ① Among the four countries, only India had 20% or more respondents with the highest level of trust.  (TRUE: India=22%, rest <10%)
  - ② In the U.K. and the U.S., more than half of respondents placed in the lowest trust category.  (TRUE: UK=52%, US=51%)
  - ③ China was the sole country where more than 40% of respondents chose "a lot" of trust.  (TRUE: China=47%)
  - ④ All four countries showed the same percentage in the "a little" trust category.  (FALSE: UK=34, US=30, China=35, India=35 — not identical)
  - ⑤ China recorded the lowest share of respondents who expressed no trust in self-driving cars at all.  (TRUE: China=10%)

### Q2: 서술형 — 수치 단답 (2문항)
- **발문**: `[서술형] 표를 참고하여 다음 물음에 답하시오.`
  
  (1) China에서 자율주행차를 "A lot" 또는 "A great deal" 신뢰한다고 응답한 비율의 합을 쓰시오.
  - **Answer**: 55% (47% + 8%)
  - Answer line: `$\Rightarrow$ \rule{4cm}{0.4pt}`

  (2) 네 나라 중 "A great deal"과 "A lot"을 합산한 신뢰 비율이 가장 높은 나라를 쓰시오.
  - U.K.: 4+10=14%, U.S.: 6+13=19%, China: 8+47=55%, India: 22+29=51%
  - **Answer**: China (55%)
  - Answer line: `$\Rightarrow$ \rule{4cm}{0.4pt}`

## Output Files
- `docs/highschool1-english-6mo/variant-set/문제25.tex`
- `docs/highschool1-english-6mo/variant-set/정답25.tex`
