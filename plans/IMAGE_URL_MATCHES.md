# Image URL Matches

- scope: workspace `*.ipynb`, `*.md`, `*.txt`
- unique_image_urls: `22`
- matched_in_rag_kb: `8`

## Document Map

| 문서 | 역할 |
|------|------|
| [PLAN.md](PLAN.md) | 실행 계획 · 에이전트 트랙 |
| [RAG_URL_KNOWLEDGE_BASE.md](RAG_URL_KNOWLEDGE_BASE.md) | 이미지 URL 포함 논문/참고 URL 원본 |
| [IMAGE_STRUCTURE_GRAPHS.md](IMAGE_STRUCTURE_GRAPHS.md) | 이미지 기반 Mermaid 다이어그램 |
| `IMAGE_URL_MATCHES.md` (이 파일) | 이미지 URL ↔ 노트북/KB 소스 매핑 |

## Matched With RAG_URL_KNOWLEDGE_BASE
- [CLIP 임베딩 유사도 개념을 시각적으로 설명하는 참고 이미지](https://greeksharifa.github.io/public/img/2021-12-19-CLIP/01a.png)
  - sources: `LLM_031_Multimodal_RAG_Part1[Answer].ipynb`, `plans/rag-upgrade/RAG_URL_KNOWLEDGE_BASE.md`, `plans/rag-upgrade/agents/result-agent-08.md`, `plans/rag-upgrade/agents/urls-agent-08.txt`
  - diagram: [IMAGE_STRUCTURE_GRAPHS.md #01 CLIP](IMAGE_STRUCTURE_GRAPHS.md#01-clip-contrastive-pre-training)
- [LangGraph 단기·장기 메모리 차이를 설명해 RAG 메모리 설계 평가에 유용한 이미지](https://langchain-ai.github.io/langgraph/concepts/img/memory/short-vs-long.png)
  - sources: `LLM_022_LangGraph_Memory.ipynb`, `plans/rag-upgrade/RAG_URL_KNOWLEDGE_BASE.md`, `plans/rag-upgrade/agents/result-agent-03.md`, `plans/rag-upgrade/agents/urls-agent-03.txt`
  - diagram: [IMAGE_STRUCTURE_GRAPHS.md #02 Short vs Long Memory](IMAGE_STRUCTURE_GRAPHS.md#02-short-vs-long-memory-recovered)
- [멀티쿼리 검색 흐름을 시각화한 이미지로 RAG 검색 확장 전략 설명 자료에 적합](https://raw.githubusercontent.com/tsdata/image_files/main/202505/multi-query.png)
  - sources: `LLM_011_Query_Expansion.ipynb`, `plans/rag-upgrade/RAG_URL_KNOWLEDGE_BASE.md`, `plans/rag-upgrade/agents/result-agent-01.md`, `plans/rag-upgrade/agents/urls-agent-01.txt`
  - diagram: [IMAGE_STRUCTURE_GRAPHS.md #03 Multi-Query/RAG-Fusion](IMAGE_STRUCTURE_GRAPHS.md#03-multi-query--rag-fusion--dmqr-rag)
- [HyDE 쿼리 확장 개념을 시각화해 RAG 검색 개선 아이디어 검토에 도움 되는 이미지](https://raw.githubusercontent.com/tsdata/image_files/main/202505/query_HyDE.png)
  - sources: `LLM_011_Query_Expansion.ipynb`, `plans/rag-upgrade/RAG_URL_KNOWLEDGE_BASE.md`, `plans/rag-upgrade/agents/result-agent-03.md`, `plans/rag-upgrade/agents/urls-agent-03.txt`
  - diagram: [IMAGE_STRUCTURE_GRAPHS.md #04 HyDE](IMAGE_STRUCTURE_GRAPHS.md#04-hyde)
- [질의 분해 과정을 시각화한 이미지로 RAG 쿼리 리라이팅·분해 전략 설명 자료에 적합한 리소스](https://raw.githubusercontent.com/tsdata/image_files/main/202505/query_decomposition.png)
  - sources: `LLM_011_Query_Expansion.ipynb`, `plans/rag-upgrade/RAG_URL_KNOWLEDGE_BASE.md`, `plans/rag-upgrade/agents/result-agent-02.md`, `plans/rag-upgrade/agents/urls-agent-02.txt`
  - diagram: [IMAGE_STRUCTURE_GRAPHS.md #05 Query Decomposition](IMAGE_STRUCTURE_GRAPHS.md#05-query-decomposition)
- [질의 재작성 흐름을 시각적으로 검토할 수 있는 참고 이미지](https://raw.githubusercontent.com/tsdata/image_files/main/202505/query_rewrite.png)
  - sources: `LLM_011_Query_Expansion.ipynb`, `plans/rag-upgrade/RAG_URL_KNOWLEDGE_BASE.md`, `plans/rag-upgrade/agents/result-agent-04.md`, `plans/rag-upgrade/agents/urls-agent-04.txt`
  - diagram: [IMAGE_STRUCTURE_GRAPHS.md #06 Query Rewrite](IMAGE_STRUCTURE_GRAPHS.md#06-query-rewrite-trainable-rewrite-retrieve-read)
- [Step-back 쿼리 예시 이미지로 질의 재작성 프롬프트 설명 자료](https://raw.githubusercontent.com/tsdata/image_files/main/202505/query_stepback.png)
  - sources: `LLM_011_Query_Expansion.ipynb`, `plans/rag-upgrade/RAG_URL_KNOWLEDGE_BASE.md`, `plans/rag-upgrade/agents/result-agent-05.md`, `plans/rag-upgrade/agents/urls-agent-05.txt`
  - diagram: [IMAGE_STRUCTURE_GRAPHS.md #07 Step-back Prompting](IMAGE_STRUCTURE_GRAPHS.md#07-step-back-prompting)
- [RAG 평가 프레임워크나 지표 흐름을 시각적으로 요약한 참고 이미지 자료](https://raw.githubusercontent.com/tsdata/image_files/main/202505/rag_evaluation.png)
  - sources: `LLM_008_RAG_Evalution.ipynb`, `plans/rag-upgrade/RAG_URL_KNOWLEDGE_BASE.md`, `plans/rag-upgrade/agents/result-agent-06.md`, `plans/rag-upgrade/agents/urls-agent-06.txt`
  - diagram: [IMAGE_STRUCTURE_GRAPHS.md #08 RAG Evaluation Pipeline](IMAGE_STRUCTURE_GRAPHS.md#08-rag-evaluationbenchmark-pipeline)

## Unmatched Image URLs (found in workspace)
- http://images.cocodataset.org/val2017/000000000285.jpg
  - sources: `LLM_029_Multimodal_LangChain_CLIP.ipynb`
- http://images.cocodataset.org/val2017/000000000776.jpg
  - sources: `LLM_029_Multimodal_LangChain_CLIP.ipynb`
- http://images.cocodataset.org/val2017/000000039769.jpg
  - sources: `LLM_029_Multimodal_LangChain_CLIP.ipynb`
- https://badge.fury.io/py/kiwipiepy.svg
  - sources: `.venv/lib/python3.13/site-packages/kiwipiepy/documentation.md`
- https://img.shields.io/pypi/v/nltk.svg
  - sources: `.venv/lib/python3.13/site-packages/nltk-3.9.2.dist-info/licenses/README.md`
- https://miro.medium.com/max/1400/1*A0Lu2dZfWsCMqWlhw1ZNfQ.png
  - sources: `ML_02_Mebership_classification.ipynb`
- https://miro.medium.com/max/700/1*3KDYxZCMmGbUDtmQdnYhmw.jpeg
  - sources: `ML_02_Mebership_classification.ipynb`
- https://upload.wikimedia.org/wikipedia/commons/3/38/VanGogh_1887_Selbstbildnis.jpg
  - sources: `LLM_030_Multimodal_LangChain_ChatModel.ipynb`
- https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg
  - sources: `LLM_030_Multimodal_LangChain_ChatModel.ipynb`
- https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/800px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg
  - sources: `LLM_030_Multimodal_LangChain_ChatModel.ipynb`
- https://user-images.githubusercontent.com/3299086/202701399-27518fe4-17b7-49d1-aefb-868dffeaa68a.png
  - sources: `docker-elk-main/extensions/fleet/README.md`
- https://user-images.githubusercontent.com/3299086/202701404-958f8d80-a7a0-4044-bbf9-bf73f3bdd17a.png
  - sources: `docker-elk-main/extensions/fleet/README.md`
- https://user-images.githubusercontent.com/3299086/202710574-32a3d419-86ea-4334-b6f7-62d7826df18d.png
  - sources: `docker-elk-main/extensions/metricbeat/README.md`
- https://user-images.githubusercontent.com/3299086/202710594-0deccf40-3a9a-4e63-8411-2e0d9cc6ad3a.png
  - sources: `docker-elk-main/extensions/metricbeat/README.md`
