from flask import render_template, request, flash, redirect, url_for, Response
from flask_login import login_required, current_user
from src.database import get_db
from src.utils.auditoria import get_audit_logs, log_action
from psycopg2.extras import RealDictCursor
from functools import wraps
import io
from datetime import datetime


def auditor_required(f):
    """Decorator para verificar que el usuario sea auditor (rol 4) o administrador (rol 2)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if current_user.id_rol not in [2, 4]:
            flash('No tienes permisos para acceder a esta sección', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@login_required
@auditor_required
def panel_auditor():
    """Panel principal del auditor"""
    log_action("Acceso al panel de auditoría")
    return render_template('auditor/panel.html')


@login_required
@auditor_required
def ver_auditoria():
    """Ver registros de auditoría"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    logs = get_audit_logs(limit=per_page * page)
    
    log_action("Consulta de registros de auditoría")
    return render_template('auditor/auditoria.html', logs=logs)


@login_required
@auditor_required
def reportes_donaciones():
    """Ver reportes de donaciones (solo lectura)"""
    db = None
    try:
        db = get_db()
        if db is None:
            flash('Error de conexión a la base de datos', 'danger')
            return redirect(url_for('panel_auditor'))
        
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        sql = """
            SELECT d.id_donacion, d.monto, d.fecha_donacion,
                   u.nombre as donador_nombre, u.fullname as donador_fullname,
                   p.nombre as proyecto_nombre
            FROM donaciones d
            JOIN usuarios u ON d.id_usuario = u.id
            JOIN proyectos p ON d.id_proyecto = p.id_proyecto
            ORDER BY d.fecha_donacion DESC
        """
        cursor.execute(sql)
        donaciones = cursor.fetchall()
        
        sql_totales = """
            SELECT 
                COUNT(*) as total_donaciones,
                COALESCE(SUM(monto), 0) as monto_total
            FROM donaciones
        """
        cursor.execute(sql_totales)
        totales = cursor.fetchone()
        
        cursor.close()
        
        log_action("Consulta de reportes de donaciones")
        return render_template('auditor/reportes-donaciones.html', 
                             donaciones=donaciones, totales=totales)
    except Exception as ex:
        print(f"Error en reportes_donaciones: {ex}")
        flash('Error al obtener los reportes', 'danger')
        return redirect(url_for('panel_auditor'))
    finally:
        if db:
            db.close()


@login_required
@auditor_required
def reportes_gastos():
    """Ver reportes de gastos (solo lectura)"""
    db = None
    try:
        db = get_db()
        if db is None:
            flash('Error de conexión a la base de datos', 'danger')
            return redirect(url_for('panel_auditor'))
        
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        sql = """
            SELECT g.id_gasto, g.categoria, g.descripcion, g.monto, g.fecha_gasto,
                   u.nombre as usuario_nombre, u.fullname as usuario_fullname,
                   p.nombre as proyecto_nombre
            FROM gastos g
            JOIN usuarios u ON g.id_usuario = u.id
            JOIN proyectos p ON g.id_proyecto = p.id_proyecto
            ORDER BY g.fecha_gasto DESC
        """
        cursor.execute(sql)
        gastos = cursor.fetchall()
        
        sql_totales = """
            SELECT 
                COUNT(*) as total_gastos,
                COALESCE(SUM(monto), 0) as monto_total
            FROM gastos
        """
        cursor.execute(sql_totales)
        totales = cursor.fetchone()
        
        cursor.close()
        
        log_action("Consulta de reportes de gastos")
        return render_template('auditor/reportes-gastos.html', 
                             gastos=gastos, totales=totales)
    except Exception as ex:
        print(f"Error en reportes_gastos: {ex}")
        flash('Error al obtener los reportes', 'danger')
        return redirect(url_for('panel_auditor'))
    finally:
        if db:
            db.close()


@login_required
@auditor_required
def exportar_donaciones_excel():
    """Exportar donaciones a Excel"""
    import pandas as pd
    
    db = None
    try:
        db = get_db()
        if db is None:
            flash('Error de conexión a la base de datos', 'danger')
            return redirect(url_for('reportes_donaciones'))
        
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        sql = """
            SELECT d.id_donacion as "ID", 
                   u.fullname as "Donador",
                   u.correo as "Correo",
                   p.nombre as "Proyecto",
                   d.monto as "Monto",
                   d.fecha_donacion as "Fecha"
            FROM donaciones d
            JOIN usuarios u ON d.id_usuario = u.id
            JOIN proyectos p ON d.id_proyecto = p.id_proyecto
            ORDER BY d.fecha_donacion DESC
        """
        cursor.execute(sql)
        donaciones = cursor.fetchall()
        cursor.close()
        
        df = pd.DataFrame(donaciones)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Donaciones', index=False)
        output.seek(0)
        
        log_action("Exportación de donaciones a Excel")
        
        filename = f"donaciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return Response(
            output.getvalue(),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as ex:
        print(f"Error en exportar_donaciones_excel: {ex}")
        flash('Error al exportar los datos', 'danger')
        return redirect(url_for('reportes_donaciones'))
    finally:
        if db:
            db.close()


@login_required
@auditor_required
def exportar_gastos_excel():
    """Exportar gastos a Excel"""
    import pandas as pd
    
    db = None
    try:
        db = get_db()
        if db is None:
            flash('Error de conexión a la base de datos', 'danger')
            return redirect(url_for('reportes_gastos'))
        
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        sql = """
            SELECT g.id_gasto as "ID",
                   p.nombre as "Proyecto",
                   g.categoria as "Categoría",
                   g.descripcion as "Descripción",
                   g.monto as "Monto",
                   g.fecha_gasto as "Fecha",
                   u.fullname as "Registrado por"
            FROM gastos g
            JOIN usuarios u ON g.id_usuario = u.id
            JOIN proyectos p ON g.id_proyecto = p.id_proyecto
            ORDER BY g.fecha_gasto DESC
        """
        cursor.execute(sql)
        gastos = cursor.fetchall()
        cursor.close()
        
        df = pd.DataFrame(gastos)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Gastos', index=False)
        output.seek(0)
        
        log_action("Exportación de gastos a Excel")
        
        filename = f"gastos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return Response(
            output.getvalue(),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as ex:
        print(f"Error en exportar_gastos_excel: {ex}")
        flash('Error al exportar los datos', 'danger')
        return redirect(url_for('reportes_gastos'))
    finally:
        if db:
            db.close()


@login_required
@auditor_required
def exportar_donaciones_pdf():
    """Exportar donaciones a PDF"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    
    db = None
    try:
        db = get_db()
        if db is None:
            flash('Error de conexión a la base de datos', 'danger')
            return redirect(url_for('reportes_donaciones'))
        
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        sql = """
            SELECT d.id_donacion, u.fullname, p.nombre, d.monto, d.fecha_donacion
            FROM donaciones d
            JOIN usuarios u ON d.id_usuario = u.id
            JOIN proyectos p ON d.id_proyecto = p.id_proyecto
            ORDER BY d.fecha_donacion DESC
        """
        cursor.execute(sql)
        donaciones = cursor.fetchall()
        
        sql_totales = """
            SELECT COUNT(*) as total, COALESCE(SUM(monto), 0) as monto_total
            FROM donaciones
        """
        cursor.execute(sql_totales)
        totales = cursor.fetchone()
        cursor.close()
        
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=landscape(letter))
        elements = []
        
        styles = getSampleStyleSheet()
        elements.append(Paragraph("Reporte de Donaciones", styles['Heading1']))
        elements.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        data = [['ID', 'Donador', 'Proyecto', 'Monto', 'Fecha']]
        for d in donaciones:
            data.append([
                str(d['id_donacion']),
                d['fullname'][:30] if d['fullname'] else '',
                d['nombre'][:30] if d['nombre'] else '',
                f"${d['monto']:,.2f}",
                d['fecha_donacion'].strftime('%d/%m/%Y') if d['fecha_donacion'] else ''
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"Total de donaciones: {totales['total']}", styles['Normal']))
        elements.append(Paragraph(f"Monto total: ${totales['monto_total']:,.2f}", styles['Normal']))
        
        doc.build(elements)
        output.seek(0)
        
        log_action("Exportación de donaciones a PDF")
        
        filename = f"donaciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return Response(
            output.getvalue(),
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as ex:
        print(f"Error en exportar_donaciones_pdf: {ex}")
        flash('Error al exportar los datos', 'danger')
        return redirect(url_for('reportes_donaciones'))
    finally:
        if db:
            db.close()


@login_required
@auditor_required
def exportar_gastos_pdf():
    """Exportar gastos a PDF"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    
    db = None
    try:
        db = get_db()
        if db is None:
            flash('Error de conexión a la base de datos', 'danger')
            return redirect(url_for('reportes_gastos'))
        
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        sql = """
            SELECT g.id_gasto, p.nombre as proyecto, g.categoria, g.monto, g.fecha_gasto
            FROM gastos g
            JOIN proyectos p ON g.id_proyecto = p.id_proyecto
            ORDER BY g.fecha_gasto DESC
        """
        cursor.execute(sql)
        gastos = cursor.fetchall()
        
        sql_totales = """
            SELECT COUNT(*) as total, COALESCE(SUM(monto), 0) as monto_total
            FROM gastos
        """
        cursor.execute(sql_totales)
        totales = cursor.fetchone()
        cursor.close()
        
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=landscape(letter))
        elements = []
        
        styles = getSampleStyleSheet()
        elements.append(Paragraph("Reporte de Gastos", styles['Heading1']))
        elements.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        data = [['ID', 'Proyecto', 'Categoría', 'Monto', 'Fecha']]
        for g in gastos:
            data.append([
                str(g['id_gasto']),
                g['proyecto'][:30] if g['proyecto'] else '',
                g['categoria'][:20] if g['categoria'] else '',
                f"${g['monto']:,.2f}",
                g['fecha_gasto'].strftime('%d/%m/%Y') if g['fecha_gasto'] else ''
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"Total de gastos: {totales['total']}", styles['Normal']))
        elements.append(Paragraph(f"Monto total: ${totales['monto_total']:,.2f}", styles['Normal']))
        
        doc.build(elements)
        output.seek(0)
        
        log_action("Exportación de gastos a PDF")
        
        filename = f"gastos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return Response(
            output.getvalue(),
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as ex:
        print(f"Error en exportar_gastos_pdf: {ex}")
        flash('Error al exportar los datos', 'danger')
        return redirect(url_for('reportes_gastos'))
    finally:
        if db:
            db.close()


@login_required
@auditor_required
def exportar_auditoria_excel():
    """Exportar registros de auditoría a Excel"""
    import pandas as pd
    
    logs = get_audit_logs(limit=1000)
    
    data = []
    for log in logs:
        data.append({
            'ID': log['id'],
            'Usuario': log['usuario_fullname'],
            'Acción': log['accion'],
            'Fecha': log['fecha']
        })
    
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Auditoría', index=False)
    output.seek(0)
    
    log_action("Exportación de auditoría a Excel")
    
    filename = f"auditoria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return Response(
        output.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )
