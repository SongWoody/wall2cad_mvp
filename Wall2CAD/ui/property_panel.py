"""
Wall2CAD - 속성 패널
SAM 매개변수 조정 및 설정 UI
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QLabel, 
                            QSlider, QSpinBox, QDoubleSpinBox, QComboBox,
                            QCheckBox, QPushButton, QHBoxLayout, QFormLayout)
from PyQt6.QtCore import Qt, pyqtSignal

class PropertyPanel(QWidget):
    """속성 패널 - SAM 매개변수 및 설정"""
    
    # 시그널 정의
    sam_params_changed = pyqtSignal(dict)
    export_settings_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        
        # SAM 매개변수 그룹
        self.create_sam_params_group(layout)
        
        # 벡터 후처리 그룹
        self.create_vector_processing_group(layout)
        
        # 내보내기 설정 그룹
        self.create_export_settings_group(layout)
        
        # 레이어 관리 그룹
        self.create_layer_management_group(layout)
        
        # 버튼 그룹
        self.create_button_group(layout)
        
        # 스트레치 추가
        layout.addStretch()
        
    def create_sam_params_group(self, parent_layout):
        """SAM 매개변수 그룹 생성"""
        group = QGroupBox("SAM 매개변수")
        layout = QFormLayout(group)
        
        # 모델 선택
        self.model_combo = QComboBox()
        self.model_combo.addItems(['vit_b', 'vit_l', 'vit_h'])
        self.model_combo.setCurrentText('vit_h')
        layout.addRow("모델:", self.model_combo)
        
        # Points per side
        self.points_per_side_spin = QSpinBox()
        self.points_per_side_spin.setRange(8, 128)
        self.points_per_side_spin.setValue(32)
        layout.addRow("그리드 밀도:", self.points_per_side_spin)
        
        # Prediction IoU threshold
        self.iou_thresh_spin = QDoubleSpinBox()
        self.iou_thresh_spin.setRange(0.1, 1.0)
        self.iou_thresh_spin.setSingleStep(0.05)
        self.iou_thresh_spin.setValue(0.88)
        layout.addRow("IoU 임계값:", self.iou_thresh_spin)
        
        # Stability score threshold
        self.stability_thresh_spin = QDoubleSpinBox()
        self.stability_thresh_spin.setRange(0.1, 1.0)
        self.stability_thresh_spin.setSingleStep(0.05)
        self.stability_thresh_spin.setValue(0.95)
        layout.addRow("안정성 임계값:", self.stability_thresh_spin)
        
        # Minimum mask region area
        self.min_area_spin = QSpinBox()
        self.min_area_spin.setRange(10, 10000)
        self.min_area_spin.setValue(100)
        layout.addRow("최소 영역 크기:", self.min_area_spin)
        
        parent_layout.addWidget(group)
        
    def create_vector_processing_group(self, parent_layout):
        """벡터 후처리 그룹 생성"""
        group = QGroupBox("벡터 후처리")
        layout = QFormLayout(group)
        
        # 스무딩 활성화
        self.smoothing_check = QCheckBox("스무딩 적용")
        self.smoothing_check.setChecked(True)
        layout.addRow(self.smoothing_check)
        
        # 스무딩 강도
        self.smoothing_strength = QDoubleSpinBox()
        self.smoothing_strength.setRange(0.1, 10.0)
        self.smoothing_strength.setSingleStep(0.1)
        self.smoothing_strength.setValue(1.0)
        layout.addRow("스무딩 강도:", self.smoothing_strength)
        
        # 노이즈 제거
        self.noise_removal_check = QCheckBox("노이즈 제거")
        self.noise_removal_check.setChecked(True)
        layout.addRow(self.noise_removal_check)
        
        # 구멍 채우기
        self.fill_holes_check = QCheckBox("구멍 채우기")
        self.fill_holes_check.setChecked(False)
        layout.addRow(self.fill_holes_check)
        
        parent_layout.addWidget(group)
        
    def create_export_settings_group(self, parent_layout):
        """내보내기 설정 그룹 생성"""
        group = QGroupBox("DXF 내보내기 설정")
        layout = QFormLayout(group)
        
        # DXF 버전
        self.dxf_version_combo = QComboBox()
        self.dxf_version_combo.addItems(['R12', 'R2000', 'R2010', 'R2018'])
        self.dxf_version_combo.setCurrentText('R2018')
        layout.addRow("DXF 버전:", self.dxf_version_combo)
        
        # 단위 설정
        self.units_combo = QComboBox()
        self.units_combo.addItems(['mm', 'cm', 'm', 'inch'])
        self.units_combo.setCurrentText('mm')
        layout.addRow("단위:", self.units_combo)
        
        # 스케일 팩터
        self.scale_factor_spin = QDoubleSpinBox()
        self.scale_factor_spin.setRange(0.001, 1000.0)
        self.scale_factor_spin.setSingleStep(0.1)
        self.scale_factor_spin.setValue(1.0)
        layout.addRow("스케일 팩터:", self.scale_factor_spin)
        
        parent_layout.addWidget(group)
        
    def create_layer_management_group(self, parent_layout):
        """레이어 관리 그룹 생성"""
        group = QGroupBox("레이어 관리")
        layout = QVBoxLayout(group)
        
        # 임시 라벨
        label = QLabel("레이어 목록이 여기에 표시됩니다")
        label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(label)
        
        parent_layout.addWidget(group)
        
    def create_button_group(self, parent_layout):
        """버튼 그룹 생성"""
        layout = QVBoxLayout()
        
        # SAM 처리 버튼
        self.process_button = QPushButton("세그멘테이션 실행")
        self.process_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        layout.addWidget(self.process_button)
        
        # DXF 내보내기 버튼
        self.export_button = QPushButton("DXF 내보내기")
        self.export_button.setEnabled(False)
        layout.addWidget(self.export_button)
        
        parent_layout.addLayout(layout)
        
    def setup_connections(self):
        """시그널-슬롯 연결"""
        # SAM 매개변수 변경 시
        self.model_combo.currentTextChanged.connect(self.emit_sam_params)
        self.points_per_side_spin.valueChanged.connect(self.emit_sam_params)
        self.iou_thresh_spin.valueChanged.connect(self.emit_sam_params)
        self.stability_thresh_spin.valueChanged.connect(self.emit_sam_params)
        self.min_area_spin.valueChanged.connect(self.emit_sam_params)
        
        # 내보내기 설정 변경 시
        self.dxf_version_combo.currentTextChanged.connect(self.emit_export_settings)
        self.units_combo.currentTextChanged.connect(self.emit_export_settings)
        self.scale_factor_spin.valueChanged.connect(self.emit_export_settings)
        
    def emit_sam_params(self):
        """SAM 매개변수 시그널 발신"""
        params = {
            'model': self.model_combo.currentText(),
            'points_per_side': self.points_per_side_spin.value(),
            'pred_iou_thresh': self.iou_thresh_spin.value(),
            'stability_score_thresh': self.stability_thresh_spin.value(),
            'min_mask_region_area': self.min_area_spin.value()
        }
        self.sam_params_changed.emit(params)
        
    def emit_export_settings(self):
        """내보내기 설정 시그널 발신"""
        settings = {
            'dxf_version': self.dxf_version_combo.currentText(),
            'units': self.units_combo.currentText(),
            'scale_factor': self.scale_factor_spin.value()
        }
        self.export_settings_changed.emit(settings)
        
    def get_sam_params(self):
        """현재 SAM 매개변수 반환"""
        return {
            'model': self.model_combo.currentText(),
            'points_per_side': self.points_per_side_spin.value(),
            'pred_iou_thresh': self.iou_thresh_spin.value(),
            'stability_score_thresh': self.stability_thresh_spin.value(),
            'min_mask_region_area': self.min_area_spin.value(),
            'smoothing': self.smoothing_check.isChecked(),
            'smoothing_strength': self.smoothing_strength.value(),
            'noise_removal': self.noise_removal_check.isChecked(),
            'fill_holes': self.fill_holes_check.isChecked()
        }
        
    def get_export_settings(self):
        """현재 내보내기 설정 반환"""
        return {
            'dxf_version': self.dxf_version_combo.currentText(),
            'units': self.units_combo.currentText(),
            'scale_factor': self.scale_factor_spin.value()
        }