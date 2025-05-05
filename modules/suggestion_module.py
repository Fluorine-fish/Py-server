from datetime import datetime, timedelta

class SuggestionGenerator:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.age_group = "child"  # 默认为儿童模式
        
        # 定义年龄组
        self.age_groups = {
            "young_child": (4, 8),    # 低龄儿童
            "child": (9, 12),         # 儿童
            "teenager": (13, 15)      # 青少年
        }
        
        # 儿童友好的提示语模板
        self.child_posture_suggestions = {
            'head_tilt': {
                'severe': '小朋友，你的头歪得有点多哦！让我们一起做一个小游戏：\n1. 想象你的头顶上有一本书，要平平地顶着它\n2. 做一做小鸟点头、小兔子摇头的游戏\n3. 休息一下，活动一下脖子，像小花朵一样转一转',
                'moderate': '亲爱的小朋友，让我们把头摆正一点点：\n1. 坐直一点，像一个小王子/小公主一样\n2. 让眼睛平视前方，就像在看远处的小星星',
                'good': '太棒了！你的坐姿像个小军人一样笔直，继续保持哦！'
            },
            'duration': {
                'long': '小朋友，是时候做个小游戏啦！\n1. 站起来转一转，像小蝴蝶一样飞一飞\n2. 做做眼保健操，让眼睛休息一下\n3. 喝一口水，像小鸟儿一样补充能量',
                'medium': '建议小朋友活动一下哦：\n1. 伸个懒腰，像早晨的小太阳一样\n2. 转转脖子，像风车一样转一转',
                'short': '真棒！你的坐姿很好，继续保持哦！'
            }
        }
        
        self.child_emotion_suggestions = {
            'stress': '小朋友，让我们做个有趣的游戏：\n1. 做个"气球呼吸"游戏 - 慢慢吸气让气球变大，呼气让气球飞走\n2. 玩"彩虹喝水"游戏 - 每喝一口水想象喝下一种彩虹的颜色\n3. 变身"快乐小袋鼠"蹦跳五下，跳走所有烦恼',
            'fatigue': '看起来有点累了呢，来玩个"精力充电"游戏：\n1. 假装自己是一棵小树，伸展枝叶碰触阳光\n2. 学小鸟拍拍翅膀，甩甩手臂\n3. 闭上眼睛，数一数脑海中有几只小绵羊',
            'focused': '哇！你太厉害啦！专注力超强：\n1. 奖励自己做个"星星跳"庆祝动作\n2. 给自己比个大拇指\n3. 休息时刻到了，来玩个快乐伸展操',
            'distracted': '让我们玩个"注意力小魔法"游戏：\n1. 找出房间里的三个蓝色物品\n2. 闭眼听听周围有几种声音\n3. 做个"专注小士兵"，挺直腰板坐好'
        }
        
        self.child_eyesight_suggestions = {
            'distance': {
                'too_close': '亲爱的小朋友，你离书本太近啦！\n1. 把书本放到一个手臂的距离\n2. 想象书本是害羞的小动物，不要离它太近\n3. 保持好距离，保护好眼睛',
                'good': '真棒！你和书本的距离刚刚好，像一个小专家一样！'
            },
            'lighting': {
                'too_dark': '这里有点暗暗的：\n1. 让我们打开台灯，照亮你的小天地\n2. 调整一下灯光，让它更舒服\n3. 光线要像温暖的阳光一样',
                'too_bright': '阳光有点太强啦：\n1. 拉上窗帘，像给窗户戴上墨镜\n2. 调整台灯的位置\n3. 让光线温柔一点',
                'good': '光线正好，像春天的阳光一样温暖！'
            },
            'blink_rate': {
                'low': '来玩个"眨眨眼"游戏吧：\n1. 数到三一起眨眼，看谁眨得最可爱\n2. 玩"远方寻宝"，找到窗外最远的一棵树\n3. 闭眼做个"彩虹想象"，想象看到各种颜色',
                'normal': '真棒！你的眼睛保护得很好，继续保持！想不想玩个"眼睛体操"？'
            }
        }

        # 保留原有的成人提示语模板
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
    
    def set_age_group(self, age):
        """设置年龄组"""
        for group, (min_age, max_age) in self.age_groups.items():
            if min_age <= age <= max_age:
                self.age_group = group
                return
        self.age_group = "child"  # 默认为儿童组
    
    def get_suggestion_template(self, category):
        """根据年龄组选择合适的提示语模板"""
        if self.age_group in ["young_child", "child"]:
            if category == "posture":
                return self.child_posture_suggestions
            elif category == "emotion":
                return self.child_emotion_suggestions
            elif category == "eyesight":
                return self.child_eyesight_suggestions
        return getattr(self, f"{category}_suggestions")

    def generate_posture_suggestions(self, recent_hours=1):
        """生成姿势相关建议"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=recent_hours)
        
        stats = self.db_manager.get_posture_stats(start_time, end_time)
        if not stats or 'stats' not in stats:
            return []
            
        suggestions = []
        s = stats['stats']
        template = self.get_suggestion_template("posture")
        
        # 分析头部角度
        if s['avg_angle'] > 30:
            suggestions.append(template['head_tilt']['severe'])
        elif s['avg_angle'] > 15:
            suggestions.append(template['head_tilt']['moderate'])
        else:
            suggestions.append(template['head_tilt']['good'])
            
        # 分析不良姿势持续时间
        if s['bad_duration'] > 1800:  # 30分钟
            suggestions.append(template['duration']['long'])
        elif s['bad_duration'] > 600:  # 10分钟
            suggestions.append(template['duration']['medium'])
            
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
        template = self.get_suggestion_template("emotion")
        
        # 分析情绪分布
        emotion_counts = {d['emotion_type']: d['count'] for d in dist}
        total_count = sum(emotion_counts.values())
        
        if total_count > 0:
            # 检查压力状态
            if (emotion_counts.get('angry', 0) + emotion_counts.get('sad', 0)) / total_count > 0.3:
                suggestions.append(template['stress'])
                
            # 检查疲劳状态
            if emotion_counts.get('neutral', 0) / total_count > 0.6:
                suggestions.append(template['fatigue'])
                
            # 检查专注状态
            if emotion_counts.get('focused', 0) / total_count > 0.5:
                suggestions.append(template['focused'])
            elif emotion_counts.get('distracted', 0) / total_count > 0.3:
                suggestions.append(template['distracted'])
                
        return suggestions
        
    def generate_eyesight_suggestions(self, recent_minutes=30):
        """生成用眼健康建议"""
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=recent_minutes)
        
        stats = self.db_manager.get_eyesight_stats(start_time, end_time)
        if not stats:
            return []
            
        suggestions = []
        template = self.get_suggestion_template("eyesight")
        
        # 计算平均值
        avg_distance = sum(s.screen_distance for s in stats) / len(stats) if stats else 0
        avg_light = sum(s.ambient_light for s in stats) / len(stats) if stats else 0
        avg_blink = sum(s.blink_rate for s in stats) / len(stats) if stats else 0
        
        # 分析观看距离
        if avg_distance < 50:
            suggestions.append(template['distance']['too_close'])
        else:
            suggestions.append(template['distance']['good'])
            
        # 分析光照环境
        if avg_light < 250:
            suggestions.append(template['lighting']['too_dark'])
        elif avg_light > 1000:
            suggestions.append(template['lighting']['too_bright'])
        else:
            suggestions.append(template['lighting']['good'])
            
        # 分析眨眼频率
        if avg_blink < 15:
            suggestions.append(template['blink_rate']['low'])
        else:
            suggestions.append(template['blink_rate']['normal'])
            
        return suggestions
        
    def generate_comprehensive_suggestions(self):
        """生成综合建议"""
        suggestions = {
            'posture': self.generate_posture_suggestions(),
            'emotion': self.generate_emotion_suggestions(),
            'eyesight': self.generate_eyesight_suggestions()
        }
        
        return suggestions

    def generate_posture_suggestion(self, posture_status):
        child_suggestions = {
            'head_tilt': '让我们玩个好姿势游戏：\n1. 假装你是个骄傲的小王子/公主，头要漂亮地抬起来\n2. 学长颈鹿伸展脖子，慢慢左右转动\n3. 数到10，看看能不能保持像士兵一样笔直',
            'shoulder_slump': '来跟我一起做"小翅膀操"：\n1. 想象你是只小鸟，把翅膀（肩膀）张开\n2. 向后转动小翅膀，画个圆圆\n3. 挺起胸膛，做最漂亮的小鸟',
            'back_arch': '变身"小树苗"时间到：\n1. 像小树一样笔直地生长\n2. 感受背部贴着椅子，像靠着大树\n3. 数三下，挺直腰板像个小超人',
            'correct': '太棒了！你的坐姿像个小模特一样完美！继续保持哦～'
        }
        
        if self.user_age <= 12:
            return child_suggestions.get(posture_status, "让我们一起保持正确的坐姿，像小超人一样！")