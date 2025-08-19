# Wall2CAD MVP

SAM(Segment Anything Model)을 활용한 AI 기반 이미지 분할 및 DXF 변환 도구입니다.

## 개요

Wall2CAD MVP는 고급 AI 분할 기술을 사용하여 건축용 벽면 이미지를 CAD 호환 DXF 파일로 변환하는 데스크톱 애플리케이션입니다. 이미지 로드, SAM 모델을 통한 처리, CAD 소프트웨어에서 사용할 수 있는 DXF 파일로 내보내기를 위한 사용자 친화적인 인터페이스를 제공합니다.

## 주요 기능

- **AI 기반 자동 분할**: SAM(Segment Anything Model)을 활용한 자동 객체 감지
- **DXF 내보내기**: 분할된 마스크를 산업 표준 DXF 형식으로 변환
- **사용자 친화적 인터페이스**: 실시간 진행상황 표시가 포함된 PyQt5 기반 GUI
- **멀티스레드 처리**: UI 응답성 유지를 위한 백그라운드 처리
- **레이어 자동 구성**: 세그먼트 속성에 따라 DXF 출력을 레이어별로 자동 구성

## 시스템 요구사항

- Python 3.7 이상
- CUDA 지원 GPU (권장) 또는 CPU
- 최소 8GB RAM
- 모델 파일용 4GB 이상의 여유 디스크 공간

## 설치 방법

1. **프로젝트 다운로드**
```bash
cd wall2cad_mvp
```

2. **의존성 설치**
```bash
pip install -r requirements.txt
```

3. **SAM 모델 다운로드**
   
   **중요**: SAM 모델 파일 `sam_vit_h_4b8939.pth`는 파일 크기가 큰 관계로(2.5GB) 이 저장소에 포함되지 않습니다.
   
   허깅페이스에서 다운로드해주세요:
   ```bash
   # 방법 1: 직접 다운로드
   wget https://huggingface.co/facebook/sam-vit-huge/resolve/main/sam_vit_h_4b8939.pth
   
   # 방법 2: Hugging Face Hub 사용
   pip install huggingface_hub
   python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='facebook/sam-vit-huge', filename='sam_vit_h_4b8939.pth', local_dir='.')"
   ```
   
   다운로드한 `sam_vit_h_4b8939.pth` 파일을 `wall2cad_mvp` 디렉토리에 위치시켜 주세요.

4. **Segment Anything 설치**
```bash
pip install git+https://github.com/facebookresearch/segment-anything.git
```

## 사용 방법

1. **애플리케이션 실행**
```bash
python main.py
```

2. **이미지 로드**
   - "Load Image" 버튼 클릭 또는 Ctrl+O 단축키 사용
   - JPG, PNG, BMP 이미지 파일 선택
   - AI 처리 완료 대기 (수 분 소요될 수 있음)

3. **결과 확인**
   - 원본 이미지 위에 빨간색 윤곽선으로 분할된 마스크가 표시됨
   - 상태 표시줄에서 처리 정보 확인

4. **DXF로 내보내기**
   - "Export DXF" 버튼 클릭
   - 저장 위치와 파일명 선택
   - DXF 파일에는 감지된 세그먼트를 나타내는 폴리라인이 포함됨

## 파일 구조

```
wall2cad_mvp/
├── main.py              # 애플리케이션 진입점
├── ui_main.py           # 메인 윈도우 및 UI 컴포넌트
├── sam_processor.py     # SAM 모델 래퍼 및 처리
├── dxf_converter.py     # DXF 내보내기 기능
├── requirements.txt     # Python 의존성
├── sam_vit_h_4b8939.pth # SAM 모델 가중치 (다운로드 필요)
└── README.md           # 이 파일
```

## 컴포넌트 상세

### SAM 프로세서 (`sam_processor.py`)
- SAM 모델 로딩 및 초기화 처리
- 최적화된 매개변수로 자동 마스크 생성 제공
- 사용 가능한 경우 GPU 가속 지원

### DXF 변환기 (`dxf_converter.py`)
- SAM 마스크를 DXF 폴리라인으로 변환
- 세그먼트 크기 및 품질에 따라 레이어별로 출력 구성
- 좌표계 변환 처리 (이미지 → CAD)

### UI 메인 (`ui_main.py`)
- PyQt5 기반 그래픽 인터페이스
- UI 정지 방지를 위한 멀티스레드 처리
- 실시간 진행상황 피드백 및 오류 처리

## 지원 이미지 형식

- JPEG (.jpg, .jpeg)
- PNG (.png)
- Bitmap (.bmp)

## 성능 정보

- **첫 실행**: 초기 모델 로딩에 1-2분 소요
- **처리 시간**: 이미지 크기와 복잡도에 따라 변동 (일반적으로 2-5분)
- **GPU 가속**: CUDA 지원 GPU 사용시 현저히 빨라짐
- **메모리 사용량**: 처리 중 4-8GB RAM 필요

## 문제 해결

### 모델 로딩 문제
- `sam_vit_h_4b8939.pth` 파일이 올바른 디렉토리에 있는지 확인
- 충분한 디스크 공간과 RAM이 있는지 확인
- GPU 사용시 CUDA 설치 상태 확인

### 처리 오류
- 더 작은 이미지 크기 시도 (권장: 2000x2000 픽셀 이하)
- 이미지 파일이 손상되지 않았는지 확인
- 사용 가능한 시스템 메모리 확인

### DXF 내보내기 문제
- 대상 디렉토리의 쓰기 권한 확인
- 충분한 디스크 공간 확인
- 다른 내보내기 위치로 시도

## 의존성

- PyQt5: GUI 프레임워크
- torch: 딥러닝용 PyTorch
- torchvision: 컴퓨터 비전 유틸리티
- opencv-python: 이미지 처리
- matplotlib: 시각화
- numpy: 수치 연산
- ezdxf: DXF 파일 생성

## 라이센스

이 프로젝트는 교육 및 연구 목적으로 사용됩니다.

## 지원

문제가 발생하거나 질문이 있는 경우 다음을 확인하세요:
1. 모든 의존성이 올바르게 설치되었는지 확인
2. SAM 모델 파일이 제대로 다운로드되었는지 확인
3. 시스템 요구사항이 충족되는지 확인

---

**참고**: 이것은 핵심 기능에 중점을 둔 MVP(Minimum Viable Product) 버전입니다. 향후 버전에서는 추가 기능과 최적화가 포함될 수 있습니다.