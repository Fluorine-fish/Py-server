from datetime import datetime, timedelta

class SuggestionGenerator:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
        # 定义各类建议模板
        self.posture_suggestions = {
            'head_tilt': {
                'severe': '您的头部倾斜角度过大，这可能导致颈椎疲劳。建议：\n1. 调整显示器高度\n2. 保持头部正直\n3. 每工作1小时做5分钟颈部放松运动',
                'moderate': '注意保持头部正直，建议：\n1. 适当调整座椅高度\n2. 保持显示器在视线水平位置',
                'good': '保持当前良好坐姿，记得定期活动'
            },
            'duration': {
                'long': '您已连续保持不良姿势较长时间，建议立即调整坐姿并活动颈部',
                'medium': '注意保持正确坐姿，建议适时调整姿势',
                'short': '建议保持当前坐姿习惯'
            }
        }
        
        self.emotion_suggestions = {
            'stress': '检测到您可能处于压力状态，建议：\n1. 进行3-5分钟的深呼吸练习\n2. 短暂休息，喝杯水\n3. 做一些简单的伸展运动',
            'fatigue': '您可能出现疲劳状态，建议：\n1. 适当休息\n2. 远眺放松眼睛\n3. 起身活动放松身体',
            'focused': '当前状态专注，继续保持！记得适时休息',
            'distracted': '注意力可能有所分散，建议：\n1. 清理桌面环境\n2. 设置勿扰模式\n3. 制定短期目标提高专注度'
        }
        
        self.eyesight_suggestions = {
            'distance': {
                'too_close': '您与屏幕距离过近，建议：\n1. 保持50-70厘米的观看距离\n2. 调整显示器位置\n3. 必要时考虑使用显示器支架',
                'good': '当前观看距离适宜，请保持'
            },
            'lighting': {
                'too_dark': '当前环境光线不足，建议：\n1. 开启适当照明\n2. 避免在黑暗环境下用眼\n3. 调整屏幕亮度',
                'too_bright': '环境光线过强，建议：\n1. 避免强光直射屏幕\n2. 调整窗帘或照明\n3. 考虑使用防眩光屏幕',
                'good': '当前光照环境适宜，请保持'
            },
            'blink_rate': {
                'low': '您的眨眼频率偏低，建议：\n1. 有意识增加眨眼次数\n2. 使用20-20-20法则：每20分钟远眺20英尺外的物体20秒\n3. 使用人工泪液滋润眼睛',
                'normal': '当前眨眼频率正常，继续保持'
            }
        }
    
    def generate_posture_suggestions(self, recent_hours=1):
        """生成姿势相关建议"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=recent_hours)
        
        stats = self.db_manager.get_posture_stats(start_time, end_time)
        if not stats or 'stats' not in stats:
            return []
            
        suggestions = []
        s = stats['stats']
        
        # 分析头部角度
        if s['avg_angle'] > 30:
            suggestions.append(self.posture_suggestions['head_tilt']['severe'])
        elif s['avg_angle'] > 15:
            suggestions.append(self.posture_suggestions['head_tilt']['moderate'])
        else:
            suggestions.append(self.posture_suggestions['head_tilt']['good'])
            
        # 分析不良姿势持续时间
        if s['bad_duration'] > 1800:  # 30分钟
            suggestions.append(self.posture_suggestions['duration']['long'])
        elif s['bad_duration'] > 600:  # 10分钟
            suggestions.append(self.posture_suggestions['duration']['medium'])
            
        return suggestions
        
    def generate_emotion_suggestions(self, recent_hours=1):
        """生成情绪相关建议"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=recent_hours)
        
        stats = self.db_manager.get_emotion_stats(start_time, end_time)
        if not stats or 'distribution' not in stats:
            return []
            
        suggestions = []
        dist = stats['distribution']
        
        # 分析情绪分布
        emotion_counts = {d['emotion_type']: d['count'] for d in dist}
        total_count = sum(emotion_counts.values())
        
        if total_count > 0:
            # 检查压力状态
            if (emotion_counts.get('angry', 0) + emotion_counts.get('sad', 0)) / total_count > 0.3:
                suggestions.append(self.emotion_suggestions['stress'])
                
            # 检查疲劳状态
            if emotion_counts.get('neutral', 0) / total_count > 0.6:
                suggestions.append(self.emotion_suggestions['fatigue'])
                
            # 检查专注状态
            if emotion_counts.get('focused', 0) / total_count > 0.5:
                suggestions.append(self.emotion_suggestions['focused'])
            elif emotion_counts.get('distracted', 0) / total_count > 0.3:
                suggestions.append(self.emotion_suggestions['distracted'])
                
        return suggestions
        
    def generate_eyesight_suggestions(self, recent_minutes=30):
        """生成用眼健康建议"""
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=recent_minutes)
        
        stats = self.db_manager.get_eyesight_stats(start_time, end_time)
        if not stats:
            return []
            
        suggestions = []
        
        # 计算平均值
        avg_distance = sum(s.screen_distance for s in stats) / len(stats) if stats else 0
        avg_light = sum(s.ambient_light for s in stats) / len(stats) if stats else 0
        avg_blink = sum(s.blink_rate for s in stats) / len(stats) if stats else 0
        
        # 分析观看距离
        if avg_distance < 50:
            suggestions.append(self.eyesight_suggestions['distance']['too_close'])
        else:
            suggestions.append(self.eyesight_suggestions['distance']['good'])
            
        # 分析光照环境
        if avg_light < 250:
            suggestions.append(self.eyesight_suggestions['lighting']['too_dark'])
        elif avg_light > 1000:
            suggestions.append(self.eyesight_suggestions['lighting']['too_bright'])
        else:
            suggestions.append(self.eyesight_suggestions['lighting']['good'])
            
        # 分析眨眼频率
        if avg_blink < 15:
            suggestions.append(self.eyesight_suggestions['blink_rate']['low'])
        else:
            suggestions.append(self.eyesight_suggestions['blink_rate']['normal'])
            
        return suggestions
        
    def generate_comprehensive_suggestions(self):
        """生成综合建议"""
        suggestions = {
            'posture': self.generate_posture_suggestions(),
            'emotion': self.generate_emotion_suggestions(),
            'eyesight': self.generate_eyesight_suggestions()
        }
        
        return suggestions