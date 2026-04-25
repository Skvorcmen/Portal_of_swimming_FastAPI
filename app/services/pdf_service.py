from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from io import BytesIO
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Competition, Heat, HeatEntry, SwimEvent, Entry, AthleteProfile, User


class PDFService:
    
    @staticmethod
    async def generate_start_list(competition_id: int, session: AsyncSession) -> BytesIO:
        """Генерация предстартового протокола"""
        # Получаем все заплывы через SwimEvent
        result = await session.execute(
            select(Heat)
            .join(SwimEvent, Heat.swim_event_id == SwimEvent.id)
            .where(SwimEvent.competition_id == competition_id)
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
        elements.append(Paragraph("Предстартовый протокол", title_style))
        elements.append(Spacer(1, 20))

        for heat in heats:
            # Получаем информацию о дистанции
            event_result = await session.execute(
                select(SwimEvent).where(SwimEvent.id == heat.swim_event_id)
            )
            event = event_result.scalar_one()
            
            heat_style = ParagraphStyle(
                "HeatTitle", parent=styles["Heading2"], fontSize=12, spaceAfter=10
            )
            elements.append(Paragraph(f"Заплыв №{heat.heat_number} - {event.distance}м {event.stroke}", heat_style))
            
            # Получаем участников заплыва
            entries_result = await session.execute(
                select(HeatEntry, Entry, AthleteProfile, User)
                .join(Entry, HeatEntry.entry_id == Entry.id)
                .join(AthleteProfile, Entry.athlete_id == AthleteProfile.id)
                .join(User, AthleteProfile.user_id == User.id)
                .where(HeatEntry.heat_id == heat.id)
                .order_by(HeatEntry.lane)
            )
            heat_entries = entries_result.all()
            
            if heat_entries:
                data = [["Дорожка", "Спортсмен", "Результат"]]
                for he, entry, athlete, user in heat_entries:
                    data.append([
                        str(he.lane),
                        user.full_name,
                        str(entry.entry_time) if entry.entry_time else "-"
                    ])
                
                table = Table(data, colWidths=[3*cm, 8*cm, 4*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)
            else:
                elements.append(Paragraph("Нет участников", styles["Normal"]))
            
            elements.append(Spacer(1, 20))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    @staticmethod
    async def generate_results_protocol(competition_id: int, session: AsyncSession) -> BytesIO:
        """Генерация итогового протокола"""
        # Получаем все заплывы
        result = await session.execute(
            select(Heat)
            .join(SwimEvent, Heat.swim_event_id == SwimEvent.id)
            .where(SwimEvent.competition_id == competition_id)
            .order_by(Heat.heat_number)
        )
        heats = result.scalars().all()

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        elements = []

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
            event_result = await session.execute(
                select(SwimEvent).where(SwimEvent.id == heat.swim_event_id)
            )
            event = event_result.scalar_one()
            
            heat_style = ParagraphStyle(
                "HeatTitle", parent=styles["Heading2"], fontSize=12, spaceAfter=10
            )
            elements.append(Paragraph(f"Заплыв №{heat.heat_number} - {event.distance}м {event.stroke} (результаты)", heat_style))
            
            # Получаем участников с результатами
            entries_result = await session.execute(
                select(HeatEntry, Entry, AthleteProfile, User)
                .join(Entry, HeatEntry.entry_id == Entry.id)
                .join(AthleteProfile, Entry.athlete_id == AthleteProfile.id)
                .join(User, AthleteProfile.user_id == User.id)
                .where(HeatEntry.heat_id == heat.id)
                .order_by(HeatEntry.place)
            )
            heat_entries = entries_result.all()
            
            if heat_entries:
                data = [["Место", "Дорожка", "Спортсмен", "Результат"]]
                for he, entry, athlete, user in heat_entries:
                    data.append([
                        str(he.place) if he.place else "-",
                        str(he.lane),
                        user.full_name,
                        f"{he.result_time:.2f}" if he.result_time else "-"
                    ])
                
                table = Table(data, colWidths=[2*cm, 2.5*cm, 8*cm, 3*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)
            else:
                elements.append(Paragraph("Нет результатов", styles["Normal"]))
            
            elements.append(Spacer(1, 20))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    @staticmethod
    async def generate_competition_rules(competition_id: int, session: AsyncSession) -> BytesIO:
        """Генерация положения о соревновании"""
        result = await session.execute(
            select(Competition).where(Competition.id == competition_id)
        )
        competition = result.scalar_one_or_none()

        if not competition:
            raise ValueError("Competition not found")

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        elements = []

        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=16,
            alignment=1,
            spaceAfter=30,
        )
        elements.append(Paragraph("ПОЛОЖЕНИЕ О СОРЕВНОВАНИИ", title_style))
        elements.append(Spacer(1, 20))

        elements.append(Paragraph(f"<b>1. Общие положения</b>", styles["Heading2"]))
        elements.append(Paragraph(f"1.1. {competition.name}", styles["Normal"]))
        elements.append(Spacer(1, 10))
        
        elements.append(Paragraph(f"<b>2. Сроки и место проведения</b>", styles["Heading2"]))
        elements.append(Paragraph(f"2.1. Дата проведения: {competition.start_date.strftime('%d.%m.%Y')} - {competition.end_date.strftime('%d.%m.%Y')}", styles["Normal"]))
        elements.append(Paragraph(f"2.2. Место проведения: {competition.venue or 'Не указано'}, {competition.city or 'Не указан'}", styles["Normal"]))
        elements.append(Spacer(1, 10))
        
        elements.append(Paragraph(f"<b>3. Участники</b>", styles["Heading2"]))
        elements.append(Paragraph(f"3.1. Максимальное количество участников: {competition.max_participants or 'Не ограничено'}", styles["Normal"]))

        doc.build(elements)
        buffer.seek(0)
        return buffer
