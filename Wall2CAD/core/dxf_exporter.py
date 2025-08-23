"""
Wall2CAD - DXF 내보내기
벡터 데이터를 DXF 파일로 변환
"""

import os
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import ezdxf
from ezdxf import units

class DXFExporter:
    """DXF 파일 내보내기 클래스"""
    
    def __init__(self):
        self.doc = None
        self.msp = None  # Model space
        
    def create_document(self, dxf_version: str = "R2018", units_type: str = "mm") -> bool:
        """
        DXF 문서 생성
        
        Args:
            dxf_version: DXF 버전 (R12, R2000, R2010, R2018)
            units_type: 단위 (mm, cm, m, inch)
            
        Returns:
            bool: 생성 성공 여부
        """
        try:
            # DXF 문서 생성
            self.doc = ezdxf.new(dxfversion=dxf_version)
            self.msp = self.doc.modelspace()
            
            # 단위 설정
            unit_map = {
                'mm': units.MM,
                'cm': units.CM,
                'm': units.M,
                'inch': units.INCH
            }
            
            if units_type in unit_map:
                self.doc.units = unit_map[units_type]
                
            print(f"DXF document created: {dxf_version}, units: {units_type}")
            return True
            
        except Exception as e:
            print(f"Error creating DXF document: {e}")
            return False
            
    def add_contours_as_polylines(self, contour_data: List[Dict[str, Any]], 
                                 scale_factor: float = 1.0,
                                 image_height: Optional[int] = None,
                                 layer_prefix: str = "WALL2CAD") -> int:
        """
        윤곽선을 폴리라인으로 DXF에 추가
        
        Args:
            contour_data: 윤곽선 데이터 리스트
            scale_factor: 스케일 팩터
            image_height: 이미지 높이 (Y축 반전용)
            layer_prefix: 레이어 이름 접두사
            
        Returns:
            int: 추가된 폴리라인 수
        """
        if self.doc is None:
            print("Error: DXF document not created")
            return 0
            
        polyline_count = 0
        
        for i, data in enumerate(contour_data):
            try:
                contour = data['contour']
                area = data.get('area', 0)
                
                # 레이어 결정 (크기 기준)
                layer_name = self._get_layer_name(area, layer_prefix)
                self._ensure_layer_exists(layer_name, area)
                
                # 윤곽선 포인트 변환
                points = self._convert_contour_points(
                    contour, scale_factor, image_height
                )
                
                if len(points) < 3:  # 최소 3개 점 필요
                    continue
                    
                # 폴리라인 생성
                polyline = self.msp.add_lwpolyline(
                    points, 
                    close=True,
                    dxfattribs={'layer': layer_name}
                )
                
                polyline_count += 1
                
            except Exception as e:
                print(f"Error adding contour {i} as polyline: {e}")
                continue
                
        print(f"Added {polyline_count} polylines to DXF")
        return polyline_count
        
    def _convert_contour_points(self, contour: np.ndarray, 
                              scale_factor: float,
                              image_height: Optional[int] = None) -> List[Tuple[float, float]]:
        """윤곽선 포인트를 DXF 좌표계로 변환"""
        points = []
        
        # 윤곽선이 3차원 배열인 경우 처리
        if len(contour.shape) == 3:
            contour = contour.squeeze()
            
        for point in contour:
            if len(point) >= 2:
                x = float(point[0]) * scale_factor
                y = float(point[1]) * scale_factor
                
                # Y축 반전 (이미지 좌표계 -> CAD 좌표계)
                if image_height is not None:
                    y = (image_height * scale_factor) - y
                    
                points.append((x, y))
                
        return points
        
    def _get_layer_name(self, area: float, prefix: str) -> str:
        """영역 크기에 따른 레이어 이름 결정"""
        if area < 1000:
            return f"{prefix}_SMALL"
        elif area < 10000:
            return f"{prefix}_MEDIUM"
        elif area < 100000:
            return f"{prefix}_LARGE"
        else:
            return f"{prefix}_XLARGE"
            
    def _ensure_layer_exists(self, layer_name: str, area: float):
        """레이어가 존재하지 않으면 생성"""
        if layer_name not in self.doc.layers:
            # 크기에 따른 색상 결정
            color = self._get_layer_color(area)
            
            self.doc.layers.add(
                layer_name,
                color=color,
                linetype="CONTINUOUS"
            )
            
    def _get_layer_color(self, area: float) -> int:
        """영역 크기에 따른 색상 결정"""
        if area < 1000:
            return 5  # Blue
        elif area < 10000:
            return 3  # Green
        elif area < 100000:
            return 2  # Yellow
        else:
            return 1  # Red
            
    def add_image_reference(self, image_path: str, 
                          scale_factor: float = 1.0,
                          position: Tuple[float, float] = (0, 0)) -> bool:
        """
        배경 이미지 참조 추가
        
        Args:
            image_path: 이미지 파일 경로
            scale_factor: 스케일 팩터
            position: 삽입 위치
            
        Returns:
            bool: 추가 성공 여부
        """
        try:
            if not os.path.exists(image_path):
                print(f"Image file not found: {image_path}")
                return False
                
            # 이미지 참조 레이어 생성
            img_layer = "WALL2CAD_IMAGE"
            if img_layer not in self.doc.layers:
                self.doc.layers.add(img_layer, color=8)  # Gray
                
            # 이미지 정의 추가
            image_def = self.doc.add_image_def(image_path)
            
            # 이미지 삽입
            self.msp.add_image(
                image_def=image_def,
                insert=position,
                size_in_units=(1 * scale_factor, 1 * scale_factor),
                dxfattribs={'layer': img_layer}
            )
            
            print(f"Added image reference: {os.path.basename(image_path)}")
            return True
            
        except Exception as e:
            print(f"Error adding image reference: {e}")
            return False
            
    def add_text_annotations(self, annotations: List[Dict[str, Any]]) -> int:
        """텍스트 주석 추가"""
        if self.doc is None:
            return 0
            
        # 주석 레이어 생성
        text_layer = "WALL2CAD_TEXT"
        if text_layer not in self.doc.layers:
            self.doc.layers.add(text_layer, color=7)  # White/Black
            
        count = 0
        for annotation in annotations:
            try:
                position = annotation.get('position', (0, 0))
                text = annotation.get('text', '')
                height = annotation.get('height', 2.5)
                
                self.msp.add_text(
                    text,
                    height=height,
                    dxfattribs={
                        'insert': position,
                        'layer': text_layer
                    }
                )
                count += 1
                
            except Exception as e:
                print(f"Error adding text annotation: {e}")
                continue
                
        return count
        
    def set_document_properties(self, title: str = "Wall2CAD Export",
                              author: str = "Wall2CAD",
                              subject: str = "Segmentation Vector Export") -> bool:
        """문서 속성 설정"""
        try:
            if self.doc is None:
                return False
                
            header = self.doc.header
            header['$DWGTITLE'] = title
            header['$DWGAUTHOR'] = author  
            header['$DWGSUBJECT'] = subject
            
            return True
            
        except Exception as e:
            print(f"Error setting document properties: {e}")
            return False
            
    def save(self, file_path: str) -> bool:
        """
        DXF 파일 저장
        
        Args:
            file_path: 저장할 파일 경로
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            if self.doc is None:
                print("Error: No DXF document to save")
                return False
                
            # 디렉토리 생성
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 파일 저장
            self.doc.saveas(file_path)
            
            print(f"DXF file saved: {file_path}")
            return True
            
        except Exception as e:
            print(f"Error saving DXF file: {e}")
            return False
            
    def get_export_stats(self) -> Dict[str, Any]:
        """내보내기 통계 반환"""
        if self.doc is None:
            return {}
            
        try:
            entities = list(self.msp)
            
            stats = {
                'total_entities': len(entities),
                'polylines': sum(1 for e in entities if e.dxftype() == 'LWPOLYLINE'),
                'images': sum(1 for e in entities if e.dxftype() == 'IMAGE'),
                'texts': sum(1 for e in entities if e.dxftype() == 'TEXT'),
                'layers': len(self.doc.layers),
                'dxf_version': self.doc.dxfversion,
                'units': getattr(self.doc, 'units', 'Unknown')
            }
            
            return stats
            
        except Exception as e:
            print(f"Error getting export stats: {e}")
            return {}
            
    def close(self):
        """리소스 정리"""
        self.doc = None
        self.msp = None