1) 입력 x에 대해 y를 단계적으로 생성하면서 매 단계마다 반성 토큰 r_t(검색필요도, 근거충분도, 중단여부)를 예측한다.
2) if r_t.검색필요도 > τ then 문서 D_t ← Retrieve(x, y_{<t}) 하고 y_t ← Generate(x, y_{<t}, D_t) else y_t ← Generate(x, y_{<t}) 를 수행한다.
3) if r_t.중단여부 = True or 길이 한계 도달 then 종료하고, 최종 출력은 반성 점수와 근거 일치도를 최대화하도록 선택/재순위화한다.