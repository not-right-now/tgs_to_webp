"""
TGS to WebP Converter Module

A simple Python module for converting TGS (Telegram animated stickers) to WebP format.
TGS files are gzip-compressed Lottie JSON animations.
"""

import os
import math
import webp
import time
from PIL import Image, ImageDraw
import rlottie_python as rlottie

class TGSToWebPConverter:
    """Converter class for TGS to WebP conversion with automatic timing preservation."""
    
    def __init__(self, width: int = -1, height: int = -1, quality: int = 80,
                keep_aspect: bool = True, allow_upscale: bool = True, pad: bool = True,
                fps: float = 30.0, preserve_timing: bool = True):
        """
        Initialize the converter.
        
        Args:
            width: Output width in pixels
            height: Output height in pixels
            quality: WebP quality (0-100)
            keep_aspect: Preserve original aspect ratio (default True).
            allow_upscale: Allow enlarging smaller sources to meet target (default True).
            pad: When keep_aspect=True, pad with transparent canvas to fill target if True (default).
                If False, use cover+center-crop mode instead.
            fps: Target frames per second (ignored if preserve_timing=True)
            preserve_timing: If True, automatically adjusts FPS to preserve original animation timing
        """
        self.width = width
        self.height = height
        self.quality = quality
        self.keep_aspect = keep_aspect
        self.allow_upscale = allow_upscale
        self.pad = pad
        self.fps = fps
        self.preserve_timing = preserve_timing
    
    @staticmethod
    def _select_indices(total_frames: int, original_duration: float, count: int) -> list[int]:
        """
        Selects a specific count of frame indices from a total number of frames.
        """
        if count <= 0:
            selected_indices = []
        elif count == 1:
            selected_indices = [0]
        elif count >= total_frames:
            selected_indices = list(range(total_frames))
        else:
            # Calculate target timestamps
            d = max(original_duration, 1e-6)
            targets = [i * (d / (count - 1)) for i in range(count)]
            # Map timestamps back to frame indices
            selected_indices = []
            for t in targets:
                idx = int(round((t / d) * (total_frames - 1)))
                if idx < 0: idx = 0
                if idx > total_frames - 1: idx = total_frames - 1
                # avoid duplicates by ensuring monotonic increasing indices
                if not selected_indices or idx > selected_indices[-1]:
                    selected_indices.append(idx)
            # If we lost some frames due to removing duplicates, fill by evenly spaced integer indices
            if len(selected_indices) < count:
                selected_indices = [int(round(i * (total_frames - 1) / (count - 1))) for i in range(count)]

        return selected_indices
    
    def _render_lottie_frame(self, lottie_animation, frame_num: int) -> Image.Image:
        """
        Renders a single frame from a Lottie animation using the wrapper method.
        """
        try:
            # This returns a PIL Image object
            pil_image = lottie_animation.render_pillow_frame(frame_num=frame_num)
            
            # ============ Resize if needed =============

            orig_w, orig_h = pil_image.size
            target_w = self.width if self.width != -1 else orig_w
            target_h = self.height if self.height != -1 else orig_h
            pad_mode = self.pad

            # if haven't given width and height or given but our image is already of that dimension, we need not to resize
            if (orig_w, orig_h) == (target_w, target_h):
                return pil_image.convert("RGBA")
            
            if self.keep_aspect:
                if pad_mode:
                    # Fit inside target, then pad (transparent canvas)
                    scale = min(target_w / orig_w, target_h / orig_h)
                else:
                    # Cover the target, then crop center
                    scale = max(target_w / orig_w, target_h / orig_h)
                
                if not self.allow_upscale and scale > 1.0:
                    scale = 1.0
                    pad_mode = True # Force padding if we can't upscale to crop

                if pad_mode:
                    # fit: make sure new dims are <= target (use floor / clamp)
                    new_w = max(1, int(math.floor(orig_w * scale)))
                    new_h = max(1, int(math.floor(orig_h * scale)))
                    # clamp in case of rounding overshoot
                    new_w = min(new_w, target_w)
                    new_h = min(new_h, target_h)
                else:
                    # cover: make sure new dims are >= target (use ceil / ensure minimum)
                    new_w = max(1, int(math.ceil(orig_w * scale)))
                    new_h = max(1, int(math.ceil(orig_h * scale)))
                    if new_w < target_w:
                        new_w = target_w
                    if new_h < target_h:
                        new_h = target_h
                
                resized = pil_image.resize((new_w, new_h), Image.LANCZOS).convert("RGBA")

                if pad_mode:
                    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
                    left = (target_w - new_w) // 2
                    top = (target_h - new_h) // 2
                    canvas.paste(resized, (left, top), resized)
                    final_img = canvas
                else: # Crop mode
                    left = (new_w - target_w) // 2
                    top = (new_h - target_h) // 2
                    final_img = resized.crop((left, top, left + target_w, top + target_h))
            else: # Stretch mode
                desired_w, desired_h = target_w, target_h
                if not self.allow_upscale:
                    # clamp each dimension separately so we don't upscale any axis
                    desired_w = min(desired_w, orig_w)
                    desired_h = min(desired_h, orig_h)
                    
                if (desired_w, desired_h) == (orig_w, orig_h):
                    resized = pil_image.convert("RGBA")
                else:
                    resized = pil_image.resize((desired_w, desired_h), Image.LANCZOS).convert("RGBA")
                # Ensure final output is exactly target size by centering resized on transparent canvas when needed
                if desired_w == target_w and desired_h == target_h:
                    final_img = resized
                else:
                    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
                    left = (target_w - desired_w) // 2
                    top = (target_h - desired_h) // 2
                    canvas.paste(resized, (left, top), resized)
                    final_img = canvas
            
            return final_img
                
        except Exception as e:
            # The exception block calls the fallback function
            print(f"Warning: Rlottie frame rendering failed, using fallback: {e}")
            fallback_width = self.width if self.width != -1 else 512
            fallback_height = self.height if self.height != -1 else 512
            total_frames = lottie_animation.lottie_animation_get_totalframe()
            return self._create_fallback_frame(frame_num, total_frames, width=fallback_width, height=fallback_height)

    
    def _create_fallback_frame(self, frame_num: int, total_frames: int, width: int = 512, height: int = 512) -> Image.Image:
        """Create a simple fallback frame when Lottie rendering fails."""
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Calculate animation progress
        progress = frame_num / max(total_frames - 1, 1)
        
        # Create a simple animated element
        center_x = int(width * (0.2 + 0.6 * progress))
        center_y = int(height * 0.5)
        radius = int(30 + 20 * abs(0.5 - progress) * 2)
        
        # Draw a circle
        color = (51, 153, 255, 200)  # Blue with transparency
        draw.ellipse([center_x - radius, center_y - radius, 
                     center_x + radius, center_y + radius], fill=color)
        
        return img
    

    
    def convert(self, tgs_path: str, webp_path: str) -> bool:
        """
        Convert TGS file to animated WebP.
        
        Args:
            tgs_path: Path to input TGS file
            webp_path: Path to output WebP file
            
        Returns:
            True if conversion successful, False otherwise
            
        Raises:
            FileNotFoundError: If TGS file doesn't exist
            ValueError: If TGS file is invalid
            IOError: If output file cannot be written
        """
        start_time = time.monotonic()
        if not os.path.exists(tgs_path):
            raise FileNotFoundError(f"TGS file not found: {tgs_path}")
        
        try:
            # Use the rlottie loader
            lottie_animation = rlottie.LottieAnimation.from_tgs(tgs_path)
            
            max_frames = 180  # Performance limit

            # Get animation properties
            original_total_frames = lottie_animation.lottie_animation_get_totalframe()
            if not original_total_frames:
                print("The TGS appearss to have no frame or corrupted.")
                return False
            
            original_fps = float(lottie_animation.lottie_animation_get_framerate())
            # Calculate original duration in seconds
            original_duration = original_total_frames / max(original_fps, 1.0)

            # select which frames to render
            indices_to_render = self._select_indices(original_total_frames, original_duration, max_frames)
            total_frames = len(indices_to_render)

            if self.preserve_timing:
                output_fps = total_frames / original_duration
                # Logging details 
                if original_total_frames <= max_frames:
                    print(f"Preserving all {total_frames} frames, adjusting FPS to {output_fps:.1f} to maintain {original_duration:.2f}s duration")
                else:
                    print(f"Limiting to a total of {max_frames} frames, adjusting FPS to {output_fps:.1f} to maintain {original_duration:.2f}s duration")
                
            else:
                # Use user-specified FPS
                output_fps = self.fps
                if original_total_frames <= max_frames:
                    print(f"Preserving all {total_frames} frames, using specified FPS of {self.fps}, which will alter the final duration.")
                else:
                    print(f"Limiting to a total of {max_frames} frames, using specified FPS of {self.fps}, which will alter the final duration.")
            
            
            if output_fps <= 0.0: output_fps = 1 # Avoid zero

            # Render all selected frames
            frames = []
            for frame_index in indices_to_render:
                frame = self._render_lottie_frame(lottie_animation, frame_index)
                frames.append(frame)
            
            if not frames:
                raise ValueError("No frames could be rendered from TGS file")
            
            
            # Ensure output directory exists
            output_dir = os.path.dirname(webp_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                
            # Save as animated WebP
            webp.save_images(
                frames, 
                webp_path, 
                fps=output_fps, 
                quality=self.quality
            )
                        
            return True
            
        except Exception as e:
            raise IOError(f"Conversion failed: {e}")
        
        finally:
            end_time = time.monotonic()
            duration = end_time - start_time
            print(f"⌛ Total time taken: {duration:.2f} seconds.")

def convert_tgs_to_webp(tgs_path: str, webp_path: str, 
                       width: int = -1, height: int = -1, 
                       quality: int = 80,
                       keep_aspect: bool = True,
                       allow_upscale: bool = True,
                       pad: bool = True,
                       fps: float = 30.0, 
                       preserve_timing: bool = True) -> bool:
    """
    Simple function to convert TGS to WebP with automatic timing preservation.
    
    Args:
        tgs_path: Path to input TGS file
        webp_path: Path to output WebP file
        width: Output width in pixels (default: Original)
        height: Output height in pixels (default: Original)
        quality: WebP quality 0-100 (default: 80)
        keep_aspect: Preserve original aspect ratio (default True).
        allow_upscale: Allow enlarging smaller sources to meet target (default True).
        pad: When keep_aspect=True, pad with transparent canvas to fill target if True (default).
            If False, use cover+center-crop mode instead.
        fps: Target frames per second (ignored if preserve_timing=True, default: 30)
        preserve_timing: Automatically preserve original animation timing (default: True)
        
    Returns:
        True if conversion successful, False otherwise       
    """
    converter = TGSToWebPConverter(width, height, quality, keep_aspect, allow_upscale, pad, fps, preserve_timing)
    try:
        return converter.convert(tgs_path, webp_path)
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    import sys, argparse
    
    
    parser = argparse.ArgumentParser(
        description="Convert TGS (Telegram animated stickers) to animated WebP.",
        # This helps in formatting the help text nicely
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Required positional arguments
    parser.add_argument("input_file", help="Path to the input TGS file.")
    parser.add_argument("output_file", help="Path for the output WebP file.")

    # Optional arguments with default values
    parser.add_argument("--width", type=int, default=-1, help="Output width in pixels. Default: Original.")
    parser.add_argument("--height", type=int, default=-1, help="Output height in pixels. Default: Original.")
    parser.add_argument("--quality", type=int, default=80, help="WebP quality (0-100). Default: 80.")
    parser.add_argument("--fps", type=float, default=30.0,
                        help="Frames per second. \n(Note: This is ignored by default unless you disable timing preservation).")

    # arguments with a default a boolean flag
    parser.add_argument("--no-keep-aspect", dest="keep_aspect", action="store_false",
                        help="Disable preserving aspect ratio (stretch the image).")
    parser.add_argument("--no-upscale", dest="allow_upscale", action="store_false",
                        help="Disable upscaling (do not enlarge source).")
    parser.add_argument("--crop", dest="pad", action="store_false",
                        help="When keeping aspect, use crop instead of padding.")
    parser.add_argument("--no-preserve-timing", action="store_false", dest="preserve_timing",
                        help="Disable automatic timing preservation to use the manual FPS value.")

    # Let argparse handle the arguments
    args = parser.parse_args()

    # Call the main function with the parsed arguments
    success = convert_tgs_to_webp(
        tgs_path=args.input_file,
        webp_path=args.output_file,
        width=args.width,
        height=args.height,
        quality=args.quality,
        keep_aspect=args.keep_aspect,
        allow_upscale=args.allow_upscale,
        pad=args.pad,
        fps=args.fps,
        preserve_timing=args.preserve_timing

    )

    if success:
        print(f"✅ Successfully converted {args.input_file} to {args.output_file}")
    else:
        print(f"❌ Failed to convert {args.input_file}")
        sys.exit(1)
