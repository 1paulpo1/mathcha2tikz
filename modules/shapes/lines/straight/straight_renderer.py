from typing import Dict, Any, Optional, Tuple

from mathcha2tikz.utils.style_utils import (
    merge_style_str_with_dict,
    split_style_parts,
    format_number,
    style_dict_to_str,
    apply_arrow_styles,
)
from mathcha2tikz.utils.id_utils import build_id_header

class StraightRenderer:

    def _fmt_num(self, value: Any) -> str:
        return format_number(value)

    def _style_from_dict(self, styles: Dict[str, Any]) -> str:
        return style_dict_to_str(styles, self._fmt_num)

    def _build_id_header(self, shape_id: Optional[str], raw: str = '') -> str:
        return build_id_header("Straight Lines", shape_id, raw)

    def render(self, processed_data: dict) -> dict:
        """
        Генерирует новую TikZ-команду на основе обработанных данных
        
        Args:
            processed_data: Dictionary containing processed line data
            
        Returns:
            Dictionary with the generated TikZ code
        """
        if 'raw' in processed_data:
            return {'tikz_code': processed_data['raw']}
        
        # If tikz_code is already processed, return it
        if 'tikz_code' in processed_data:
            return {'tikz_code': processed_data['tikz_code']}
        
        # Extract data
        style_str = processed_data.get('style_str', '')
        styles_dict = processed_data.get('styles') or {}
        if styles_dict:
            style_str = merge_style_str_with_dict(style_str, styles_dict, self._fmt_num)
        start_point = processed_data.get('start_point', (0, 0))
        end_point = processed_data.get('end_point', (0, 0))
        
        # Process arrow styles
        style_str = apply_arrow_styles(style_str, processed_data)
        
        # Format coordinates
        def format_coord(coord):
            if isinstance(coord, (int, float)):
                return f"{int(coord) if isinstance(coord, float) and coord.is_integer() else coord}"
            return f"{int(coord[0]) if isinstance(coord[0], float) and coord[0].is_integer() else coord[0]}, {int(coord[1]) if isinstance(coord[1], float) and coord[1].is_integer() else coord[1]}"
        
        start_str = f"({format_coord(start_point)})"
        end_str = f"({format_coord(end_point)})"
        
        # Format ID comment - only add if not already present in the raw data
        # TODO: refactor ID comment logic making unified comment module for all shapes
        id_line = ""
        if 'id' in processed_data and processed_data['id'] and 'raw' not in processed_data:
            id_line = self._build_id_header(processed_data['id'], processed_data.get('raw', ''))
        
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
        command = f"{id_line}\\draw{style_str} {start_str} -- {end_str};"
        
        # If no styles, add some spacing for better readability
        if not style_str and 'raw' in processed_data and '    ' in processed_data['raw']:
            command = f"{id_line}\\draw    {start_str} -- {end_str} ;"
        
        return {'tikz_code': command}