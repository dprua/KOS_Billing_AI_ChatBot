# KT 빌링 과제 분석 챗봇

📋 KT 빌링 시스템 관련 과제 분석 및 유사 프로젝트 검색을 위한 RAG(Retrieval-Augmented Generation) 기반 챗봇
([링크](https://dprua-webapp-001-cagqaphrgtamg2fv.canadacentral-01.azurewebsites.net/)) 

## 📖 프로젝트 개요

KT 빌링 과제 분석 챗봇은 신규 개발 요구사항을 분석하고, 과거 유사한 프로젝트를 검색하여 참고 정보를 제공하는 AI 기반 시스템입니다. Azure의 다양한 클라우드 서비스를 활용하여 문서 저장, 벡터 검색, AI 분석 기능을 제공합니다.

## 🎯 주요 기능

### 1. 과제 분석
- 신규 개발 요구사항 입력 및 분석
- AI 기반 기능 요구사항 도출
- 과거 유사 프로젝트와의 비교 분석
- 개발 방향성 및 참고사항 제시

### 2. 문서 업로드 및 관리
- 다양한 형식의 문서 업로드 지원예정..[현재는 CSV 파일만 업로드 가능] (TXT, PDF, DOCX, CSV)
- 프로젝트 유형별 메타데이터 관리
- 자동 텍스트 추출 및 청킹
- Azure Blob Storage를 통한 안전한 문서 저장

### 3. 지능형 검색
- 벡터 기반 유사도 검색
- 프로젝트 유형, 기술스택, 담당부서별 필터링
- 상위 K개 유사 프로젝트 검색

## 🏗️ 시스템 아키텍처

```
[Streamlit Frontend] 
       ↓
[Document Processor] → [Azure Blob Storage]
       ↓
[Text Embedding] → [Azure AI Search]
       ↓
[Project Analyzer] → [Azure OpenAI]
       ↓
[Analysis Results]
```

## 🛠️ 기술 스택

### Backend
- **Python 3.8+**
- **Streamlit** - 웹 인터페이스
- **Azure OpenAI** - GPT-4o-mini, Text-Embedding-3-Small
- **Azure AI Search** - 벡터 검색 엔진
- **Azure Blob Storage** - 문서 저장소

### AI/ML
- **OpenAI GPT-4o-mini** - 텍스트 생성 및 분석
- **Text-Embedding-3-Small** - 텍스트 임베딩
- **tiktoken** - 토큰 계산

### Azure Services
- **Azure OpenAI Service**
- **Azure Cognitive Search (AI Search)**
- **Azure Blob Storage**

## 📁 프로젝트 구조

```
kt-billing-chatbot/
├── test.py                 # 메인 애플리케이션 코드
├── streamlit.sh           # 배포용 실행 스크립트
├── requirements.txt       # Python 패키지 의존성
├── .env                   # 환경변수 (로컬 개발용)
└── README.md             # 프로젝트 문서
```

## ⚙️ 설치 및 설정

### 1. 필수 요구사항
- Python 3.8 이상
- Azure 구독
- Azure OpenAI Service 리소스
- Azure AI Search 서비스
- Azure Storage Account

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 환경변수를 설정하세요:

```bash
# Azure OpenAI 설정
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_KEY=your_openai_api_key

# Azure AI Search 설정  
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_KEY=your_search_admin_key

# Azure Blob Storage 설정
AZURE_BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 로컬 실행

```bash
streamlit run test.py
```

## 🚀 Azure Web App 배포

### 1. 배포 스크립트 실행

```bash
chmod +x streamlit.sh
./streamlit.sh
```

### 2. Azure Web App 설정

Azure Portal에서 다음 앱 설정을 구성하세요:

- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_KEY`
- `AZURE_SEARCH_ENDPOINT`
- `AZURE_SEARCH_KEY`
- `AZURE_BLOB_CONNECTION_STRING`

### 3. 배포 확인

배포 후 `https://your-app-name.azurewebsites.net`에서 애플리케이션에 접속할 수 있습니다.

## 📚 사용 방법

### 1. 과제 분석하기

1. **과제 분석** 탭을 선택합니다
2. 프로젝트 제목을 입력합니다
3. 상세한 개발 요구사항을 작성합니다
4. **분석 시작** 버튼을 클릭합니다
5. AI 분석 결과와 유사 과제 정보를 확인합니다

### 2. 문서 업로드하기

1. **문서 업로드** 탭을 선택합니다
2. 업로드할 파일을 선택합니다 (TXT, PDF, DOCX, CSV)
3. 프로젝트 메타데이터를 입력합니다:
   - 프로젝트 유형: Billing, Order, SETL
   - 기술스택: 사용된 기술 (예: Java, Spring, Oracle)
   - 담당부서: DEV, OPS, QA
4. **업로드** 버튼을 클릭합니다

## 🎛️ 주요 클래스 설명

### Config
환경변수 및 Azure 서비스 설정 관리

### AzureServices
Azure 서비스 클라이언트 초기화 및 관리

### DocumentProcessor
- 문서 업로드 및 텍스트 추출
- 텍스트 청킹 및 임베딩 생성
- Azure AI Search 인덱싱

### ProjectAnalyzer
- 벡터 기반 유사 프로젝트 검색
- GPT-4o-mini를 활용한 요구사항 분석
- 컨텍스트 기반 분석 결과 생성

### StreamlitApp
Streamlit 기반 웹 인터페이스 제공

## 🔧 설정 가능한 항목

### AI 모델 설정
```python
CHAT_MODEL = "gpt-4o-mini-dprua"
EMBEDDING_MODEL = "text-embedding-3-small"
```

### 검색 설정
```python
SEARCH_INDEX_NAME = "rag-1757924013216"
BLOB_CONTAINER_NAME = "project-documents"
```

### 청킹 설정
```python
max_tokens = 1000  # 청크당 최대 토큰 수
top_k = 2          # 반환할 유사 프로젝트 수
```

## 📊 지원하는 메타데이터

### 프로젝트 유형
- **Billing**: 빌링 시스템
- **Order**: 주문 관리 시스템  
- **SETL**: 정산 시스템

### 담당부서
- **DEV**: 개발팀
- **OPS**: 운영팀
- **QA**: 품질보증팀

## 🚨 문제 해결

### 일반적인 오류

1. **Azure 서비스 연결 실패**
   - 환경변수가 올바르게 설정되었는지 확인
   - Azure 리소스의 접근 권한 확인

2. **문서 업로드 실패**
   - 파일 크기 및 형식 확인
   - Blob Storage 컨테이너 존재 여부 확인

3. **검색 결과가 없음**
   - AI Search 인덱스에 문서가 있는지 확인
   - 검색 쿼리의 적절성 검토

### 로그 확인

애플리케이션 로그는 Python의 `logging` 모듈을 통해 출력됩니다:

```python
logging.basicConfig(level=logging.INFO)
```

## 🔐 보안 고려사항

- 모든 API 키는 환경변수로 관리
- Azure 리소스에 대한 적절한 접근 제어 설정
- HTTPS를 통한 안전한 데이터 전송
- 민감한 정보는 Azure Key Vault 사용 권장

## 📈 성능 최적화

- 임베딩 캐싱을 통한 응답 시간 개선
- 청크 크기 최적화를 통한 검색 정확도 향상
- Azure AI Search의 인덱싱 전략 최적화

## 🤝 기여 방법

1. 이 저장소를 포크합니다
2. 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 등록해 주세요.

---

🎉 **KT 빌링 과제 분석 챗봇**으로 더 효율적인 프로젝트 분석을 경험해보세요!
