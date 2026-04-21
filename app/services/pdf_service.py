from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from io import BytesIO
from datetime import datetime
from app.models import Competition, Heat, HeatEntry


class PDFService:
    @staticmethod
    async def generate_start_list(competition_id: int, session) -> BytesIO:
        """Генерация предстартового протокола"""
        # Получаем данные
        result = await session.execute(
            select(Heat)
            .where(Heat.competition_id == competition_id)
            .order_by(Heat.heat_number)
        )
        heats = result.scalars().all()

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm
        )
        styles = getSampleStyleSheet()
        elements = []

        # Заголовок
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=16,
            alignment=1,  # Center
            spaceAfter=30,
        )
        elements.append(Paragraph("Предстартовый протокол", title_style))
        elements.append(Spacer(1, 20))

        # Данные для каждого заплыва
        for heat in heats:
            heat_style = ParagraphStyle(
                "HeatTitle", parent=styles["Heading2"], fontSize=12, spaceAfter=10
            )
            elements.append(Paragraph(f"Заплыв №{heat.heat_number}", heat_style))

            # Получаем участников
            entries_result = await session.execute(
                select(HeatEntry)
                .where(HeatEntry.heat_id == heat.id)
                .order_by(HeatEntry.lane)
            )
            entries = entries_result.scalars().all()

            # Таблица
            data = [["Дорожка", "Спортсмен", "Время"]]
            for entry in entries:
                athlete_name = (
                    entry.entry.athlete.user.full_name if entry.entry.athlete else "N/A"
                )
                data.append(
                    [str(entry.lane), athlete_name, entry.entry.entry_time or "-"]
                )

            table = Table(data, colWidths=[3 * cm, 8 * cm, 4 * cm])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            elements.append(table)
            elements.append(Spacer(1, 20))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    @staticmethod
    async def generate_results_protocol(competition_id: int, session) -> BytesIO:
        """Генерация итогового протокола"""
        # Получаем завершённые заплывы
        result = await session.execute(
            select(Heat)
            .where(Heat.competition_id == competition_id, Heat.status == "completed")
            .order_by(Heat.heat_number)
        )
        heats = result.scalars().all()

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm
        )
        styles = getSampleStyleSheet()
        elements = []

        # Заголовок
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=16,
            alignment=1,
            spaceAfter=30,
        )
        elements.append(Paragraph("Итоговый протокол соревнований", title_style))
        elements.append(Spacer(1, 20))

        for heat in heats:
            heat_style = ParagraphStyle(
                "HeatTitle", parent=styles["Heading2"], fontSize=12, spaceAfter=10
            )
            elements.append(
                Paragraph(f"Заплыв №{heat.heat_number} (результаты)", heat_style)
            )

            entries_result = await session.execute(
                select(HeatEntry)
                .where(HeatEntry.heat_id == heat.id)
                .order_by(HeatEntry.place)
            )
            entries = entries_result.scalars().all()

            data = [["Место", "Дорожка", "Спортсмен", "Результат"]]
            for entry in entries:
                athlete_name = (
                    entry.entry.athlete.user.full_name if entry.entry.athlete else "N/A"
                )
                result_time = f"{entry.result_time:.2f}" if entry.result_time else "-"
                data.append(
                    [
                        str(entry.place or "-"),
                        str(entry.lane),
                        athlete_name,
                        result_time,
                    ]
                )

            table = Table(data, colWidths=[2 * cm, 2.5 * cm, 8 * cm, 3 * cm])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            elements.append(table)
            elements.append(Spacer(1, 20))

        doc.build(elements)
        buffer.seek(0)
        return buffer
