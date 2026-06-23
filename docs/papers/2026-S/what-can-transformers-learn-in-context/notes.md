# What Can Transformers Learn In-Context? - sidecar notes

원본 PDF: `2022_what_can_transformers_learn_in_context.pdf`

읽는 위치: 2026-S paper pack의 첫 번째 companion note

다음 목표: `2021_decision_transformer.pdf`

## 왜 이 논문부터 시작하는가

Decision Transformer, RT-2, OpenVLA, pi0를 읽다 보면 계속 같은 질문이 나온다.

> "이 모델은 그냥 훈련 데이터에서 비슷한 패턴을 꺼내는 건가, 아니면 context 안에서 뭔가를 새로 배우는 건가?"

이 논문은 그 질문을 자연어가 아니라 아주 깨끗한 함수 학습 문제로 바꾼다. prompt 안에 `(x, y)` 예시들을 넣고, 새 `x_query`의 값을 맞히게 한다. 즉, Transformer가 한 번의 forward pass 안에서 linear regression, sparse regression, tree learning, neural net fitting 비슷한 일을 할 수 있는지 본다.

VLA/physical AI 쪽으로 연결하면 이 관점이 중요하다. 나중에 trajectory, demonstration, robot observation-action history가 전부 "context"가 된다. 이 논문은 그 context가 단순 memory인지, 암묵적인 학습 알고리즘인지 구분하는 첫 렌즈다.

## 읽기 전 배경지식

- **In-context learning**: parameter update 없이 prompt 안의 예시만 보고 새 query에 답하는 능력.
- **Meta-learning**: 여러 task를 보며 "새 task를 빨리 푸는 방법" 자체를 학습하는 큰 틀.
- **Least squares**: linear function을 배우는 최적 기준선. 이 논문에서 Transformer 성능을 재는 핵심 baseline이다.
- **Function class**: linear function, sparse linear function, decision tree, two-layer ReLU network처럼 "배워야 하는 함수들의 집합".
- **Distribution shift**: training prompt와 test prompt의 입력 분포, noise, query 위치가 달라지는 상황.
- **Decoder-only Transformer**: GPT 계열 구조. 여기서는 text token이 아니라 벡터와 scalar output을 번갈아 넣는다.

## 30초 요약

이 논문은 Transformer를 scratch부터 훈련해서 prompt 안의 예시들로 unseen function을 맞히게 한다. linear function에서는 least squares에 가까운 성능을 보이고, sparse linear function에서는 Lasso 비슷하게 sparsity를 이용하며, decision tree와 two-layer NN에서도 task-specific learner에 버금가는 결과를 낸다. 핵심 주장은 "Transformer가 단순 prompt memorization 이상으로, 특정 분포에서 작동하는 학습 알고리즘을 내부에 encode할 수 있다"이다.

주의할 점은 이것이 곧 GPT-3 같은 language model이 항상 진짜 학습을 한다는 증거는 아니라는 것이다. 여기서는 ICL을 하도록 명시적으로 synthetic prompt distribution을 만들어 훈련했다.

## 페이지별 reading guide

| PDF page | 읽을 곳 | 옆에 적어둘 포인트 |
| --- | --- | --- |
| p.1 | Abstract, Introduction 시작 | 이 논문은 "LLM이 ICL을 한다"가 아니라 "Transformer를 ICL하도록 훈련하면 어떤 function class까지 가능한가"를 묻는다. |
| p.2 | 문제 정의, Figure 1 | prompt는 `(x1, f(x1), ..., xk, f(xk), x_query)` 형태다. 자연어 few-shot 예시를 수학 함수 예시로 바꾼 셈이다. |
| p.3 | Section 2, Eq. (2) | 훈련 objective는 모든 prefix에서 다음 함수값을 맞히게 하는 것. text next-token prediction과 거의 같은 구조로 읽으면 된다. |
| p.4 | Section 3, baselines | least squares는 linear regression의 강한 기준선이다. Transformer가 이것에 가까우면 단순 nearest-neighbor보다 훨씬 정교한 일을 하는 것이다. |
| p.5 | Figure 2, memorization 논의 | 핵심 결과 1. prompt/weight vector memorization만으로는 성능을 설명하기 어렵다고 주장한다. 여기서 "algorithm encoded in weights" 관점을 잡는다. |
| p.6 | Figure 3, Section 4 시작 | 모델이 query input 주변에서 실제 linear function처럼 움직이는지 본다. gradient alignment는 "겉보기 정답률"보다 더 내부적인 check다. |
| p.7 | Figure 4, OOD prompts | input covariance, label noise, orthant mismatch에도 어느 정도 버틴다. 단, 완벽한 robust algorithm은 아니다. |
| p.8 | Section 5 시작 | sparse linear, decision tree, two-layer NN으로 난도를 올린다. 여기부터는 "어떤 학습 알고리즘을 흉내내는가"를 baseline별로 보자. |
| p.9 | Figure 5 | 이 논문의 가장 재미있는 figure. Lasso, tree learner, gradient descent baseline과 Transformer를 비교한다. |
| p.10 | Section 6 | capacity와 dimension이 중요하다. 큰 모델일수록 높은 차원과 OOD prompt에 강해진다. |
| p.11 | Figure 6, curriculum, training data ablation | ICL이 그냥 생기는 게 아니라 훈련 난이도와 데이터 다양성에 민감하다. curriculum은 emergence를 빠르게 만든다. |
| p.12 | Related work | ICL, Transformer circuits, meta-learning, data-driven algorithm design의 위치를 잡는다. |
| p.13 | Discussion | 결론은 과장하지 않는다. synthetic setting에서 시작했고, language model로 일반화하려면 추가 연구가 필요하다고 둔다. |
| p.19-p.21 | Appendix A | architecture, training schedule, baseline 구현. 결과를 믿을지 판단할 때 필요한 세부사항이다. |
| p.22-p.31 | Appendix B | Figure 7-14. robustness, capacity, seed variance, curriculum, memorization 논의를 더 확인하고 싶을 때 본다. |

## 핵심 수식과 개념

### Eq. (1): ICL을 성능 기준으로 정의하기

논문은 "모델이 function class `F`를 in-context learn한다"를 평균 loss가 충분히 작다는 조건으로 정의한다. 중요한 점은 이 성능이 **훈련 방식이 아니라 모델 자체의 inference-time behavior**라는 것이다.

읽을 때는 이렇게 바꿔 생각하면 된다.

`prompt examples + query`를 넣었을 때 `f(x_query)`를 잘 맞히면, 그 모델은 그 function class에 대해 ICL을 한다.

### Eq. (2): prefix별 next output prediction

훈련은 prompt 전체를 한 번에 넣고, 각 prefix에서 다음 함수값을 맞히게 한다. 자연어에서 "앞 token들을 보고 다음 token을 맞힌다"와 같은 구조인데, token 자리에 `(x, f(x))`가 들어간다.

이게 Decision Transformer로 넘어갈 때 중요하다. DT도 `(return-to-go, state, action)` 토큰들을 autoregressive하게 배치해서 다음 action을 예측한다.

### "Algorithm in weights" 관점

Transformer가 test prompt의 unseen function을 잘 맞힌다면, 매번 gradient descent를 실행하지 않아도 모델 안에 어떤 학습 절차가 압축되어 있다고 볼 수 있다. 다만 이 절차는 사람이 아는 closed-form algorithm과 같을 수도 있고, training distribution에 특화된 heuristic일 수도 있다.

## Figure/Table 해설

### Figure 1

훈련 때는 random function과 random input들을 계속 샘플링한다. inference 때는 처음 보는 function에서 나온 몇 개의 예시만 주고 query를 맞힌다. 이 그림은 논문 전체의 protocol이다.

### Figure 2

linear function에서 Transformer error가 least squares와 거의 같은 속도로 내려간다. 특히 in-context examples가 dimension 근처에 도달할 때 error가 크게 줄어드는 모양을 보자. 이건 모델이 단순 평균이나 nearest-neighbor보다 linear regression 쪽에 가까운 일을 한다는 신호다.

### Figure 3

고정된 prompt prefix에 대해 query input을 움직이면 모델 출력도 거의 linear function처럼 움직인다. 오른쪽 gradient plot은 모델의 local behavior가 true `w` 또는 projected `w`와 정렬되는지 보여준다. "정답만 맞힌다"보다 더 강한 sanity check다.

### Figure 4

OOD prompt에서 성능이 얼마나 무너지는지 본다. skewed covariance, noisy output, different orthants가 대표 case다. 결론은 "꽤 robust하지만, training distribution 밖에서 완벽한 regression solver는 아니다" 정도로 읽으면 된다.

### Figure 5

복잡한 function class 실험이다.

- sparse linear: Transformer가 sparsity를 이용해 Lasso와 비슷해진다.
- decision tree: greedy tree/XGBoost baseline보다 나은 구간이 있다.
- two-layer NN: gradient descent로 fitting한 NN baseline과 비슷하다.
- NN-trained model on linear functions: 다른 function class로 어느 정도 transfer도 된다.

여기서 가장 중요한 문장은 "single forward pass 안에서 iterative algorithm 비슷한 효과가 난다"이다. 단, 이것이 general-purpose optimizer라는 뜻은 아니다.

### Figure 6

capacity와 dimension의 관계다. 더 큰 모델은 더 높은 차원과 OOD prompt에서 유리하다. 이 그림은 나중에 VLA foundation model을 볼 때 "모델 크기가 단순 memorization capacity만이 아니라 context-conditioned adaptation 능력에도 영향을 준다"는 식으로 연결된다.

### Appendix Figure 7-14

본문 주장을 검증하는 보조 자료다.

- Figure 7-10: scale, OOD, capacity robustness.
- Figure 11: seed variance.
- Figure 12-13: curriculum이 training dynamics를 얼마나 바꾸는지.
- Figure 14: distinct prompts/functions 수가 성능에 미치는 영향.

## 비판적으로 볼 점

- **Synthetic task다.** linear regression과 decision tree는 분석이 깨끗하지만 natural language나 robot control의 messy context와는 거리가 있다.
- **명시적으로 ICL하도록 훈련했다.** language model에서 emergent ICL이 왜 생기는지에 대한 직접 증거는 아니다.
- **Baseline 선택을 조심하자.** least squares는 linear case에서 강하지만, decision tree나 NN case에서는 "최적 learner"가 무엇인지 덜 명확하다.
- **Forward pass가 공짜는 아니다.** inference 때 gradient descent를 안 돌릴 뿐, 그 능력을 얻기 위해 많은 synthetic prompts로 사전 훈련했다.
- **OOD robustness는 제한적이다.** input scale 변화처럼 특정 shift에서는 성능이 확실히 나빠진다.

## Decision Transformer로 연결하기

다음 논문인 Decision Transformer를 읽을 때 이 mapping을 들고 가면 된다.

| 이 논문 | Decision Transformer |
| --- | --- |
| prompt examples `(x, f(x))` | trajectory tokens `(return-to-go, state, action)` |
| query `x_query` | 현재 state와 목표 return |
| output `f(x_query)` | 다음 action |
| function class를 in-context learn | offline data에서 return-conditioned behavior를 생성 |
| least squares와 비교 | CQL, BC, %BC와 비교 |

핵심 질문도 그대로 넘어간다.

1. DT는 정말 RL 알고리즘을 대체하는가, 아니면 좋은 trajectory subset을 behavior cloning하는가?
2. return-to-go token은 이 논문의 prompt examples처럼 task를 지정하는 역할을 하는가?
3. 긴 context는 policy identification을 돕는가, 아니면 단순 history memory인가?
4. VLA에서는 language instruction, visual observation, action history가 어떤 function examples 역할을 하는가?

## 읽고 난 뒤 남길 한 줄

이 논문은 ICL을 신비한 LLM 현상이 아니라 "Transformer가 prompt 안에서 학습 알고리즘을 실행하도록 훈련될 수 있는가"라는 실험 가능한 문제로 바꾼다. 그래서 Decision Transformer와 VLA를 읽기 전 첫 렌즈로 좋다.
