# Wall2CAD Prototype - R&D Analysis

## 프로젝트 개요

**Wall2CAD Prototype**은 Segment Anything Model(SAM)을 활용하여 건축 도면 이미지에서 벽면을 자동으로 인식하고 CAD 파일(DXF)로 변환하는 연구개발 프로젝트입니다.

- **프로젝트명**: wall2cad-prototype
- **버전**: 0.1.0  
- **개발자**: Woody (syg1138@gmail.com)
- **목적**: 건축 도면의 자동화된 벽면 인식 및 CAD 변환

## 기술 스택

### Core Technologies
- **Python**: 3.12+
- **PyTorch**: 2.5.1+cu121 (CUDA 지원)
- **Segment Anything Model (SAM)**: Meta의 이미지 세그멘테이션 모델
- **OpenCV**: 이미지 처리 및 윤곽선 추출
- **ezdxf**: DXF 파일 생성 및 조작

### Dependencies
- numpy (>=2.2.5)
- matplotlib (>=3.10.3) 
- opencv-python (>=4.11.0.86)
- ezdxf (>=1.4.1)
- jupyterlab (개발환경)

## 프로젝트 구조

```
Wall2CAD_Prototype/
├── notebooks/                    # Jupyter 노트북 작업공간
│   ├── automatic_mask_generator_example.ipynb    # 자동 마스크 생성 예제
│   ├── predictor_example.ipynb                   # SAM Predictor 사용 예제
│   ├── images/                                   # 테스트 이미지들
│   └── images_2/                                 # 처리된 이미지 및 DXF 파일들
├── segment_anything/             # SAM 모델 구현
│   ├── modeling/                 # 모델 아키텍처
│   └── utils/                    # 유틸리티 함수들
├── demo/                         # React 웹 데모
└── scripts/                      # 스크립트 도구들
```

## 주요 기능

### 1. 자동 마스크 생성 (Automatic Mask Generation)
- **파일**: `automatic_mask_generator_example.ipynb`
- **기능**: 
  - SAM 모델을 사용한 전체 이미지 자동 세그멘테이션
  - 건축 도면에서 벽면 영역 자동 감지
  - 여러 마스크 통합 및 후처리
  - DXF 파일로 자동 변환

### 2. 프롬프트 기반 예측 (Prompt-based Prediction)
- **파일**: `predictor_example.ipynb`
- **기능**:
  - 포인트/박스 프롬프트를 통한 정밀한 객체 선택
  - 다중 프롬프트 지원
  - 배치 처리 가능

### 3. DXF 변환 시스템
- **기술**: ezdxf 라이브러리 활용
- **과정**:
  1. 이미지 마스크에서 윤곽선 추출 (`cv2.findContours`)
  2. 좌표계 변환 (이미지 Y축 반전)
  3. DXF 폴리라인으로 변환
  4. CAD 호환 파일 생성

## 연구 성과

### 처리 가능한 이미지 유형
- 건축 평면도
- 벽면 구조도
- 단면도 (Section1_3, Section1_4, Section3_1, Section3_2, Section4_1-5)

### 성능 특징
- **GPU 가속**: NVIDIA GeForce GTX 1660 SUPER 활용
- **모델**: SAM ViT-H (가장 높은 정확도 모델 사용)
- **자동화**: 배치 처리로 다중 이미지 동시 변환 가능

### 출력 결과
- **형식**: DXF (AutoCAD 호환)
- **정밀도**: 픽셀 단위 정확성
- **구조**: 닫힌 폴리라인 (closed polyline)으로 벽면 표현

## 기술적 특징

### SAM 모델 활용
- **체크포인트**: sam_vit_h_4b8939.pth (ViT-Huge 모델)
- **설정**: 기본 파라미터로 최적화
- **처리 방식**: GPU 메모리 효율적 배치 처리

### 이미지 전처리
- BGR → RGB 색공간 변환
- 자동 리사이징 및 정규화
- 노이즈 감소 및 윤곽선 최적화

### 좌표계 변환
- 이미지 좌표 → CAD 좌표계 변환
- Y축 반전 처리 (이미지: 위→아래, CAD: 아래→위)
- 정밀한 벡터 변환

## 개발 환경

### 하드웨어 요구사항
- **GPU**: NVIDIA CUDA 지원 그래픽카드 (GTX 1660 SUPER 이상 권장)
- **메모리**: 8GB RAM 이상
- **저장공간**: 모델 파일 약 2.5GB

### 소프트웨어 환경
- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.12 이상
- **CUDA**: 12.1 이상
- **개발도구**: JupyterLab, VS Code

## 향후 발전 방향

### 1. 정확도 개선
- 건축 도면 특화 파인튜닝
- 벽면 인식 정확도 향상
- 노이즈 및 불필요 요소 필터링

### 2. 기능 확장
- 문/창문 자동 인식
- 치수 정보 추출
- 3D 모델 변환

### 3. 사용성 개선
- 웹 기반 인터페이스 완성
- 실시간 프리뷰 기능
- 배치 처리 UI

### 4. 최적화
- 처리 속도 향상
- 메모리 사용량 최적화
- 모바일/엣지 디바이스 지원

## 라이센스 및 참조

- **SAM Model**: Apache 2.0 License (Meta AI)
- **프로젝트**: 연구용 프로토타입
- **참조 논문**: "Segment Anything" (Kirillov et al., 2023)

## 기술 지원

이 프로젝트는 Meta AI의 Segment Anything Model을 기반으로 하며, 건축 및 엔지니어링 분야의 CAD 자동화를 목표로 개발되었습니다.