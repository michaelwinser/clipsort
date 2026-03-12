"""QR code generation for clapper boards."""

from __future__ import annotations

import json
from pathlib import Path


class QRGenerator:
    """Generate QR codes encoding scene/take metadata."""

    def generate_data(self, scene: int, take: int, project: str | None = None) -> str:
        """Build a JSON payload for a QR code.

        Args:
            scene: Scene number.
            take: Take number.
            project: Optional project name.

        Returns:
            JSON string with schema ``{"v":1, "scene":N, "take":N}``.
        """
        data: dict = {"v": 1, "scene": scene, "take": take}
        if project is not None:
            data["project"] = project
        return json.dumps(data)

    @staticmethod
    def _build_label(scene: int, take: int, project: str | None = None) -> str:
        """Build a human-readable label like 'Scene 1 Take 2' or 'MyFilm — Scene 1 Take 2'."""
        label = f"Scene {scene} Take {take}"
        if project:
            label = f"{project} — {label}"
        return label

    def generate_single(
        self,
        scene: int,
        take: int,
        project: str | None = None,
        output_path: Path | str = "qr.png",
    ) -> Path:
        """Generate a single QR code PNG with a human-readable label.

        Args:
            scene: Scene number.
            take: Take number.
            project: Optional project name.
            output_path: Where to write the PNG file.

        Returns:
            Path to the generated PNG file.
        """
        import qrcode
        from PIL import Image, ImageDraw, ImageFont

        data = self.generate_data(scene, take, project)
        qr_img = qrcode.make(data).convert("RGB")
        qr_w, qr_h = qr_img.size

        # Build the label text
        label = self._build_label(scene, take, project)

        # Use default font; size the label bar proportionally
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", size=max(qr_h // 12, 14))
        except OSError:
            font = ImageFont.load_default()

        # Measure text
        draw_tmp = ImageDraw.Draw(qr_img)
        bbox = draw_tmp.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        padding = max(text_h // 2, 6)
        label_bar_h = text_h + padding * 2

        # Composite: QR on top, white label bar on bottom
        canvas = Image.new("RGB", (qr_w, qr_h + label_bar_h), "white")
        canvas.paste(qr_img, (0, 0))
        draw = ImageDraw.Draw(canvas)
        text_x = (qr_w - text_w) // 2
        text_y = qr_h + padding
        draw.text((text_x, text_y), label, fill="black", font=font)

        output_path = Path(output_path)
        canvas.save(str(output_path))
        return output_path

    def generate_sheet(
        self,
        scenes: int,
        takes: int,
        project: str | None = None,
        output_path: Path | str = "qr_sheet.pdf",
    ) -> Path:
        """Generate a printable PDF sheet of QR codes.

        Creates a grid of QR codes, one for each scene/take combination.

        Args:
            scenes: Number of scenes (1..scenes).
            takes: Number of takes per scene (1..takes).
            project: Optional project name.
            output_path: Where to write the PDF file.

        Returns:
            Path to the generated PDF file.
        """
        import qrcode
        from fpdf import FPDF

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", size=10)

        qr_size = 40  # mm
        margin = 10
        x = margin
        y = margin + 10  # leave room for header

        for scene in range(1, scenes + 1):
            for take in range(1, takes + 1):
                # Check if we need a new row
                if x + qr_size > pdf.w - margin:
                    x = margin
                    y += qr_size + 15

                # Check if we need a new page
                if y + qr_size > pdf.h - margin:
                    pdf.add_page()
                    x = margin
                    y = margin + 10

                # Generate QR image to a temp file
                data = self.generate_data(scene, take, project)
                img = qrcode.make(data)

                import tempfile

                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    img.save(tmp.name)
                    pdf.image(tmp.name, x=x, y=y, w=qr_size, h=qr_size)
                    Path(tmp.name).unlink()

                # Label below the QR
                label = self._build_label(scene, take, project)
                pdf.set_xy(x, y + qr_size)
                pdf.cell(qr_size, 5, label, align="C")

                x += qr_size + 5

        output_path = Path(output_path)
        pdf.output(str(output_path))
        return output_path
