# Wall2CAD - 이미지 세그멘테이션 기반 벡터 변환 도구

SAM(Segment Anything Model) 기술을 활용하여 이미지에서 자동으로 객체를 세그멘테이션하고, CAD에서 사용 가능한 DXF 벡터 파일로 변환하는 데스크톱 애플리케이션입니다.

## 주요 기능

### ✅ 구현 완료
- **자동 모델 스캔**: 프로젝트 디렉토리의 SAM 모델 파일 자동 탐지
- **동적 모델 선택**: 드롭다운에서 사용 가능한 모델 선택 및 경로 표시
- **수동 모델 추가**: 다른 경로의 SAM 모델 파일 수동 추가 기능
- **Symlink 지원**: 심볼릭 링크된 모델 파일 자동 인식
- **이미지 로딩**: 다양한 이미지 포맷 지원 (JPG, PNG, BMP, TIFF)
- **PyQt6 기반 UI**: 메인 윈도우, 뷰포트, 속성 패널, 툴바 구현
- **설정 관리**: 사용자 설정 저장/로드 시스템

### 🚧 개발 진행 중
- **자동 세그멘테이션**: Meta SAM 모델을 활용한 정밀한 객체 분할
- **실시간 미리보기**: 세그멘테이션 결과 즉시 확인
- **벡터 변환**: 마스크를 CAD 호환 벡터로 자동 변환
- **DXF 내보내기**: 다양한 DXF 버전 지원 (R12~R2018)

### 📋 계획 중
- **배치 처리**: 여러 이미지 일괄 처리 지원
- **벡터 편집**: 실시간 벡터 수정 및 편집
- **레이어 관리**: 자동 레이어 분류 및 관리

## 시스템 요구사항

### 최소 요구사항
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8 이상
- **RAM**: 8GB 이상 권장
- **저장공간**: 5GB 이상 (SAM 모델 포함)

### 권장 요구사항
- **GPU**: CUDA 지원 GPU (처리 속도 향상)
- **RAM**: 16GB 이상
- **CPU**: 멀티코어 프로세서

## 설치 방법

### 1. 저장소 복제
```bash
git clone https://github.com/your-repo/Wall2CAD.git
cd Wall2CAD
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. SAM 모델 다운로드
```bash
# Hugging Face Hub을 통한 자동 다운로드
pip install huggingface_hub
python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='facebook/sam-vit-huge', filename='sam_vit_h_4b8939.pth', local_dir='.')"
```

> **참고**: 모델 파일은 프로젝트 루트 디렉토리에 배치하면 애플리케이션이 자동으로 탐지합니다. 
> 다른 경로에 있는 모델도 UI의 "추가..." 버튼으로 수동 추가 가능합니다.

### 4. Segment Anything 모듈 설치
```bash
pip install git+https://github.com/facebookresearch/segment-anything.git
```

## 사용 방법

### 애플리케이션 실행
```bash
python main.py
```

### 기본 워크플로우
1. **이미지 로드**: `파일 > 이미지 열기` 또는 툴바의 열기 버튼
2. **모델 선택**: 속성 패널에서 사용할 SAM 모델 선택 (자동 스캔된 목록에서)
3. **매개변수 설정**: 우측 속성 패널에서 SAM 매개변수 조정
4. **세그멘테이션 실행**: `세그멘테이션 실행` 버튼 클릭 *(구현 예정)*
5. **결과 확인**: 뷰포트에서 마스크 오버레이 확인 *(구현 예정)*
6. **벡터 편집**: 필요시 개별 벡터 수정 *(구현 예정)*
7. **DXF 내보내기**: `DXF 내보내기` 버튼으로 저장 *(구현 예정)*

## 프로젝트 구조

```
Wall2CAD/
├── main.py                 # 애플리케이션 진입점
├── ui/                     # 사용자 인터페이스
│   ├── main_window.py      # 메인 윈도우
│   ├── viewport.py         # CAD 스타일 뷰포트
│   ├── property_panel.py   # 속성 패널
│   └── toolbar.py          # 도구모음
├── core/                   # 핵심 로직
│   ├── sam_processor.py    # SAM 모델 처리
│   ├── image_loader.py     # 이미지 로딩
│   ├── mask_processor.py   # 마스크 후처리
│   └── dxf_exporter.py     # DXF 변환
├── utils/                  # 유틸리티
│   ├── config.py           # 설정 관리
│   ├── model_scanner.py    # SAM 모델 스캐너 (신규)
│   └── logger.py           # 로깅
└── resources/              # 리소스 파일
    ├── models/             # SAM 모델 파일
    └── icons/              # UI 아이콘
```

## 설정 옵션

### SAM 매개변수
- **Model Type**: vit_b, vit_l, vit_h (정확도 순)
- **Points per Side**: 그리드 밀도 (8-128)
- **IoU Threshold**: 품질 임계값 (0.1-1.0)
- **Stability Score**: 안정성 임계값 (0.1-1.0)
- **Min Area**: 최소 영역 크기 (픽셀)

### 벡터 후처리
- **Smoothing**: Douglas-Peucker 알고리즘 적용
- **Noise Removal**: 작은 영역 제거
- **Fill Holes**: 구멍 채우기

### DXF 내보내기
- **Version**: R12, R2000, R2010, R2018
- **Units**: mm, cm, m, inch
- **Scale Factor**: 좌표 스케일 조정
- **Layer Management**: 크기별 자동 레이어 분류

## 성능 최적화

### GPU 가속 활성화
```python
# 설정에서 CUDA 사용 여부 확인
import torch
print(f"CUDA Available: {torch.cuda.is_available()}")
```

### 메모리 사용량 최적화
- 대용량 이미지는 자동으로 크기 조정
- 처리 후 불필요한 데이터 자동 정리
- 배치 처리 시 청크 단위로 처리

## 문제 해결

### 일반적인 문제

**Q: SAM 모델 로딩이 실패합니다**
A: 
- 프로젝트 루트에 `.pth` 파일이 있는지 확인하세요
- UI의 "새로고침" 버튼을 클릭하여 모델 목록을 업데이트하세요
- "추가..." 버튼으로 다른 경로의 모델을 수동 추가할 수 있습니다

**Q: 메모리 부족 오류가 발생합니다**
A: 이미지 크기를 줄이거나 더 작은 SAM 모델(vit_b)을 사용해보세요.

**Q: GPU 가속이 작동하지 않습니다**
A: CUDA 호환 PyTorch가 설치되어 있는지 확인하세요.

### 로그 확인
로그 파일은 다음 위치에 저장됩니다:
- Windows: `%USERPROFILE%\.wall2cad\logs\`
- macOS/Linux: `~/.wall2cad/logs/`

## 개발 정보

### 기술 스택
- **UI**: PyQt6
- **AI/ML**: PyTorch, Segment Anything
- **이미지 처리**: OpenCV, scikit-image
- **CAD**: ezdxf

### 기여하기
1. 포크 생성
2. 기능 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'Add AmazingFeature'`)
4. 브랜치 푸시 (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 연락처

- 프로젝트 페이지: [GitHub Repository](https://github.com/your-repo/Wall2CAD)
- 이슈 제보: [Issues](https://github.com/your-repo/Wall2CAD/issues)
- 이메일: your-email@example.com

## 개발 로드맵

### Phase 1: 기본 인프라 (완료) ✅
- [x] 프로젝트 구조 설정
- [x] PyQt6 UI 프레임워크 구축
- [x] 설정 관리 시스템
- [x] 이미지 로딩 기능
- [x] SAM 모델 스캐너 및 동적 선택

### Phase 2: 핵심 기능 구현 (진행중) 🚧
- [ ] SAM 모델 로딩 및 초기화
- [ ] 세그멘테이션 워커 스레드 구현
- [ ] 마스크 결과 시각화
- [ ] 벡터 변환 알고리즘
- [ ] DXF 내보내기 기능

### Phase 3: 고급 기능 (계획) 📋
- [ ] 실시간 벡터 편집
- [ ] 배치 처리 시스템
- [ ] 레이어 관리 UI
- [ ] 성능 최적화
- [ ] 사용자 환경 개선

### Phase 4: 배포 준비 (계획) 🎯
- [ ] 통합 테스트
- [ ] 문서화 완성
- [ ] 인스톨러 제작
- [ ] CI/CD 파이프라인

## 감사의 글

- [Meta AI - Segment Anything](https://github.com/facebookresearch/segment-anything)
- [ezdxf](https://github.com/mozman/ezdxf) - DXF 파일 처리
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI 프레임워크