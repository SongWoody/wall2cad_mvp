"""
Wall2CAD - 속성 패널
SAM 매개변수 조정 및 설정 UI
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QLabel, 
                            QSlider, QSpinBox, QDoubleSpinBox, QComboBox,
                            QCheckBox, QPushButton, QHBoxLayout, QFormLayout, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from core.sam_processor import SAMProcessor

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
        
        # 모델 선택 섹션
        model_layout = QHBoxLayout()
        
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(200)
        model_layout.addWidget(self.model_combo, 1)
        
        # 새로고침 버튼
        self.refresh_models_btn = QPushButton("새로고침")
        self.refresh_models_btn.setMaximumWidth(80)
        self.refresh_models_btn.clicked.connect(self.refresh_model_list)
        model_layout.addWidget(self.refresh_models_btn)
        
        # 수동 추가 버튼
        self.add_model_btn = QPushButton("추가...")
        self.add_model_btn.setMaximumWidth(60)
        self.add_model_btn.clicked.connect(self.add_custom_model)
        model_layout.addWidget(self.add_model_btn)
        
        layout.addRow("모델:", model_layout)
        
        # 선택된 모델 경로 표시 라벨
        self.model_path_label = QLabel("경로: 모델을 선택하세요")
        self.model_path_label.setWordWrap(True)
        self.model_path_label.setStyleSheet("color: #666; font-size: 9pt; padding: 4px;")
        layout.addRow("경로:", self.model_path_label)
        
        # 모델 목록 초기화
        self.refresh_model_list()
        
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
        self.process_button = QPushButton("모델 로딩 필요")
        self.process_button.setEnabled(False)
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
        self.model_combo.currentTextChanged.connect(self.update_model_path_label)
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
            'model_path': self.get_selected_model_path(),
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
            'model_path': self.get_selected_model_path(),
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
        
    def get_sam_parameters(self):
        """세그멘테이션용 SAM 매개변수 반환 (메인 윈도우 호환용)"""
        return {
            'points_per_side': self.points_per_side_spin.value(),
            'pred_iou_thresh': self.iou_thresh_spin.value(),
            'stability_score_thresh': self.stability_thresh_spin.value(),
            'min_mask_region_area': self.min_area_spin.value()
        }
        
    def get_export_settings(self):
        """현재 내보내기 설정 반환"""
        return {
            'dxf_version': self.dxf_version_combo.currentText(),
            'units': self.units_combo.currentText(),
            'scale_factor': self.scale_factor_spin.value()
        }
        
    def refresh_model_list(self):
        """모델 목록 새로고침"""
        try:
            # 기존 항목 제거
            self.model_combo.clear()
            
            # 사용 가능한 모델 스캔
            available_models = SAMProcessor.get_available_models()
            
            # 콤보박스에 항목 추가
            current_selection = None
            for model_type in ['vit_h', 'vit_l', 'vit_b']:  # 큰 모델부터
                models = available_models.get(model_type, [])
                for model_info in models:
                    # 경로를 짧게 표시 (파일명 + 상위 1-2 디렉토리만)
                    short_path = self._get_short_path(model_info['path'])
                    display_text = f"{model_info['name']}"
                    
                    self.model_combo.addItem(display_text, model_info['path'])
                    
                    # 툴팁으로 전체 경로 표시
                    self.model_combo.setItemData(
                        self.model_combo.count() - 1, 
                        f"전체 경로: {model_info['path']}", 
                        Qt.ItemDataRole.ToolTipRole
                    )
                    
                    # 첫 번째 vit_h 모델을 기본 선택으로 설정
                    if model_type == 'vit_h' and current_selection is None:
                        current_selection = self.model_combo.count() - 1
                        
            # 모델이 하나도 없는 경우
            if self.model_combo.count() == 0:
                self.model_combo.addItem("모델이 없습니다 - '추가...' 버튼을 사용하세요", "")
                self.model_combo.setEnabled(False)
                self.process_button.setEnabled(False)
                self.process_button.setText("모델 없음")
            else:
                self.model_combo.setEnabled(True)
                # 처리 버튼은 모델 로딩 후에 활성화
                self.process_button.setEnabled(False)
                self.process_button.setText("모델 로딩 필요")
                if current_selection is not None:
                    self.model_combo.setCurrentIndex(current_selection)
                    
            # 콤보박스 크기 조정을 위한 스타일 설정
            self.model_combo.setMaxVisibleItems(10)
            self.model_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
            
            # 경로 라벨 업데이트
            self.update_model_path_label()
            
            print(f"Found {self.model_combo.count()} SAM models")
            
        except Exception as e:
            print(f"Error refreshing model list: {e}")
            self.model_combo.clear()
            self.model_combo.addItem("오류: 모델 스캔 실패", "")
            self.model_combo.setEnabled(False)
            
    def add_custom_model(self):
        """커스텀 모델 추가"""
        try:
            # 파일 다이얼로그 열기
            file_dialog = QFileDialog(self)
            file_dialog.setWindowTitle("SAM 모델 파일 선택")
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
            file_dialog.setNameFilter("PyTorch 모델 파일 (*.pth);;모든 파일 (*)")
            
            if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
                file_paths = file_dialog.selectedFiles()
                if file_paths:
                    file_path = file_paths[0]
                    
                    # 모델 파일 검증
                    if SAMProcessor.validate_model_file(file_path):
                        # 모델 추가
                        if SAMProcessor.add_custom_model(file_path):
                            # 목록 새로고침
                            self.refresh_model_list()
                            
                            # 방금 추가한 모델로 선택
                            for i in range(self.model_combo.count()):
                                if self.model_combo.itemData(i) == file_path:
                                    self.model_combo.setCurrentIndex(i)
                                    break
                                    
                            print(f"Custom model added: {file_path}")
                        else:
                            self.show_error("모델 추가에 실패했습니다.")
                    else:
                        self.show_error("유효하지 않은 SAM 모델 파일입니다.")
                        
        except Exception as e:
            print(f"Error adding custom model: {e}")
            self.show_error(f"모델 추가 중 오류가 발생했습니다: {e}")
            
    def show_error(self, message: str):
        """오류 메시지 표시"""
        print(f"Error: {message}")
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "오류", message)
        
    def get_selected_model_path(self) -> str:
        """선택된 모델의 파일 경로 반환"""
        current_data = self.model_combo.currentData()
        return current_data if current_data else ""
        
    def _get_short_path(self, full_path: str) -> str:
        """경로를 짧게 표시하기 위한 헬퍼 함수"""
        import os
        try:
            # 경로를 분리
            path_parts = full_path.replace('\\', '/').split('/')
            filename = path_parts[-1]
            
            if len(path_parts) <= 2:
                return full_path
                
            # 파일명 + 상위 1-2 디렉토리만 표시
            if len(path_parts) >= 3:
                return f".../{path_parts[-2]}/{filename}"
            else:
                return f"{path_parts[-2]}/{filename}"
                
        except Exception:
            return os.path.basename(full_path)
            
    def update_model_path_label(self):
        """선택된 모델의 경로 라벨 업데이트"""
        try:
            selected_path = self.get_selected_model_path()
            if selected_path and selected_path != "":
                # 경로가 너무 길면 줄바꿈 처리
                if len(selected_path) > 50:
                    # 50자마다 줄바꿈
                    formatted_path = ""
                    for i in range(0, len(selected_path), 50):
                        if i > 0:
                            formatted_path += "\n"
                        formatted_path += selected_path[i:i+50]
                    self.model_path_label.setText(formatted_path)
                else:
                    self.model_path_label.setText(selected_path)
            else:
                self.model_path_label.setText("모델을 선택하세요")
        except Exception as e:
            print(f"Error updating model path label: {e}")
            self.model_path_label.setText("경로 표시 오류")