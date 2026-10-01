"""Generator PDF Laporan Diagnostik Kondisi Mesin (reportlab)."""
import io
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer,
                                Table, TableStyle, KeepTogether)

CYAN = colors.HexColor("#0e7490")
CYAN_BG = colors.HexColor("#ecfeff")
SLATE9 = colors.HexColor("#0f172a")
SLATE6 = colors.HexColor("#475569")
SLATE4 = colors.HexColor("#94a3b8")
SLATE2 = colors.HexColor("#e2e8f0")
SLATE1 = colors.HexColor("#f8fafc")
GREEN = colors.HexColor("#059669")
GREEN_BG = colors.HexColor("#ecfdf5")
AMBER = colors.HexColor("#d97706")
AMBER_BG = colors.HexColor("#fffbeb")
RED = colors.HexColor("#dc2626")
RED_BG = colors.HexColor("#fef2f2")

LEVEL = {
    "low": ("RISIKO RENDAH", GREEN, GREEN_BG),
    "medium": ("RISIKO SEDANG", AMBER, AMBER_BG),
    "high": ("RISIKO TINGGI", RED, RED_BG),
}
STATUS = {"ok": ("Normal", GREEN), "warn": ("Perhatian", AMBER), "alert": ("Di luar batas", RED)}

W = 174 * mm  # lebar konten (A4 - margin 18 mm)


def _styles():
    base = dict(fontName="Helvetica", textColor=SLATE9, alignment=TA_LEFT)
    return {
        "body": ParagraphStyle("body", fontSize=9, leading=13, **base),
        "small": ParagraphStyle("small", fontSize=7.5, leading=10.5, **{**base, "textColor": SLATE6}),
        "h2": ParagraphStyle("h2", fontSize=11, leading=14, spaceBefore=12, spaceAfter=5,
                             **{**base, "fontName": "Helvetica-Bold", "textColor": CYAN}),
        "cell": ParagraphStyle("cell", fontSize=8.5, leading=11, **base),
        "cellb": ParagraphStyle("cellb", fontSize=8.5, leading=11, **{**base, "fontName": "Helvetica-Bold"}),
        "hdr": ParagraphStyle("hdr", fontSize=7.5, leading=10, **{**base, "fontName": "Helvetica-Bold", "textColor": SLATE6}),
        "title": ParagraphStyle("title", fontSize=17, leading=21, **{**base, "fontName": "Helvetica-Bold", "textColor": colors.white}),
        "sub": ParagraphStyle("sub", fontSize=8.5, leading=12, **{**base, "textColor": colors.HexColor("#cffafe")}),
    }


def _p(text, style):
    return Paragraph(text, style)


def _status_par(key, S):
    label, col = STATUS[key]
    return Paragraph(f'<font color="{col.hexval()}"><b>{label}</b></font>', S["cell"])


def _prob_bar(prob, medium_from, high_from, width=W - 8 * mm, h=6 * mm):
    d = Drawing(width, h + 9 * mm)
    y = 5 * mm
    x1, x2 = width * medium_from / 100, width * high_from / 100
    d.add(Rect(0, y, x1, h, fillColor=colors.HexColor("#d1fae5"), strokeColor=None))
    d.add(Rect(x1, y, x2 - x1, h, fillColor=colors.HexColor("#fef3c7"), strokeColor=None))
    d.add(Rect(x2, y, width - x2, h, fillColor=colors.HexColor("#fee2e2"), strokeColor=None))
    mx = width * max(0.0, min(prob, 100.0)) / 100
    col = GREEN if prob < medium_from else (AMBER if prob < high_from else RED)
    d.add(Rect(0, y, mx, h, fillColor=col, strokeColor=None))
    d.add(Polygon([mx - 2.2 * mm, y + h + 2.8 * mm, mx + 2.2 * mm, y + h + 2.8 * mm, mx, y + h + 0.3 * mm],
                  fillColor=SLATE9, strokeColor=None))
    for xv, txt in [(0, "0%"), (x1, f"{medium_from:.0f}%"), (x2, f"{high_from:.0f}% (batas keputusan)"), (width, "100%")]:
        anchor = "start" if xv == 0 else ("end" if xv == width else "middle")
        d.add(String(xv, 0.8 * mm, txt, fontName="Helvetica", fontSize=6.5, fillColor=SLATE6, textAnchor=anchor))
    return d


def _mini_bar(pct, color, width=70 * mm, h=3.4 * mm):
    d = Drawing(width, h)
    d.add(Rect(0, 0, width, h, fillColor=SLATE2, strokeColor=None))
    d.add(Rect(0, 0, width * max(0.0, min(pct, 100.0)) / 100, h, fillColor=color, strokeColor=None))
    return d


def _grid(data, widths, header=True, extra=None):
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, SLATE2),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), SLATE1), ("LINEBELOW", (0, 0), (-1, 0), 0.8, SLATE2)]
    if extra:
        st += extra
    t.setStyle(TableStyle(st))
    return t


def build_report_pdf(r, meta=None):
    """r: hasil analyze_machine(). meta: dict machine_id, company, prepared_by (opsional)."""
    meta = meta or {}
    S = _styles()
    e = lambda k, default="-": escape((meta.get(k) or default).strip()) or default
    lvl_label, lvl_col, lvl_bg = LEVEL[r["level"]]
    sup, uns, rec = r["supervised"], r["unsupervised"], r["recommendation"]

    buf = io.BytesIO()
    doc = BaseDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                          topMargin=16 * mm, bottomMargin=18 * mm,
                          title=f"Laporan Diagnostik {r['report_id']}", author="AI Predictive Maintenance")

    def footer(c, d):
        c.saveState()
        c.setStrokeColor(SLATE2); c.line(18 * mm, 13 * mm, A4[0] - 18 * mm, 13 * mm)
        c.setFont("Helvetica", 7); c.setFillColor(SLATE6)
        c.drawString(18 * mm, 9 * mm, f"AI Predictive Maintenance  |  {r['report_id']}  |  Dokumen dihasilkan otomatis")
        c.drawRightString(A4[0] - 18 * mm, 9 * mm, f"Halaman {d.page}")
        c.restoreState()

    doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(18 * mm, 18 * mm, W, A4[1] - 34 * mm, id="f",
                                                              leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)],
                                       onPage=footer)])
    el = []

    # ---- Header ----
    head = Table([[[_p("Laporan Diagnostik Kondisi Mesin", S["title"]),
                    _p("Analisis prediktif berbasis Random Forest (supervised) dan K-Means (unsupervised)", S["sub"])]]],
                 colWidths=[W])
    head.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), CYAN), ("LEFTPADDING", (0, 0), (-1, -1), 12),
                              ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 12)]))
    el += [head, Spacer(1, 8)]

    meta_rows = [
        [_p("ID Laporan", S["hdr"]), _p(r["report_id"], S["cell"]), _p("Tanggal Analisis", S["hdr"]), _p(r["generated_at"], S["cell"])],
        [_p("Nama / ID Mesin", S["hdr"]), _p(e("machine_id"), S["cell"]), _p("Ditujukan Kepada", S["hdr"]), _p(e("company"), S["cell"])],
        [_p("Disusun Oleh", S["hdr"]), _p(e("prepared_by"), S["cell"]), _p("", S["hdr"]), _p("", S["cell"])],
    ]
    el.append(_grid(meta_rows, [30 * mm, 57 * mm, 30 * mm, 57 * mm], header=False))

    # ---- Ringkasan ----
    el.append(_p("1. Ringkasan Kondisi", S["h2"]))
    def stat(label, value, col=SLATE9):
        return [_p(label, S["hdr"]), Paragraph(f'<font size="15" color="{col.hexval()}"><b>{value}</b></font>', S["body"])]
    cards = Table([[stat("SKOR KESEHATAN", f"{r['health_score']:.1f}%", lvl_col),
                    stat("PROBABILITAS GAGAL", f"{sup['failure_probability']:.1f}%", lvl_col),
                    stat("TINGKAT RISIKO", lvl_label.replace("RISIKO ", ""), lvl_col),
                    stat("KELOMPOK (K-MEANS)", f"Cluster {uns['cluster']}")]],
                  colWidths=[W / 4] * 4)
    cards.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, SLATE2), ("INNERGRID", (0, 0), (-1, -1), 0.6, SLATE2),
                               ("BACKGROUND", (0, 0), (-1, -1), lvl_bg), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                               ("LEFTPADDING", (0, 0), (-1, -1), 8)]))
    el += [cards, Spacer(1, 6), _p(escape(r["description"]), S["body"])]

    # ---- Parameter ----
    el.append(_p("2. Parameter Input Mesin", S["h2"]))
    rows = [[_p("PARAMETER", S["hdr"]), _p("NILAI", S["hdr"]), _p("ACUAN", S["hdr"]), _p("STATUS", S["hdr"])]]
    for p in r["parameters"]:
        rows.append([_p(p["label"], S["cellb"]), _p(escape(p["value"]), S["cell"]),
                     _p(escape(p["ref"]), S["cell"]), _status_par(p["status"], S)])
    el.append(_grid(rows, [34 * mm, 50 * mm, 60 * mm, 30 * mm]))

    # ---- Supervised ----
    sec = [_p("3. Probabilitas Kegagalan (Supervised Learning - Random Forest)", S["h2"]),
           _p(f"Probabilitas kegagalan mesin untuk kondisi input ini adalah <b>{sup['failure_probability']:.1f}%</b> "
              f"(tingkat: <font color='{lvl_col.hexval()}'><b>{lvl_label.title()}</b></font>). "
              "Model menandai kegagalan bila probabilitas mencapai batas keputusan 50%.", S["body"]),
           Spacer(1, 4), _prob_bar(sup["failure_probability"], sup["medium_from"], sup["decision_threshold"])]
    if sup["feature_importance"]:
        fr = [[_p("FAKTOR", S["hdr"]), _p("PENGARUH GLOBAL TERHADAP MODEL", S["hdr"]), _p("", S["hdr"])]]
        for f in sup["feature_importance"]:
            fr.append([_p(escape(f["feature"]), S["cell"]), _mini_bar(f["importance"] * 2.5, CYAN),
                       _p(f"{f['importance']:.1f}%", S["cell"])])
        sec += [Spacer(1, 4), _p("Faktor yang paling berpengaruh pada model secara umum (bukan khusus mesin ini):", S["small"]),
                _grid(fr, [58 * mm, 90 * mm, 26 * mm])]
    el.append(KeepTogether(sec))

    # ---- Unsupervised ----
    sec = [_p("4. Pengelompokan Kondisi Operasi (Unsupervised Learning - K-Means)", S["h2"]),
           _p(f"Kondisi mesin ini masuk ke <b>Cluster {uns['cluster']} - {escape(uns['cluster_name'])}</b>. "
              "Bilah di bawah menunjukkan kedekatan relatif terhadap tiap centroid (semakin tinggi = semakin mirip).", S["body"]),
           Spacer(1, 4)]
    cr = [[_p("CLUSTER", S["hdr"]), _p("KEDEKATAN", S["hdr"]), _p("", S["hdr"]), _p("JARAK", S["hdr"])]]
    extra = []
    for i, c in enumerate(uns["clusters"], start=1):
        name = f"Cluster {c['id']} - {escape(c['name'])}" + (" (terpilih)" if c["assigned"] else "")
        cr.append([_p(f"<b>{name}</b>" if c["assigned"] else name, S["cell"]),
                   _mini_bar(c["similarity"], CYAN if c["assigned"] else SLATE4, 62 * mm),
                   _p(f"{c['similarity']:.1f}%", S["cell"]), _p(f"{c['distance']:.2f}", S["cell"])])
        if c["assigned"]:
            extra.append(("BACKGROUND", (0, i), (-1, i), CYAN_BG))
    sec.append(_grid(cr, [62 * mm, 66 * mm, 22 * mm, 24 * mm], extra=extra))
    sec += [Spacer(1, 3)] + [_p(f"<b>Cluster {c['id']}</b> - {escape(c['profile'])}", S["small"]) for c in uns["clusters"]]
    el.append(KeepTogether(sec))

    # ---- Aturan mode kegagalan ----
    el.append(_p("5. Pemeriksaan Aturan Mode Kegagalan", S["h2"]))
    el.append(_p("Pemeriksaan deterministik berdasarkan definisi mode kegagalan pada dataset AI4I 2020, "
                 "sebagai pembanding terhadap hasil model.", S["small"]))
    el.append(Spacer(1, 3))
    rr = [[_p("KODE", S["hdr"]), _p("MODE KEGAGALAN", S["hdr"]), _p("KONDISI", S["hdr"]), _p("NILAI", S["hdr"]), _p("HASIL", S["hdr"])]]
    for x in r["rules"]:
        res = (f'<font color="{RED.hexval()}"><b>Terpenuhi</b></font>' if x["triggered"]
               else f'<font color="{GREEN.hexval()}"><b>Tidak</b></font>')
        rr.append([_p(f"<b>{x['code']}</b>", S["cell"]), _p(escape(x["name"]), S["cell"]),
                   _p(escape(x["condition"]), S["cell"]), _p(escape(x["value"]), S["cell"]), _p(res, S["cell"])])
    el.append(_grid(rr, [14 * mm, 28 * mm, 70 * mm, 38 * mm, 24 * mm]))

    # ---- Rekomendasi ----
    notes = "".join(f"<br/>- {escape(n)}" for n in rec["notes"])
    box = Table([[[_p(f"<b>Rekomendasi: {escape(rec['title'])}</b>", ParagraphStyle("rt", parent=S["body"], fontSize=10, textColor=lvl_col)),
                   Spacer(1, 2), _p(escape(rec["text"]) + notes, S["body"])]]], colWidths=[W])
    box.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.8, lvl_col), ("BACKGROUND", (0, 0), (-1, -1), lvl_bg),
                             ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                             ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 9)]))
    el.append(KeepTogether([_p("6. Rekomendasi Tindakan", S["h2"]), box,
                            Spacer(1, 3), _p("Rekomendasi disusun dengan aturan sederhana dari probabilitas kegagalan dan pemeriksaan parameter; "
                                             "bukan keluaran model pembelajaran.", S["small"])]))

    # ---- Catatan model ----
    mi = r["model_info"]; rf, km = mi["rf"], mi["km"]
    pct = lambda v: "-" if v is None else f"{v * 100:.1f}%"
    num = lambda v: "-" if v is None else f"{v:.3f}"
    note = [_p("7. Catatan Model dan Batasan", S["h2"]),
            _p(f"<b>Random Forest</b> (data uji): akurasi {pct(rf['accuracy'])}, AUC-ROC {num(rf['auc'])}, "
               f"presisi {pct(rf['precision'])}, recall {pct(rf['recall'])}, F1 {pct(rf['f1'])}. "
               f"<b>K-Means</b>: silhouette {num(km['silhouette'])}, Davies-Bouldin {num(km['davies_bouldin'])}.", S["body"]),
            Spacer(1, 3),
            _p("Recall yang belum tinggi berarti sebagian kegagalan nyata dapat tidak terdeteksi oleh model. "
               "Hasil ini merupakan alat bantu pengambilan keputusan dan sebaiknya dikombinasikan dengan inspeksi lapangan "
               "serta penilaian teknisi. Model dilatih pada dataset AI4I 2020 (data sintetis) sehingga belum merepresentasikan "
               "kondisi mesin spesifik di lapangan.", S["small"])]
    el.append(KeepTogether(note))

    doc.build(el)
    return buf.getvalue()