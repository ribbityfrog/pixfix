
from PyQt6.QtWidgets import QApplication, QFileDialog, QWidget, QMessageBox
import sys
import cv2
import os
import numpy as np


def process_ref_image(ref_path, output_folder, tolerance=30):
    img = cv2.imread(ref_path)
    if img is None:
        print(f"Could not read {ref_path}")
        return
    mask = np.any(img > tolerance, axis=2)
    out_img = np.zeros_like(img)
    out_img[mask] = [0, 255, 0]
    out_img[(out_img != [0, 255, 0]).any(axis=2)] = [0, 0, 0]
    out_path = os.path.join(output_folder, os.path.splitext(os.path.basename(ref_path))[0] + '.jpg')
    cv2.imwrite(out_path, out_img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
    print(f"Saved treated ref image to {out_path}")

def iterative_median_inpaint(img, green_area, max_passes=100, start_ksize=2):
    treated = green_area.copy()
    result = img.copy()
    height, width = img.shape[:2]
    ksize = start_ksize
    initial_to_treat = np.count_nonzero(treated)
    print(f"Initial pixels to treat: {initial_to_treat}")
    for pass_num in range(max_passes):
        changes = 0
        new_result = result.copy()
        for y in range(height):
            for x in range(width):
                if treated[y, x]:
                    neighbors = []
                    out_of_mask_or_treated = 0
                    total_neighbors = 0
                    for dy in range(-ksize//2, ksize//2+1):
                        for dx in range(-ksize//2, ksize//2+1):
                            ny, nx = y+dy, x+dx
                            if 0 <= ny < height and 0 <= nx < width:
                                total_neighbors += 1
                                if not treated[ny, nx]:
                                    out_of_mask_or_treated += 1
                                    neighbors.append(result[ny, nx])
                    if out_of_mask_or_treated > total_neighbors // 2 and neighbors:
                        neighbors_arr = np.array(neighbors)
                        min_vals = neighbors_arr.min(axis=0)
                        max_vals = neighbors_arr.max(axis=0)
                        median = np.median(neighbors_arr, axis=0).astype(np.uint8)
                        clamped = np.clip(median, min_vals, max_vals)
                        new_result[y, x] = clamped
                        treated[y, x] = False
                        changes += 1
        result = new_result
        remaining = np.count_nonzero(treated)
        print(f"Pass {pass_num+1}: corrected {changes} pixels, {remaining} green pixels left.")
        if changes == 0 and remaining > 0:
            ksize += 1
            print(f"No pixels corrected, growing area to {ksize}x{ksize} for next pass.")
        if remaining == 0:
            print(f"All green area treated after {pass_num+1} passes.")
            break
    # Final pass: treat any remaining green pixels using only already treated neighbors in the largest window
    remaining = np.argwhere(treated)
    if len(remaining) > 0:
        final_ksize = ksize + max_passes - 1
        print(f"Final pass: treating {len(remaining)} remaining green pixels using only already treated neighbors in {final_ksize}x{final_ksize} window...")
        for y, x in remaining:
            neighbors = []
            for dy in range(-final_ksize//2, final_ksize//2+1):
                for dx in range(-final_ksize//2, final_ksize//2+1):
                    ny, nx = y+dy, x+dx
                    if 0 <= ny < height and 0 <= nx < width and not treated[ny, nx]:
                        pixel = result[ny, nx]
                        neighbors.append(pixel)
            if neighbors:
                neighbors_arr = np.array(neighbors)
                min_vals = neighbors_arr.min(axis=0)
                max_vals = neighbors_arr.max(axis=0)
                median = np.median(neighbors_arr, axis=0).astype(np.uint8)
                clamped = np.clip(median, min_vals, max_vals)
                result[y, x] = clamped
    return result

def apply_median_filter_to_green_areas(ref_path, ref_mask, img_path, output_folder, strength=1.0):
    img = cv2.imread(img_path)
    if img is None:
        print(f"Could not read {img_path}")
        return
    ref_img = cv2.imread(ref_path)
    ref_h, ref_w = ref_img.shape[:2]
    img_h, img_w = img.shape[:2]
    scale_x = img_w / ref_w
    scale_y = img_h / ref_h
    mask_resized = np.zeros((img_h, img_w), dtype=np.uint8)
    if strength > 0:
        expand_radius = int(np.ceil(max(scale_x, scale_y) * strength))
        for y in range(img_h):
            for x in range(img_w):
                ref_x = int(x / scale_x)
                ref_y = int(y / scale_y)
                if ref_mask[ref_y, ref_x]:
                    for dy in range(-expand_radius, expand_radius+1):
                        for dx in range(-expand_radius, expand_radius+1):
                            ny, nx = y+dy, x+dx
                            if 0 <= ny < img_h and 0 <= nx < img_w:
                                mask_resized[ny, nx] = 1
        print(f"Expanded green area pixels to treat (strength={strength}): {np.count_nonzero(mask_resized > 0)}")
    else:
        for y in range(img_h):
            for x in range(img_w):
                ref_x = int(x / scale_x)
                ref_y = int(y / scale_y)
                if ref_mask[ref_y, ref_x]:
                    mask_resized[y, x] = 1
        print(f"Direct green area pixels to treat: {np.count_nonzero(mask_resized > 0)}")
    green_area = mask_resized > 0
    filtered_img = iterative_median_inpaint(img, green_area, max_passes=100, start_ksize=2)
    # Apply bilateral filter only to the corrected (green) areas
    bilateral_img = cv2.bilateralFilter(filtered_img, d=9, sigmaColor=75, sigmaSpace=75)
    # Blend filtered pixels only into the corrected areas
    mask3 = np.repeat(green_area[:, :, np.newaxis], 3, axis=2)
    filtered_img[mask3] = bilateral_img[mask3]
    out_path = os.path.join(output_folder, os.path.basename(img_path))
    cv2.imwrite(out_path, filtered_img)
    print(f"Saved treated image to {out_path}")

def main():
    input_folder = os.path.join(os.path.dirname(__file__), 'original')
    output_folder = os.path.join(os.path.dirname(__file__), 'treated')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    files = os.listdir(input_folder)
    ref_file = None
    for f in files:
        if f.lower().startswith('ref.'):
            ref_file = f
            break
    if not ref_file:
        print("No ref image found.")
        return
    ref_path = os.path.join(input_folder, ref_file)
    img = cv2.imread(ref_path)
    mask = np.any(img > 30, axis=2)
    green_mask = mask
    process_ref_image(ref_path, output_folder, tolerance=30)
    valid_exts = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']
    for f in files:
        if f != ref_file and os.path.splitext(f)[1].lower() in valid_exts + [e.upper() for e in valid_exts]:
            img_path = os.path.join(input_folder, f)
            print(f"Processing {f}...")
            # Set strength to a fraction of the scale factor (e.g., 0.5 for scale/2)
            apply_median_filter_to_green_areas(ref_path, green_mask, img_path, output_folder, strength=0.5)




def run_with_gui():
    app = QApplication(sys.argv)
    # Keep reference to app to avoid garbage collection
    _ = app
    widget = QWidget()
    widget.setWindowTitle("PixFix - Select Reference Image")
    ref_path, _ = QFileDialog.getOpenFileName(widget, "Select Reference Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.gif)")
    if not ref_path:
        QMessageBox.warning(widget, "No Image Selected", "You must select a reference image.")
        return
    input_folder = os.path.dirname(ref_path)
    ref_file = os.path.basename(ref_path)
    treated_folder = os.path.join(input_folder, "treated")
    if not os.path.exists(treated_folder):
        os.makedirs(treated_folder)
    img = cv2.imread(ref_path)
    if img is None:
        QMessageBox.critical(widget, "Error", f"Could not read {ref_path}")
        return
    mask = np.any(img > 30, axis=2)
    green_mask = mask
    process_ref_image(ref_path, treated_folder, tolerance=30)
    valid_exts = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']
    files = os.listdir(input_folder)
    for f in files:
        if f != ref_file and os.path.splitext(f)[1].lower() in valid_exts + [e.upper() for e in valid_exts]:
            img_path = os.path.join(input_folder, f)
            print(f"Processing {f}...")
            apply_median_filter_to_green_areas(ref_path, green_mask, img_path, treated_folder, strength=0.5)
    QMessageBox.information(widget, "Done", f"Processing complete. Treated images saved in: {treated_folder}")

if __name__ == "__main__":
    run_with_gui()
