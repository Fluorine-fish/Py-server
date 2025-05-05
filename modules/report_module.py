from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from fpdf import FPDF
import os
from typing import Dict, Any, Optional
from .logging_module import log_manager

class ReportGenerator:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.report_path = "static/reports"
        os.makedirs(self.report_path, exist_ok=True)
        
        # 中文字体支持
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
    
    def validate_data(self, stats: Dict[str, Any], required_fields: list) -> tuple[bool, list]:
        """验证数据完整性
        
        Args:
            stats: 需要验证的统计数据
            required_fields: 必需的字段列表
            
        Returns:
            tuple: (是否验证通过, 缺失字段列表)
        """
        missing_fields = []
        if not stats:
            return False, required_fields
            
        for field in required_fields:
            if field not in stats or stats[field] is None:
                missing_fields.append(field)
                
        return len(missing_fields) == 0, missing_fields
    
    def validate_posture_stats(self, stats: Dict[str, Any]) -> bool:
        """验证姿势统计数据完整性"""
        required_fields = [
            'stats',
            'trends',
            'common_issues'
        ]
        
        is_valid, missing_fields = self.validate_data(stats, required_fields)
        if not is_valid:
            log_manager.log_system_event(
                'data_validation',
                f'姿势数据不完整，缺失字段: {", ".join(missing_fields)}',
                'warning'
            )
            return False
            
        # 验证统计数据字段
        if 'stats' in stats:
            stat_fields = [
                'avg_head_angle',
                'avg_neck_angle',
                'avg_shoulder_tilt',
                'avg_spine_angle',
                'avg_score',
                'good_duration',
                'slightly_bad_duration',
                'bad_duration',
                'severe_duration',
                'occluded_duration'
            ]
            is_valid, missing_fields = self.validate_data(stats['stats'], stat_fields)
            if not is_valid:
                log_manager.log_system_event(
                    'data_validation',
                    f'姿势统计数据不完整，缺失字段: {", ".join(missing_fields)}',
                    'warning'
                )
                return False
                
        return True
    
    def validate_emotion_stats(self, stats: Dict[str, Any]) -> bool:
        """验证情绪统计数据完整性"""
        required_fields = ['distribution', 'trends']
        is_valid, missing_fields = self.validate_data(stats, required_fields)
        if not is_valid:
            log_manager.log_system_event(
                'data_validation',
                f'情绪数据不完整，缺失字段: {", ".join(missing_fields)}',
                'warning'
            )
        return is_valid
    
    def validate_focus_stats(self, stats: list) -> bool:
        """验证专注度统计数据完整性"""
        if not stats:
            log_manager.log_system_event(
                'data_validation',
                '专注度数据为空',
                'warning'
            )
            return False
            
        required_fields = ['timestamp', 'focus_score']
        for record in stats:
            is_valid, missing_fields = self.validate_data(vars(record), required_fields)
            if not is_valid:
                log_manager.log_system_event(
                    'data_validation',
                    f'专注度数据记录不完整，缺失字段: {", ".join(missing_fields)}',
                    'warning'
                )
                return False
        return True
    
    def validate_eyesight_stats(self, stats: list) -> bool:
        """验证用眼健康统计数据完整性"""
        if not stats:
            log_manager.log_system_event(
                'data_validation',
                '用眼健康数据为空',
                'warning'
            )
            return False
            
        required_fields = [
            'timestamp',
            'screen_distance',
            'ambient_light',
            'blink_rate',
            'usage_duration',
            'warning_count'
        ]
        
        for record in stats:
            is_valid, missing_fields = self.validate_data(vars(record), required_fields)
            if not is_valid:
                log_manager.log_system_event(
                    'data_validation',
                    f'用眼健康数据记录不完整，缺失字段: {", ".join(missing_fields)}',
                    'warning'
                )
                return False
        return True

    def generate_daily_report(self, date=None):
        """生成每日报告"""
        try:
            if date is None:
                date = datetime.now()
            
            start_time = datetime.combine(date.date(), datetime.min.time())
            end_time = start_time + timedelta(days=1)
            
            log_manager.log_system_event(
                'report_generation',
                f'开始生成每日报告 {date.strftime("%Y-%m-%d")}',
                'info'
            )
            
            # 获取各项统计数据
            posture_stats = self.db_manager.get_posture_stats(start_time, end_time)
            emotion_stats = self.db_manager.get_emotion_stats(start_time, end_time)
            focus_stats = self.db_manager.get_focus_stats(start_time, end_time)
            eyesight_stats = self.db_manager.get_eyesight_stats(start_time, end_time)
            
            # 验证数据完整性
            if not self.validate_posture_stats(posture_stats):
                log_manager.log_system_event(
                    'report_generation',
                    '姿势数据验证失败，报告可能不完整',
                    'warning'
                )
                
            if not self.validate_emotion_stats(emotion_stats):
                log_manager.log_system_event(
                    'report_generation',
                    '情绪数据验证失败，报告可能不完整',
                    'warning'
                )
                
            if not self.validate_focus_stats(focus_stats):
                log_manager.log_system_event(
                    'report_generation',
                    '专注度数据验证失败，报告可能不完整',
                    'warning'
                )
                
            if not self.validate_eyesight_stats(eyesight_stats):
                log_manager.log_system_event(
                    'report_generation',
                    '用眼健康数据验证失败，报告可能不完整',
                    'warning'
                )
            
            # 创建PDF报告
            pdf = FPDF()
            pdf.add_page()
            
            # 报告标题
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, f'每日健康报告 - {date.strftime("%Y-%m-%d")}', ln=True, align='C')
            
            # 添加各部分内容
            self._add_posture_section(pdf, posture_stats)
            self._add_emotion_section(pdf, emotion_stats)
            self._add_focus_section(pdf, focus_stats)
            self._add_eyesight_section(pdf, eyesight_stats)
            
            # 保存报告
            filename = f'daily_report_{date.strftime("%Y%m%d")}.pdf'
            filepath = os.path.join(self.report_path, filename)
            pdf.output(filepath)
            
            log_manager.log_system_event(
                'report_generation',
                f'每日报告生成成功: {filename}',
                'info'
            )
            
            return filepath
            
        except Exception as e:
            error_msg = f'生成每日报告失败: {str(e)}'
            log_manager.log_system_event('report_generation', error_msg, 'error')
            raise
    
    def generate_weekly_report(self, date=None):
        """生成周报告"""
        try:
            if date is None:
                date = datetime.now()
            
            # 计算本周开始和结束时间
            start_time = date - timedelta(days=date.weekday())
            start_time = datetime.combine(start_time.date(), datetime.min.time())
            end_time = start_time + timedelta(days=7)
            
            log_manager.log_system_event(
                'report_generation',
                f'开始生成周报 {start_time.strftime("%Y-%m-%d")} 至 {end_time.strftime("%Y-%m-%d")}',
                'info'
            )
            
            # 获取统计数据
            posture_stats = self.db_manager.get_posture_stats(start_time, end_time)
            emotion_stats = self.db_manager.get_emotion_stats(start_time, end_time)
            focus_stats = self.db_manager.get_focus_stats(start_time, end_time)
            eyesight_stats = self.db_manager.get_eyesight_stats(start_time, end_time)
            
            # 验证数据完整性
            if not self.validate_posture_stats(posture_stats):
                log_manager.log_system_event(
                    'report_generation',
                    '姿势数据验证失败，报告可能不完整',
                    'warning'
                )
                
            if not self.validate_emotion_stats(emotion_stats):
                log_manager.log_system_event(
                    'report_generation',
                    '情绪数据验证失败，报告可能不完整',
                    'warning'
                )
                
            if not self.validate_focus_stats(focus_stats):
                log_manager.log_system_event(
                    'report_generation',
                    '专注度数据验证失败，报告可能不完整',
                    'warning'
                )
                
            if not self.validate_eyesight_stats(eyesight_stats):
                log_manager.log_system_event(
                    'report_generation',
                    '用眼健康数据验证失败，报告可能不完整',
                    'warning'
                )
            
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
            
            log_manager.log_system_event(
                'report_generation',
                f'周报生成成功: {filename}',
                'info'
            )
            
            return filepath
            
        except Exception as e:
            error_msg = f'生成周报失败: {str(e)}'
            log_manager.log_system_event('report_generation', error_msg, 'error')
            raise
    
    def _add_posture_section(self, pdf, stats, is_weekly=False):
        """添加姿势分析部分"""
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, '姿势分析', ln=True)
        
        pdf.set_font('Arial', '', 12)
        
        # 添加统计数据
        if stats and 'stats' in stats:
            s = stats['stats']
            pdf.cell(0, 10, f'各关节平均角度:', ln=True)
            pdf.cell(0, 10, f' - 头部: {s["avg_head_angle"]:.1f}°', ln=True)
            pdf.cell(0, 10, f' - 颈部: {s["avg_neck_angle"]:.1f}°', ln=True)
            pdf.cell(0, 10, f' - 肩部: {s["avg_shoulder_tilt"]:.1f}°', ln=True)
            pdf.cell(0, 10, f' - 脊柱: {s["avg_spine_angle"]:.1f}°', ln=True)
            pdf.cell(0, 10, f'平均姿势评分: {s["avg_score"]:.1f}', ln=True)
            
            pdf.cell(0, 10, '\n姿势时长统计:', ln=True)
            pdf.cell(0, 10, f' - 良好姿势: {self._format_duration(s["good_duration"])}', ln=True)
            pdf.cell(0, 10, f' - 轻微不良: {self._format_duration(s["slightly_bad_duration"])}', ln=True)
            pdf.cell(0, 10, f' - 不良姿势: {self._format_duration(s["bad_duration"])}', ln=True)
            pdf.cell(0, 10, f' - 严重不良: {self._format_duration(s["severe_duration"])}', ln=True)
            pdf.cell(0, 10, f' - 遮挡时长: {self._format_duration(s["occluded_duration"])}', ln=True)
        
        # 添加趋势图
        if stats and 'trends' in stats:
            plt.figure(figsize=(10, 6))
            trends = stats['trends']
            hours = [t['hour'] for t in trends]
            
            # 绘制多关节角度趋势
            plt.subplot(2, 1, 1)
            plt.plot(hours, [t['avg_head_angle'] for t in trends], label='头部角度')
            plt.plot(hours, [t['avg_neck_angle'] for t in trends], label='颈部角度')
            plt.plot(hours, [t['avg_shoulder_tilt'] for t in trends], label='肩部倾斜')
            plt.plot(hours, [t['avg_spine_angle'] for t in trends], label='脊柱角度')
            plt.title('关节角度变化趋势')
            plt.xlabel('时间')
            plt.ylabel('角度')
            plt.legend()
            
            # 绘制姿势评分趋势
            plt.subplot(2, 1, 2)
            plt.plot(hours, [t['avg_score'] for t in trends], color='green')
            plt.title('姿势综合评分趋势')
            plt.xlabel('时间')
            plt.ylabel('评分')
            
            # 调整布局并保存
            plt.tight_layout()
            img_buf = BytesIO()
            plt.savefig(img_buf, format='png', dpi=300, bbox_inches='tight')
            img_buf.seek(0)
            plt.close()
            
            # 添加图表到PDF
            pdf.image(img_buf, x=10, y=None, w=190)
            
        # 添加常见问题分析
        if stats and 'common_issues' in stats:
            pdf.cell(0, 10, '\n常见姿势问题:', ln=True)
            for issue in stats['common_issues'][:5]:  # 显示前5个最常见的问题
                issue_text = issue['issue_list'].strip('[]').strip('"').replace('\\', '')
                pdf.cell(0, 10, f' - {issue_text}: {issue["count"]}次', ln=True)
    
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