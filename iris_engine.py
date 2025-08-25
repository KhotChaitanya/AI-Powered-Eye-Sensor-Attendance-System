"""
File name      : iris_engine.py
Description    : The core engine for iris recognition. Handles segmentation,
                 feature extraction (IrisCode), and matching.
Author         : Himanshu
Contributor    : Chaitanya (Integration modifications)
"""
import cv2
import numpy as np
from dataclasses import dataclass
from typing import Tuple

@dataclass
class IrisTemplate:
    """A simple data structure to hold the iris code and its corresponding mask."""
    code: np.ndarray
    mask: np.ndarray

def _estimate_pupil_center(gray: np.ndarray) -> Tuple[int, int]:
    """Internal helper to find a rough pupil center."""
    # ... (This function remains the same) ...
    h, w = gray.shape
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    th = cv2.medianBlur(th, 5)
    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return w // 2, h // 2
    c = max(cnts, key=cv2.contourArea)
    (x, y), r = cv2.minEnclosingCircle(c)
    x = int(np.clip(x, 0, w - 1)); y = int(np.clip(y, 0, h - 1))
    return x, y

def _unwrap_iris(gray: np.ndarray, out_size=(64, 256)) -> np.ndarray:
    """Internal helper for polar unwrapping of the iris."""
    # ... (This function remains the same) ...
    cx, cy = _estimate_pupil_center(gray)
    h, w = gray.shape
    max_r = int(min(w, h) * 0.45)
    polar = cv2.warpPolar(
        gray,
        (out_size[1], out_size[0]),
        (cx, cy),
        max_r,
        cv2.WARP_POLAR_LINEAR + cv2.WARP_FILL_OUTLIERS
    )
    return polar

def _enhance(gray: np.ndarray) -> np.ndarray:
    """Internal helper to enhance image contrast."""
    # ... (This function remains the same) ...
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)

def _gabor_bank(kernels=(
    (21, 4.0, 0.0, 8.0, 0.5, 0.0),
    (21, 4.0, np.pi/4, 8.0, 0.5, 0.0),
    (21, 4.0, np.pi/2, 8.0, 0.5, 0.0),
    (21, 4.0, 3*np.pi/4, 8.0, 0.5, 0.0),
)):
    """Internal helper to create a bank of Gabor filters."""
    # ... (This function remains the same) ...
    bank = []
    for ksize, sigma, theta, lambd, gamma, psi in kernels:
        kern = cv2.getGaborKernel((ksize, ksize), sigma, theta, lambd, gamma, psi, ktype=cv2.CV_32F)
        kern -= kern.mean()
        bank.append(kern)
    return bank

def _make_mask(norm: np.ndarray) -> np.ndarray:
    """Internal helper to create a mask of valid bits."""
    # ... (This function remains the same) ...
    valid = (norm > 25) & (norm < 230)
    k = cv2.Laplacian(norm, cv2.CV_32F)
    valid &= (np.abs(k) > 1.0)
    return valid.astype(bool)

def create_iris_code(frame: np.ndarray, unwrap_size=(64, 256)) -> IrisTemplate:
    """
    Function name  : create_iris_code
    Description    : Takes a live image frame, processes it, and generates a
                     unique IrisTemplate (binary code and mask).
    Author         : Himanshu
    Modified by    : Chaitanya (Adapted to accept a live frame instead of a file path)
    """
    if frame is None:
        raise ValueError("Input frame cannot be None.")

    # ----------------------------------------------------------------------
    """
    # INTEGRATION CHANGE: Removed file path logic to work with live video.
    # Author: Chaitanya
    """
    # ----------------------------------------------------------------------
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (256, 256), interpolation=cv2.INTER_AREA)

    norm = _unwrap_iris(_enhance(gray), out_size=unwrap_size)
    mask2d = _make_mask(norm)

    bank = _gabor_bank()
    feats = []
    for kern in bank:
        resp = cv2.filter2D(norm.astype(np.float32), -1, kern)
        bits = resp >= 0
        feats.append(bits)

    code3d = np.stack(feats, axis=-1)
    mask3d = np.repeat(mask2d[:, :, None], code3d.shape[-1], axis=2)

    code = code3d.flatten()
    mask = mask3d.flatten()
    return IrisTemplate(code=code.astype(bool), mask=mask.astype(bool))

def compare_iris_codes(t1: IrisTemplate, t2: IrisTemplate, rotations: int = 8) -> Tuple[float, int]:
    """
    Function name  : compare_iris_codes
    Description    : Compares two IrisTemplates using Hamming distance, accounting
                     for slight eye rotation.
    Author         : Himanshu
    """
    # ... (This function remains the same) ...
    code1, mask1 = t1.code, t1.mask
    code2, mask2 = t2.code, t2.mask
    assert code1.shape == code2.shape and mask1.shape == mask2.shape
    n = code1.size
    best_hd, best_shift = 1.0, 0
    valid_all = mask1 & mask2
    if valid_all.sum() == 0:
        return 1.0, 0
    for s in range(-rotations, rotations + 1):
        if s == 0:
            c2s, m2s = code2, mask2
        else:
            c2s, m2s = np.roll(code2, s), np.roll(mask2, s)
        valid = mask1 & m2s
        if valid.sum() < 50:
            continue
        xor = np.logical_xor(code1[valid], c2s[valid])
        hd = xor.mean()
        if hd < best_hd:
            best_hd, best_shift = hd, s
    return float(best_hd), int(best_shift)

def is_match(hamming_distance: float, threshold: float = 0.35) -> bool:
    """
    Function name  : is_match
    Description    : Determines if two irises match based on a Hamming distance threshold.
    Author         : Himanshu
    """
    return hamming_distance <= threshold

# --- The CLI demo is no longer needed for the main app, but can be kept for testing ---
if __name__ == "__main__":
    # ... (This part can be left as is for command-line testing) ...
    pass
