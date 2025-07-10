import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from typing import Dict, List
from datetime import datetime
import tempfile

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2E86AB')
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#A23B72')
        )
    
    def generate_report(self, clusters: Dict[int, List[str]], summaries: Dict[int, str], 
                       sentiments: Dict[int, Dict] = None, filename: str = None) -> str:
        """Generate a comprehensive PDF report from clustering results."""
        
        if filename is None:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            filename = temp_file.name
            temp_file.close()
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # Title
        title = Paragraph("SurveyGPT-AI Analysis Report", self.title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Metadata
        date_str = datetime.now().strftime("%B %d, %Y")
        metadata = f"Generated on: {date_str}<br/>Total Responses: {sum(len(texts) for texts in clusters.values())}<br/>Clusters Found: {len(clusters)}"
        story.append(Paragraph(metadata, self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.heading_style))
        exec_summary = f"""This report analyzes {sum(len(texts) for texts in clusters.values())} survey responses, 
        automatically grouped into {len(clusters)} distinct clusters using AI-powered clustering algorithms. 
        Each cluster represents a common theme or pattern in the feedback."""
        story.append(Paragraph(exec_summary, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Cluster Analysis
        for cluster_id, texts in clusters.items():
            if cluster_id == -1:  # Skip noise cluster from HDBSCAN
                continue
                
            story.append(Paragraph(f"Cluster {cluster_id + 1}", self.heading_style))
            
            # Cluster metadata
            cluster_info = f"Responses in cluster: {len(texts)}"
            if sentiments and cluster_id in sentiments:
                sentiment_data = sentiments[cluster_id]
                cluster_info += f"<br/>Sentiment: {sentiment_data.get('sentiment', 'N/A').title()}"
                cluster_info += f"<br/>Confidence: {sentiment_data.get('confidence', 0):.2f}"
            
            story.append(Paragraph(cluster_info, self.styles['Normal']))
            story.append(Spacer(1, 10))
            
            # Summary
            if cluster_id in summaries:
                story.append(Paragraph("Summary:", self.styles['Heading4']))
                story.append(Paragraph(summaries[cluster_id], self.styles['Normal']))
                story.append(Spacer(1, 15))
            
            # Sample responses
            story.append(Paragraph("Sample Responses:", self.styles['Heading4']))
            sample_texts = texts[:5]  # Show first 5 responses
            for i, text in enumerate(sample_texts, 1):
                story.append(Paragraph(f"{i}. {text}", self.styles['Normal']))
                story.append(Spacer(1, 5))
            
            if len(texts) > 5:
                story.append(Paragraph(f"... and {len(texts) - 5} more responses", self.styles['Italic']))
            
            story.append(Spacer(1, 25))
        
        # Build PDF
        doc.build(story)
        return filename
    
    def generate_summary_table(self, clusters: Dict[int, List[str]], 
                             summaries: Dict[int, str]) -> Table:
        """Generate a summary table for the report."""
        data = [['Cluster', 'Responses', 'Key Themes']]
        
        for cluster_id, texts in clusters.items():
            if cluster_id == -1:  # Skip noise cluster
                continue
            summary = summaries.get(cluster_id, 'No summary available')[:100] + '...'
            data.append([f'Cluster {cluster_id + 1}', str(len(texts)), summary])
        
        table = Table(data, colWidths=[1*inch, 1*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table