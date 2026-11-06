import os
import argparse

PRO_TEMPLATE = """
import torch
import numpy as np
from PIL import Image
import os

class {class_name}:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {{
            "required": {{
                "image": ("IMAGE",),
                "strength": ("FLOAT", {{"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01}}),
            }},
            "optional": {{
                "suffix": ("STRING", {{"default": "_processed"}}),
            }}
        }}

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")
    FUNCTION = "process"
    CATEGORY = "{category}"

    def process(self, image, strength, suffix=""):
        # Image is [Batch, H, W, C] - Torch Tensor
        # Pro tip: Move to CPU only if needed, stay in GPU for speed
        results = []
        for img in image:
            # Simple multiplier (example logic)
            processed = img * strength
            results.append(processed)
            
        output_image = torch.stack(results, dim=0)
        return (output_image, f"Processed with strength {{strength}}")

NODE_CLASS_MAPPINGS = {{
    "{class_name}": {class_name}
}}

NODE_DISPLAY_NAME_MAPPINGS = {{
    "{class_name}": "{display_name}"
}}
"""

INIT_TEMPLATE = """
from .node import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
"""

def main():
    parser = argparse.ArgumentParser(description="Forge a new ComfyUI node suite.")
    parser.add_argument("--name", required=True, help="Internal class name")
    parser.add_argument("--display", help="Display name in UI")
    parser.add_argument("--category", default="FutureNodes", help="Node category")
    parser.add_argument("--out_dir", required=True, help="Output directory in custom_nodes")
    
    args = parser.parse_args()
    
    display_name = args.display if args.display else args.name
    
    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir, exist_ok=True)
        
    # Create __init__.py
    with open(os.path.join(args.out_dir, "__init__.py"), "w", encoding="utf-8") as f:
        f.write(INIT_TEMPLATE.strip())
        
    # Create node.py
    node_content = PRO_TEMPLATE.format(
        class_name=args.name,
        category=args.category,
        display_name=display_name
    )
    
    with open(os.path.join(args.out_dir, "node.py"), "w", encoding="utf-8") as f:
        f.write(node_content.strip())
        
    print(f"[*] Pro Node Suite {args.name} forged at {args.out_dir}")

if __name__ == "__main__":
    main()
