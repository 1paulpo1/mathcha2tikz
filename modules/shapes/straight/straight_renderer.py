from typing import Dict, Any

from utils.rendering.base_renderer import BaseRenderer
from utils.style_utils import split_style_parts
from utils.rendering.path_builder import build_line_coords


class StraightRenderer(BaseRenderer):

    shape_label = "Straight Lines"

    def render(self, processed_data: dict) -> dict:
        """
        Генерирует новую TikZ-команду на основе обработанных данных
        
        Args:
            processed_data: Dictionary containing processed line data
            
        Returns:
            Dictionary with the generated TikZ code
        """
        passthrough = self.passthrough(processed_data)
        if passthrough:
            return passthrough
        
        # If tikz_code is already processed, return it
        if 'tikz_code' in processed_data:
            return {'tikz_code': processed_data['tikz_code']}
        
        # Extract data
        style_str = processed_data.get('style_str', '')
        styles_dict = processed_data.get('styles') or {}
        if styles_dict:
            style_str = self.merge_styles(style_str, styles_dict)
        start_point = processed_data.get('start_point', (0, 0))
        end_point = processed_data.get('end_point', (0, 0))
        
        # Process arrow styles
        style_str = self.apply_arrows(style_str, processed_data)
        
        # Build line path
        line_path = build_line_coords(start_point, end_point, self._format_point)
        
        # Format ID comment - only add if not already present in the raw data
        id_line = ""
        if 'id' in processed_data and processed_data['id'] and 'raw' not in processed_data:
            id_line = self.id_header(processed_data['id'], processed_data.get('raw', ''))
        
        # Process styles to match expected format
        arrow_tokens = {'->', '>-', '-<', '<-', '<->', '<<-', '->>', '>->', '<-<', '<->>', '<<>>'} # TODO: needs refactor based on real arrow tokens
        if style_str and style_str.startswith('[') and style_str.endswith(']'):
            style_content = style_str[1:-1]
            styles = split_style_parts(style_content)

            rebuilt_parts = []
            for style in styles:
                if '=' in style:
                    key, value = style.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    if key == 'color':
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        rebuilt_parts.append(f"{key} = {value}")
                    elif key == 'opacity':
                        if float(value) != 1.0:
                            rebuilt_parts.append(f"{key} = {value}")
                    else:
                        rebuilt_parts.append(f"{key} = {value}")
                else:
                    token = style.strip()
                    if token in arrow_tokens:
                        rebuilt_parts.insert(0, token)
                    else:
                        rebuilt_parts.append(token)

            style_str = f"[{', '.join(rebuilt_parts)}]" if rebuilt_parts else ''
        else:
            style_str = style_str or ''
        
        # Build the final command with proper spacing
        command = f"{id_line}\\draw{style_str} {line_path};"
        
        # If no styles, add some spacing for better readability
        if not style_str and 'raw' in processed_data and '    ' in processed_data['raw']:
            command = f"{id_line}\\draw    {line_path} ;"
        
        return {'tikz_code': command}