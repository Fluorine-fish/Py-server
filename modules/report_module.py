from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from fpdf import FPDF
import os

class ReportGenerator:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.report_path = "static/reports"
        os.makedirs(self.report_path, exist_ok=True)
        
    def generate_daily_report(self, date=None):
        """生成每日报告"""
        if date is None:
            date = datetime.now()
        
        start_time = datetime.combine(date.date(), datetime.min.time())
        end_time = start_time + timedelta(days=1)
        
        # 获取各项统计数据
        posture_stats = self.db_manager.get_posture_stats(start_time, end_time)
        emotion_stats = self.db_manager.get_emotion_stats(start_time, end_time)
        focus_stats = self.db_manager.get_focus_stats(start_time, end_time)
        eyesight_stats = self.db_manager.get_eyesight_stats(start_time, end_time)
        
        # 创建PDF报告
        pdf = FPDF()
        pdf.add_page()
        
        # 报告标题
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f'每日健康报告 - {date.strftime("%Y-%m-%d")}', ln=True, align='C')
        
        # 姿势分析部分
        self._add_posture_section(pdf, posture_stats)
        
        # 情绪分析部分
        self._add_emotion_section(pdf, emotion_stats)
        
        # 专注度分析部分
        self._add_focus_section(pdf, focus_stats)
        
        # 用眼健康部分
        self._add_eyesight_section(pdf, eyesight_stats)
        
        # 保存报告
        filename = f'daily_report_{date.strftime("%Y%m%d")}.pdf'
        filepath = os.path.join(self.report_path, filename)
        pdf.output(filepath)
        
        return filepath
        
    def generate_weekly_report(self, date=None):
        """生成周报告"""
        if date is None:
            date = datetime.now()
            
        # 计算本周开始和结束时间
        start_time = date - timedelta(days=date.weekday())
        start_time = datetime.combine(start_time.date(), datetime.min.time())
        end_time = start_time + timedelta(days=7)
        
        # 获取统计数据
        posture_stats = self.db_manager.get_posture_stats(start_time, end_time)
        emotion_stats = self.db_manager.get_emotion_stats(start_time, end_time)
        focus_stats = self.db_manager.get_focus_stats(start_time, end_time)
        eyesight_stats = self.db_manager.get_eyesight_stats(start_time, end_time)
        
        # 创建PDF报告
        pdf = FPDF()
        pdf.add_page()
        
        # 报告标题
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f'周健康报告 - {start_time.strftime("%Y-%m-%d")} 至 {end_time.strftime("%Y-%m-%d")}', ln=True, align='C')
        
        # 添加各部分内容
        self._add_posture_section(pdf, posture_stats, is_weekly=True)
        self._add_emotion_section(pdf, emotion_stats, is_weekly=True)
        self._add_focus_section(pdf, focus_stats, is_weekly=True)
        self._add_eyesight_section(pdf, eyesight_stats, is_weekly=True)
        
        # 保存报告
        filename = f'weekly_report_{start_time.strftime("%Y%m%d")}.pdf'
        filepath = os.path.join(self.report_path, filename)
        pdf.output(filepath)
        
        return filepath
        
    def _add_posture_section(self, pdf, stats, is_weekly=False):
        """添加姿势分析部分"""
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, '姿势分析', ln=True)
        
        pdf.set_font('Arial', '', 12)
        
        # 添加统计数据
        if stats and 'stats' in stats:
            s = stats['stats']
            pdf.cell(0, 10, f'平均头部角度: {s["avg_angle"]:.1f}°', ln=True)
            pdf.cell(0, 10, f'良好姿势时长: {self._format_duration(s["good_duration"])}', ln=True)
            pdf.cell(0, 10, f'不良姿势时长: {self._format_duration(s["bad_duration"])}', ln=True)
            pdf.cell(0, 10, f'遮挡时长: {self._format_duration(s["occluded_duration"])}', ln=True)
        
        # 添加趋势图
        if stats and 'trends' in stats:
            plt.figure(figsize=(10, 6))
            trends = stats['trends']
            hours = [t['hour'] for t in trends]
            angles = [t['avg_angle'] for t in trends]
            plt.plot(hours, angles)
            plt.title('头部角度变化趋势')
            plt.xlabel('时间')
            plt.ylabel('角度')
            
            # 将图保存为base64字符串
            img_buf = BytesIO()
            plt.savefig(img_buf, format='png')
            img_buf.seek(0)
            plt.close()
            
            # 添加图片到PDF
            pdf.image(img_buf, x=10, y=None, w=190)
            
    def _add_emotion_section(self, pdf, stats, is_weekly=False):
        """添加情绪分析部分"""
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, '情绪分析', ln=True)
        
        pdf.set_font('Arial', '', 12)
        
        if stats and 'distribution' in stats:
            # 创建情绪分布饼图
            plt.figure(figsize=(8, 8))
            dist = stats['distribution']
            labels = [d['emotion_type'] for d in dist]
            values = [d['count'] for d in dist]
            plt.pie(values, labels=labels, autopct='%1.1f%%')
            plt.title('情绪分布')
            
            # 保存图片
            img_buf = BytesIO()
            plt.savefig(img_buf, format='png')
            img_buf.seek(0)
            plt.close()
            
            # 添加图片到PDF
            pdf.image(img_buf, x=10, y=None, w=190)
            
        if stats and 'trends' in stats:
            # 添加情绪变化趋势
            pdf.cell(0, 10, '\n情绪变化趋势:', ln=True)
            for trend in stats['trends'][:5]:  # 只显示最近5条记录
                pdf.cell(0, 10, f"{trend['hour']}: {trend['emotion_type']} ({trend['count']}次)", ln=True)
                
    def _add_focus_section(self, pdf, stats, is_weekly=False):
        """添加专注度分析部分"""
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, '专注度分析', ln=True)
        
        if stats:
            # 创建专注度趋势图
            plt.figure(figsize=(10, 6))
            times = [s.timestamp for s in stats]
            scores = [s.focus_score for s in stats]
            plt.plot(times, scores)
            plt.title('专注度变化趋势')
            plt.xlabel('时间')
            plt.ylabel('专注度')
            
            # 保存图片
            img_buf = BytesIO()
            plt.savefig(img_buf, format='png')
            img_buf.seek(0)
            plt.close()
            
            # 添加图片到PDF
            pdf.image(img_buf, x=10, y=None, w=190)
            
            # 添加统计数据
            pdf.set_font('Arial', '', 12)
            avg_score = sum(scores) / len(scores) if scores else 0
            max_score = max(scores) if scores else 0
            min_score = min(scores) if scores else 0
            
            pdf.cell(0, 10, f'平均专注度: {avg_score:.1f}', ln=True)
            pdf.cell(0, 10, f'最高专注度: {max_score:.1f}', ln=True)
            pdf.cell(0, 10, f'最低专注度: {min_score:.1f}', ln=True)
            
    def _add_eyesight_section(self, pdf, stats, is_weekly=False):
        """添加用眼健康分析部分"""
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, '用眼健康分析', ln=True)
        
        if stats:
            pdf.set_font('Arial', '', 12)
            
            # 计算平均值
            avg_distance = sum(s.screen_distance for s in stats) / len(stats) if stats else 0
            avg_light = sum(s.ambient_light for s in stats) / len(stats) if stats else 0
            avg_blink = sum(s.blink_rate for s in stats) / len(stats) if stats else 0
            total_warnings = sum(s.warning_count for s in stats)
            
            pdf.cell(0, 10, f'平均观看距离: {avg_distance:.1f} cm', ln=True)
            pdf.cell(0, 10, f'平均环境光照: {avg_light:.1f} lux', ln=True)
            pdf.cell(0, 10, f'平均眨眼频率: {avg_blink:.1f} 次/分钟', ln=True)
            pdf.cell(0, 10, f'健康提醒次数: {total_warnings}', ln=True)
            
            # 创建用眼时间分布图
            if is_weekly:
                plt.figure(figsize=(10, 6))
                dates = [s.timestamp.date() for s in stats]
                durations = [s.usage_duration / 3600 for s in stats]  # 转换为小时
                plt.bar(dates, durations)
                plt.title('每日用眼时间分布')
                plt.xlabel('日期')
                plt.ylabel('用眼时间(小时)')
                
                # 保存图片
                img_buf = BytesIO()
                plt.savefig(img_buf, format='png')
                img_buf.seek(0)
                plt.close()
                
                # 添加图片到PDF
                pdf.image(img_buf, x=10, y=None, w=190)
                
    def _format_duration(self, seconds):
        """格式化持续时间"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}小时{minutes}分钟"