from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET


NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
SERIAL_DATE_BASE = datetime(1899, 12, 30)
SERIAL_RE = re.compile(r"^\d+(?:\.0+)?$")


def clean_text(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).replace("\u00a0", " ").strip()


def normalize_excel_date(value: str | None) -> str:
    text = clean_text(value)
    if not text:
        return ""
    if SERIAL_RE.fullmatch(text):
        as_int = int(float(text))
        return (SERIAL_DATE_BASE + timedelta(days=as_int)).strftime("%d.%m.%Y")
    return text


def read_xlsx_rows(path: str | Path) -> list[list[str]]:
    workbook_path = Path(path)
    with zipfile.ZipFile(workbook_path) as archive:
        shared_strings = _read_shared_strings(archive)
        sheet_xml = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        rows: list[list[str]] = []
        for row in sheet_xml.findall(".//x:sheetData/x:row", NS):
            values: list[str] = []
            for cell in row.findall("x:c", NS):
                values.append(_read_cell_value(cell, shared_strings))
            rows.append(values)
        return rows


def _read_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []

    shared_xml = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    values: list[str] = []
    for item in shared_xml.findall(".//x:si", NS):
        text_nodes = [node.text or "" for node in item.findall(".//x:t", NS)]
        values.append(clean_text("".join(text_nodes)))
    return values


def _read_cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t", "")
    if cell_type == "s":
        index = cell.findtext("x:v", default="", namespaces=NS)
        if index == "":
            return ""
        return clean_text(shared_strings[int(index)])
    if cell_type == "inlineStr":
        text_nodes = [node.text or "" for node in cell.findall(".//x:t", NS)]
        return clean_text("".join(text_nodes))
    return clean_text(cell.findtext("x:v", default="", namespaces=NS))
