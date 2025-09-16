import streamlit as st
import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import urllib.parse
import base64
import re

# Azure SDK imports
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
import tiktoken
from dotenv import load_dotenv

# 환경 변수 로드 (개발환경에서만, Azure에서는 App Settings 사용)
# if os.path.exists('.env'):

load_dotenv()

class Config:
    # Azure OpenAI 설정
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
    AZURE_OPENAI_API_VERSION = "2024-02-01"
    CHAT_MODEL = "gpt-4o-mini-dprua"
    EMBEDDING_MODEL = "text-embedding-3-small"
    
    # Azure AI Search 설정
    SEARCH_SERVICE_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
    SEARCH_API_KEY = os.getenv("AZURE_SEARCH_KEY")
    SEARCH_INDEX_NAME = "rag-1757924013216"
    
    # Azure Blob Storage 설정
    BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
    BLOB_CONTAINER_NAME = "project-documents"
    
    # 환경변수 검증
    @classmethod
    def validate_config(cls):
        required_vars = [
            'AZURE_OPENAI_ENDPOINT',
            'AZURE_OPENAI_KEY', 
            'SEARCH_SERVICE_ENDPOINT',
            'SEARCH_API_KEY',
            'BLOB_CONNECTION_STRING'
        ]
        
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            st.error(f"다음 환경변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
            st.stop()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureServices:
    """Azure 서비스 연동 클래스"""
    
    def __init__(self):
        self.openai_client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )
        
        self.blob_service_client = BlobServiceClient.from_connection_string(
            Config.BLOB_CONNECTION_STRING
        )
        
        self.search_client = SearchClient(
            endpoint=Config.SEARCH_SERVICE_ENDPOINT,
            index_name=Config.SEARCH_INDEX_NAME,
            credential=AzureKeyCredential(Config.SEARCH_API_KEY)
        )
        
        self.search_index_client = SearchIndexClient(
            endpoint=Config.SEARCH_SERVICE_ENDPOINT,
            credential=AzureKeyCredential(Config.SEARCH_API_KEY)
        )

class DocumentProcessor:
    """문서 처리 및 인덱싱 클래스"""
    
    def __init__(self, azure_services: AzureServices):
        self.azure_services = azure_services
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")
    
    def upload_document(self, file_content: bytes, filename: str, metadata: Dict) -> bool:
        """문서를 Blob Storage에 업로드"""
        try:
            blob_client = self.azure_services.blob_service_client.get_blob_client(
                container=Config.BLOB_CONTAINER_NAME,
                blob=filename
            )
            
            # 메타데이터 추가
            metadata.update({
                "upload_date": datetime.now().isoformat(),
                "processed": "false"
            })
            
            blob_client.upload_blob(
                file_content,
                metadata=metadata,
                overwrite=True
            )
            
            logger.info(f"Document uploaded successfully: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}")
            return False
    
    def extract_text_from_document(self, file_content: bytes, file_type: str) -> str:
        """문서에서 텍스트 추출 (확장 가능)"""
        try:
            if file_type.lower() in ['txt']:
                return file_content.decode('utf-8')
            elif file_type.lower() in ['pdf']:
                # PDF 처리 로직 (PyPDF2, pdfplumber 등 사용)
                return "PDF 처리 기능 구현 필요"
            elif file_type.lower() in ['docx']:
                # Word 문서 처리 로직 (python-docx 사용)
                return "DOCX 처리 기능 구현 필요"
            # elif file_type.lower() in ['csv']:
            #     # Word 문서 처리 로직 (python-docx 사용)
                return "DOCX 처리 기능 구현 필요"
            else:
                return file_content.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return ""
    
    def chunk_text(self, text: str, max_tokens: int = 1000) -> List[str]:
        """텍스트를 청크로 분할"""
        sentences = text.split('.')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            test_chunk = current_chunk + sentence + "."
            if len(self.tokenizer.encode(test_chunk)) <= max_tokens:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + "."
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_embedding(self, text: str) -> List[float]:
        """텍스트 임베딩 생성"""
        try:
            if not isinstance(text, str) or not text.strip():
                logger.error("Embedding input must be a non-empty string")
                return []
            
            response = self.azure_services.openai_client.embeddings.create(
                model=Config.EMBEDDING_MODEL,
                input=text
            )
            
            embedding = response.data[0].embedding
            
            # 임베딩이 2차원 배열로 반환되는 경우 1차원으로 평탄화
            if isinstance(embedding, list) and isinstance(embedding[0], list):
                embedding = embedding[0]  # 첫 번째 배열을 선택
            
            return embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            return []
        
    def index_document(self, filename: str, content: str, metadata: Dict) -> bool:
        """문서를 AI Search에 인덱싱"""
        try:
            chunks = self.chunk_text(content)
            documents = []
            
            for i, chunk in enumerate(chunks):
                embedding = self.get_embedding(chunk)
                if not embedding or not isinstance(embedding, list) or not all(isinstance(val, (int, float)) for val in embedding):
                    logger.warning(f"Invalid embedding for chunk {i}, skipping this chunk.")
                    continue
                
                import uuid
                doc_id = str(uuid.uuid4())
                document = {
                    "chunk_id": doc_id,
                    "filename": filename,
                    "chunk": chunk,
                    "text_vector": embedding,
                    "project_type": metadata.get("project_type"),  # 이미 영어
                    "technology": metadata.get("technology"),
                    "department": metadata.get("department")      # 이미 영어
                    # "chunk_index": i
                }
                documents.append(document)
        
            # AI Search에 문서 업로드
            if documents:
                result = self.azure_services.search_client.upload_documents(documents)
                logger.info(f"Indexed {len(documents)} chunks for {filename}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error indexing document: {str(e)}")
            return False

class ProjectAnalyzer:
    """과제 분석 클래스"""
    
    def __init__(self, azure_services: AzureServices):
        self.azure_services = azure_services
    
    def search_similar_projects(self, query: str, top_k: int = 2) -> List[Dict]:
        """유사한 과제 검색"""
        try:
            # 쿼리 임베딩 생성
            query_embedding = self._get_query_embedding(query)
            if not query_embedding:
                return []
            
            # 벡터 검색 수행
            vector_query = VectorizedQuery(
                vector=query_embedding,
                k_nearest_neighbors=top_k,
                fields="text_vector"
            )
            
            results = self.azure_services.search_client.search(
                search_text=query,
                vector_queries=[vector_query],
                select=["filename", "chunk", "project_type", "technology", "department"],
                top=top_k
            )

            similar_projects = []
            for result in results:
                print(result.get("@search.score", 0))
                similar_projects.append({
                    "filename": result.get("filename", ""),
                    "chunk": result.get("chunk", ""),
                    "project_type": result.get("project_type", ""),
                    "technology": result.get("technology", ""),
                    "department": result.get("department", ""),
                    "score": result.get("@search.score", 0)
                    # "upload_date": result.get("upload_date", "")
                })
            
            return similar_projects
            
        except Exception as e:
            logger.error(f"Error searching similar projects: {str(e)}")
            return []
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """쿼리 임베딩 생성"""
        try:
            response = self.azure_services.openai_client.embeddings.create(
                model=Config.EMBEDDING_MODEL,
                input=query
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting query embedding: {str(e)}")
            return []
    
    def analyze_requirements(self, user_input: str, similar_projects: List[Dict]) -> str:
        """요구사항 분석 및 개발 기능 제안"""
        try:
            # 유사 과제 정보를 컨텍스트로 구성
            context = self._build_context(similar_projects)
            
            system_prompt = """
            당신은 KT 빌링 시스템 전문가입니다. 사용자의 개발 요구사항을 분석하여 다음을 제공해주세요:
            
            1. 개발이 필요한 주요 기능들
            2. 유사한 과거 프로젝트와의 비교 분석
            
            답변은 구체적이고 실용적으로 작성해주시고 모든 답변은 {context} 기반으로 작성하세요. {context}에 없는 내용은 작성하지 마시고 {context} 에 상품레퍼런스, 청구레퍼런스 내용 및 자바소스 관련 내용이 있다면 반드시 적어주세요.
            
            """
            
            user_prompt = f"""
            신규 개발 요구사항:
            {user_input}
            
            참고할 수 있는 과거 유사 프로젝트:
            {context}
            
            위 정보를 바탕으로 개발이 필요한 기능과 과거 프로젝트와의 비교를 포함하여 분석해주세요.
            conetext에 있는 내용만 참고하세요.
            """
            
            response = self.azure_services.openai_client.chat.completions.create(
                model=Config.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            print(1)
            print(response)
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error analyzing requirements: {str(e)}")
            return "요구사항 분석 중 오류가 발생했습니다."
    
    def _build_context(self, similar_projects: List[Dict]) -> str:
        """유사 프로젝트 컨텍스트 구성"""
        if not similar_projects:
            return "관련된 과거 프로젝트를 찾을 수 없습니다."
        
        context = "=== 과거 유사 프로젝트 정보 ===\n\n"
        for i, project in enumerate(similar_projects, 1):
            context += f"프로젝트 {i}:\n"
            context += f"- 파일명: {project['filename']}\n"
            context += f"- 프로젝트 유형: {project['project_type']}\n"
            context += f"- 기술스택: {project['technology']}\n"
            context += f"- 담당부서: {project['department']}\n"
            context += f"- 유사도: {project['score']:.2f}\n"
            context += f"- 내용: {project['chunk'][:500]}...\n"
            context += "\n" + "="*50 + "\n\n"
        
        return context

class StreamlitApp:
    """Streamlit 앱 클래스"""
    
    def __init__(self):
        # 환경변수 검증
        Config.validate_config()
        
        self.azure_services = AzureServices()
        self.document_processor = DocumentProcessor(self.azure_services)
        self.project_analyzer = ProjectAnalyzer(self.azure_services)
    
    def run(self):
        st.set_page_config(
            page_title="KT 빌링 과제 분석 챗봇",
            page_icon="📋",
            layout="wide"
        )
        
        st.title("📋 KT 빌링 과제 분석 챗봇")
        st.markdown("---")
        
        # 서비스 상태 체크 (사이드바 렌더링 전)
        if not self._check_azure_services():
            st.error("⚠️ Azure 서비스 연결에 문제가 있습니다. 환경 변수를 확인해주세요.")
            return
        
        # 사이드바
        self._render_sidebar()
        
        # 메인 컨텐츠 
        tab1, tab2 = st.tabs(["과제 분석", "문서 업로드"])
        
        with tab1:
            self._render_analysis_tab()
        
        with tab2:
            self._render_upload_tab()
    
    def _render_sidebar(self):
        st.sidebar.header("설정")
        
        # Azure 서비스 상태 확인
        st.sidebar.subheader("서비스 상태")
        if self._check_azure_services():
            st.sidebar.success("✅ Azure 서비스 연결됨")
        else:
            st.sidebar.error("❌ Azure 서비스 연결 실패")
        
        # 통계 정보
        st.sidebar.subheader("문서 통계")
        total_docs = self._get_document_count()
        st.sidebar.metric("저장된 문서 수", total_docs)
    
    def _render_analysis_tab(self):
        st.header("과제 분석")
        
        # 사용자 입력
        with st.form("analysis_form"):
            project_title = st.text_input("프로젝트 제목", placeholder="예: 모바일 빌링 시스템 개선")
            
            requirements = st.text_area(
                "개발 요구사항",
                height=200,
                placeholder="상세한 개발 요구사항을 입력해주세요..."
            )
            
            submitted = st.form_submit_button("분석 시작", type="primary")
        
        if submitted and requirements:
            with st.spinner("과제를 분석하고 있습니다..."):
                # 유사 프로젝트 검색
                search_query = f"{project_title} {requirements}"
                similar_projects = self.project_analyzer.search_similar_projects(search_query)
                
                # 요구사항 분석
                analysis_result = self.project_analyzer.analyze_requirements(
                    requirements, similar_projects
                )
                
                # 결과 표시
                st.success("분석이 완료되었습니다!")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("📋 분석 결과")
                    st.markdown(analysis_result)
                
                with col2:
                    st.subheader("📚 유사 과제")
                    if similar_projects:
                        # 영문 코드를 한국어로 변환
                        project_type_map = {
                            "billing_system": "빌링 시스템",
                            "customer_management": "고객관리", 
                            "settlement_system": "정산 시스템",
                            "mobile_app": "모바일 앱",
                            "web_service": "웹 서비스",
                            "data_analysis": "데이터 분석",
                            "infrastructure": "인프라",
                            "security": "보안",
                            "others": "기타"
                        }
                        
                        department_map = {
                            "development_team": "개발팀",
                            "planning_team": "기획팀",
                            "operations_team": "운영팀",
                            "quality_assurance_team": "품질팀",
                            "data_team": "데이터팀",
                            "infrastructure_team": "인프라팀", 
                            "security_team": "보안팀",
                            "others": "기타"
                        }
                        
                        for i, project in enumerate(similar_projects[:2], 1):
                            with st.expander(f"유사 과제 {i} (유사도: {project['score']:.2f})"):
                                st.write(f"**파일명:** {project['filename']}")
                                
                                project_type_kr = project_type_map.get(project['project_type'], project['project_type'])
                                department_kr = department_map.get(project['department'], project['department'])
                                
                                st.write(f"**프로젝트 유형:** {project_type_kr}")
                                st.write(f"**기술스택:** {project['technology']}")
                                st.write(f"**담당부서:** {department_kr}")
                                st.write(f"**내용:** {project['chunk'][:500]}...")
                    else:
                        st.info("유사한 과거 과제를 찾을 수 없습니다.")
    
    def _render_upload_tab(self):
        st.header("문서 업로드")
        
        with st.form("upload_form"):
            uploaded_file = st.file_uploader(
                "과제 문서 선택",
                type=['txt', 'pdf', 'docx', 'csv'],
                help="TXT, PDF, DOCX, CSV 파일을 업로드할 수 있습니다."
            )
            
            col1, col2 = st.columns(2)
            with col1:
                project_type = st.selectbox(
                    "프로젝트 유형",
                    ["Billing", "Order", "SETL"]
                )
                technology = st.text_input("기술스택", placeholder="예: Java, Spring, Oracle")
            
            with col2:
                department = st.selectbox(
                    "담당부서",
                    ["DEV", "OPS", "QA"]
                )
            upload_submitted = st.form_submit_button("업로드", type="primary")
        
        if upload_submitted and uploaded_file:
            with st.spinner("문서를 업로드하고 인덱싱하고 있습니다..."):
                # 메타데이터 구성
                metadata = {
                    "project_type": project_type,
                    "technology": technology,
                    "department": department
                }
                
                # 파일 업로드
                file_content = uploaded_file.read()
                filename = uploaded_file.name
                
                # Blob Storage에 업로드
                upload_success = self.document_processor.upload_document(
                    file_content, filename, metadata
                )
                
                if upload_success:
                    # 텍스트 추출 및 인덱싱
                    file_type = filename.split('.')[-1]
                    content = self.document_processor.extract_text_from_document(
                        file_content, file_type
                    )
                    print(content)
                    if content:
                        index_success = self.document_processor.index_document(
                            filename, content, metadata
                        )
                        
                        if index_success:
                            st.success(f"✅ '{filename}' 업로드 및 인덱싱이 완료되었습니다!")
                        else:
                            st.warning("⚠️ 업로드는 완료되었지만 인덱싱에 실패했습니다.")
                            # st.success(f"✅ '{filename}' 업로드 및 인덱싱이 완료되었습니다!")
                    else:
                        st.error("❌ 문서에서 텍스트를 추출할 수 없습니다.")
                else:
                    st.error("❌ 파일 업로드에 실패했습니다.")
    
    def _check_azure_services(self) -> bool:
        """Azure 서비스 연결 상태 확인"""
        try:
            # 간단한 연결 테스트
            self.azure_services.blob_service_client.get_account_information()
            return True
        except:
            return False
    
    def _get_document_count(self) -> int:
        """저장된 문서 수 조회"""
        try:
            container_client = self.azure_services.blob_service_client.get_container_client(
                Config.BLOB_CONTAINER_NAME
            )
            return len(list(container_client.list_blobs()))
        except:
            return 0

def main():
    try:
        app = StreamlitApp()
        app.run()
    except Exception as e:
        st.error(f"애플리케이션 실행 중 오류가 발생했습니다: {str(e)}")
        logger.error(f"Application error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()