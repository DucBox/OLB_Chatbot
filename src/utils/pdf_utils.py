import requests
import os
import shutil
import re
import time
from PyPDF2 import PdfReader, PdfWriter
from src.utils.config import TEMP_PDF_PATH
from shapely.geometry import box as shapely_box

def bbox_overlap(b1, b2):
    box1 = shapely_box(b1[0], b1[1], b1[2], b1[3])
    box2 = shapely_box(b2[0], b2[1], b2[2], b2[3])
    
    return box1.intersection(box2).area / box2.area
def split_pdf_to_pages(pdf_path: str, output_dir: str) -> list[str]:
    reader = PdfReader(pdf_path)
    output_paths = []

    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)

        out_path = os.path.join(output_dir, f"page_{i+1}.pdf")
        with open(out_path, "wb") as f:
            writer.write(f)
        output_paths.append(out_path)

    return output_paths

def extract_text_by_layout_order(file_path: str, api_key: str):
    headers = {"X-Api-Key": api_key}
    
    output_dir = TEMP_PDF_PATH
    os.makedirs(output_dir, exist_ok=True)
    
    split_pages = split_pdf_to_pages(file_path, output_dir)
    total_pages = len(split_pages)

    print(f"📄 Total pages: {total_pages}")
    all_page_outputs = []

    for page_num, page_path in enumerate(split_pages, start=1):
        print(f"\n=== Processing page {page_num} ===")

        # Layout
        f_page = {"file": (os.path.basename(page_path), open(page_path, "rb"), "application/pdf")}
        layout_resp = requests.post("https://www.datalab.to/api/v1/layout", files=f_page, headers=headers)
        layout_check_url = layout_resp.json()["request_check_url"]

        for _ in range(300):
            time.sleep(1)
            layout_result = requests.get(layout_check_url, headers=headers).json()
            if layout_result["status"] == "complete":
                break
        else:
            raise TimeoutError(f"Layout polling page {page_num} timed out")

        # OCR
        f_ocr = {"file": (os.path.basename(page_path), open(page_path, "rb"), "application/pdf")}
        ocr_resp = requests.post("https://www.datalab.to/api/v1/ocr", files=f_ocr, headers=headers, data={"langs": "en,vi"})
        ocr_check_url = ocr_resp.json()["request_check_url"]

        for _ in range(300):
            time.sleep(1)
            ocr_result = requests.get(ocr_check_url, headers=headers).json()
            if ocr_result["status"] == "complete":
                break
        else:
            raise TimeoutError(f"OCR polling page {page_num} timed out")

        layout_page = layout_result["pages"][0] 
        ocr_page = ocr_result["pages"][0]
        ocr_lines = ocr_page["text_lines"]

        layout_boxes = layout_page["bboxes"]
        for lbox in layout_boxes:
            lbox["text"] = ""
            lbox_bbox = lbox["bbox"]
            for line in ocr_lines:
                if bbox_overlap(lbox_bbox, line["bbox"]) > 0.5:
                    lbox["text"] += line["text"] + " "

        layout_boxes.sort(key=lambda x: x["position"])
        all_page_outputs.append((page_num, layout_boxes))
    shutil.rmtree(output_dir)
    return all_page_outputs

def reconstruct_page(blocks: list[dict]) -> list[str]:
    output = []
    for box in blocks:
        label = box["label"]
        text = box.get("text", "").strip()
        if not text:
            continue
        if label == "Section-header":
            output.append(f"🔷 {text.upper()}")
        elif label == "Text":
            output.append(f"  ↳ {text}")
        elif label == "List-item":
            output.append(f"    • {text}")
        elif label == "Title":
            output.append(f"🏷️ {text}")
        elif label == "Caption":
            output.append(f"🖼️ Caption: {text}")
        elif label == "Footnote":
            output.append(f"📝 Footnote: {text}")
        elif label == "Formula":
            output.append(f"🔢 Formula: {text}")
        elif label == "Page-footer":
            output.append(f"📄 Footer: {text}")
        elif label == "Page-header":
            output.append(f"📄 Header: {text}")
        elif label == "Picture" or label == "Figure":
            output.append(f"🖼️ [Image/Figure]: {text}")
        elif label == "Table":
            output.append(f"📊 [Table]: {text}")
        else:
            output.append(f"❓ {label}: {text}")  
    return output

