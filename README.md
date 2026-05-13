# 닷코(Datco) AI 챗봇 과제물 🤖 

## 이 프로젝트는 로컬 환경에서 Llama 모델을 활용한 PDF 문서 전문 챗봇입니다. 아래 순서에 따라 환경 설정을 진행해 주세요.

### 1. 파이썬 3.12.9(Feb.4,2025) 설치 

#### 1. 공식 홈페이지 : https://www.python.org/downloads/release/python-3129/ (Windows용 Installer 다운로드)

  ⚠️주의사항 : 설치 초기 화면 하단의 **Add Python.exe to PATH** 옵션을 반드시 체크하세요.

#### 2. 설치 확인: 명령 프롬프트(CMD)에서 아래 명령어 입력

```bash
py -3.12 --version
```

### 2. visual Studio Build Tools 설치  

#### 1. 공식 홈페이지 : https://visualstudio.microsoft.com/ko/downloads/ (하단에 Visual Studio 2026용 빌드 도구 다운로드)

#### 2. 워크로드 : C++를 사용한 데스크톱 개발 선택

#### 3. 개발 옵션 (필수) : 

##### \- MSVC v14x - VS 2022 C++ x64/x86 빌드 도구

##### \- Windows 10(또는 11) SDK

#### 4. 설치 완료 후 반드시 **다시 시작** 

### 3. OLLAMA 및 LLM 모델 설치

#### 1. 공식 홈페이지 : https://ollama.com/download (Download for Windows)

#### 2. LLM 모델 설치 (CMD)

##### \- 답변 생성 모델

```bash
ollama run hf.co/MLP-KTLim/llama-3-Korean-Bllossom-8B-gguf-Q4_K_M
```

##### \- 임베딩 모델

```bash
ollama pull mxbai-embed-large
```

   💡Tip : 설치 완료 후 자동으로 채팅창이 열리면 **/bye**를 통해 종료할 수 있음

### 4. 프로젝트 가상환경 설정 (CMD)

#### 1. 가상환경 생성 (프로젝트 폴더 위에서 생성)

```bash
py -3.12 -m venv venv
```

#### 2. 가상환경 활성화 

```bash
.\venv\Scripts\activate
```

#### 3. pip 최신 업데이트 (오류 방지용)

```bash
python -m pip install --upgrade pip
```

#### 4. 패키지 설치

```bash
pip install -r requirements.txt
```

### 5. 실행 방법 (CMD)

#### 1. 프로젝트 폴더 내에서 run.bat 파일 실행 (Ollama가 실행되고 있어야 함)

#### 2. 터미널에 출력되는 로컬 주소(예: http://127.0.0.1:xxxx) 를 브라우저에 입력하여 접속



