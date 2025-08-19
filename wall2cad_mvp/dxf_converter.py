"""
Wall2CAD MVP - DXF Converter
"""

import numpy as np
import cv2
import ezdxf
from ezdxf import units

class DXFConverter:
    """Convert SAM masks to DXF format"""
    
    def __init__(self):
        """Initialize DXF converter"""
        pass
        
    def export_masks_to_dxf(self, masks, image_shape, output_path):
        """
        Export masks to DXF file
        
        Args:
            masks: List of mask dictionaries from SAM
            image_shape: Shape of original image (height, width, channels)
            output_path: Output DXF file path
        """
        print(f"Converting {len(masks)} masks to DXF...")
        
        # Create new DXF document
        doc = ezdxf.new(dxfversion='R2010')
        doc.units = units.MM  # Set units to millimeters
        
        # Get model space
        msp = doc.modelspace()
        
        # Image dimensions
        height, width = image_shape[:2]
        
        # Process each mask
        contour_count = 0
        
        for i, mask_data in enumerate(masks):
            mask = mask_data['segmentation']
            
            # Convert mask to uint8 for contour detection
            mask_uint8 = (mask.astype(np.uint8)) * 255
            
            # Find contours
            contours, _ = cv2.findContours(
                mask_uint8, 
                cv2.RETR_EXTERNAL, 
                cv2.CHAIN_APPROX_TC89_L1  # Better approximation for CAD
            )
            
            for contour in contours:
                contour = contour.squeeze()
                
                # Skip invalid contours
                if len(contour.shape) != 2 or contour.shape[0] < 3:
                    continue
                    
                # Convert to DXF coordinates (flip Y axis)
                points = []
                for x, y in contour:
                    # Flip Y coordinate (DXF origin is bottom-left)
                    dxf_x = float(x)
                    dxf_y = float(height - y)
                    points.append((dxf_x, dxf_y))
                
                # Close the contour if not already closed
                if len(points) > 2 and points[0] != points[-1]:
                    points.append(points[0])
                
                # Add polyline to DXF
                try:
                    polyline = msp.add_lwpolyline(points, close=True)
                    
                    # Set layer based on mask properties
                    layer_name = self._get_layer_name(mask_data, i)
                    
                    # Create layer if it doesn't exist
                    if layer_name not in doc.layers:
                        doc.layers.add(layer_name)
                    
                    polyline.dxf.layer = layer_name
                    contour_count += 1
                    
                except Exception as e:
                    print(f"Warning: Failed to add contour {contour_count}: {str(e)}")
                    continue
        
        # Save DXF file
        doc.saveas(output_path)
        print(f"DXF saved: {output_path} ({contour_count} contours)")
        
        return contour_count
        
    def _get_layer_name(self, mask_data, index):
        """
        Generate layer name based on mask properties
        
        Args:
            mask_data: Mask dictionary from SAM
            index: Mask index
            
        Returns:
            Layer name string
        """
        area = mask_data.get('area', 0)
        predicted_iou = mask_data.get('predicted_iou', 0)
        
        # Classify masks by size
        if area > 10000:
            size_category = "Large"
        elif area > 1000:
            size_category = "Medium"
        else:
            size_category = "Small"
            
        # Classify by quality
        if predicted_iou > 0.9:
            quality = "High"
        elif predicted_iou > 0.7:
            quality = "Med"
        else:
            quality = "Low"
            
        return f"{size_category}_{quality}_{index:03d}"
        
    def masks_to_contours(self, masks, image_shape):
        """
        Convert masks to contour data for preview
        
        Args:
            masks: List of mask dictionaries
            image_shape: Image dimensions
            
        Returns:
            List of contour arrays
        """
        all_contours = []
        height = image_shape[0]
        
        for mask_data in masks:
            mask = mask_data['segmentation']
            mask_uint8 = (mask.astype(np.uint8)) * 255
            
            contours, _ = cv2.findContours(
                mask_uint8, 
                cv2.RETR_EXTERNAL, 
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            for contour in contours:
                contour = contour.squeeze()
                if len(contour.shape) == 2 and contour.shape[0] >= 3:
                    all_contours.append(contour)
                    
        return all_contours