"""
模拟API响应模块 - 提供假数据用于前端测试
"""
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import RedirectResponse, StreamingResponse
from pathlib import Path
import time
import asyncio
import os
from datetime import datetime, timedelta
import random
import base64
import os
from typing import Optional, Dict, Any, List

# 创建路由器
router = APIRouter(prefix="/api", tags=["mock_api"])

# ===================
# 设备相关API
# ===================

@router.get('/device-info')
async def device_info():
    """返回设备基本信息"""
    return {
        'id': 'LAMP2025001',
        'name': '曈灵智能台灯',
        'model': 'TL-2025Pro',
        'firmware': 'v2.5.3',
        'hardware': 'v1.2',
        'mac': '00:11:22:33:44:55'
    }

@router.get('/device/status')
async def device_status():
    """返回设备状态信息"""
    return {
        'online': True,
        'lastSeen': datetime.now().isoformat(),
        'batteryLevel': random.randint(70, 95),
        'charging': random.choice([True, False]),
        'temperature': round(random.uniform(25.0, 32.0), 1),
        'memory': {
            'total': 512,
            'used': random.randint(180, 320)
        },
        'uptime': random.randint(3600, 86400)  # 1小时到1天之间
    }

@router.get('/device/settings')
async def device_settings():
    """返回设备设置信息"""
    return {
        'brightness': random.randint(50, 80),
        'colorTemperature': random.choice([2700, 4000, 5500, 6500]),
        'autoAdjust': True,
        'notifications': {
            'posture': True,
            'eye': True,
            'emotion': False
        },
        'powerSaving': random.choice([True, False])
    }

@router.post('/device/settings')
async def update_settings(settings: Dict[str, Any]):
    """更新设备设置"""
    # 模拟处理延迟
    await asyncio.sleep(0.5)
    return {
        'success': True,
        'message': '设置已更新',
        'settings': settings
    }

# ===================
# 监控相关API
# ===================

@router.get('/monitor/posture')
async def posture_data():
    """返回坐姿监测数据"""
    current_hour = datetime.now().hour
    # 晚上时分数稍低
    base_score = 85 if 9 <= current_hour <= 18 else 70
    
    return {
        'currentScore': base_score + random.randint(-10, 10),
        'warnCount': random.randint(1, 5),
        'averageScore': base_score - random.randint(0, 5),
        'lastDetected': (datetime.now() - timedelta(minutes=random.randint(1, 15))).isoformat(),
        'screenTime': random.randint(3600, 7200),  # 1-2小时
        'goodPostureRate': random.randint(60, 85)
    }

@router.get('/monitor/posture/history')
async def posture_history(timeRange: str = 'day'):
    """返回坐姿历史数据"""
    if timeRange == 'day':
        return {
            'goodTime': str(round(random.uniform(2.5, 4.5), 1)),
            'mildTime': str(round(random.uniform(1.0, 2.0), 1)),
            'badTime': str(round(random.uniform(0.3, 1.0), 1)),
            'goodRate': str(random.randint(60, 75)),
            'problemTimeSlot': '下午3-5点',
            'improvementMessage': '今天坐姿良好，请继续保持。'
        }
    elif timeRange == 'week':
        return {
            'goodTime': str(round(random.uniform(15.0, 25.0), 1)),
            'mildTime': str(round(random.uniform(5.0, 10.0), 1)),
            'badTime': str(round(random.uniform(2.0, 5.0), 1)),
            'goodRate': str(random.randint(60, 75)),
            'problemTimeSlot': '周四下午',
            'improvementMessage': '本周坐姿改善效果明显，请继续保持良好习惯。'
        }
    else:  # month
        return {
            'goodTime': str(round(random.uniform(60.0, 80.0), 1)),
            'mildTime': str(round(random.uniform(20.0, 40.0), 1)),
            'badTime': str(round(random.uniform(10.0, 20.0), 1)),
            'goodRate': str(random.randint(60, 75)),
            'problemTimeSlot': '下午时段',
            'improvementMessage': '本月总体坐姿较好，但下午时段仍需注意。'
        }

@router.get('/monitor/posture/distribution')
async def posture_distribution(timeRange: str = 'day'):
    """返回坐姿时间分布"""
    if timeRange == 'day':
        return [random.randint(1, 5) for _ in range(12)]
    elif timeRange == 'week':
        return [random.randint(2, 8) for _ in range(12)]
    else:  # month
        return [random.randint(3, 10) for _ in range(12)]

@router.get('/monitor/posture/images')
async def posture_images(page: int = 1, limit: int = 6, filter_type: str = None):
    """返回坐姿图像记录
    
    参数:
        page: 页码，从1开始
        limit: 每页记录数
        filter_type: 筛选类型 (good/bad/all)
    """
    base_time = datetime.now()
    images = []
    posture_types = ['良好坐姿', '轻度不良', '中度不良', '严重不良']
    posture_weights = [0.6, 0.2, 0.15, 0.05]  # 各类型权重
    image_colors = ['4285f4', 'fbbc05', 'ff9800', 'ea4335']  # 对应颜色
    
    for i in range(limit):
        timestamp = base_time - timedelta(hours=i + (page-1)*limit)
        score = random.randint(60, 95)
        
        # 根据分数确定坐姿类型
        posture_index = 0 if score >= 85 else (1 if score >= 70 else (2 if score >= 60 else 3))
        
        # 如果有过滤条件，跳过不符合条件的记录
        is_good_posture = posture_index == 0
        if filter_type == 'good' and not is_good_posture:
            continue
        if filter_type == 'bad' and is_good_posture:
            continue
            
        posture_type = posture_types[posture_index]
        color = image_colors[posture_index]
        
        images.append({
            'id': f'img_{page}_{i}',
            'url': f'https://placehold.co/300x240/{color}/ffffff?text={posture_type}',  # 使用彩色占位图
            'thumbnail': f'https://placehold.co/150x120/{color}/ffffff?text={posture_type}',  # 缩略图
            'timestamp': timestamp.isoformat(),
            'score': score,
            'posture_type': posture_type,
            'is_good_posture': is_good_posture,
            'duration': random.randint(5, 30),  # 持续时间(分钟)
            'note': random.choice([
                '坐姿良好，请继续保持',
                '稍微前倾，建议调整',
                '有些含胸驼背，请注意改善',
                '脖子前伸，请立即调整姿势'
            ]) if random.random() > 0.5 else None  # 50%几率有备注
        })
    
    # 如果过滤后没有足够图像，补充生成
    while len(images) < limit and (filter_type == 'good' or filter_type == 'bad'):
        timestamp = base_time - timedelta(hours=random.randint(1, 72))
        
        if filter_type == 'good':
            score = random.randint(85, 95)
            posture_index = 0
        else:  # bad
            score = random.randint(60, 84)
            posture_index = random.choices([1, 2, 3], weights=[0.5, 0.3, 0.2])[0]
            
        posture_type = posture_types[posture_index]
        color = image_colors[posture_index]
        
        images.append({
            'id': f'img_extra_{len(images)}',
            'url': f'https://placehold.co/300x240/{color}/ffffff?text={posture_type}',
            'thumbnail': f'https://placehold.co/150x120/{color}/ffffff?text={posture_type}',
            'timestamp': timestamp.isoformat(),
            'score': score,
            'posture_type': posture_type,
            'is_good_posture': posture_index == 0,
            'duration': random.randint(5, 30)
        })
    
    # 根据时间戳排序
    images.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return images

@router.get('/monitor/posture/improvement')
async def posture_improvement():
    """返回坐姿改善建议"""
    return {
        'problemTimeSlot': random.choice(['上午9-11点', '中午12-1点', '下午3-5点', '晚上7-9点']),
        'improvementMessage': random.choice([
            '建议适当调整椅子高度，保持眼睛平视屏幕。',
            '坐姿良好，请继续保持背部挺直的习惯。',
            '建议增加站立工作时间，减少久坐。',
            '检测到您长时间保持同一姿势，建议起身活动5分钟。'
        ])
    }
    
@router.get('/monitor/posture/images/{image_id}')
async def posture_image_detail(image_id: str):
    """返回单个坐姿图像的详细信息"""
    # 解析image_id获取页码和索引
    try:
        parts = image_id.split('_')
        if parts[0] == 'img':
            page = int(parts[1])
            index = int(parts[2])
        else:
            # 对于补充生成的图像使用随机数据
            page = random.randint(1, 5)
            index = random.randint(0, 5)
            
        posture_types = ['良好坐姿', '轻度不良', '中度不良', '严重不良']
        posture_weights = [0.6, 0.2, 0.15, 0.05]
        image_colors = ['4285f4', 'fbbc05', 'ff9800', 'ea4335']
        
        base_time = datetime.now() - timedelta(hours=index + (page-1)*6)
        score = random.randint(60, 95)
        
        # 根据分数确定坐姿类型
        posture_index = 0 if score >= 85 else (1 if score >= 70 else (2 if score >= 60 else 3))
        posture_type = posture_types[posture_index]
        color = image_colors[posture_index]
        
        # 生成详细的分析数据
        angle_data = {
            'neck': random.randint(10, 40),
            'shoulder': random.randint(5, 25),
            'back': random.randint(5, 30),
            'overall': score
        }
        
        # 生成建议
        suggestions = []
        if angle_data['neck'] > 20:
            suggestions.append('颈部角度过大，建议调整显示器高度或抬头挺胸')
        if angle_data['shoulder'] > 15:
            suggestions.append('肩膀前倾明显，建议挺直上身，收紧肩胛骨')
        if angle_data['back'] > 15:
            suggestions.append('脊椎弯曲度较大，建议挺直腰背，使用腰靠')
        if not suggestions:
            suggestions.append('坐姿整体良好，请继续保持')
            
        return {
            'id': image_id,
            'url': f'https://placehold.co/600x480/{color}/ffffff?text={posture_type}',  # 高清图
            'thumbnail': f'https://placehold.co/150x120/{color}/ffffff?text={posture_type}',
            'timestamp': base_time.isoformat(),
            'score': score,
            'posture_type': posture_type,
            'is_good_posture': posture_index == 0,
            'duration': random.randint(5, 30),
            'analysis': {
                'angles': angle_data,
                'key_points': {
                    'head': {'x': random.uniform(0.4, 0.6), 'y': random.uniform(0.1, 0.2)},
                    'neck': {'x': random.uniform(0.45, 0.55), 'y': random.uniform(0.2, 0.3)},
                    'shoulder_left': {'x': random.uniform(0.3, 0.4), 'y': random.uniform(0.25, 0.35)},
                    'shoulder_right': {'x': random.uniform(0.6, 0.7), 'y': random.uniform(0.25, 0.35)},
                    'spine_top': {'x': random.uniform(0.45, 0.55), 'y': random.uniform(0.3, 0.4)},
                    'spine_mid': {'x': random.uniform(0.45, 0.55), 'y': random.uniform(0.4, 0.5)},
                    'spine_bottom': {'x': random.uniform(0.45, 0.55), 'y': random.uniform(0.5, 0.6)}
                }
            },
            'suggestions': suggestions,
            'environment': {
                'lighting': f'{random.randint(300, 800)}lux',
                'desk_height': f'{random.randint(65, 80)}cm',
                'screen_distance': f'{random.randint(40, 65)}cm'
            }
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"图像未找到: {e}")

@router.get('/monitor/posture/statistics')
async def posture_statistics(time_range: str = 'day'):
    """返回坐姿统计数据"""
    # 基于时间范围调整数据量
    multiplier = 1 if time_range == 'day' else (7 if time_range == 'week' else 30)
    
    total_count = random.randint(10, 30) * multiplier
    good_count = int(total_count * random.uniform(0.6, 0.8))
    mild_count = int(total_count * random.uniform(0.1, 0.2))
    moderate_count = int(total_count * random.uniform(0.05, 0.15))
    severe_count = total_count - good_count - mild_count - moderate_count
    
    return {
        'total_records': total_count,
        'distribution': {
            'good': good_count,
            'mild': mild_count,
            'moderate': moderate_count,
            'severe': severe_count
        },
        'improvement': {
            'rate': f"{random.randint(5, 15)}%",
            'compared_to': "上周" if time_range != 'day' else "昨天",
            'is_better': random.choice([True, True, False])  # 大概率是改善的
        },
        'most_common_issue': random.choice([
            '颈部前倾',
            '肩膀耸起',
            '含胸驼背',
            '脊柱弯曲',
            '坐姿歪斜'
        ]),
        'best_time_period': random.choice([
            '上午9点-11点',
            '下午2点-4点',
            '晚上7点-9点'
        ]),
        'worst_time_period': random.choice([
            '上午11点-12点',
            '下午4点-6点',
            '晚上9点-11点'
        ])
    }

@router.get('/monitor/eye')
async def eye_data():
    """返回用眼监测数据"""
    return {
        'eyeDistance': random.randint(35, 50),
        'screenTime': random.randint(3600, 10800),  # 1-3小时
        'breakReminder': '每30分钟',
        'lastWarning': (datetime.now() - timedelta(minutes=random.randint(5, 30))).isoformat(),
        'blink_rate': random.randint(15, 25),
        'focus_time': random.randint(20, 45)
    }

@router.get('/monitor/eye/history')
async def eye_history(timeRange: str = 'day'):
    """返回用眼历史数据"""
    if timeRange == 'day':
        return {
            'totalTime': random.randint(2, 6) * 3600,  # 2-6小时，秒为单位
            'breakCount': random.randint(3, 8),
            'avgDistance': random.uniform(40.0, 48.0),
            'warningCount': random.randint(0, 5)
        }
    elif timeRange == 'week':
        return {
            'days': ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
            'screenHours': [random.uniform(1.5, 5.0) for _ in range(7)],
            'distances': [random.uniform(35.0, 50.0) for _ in range(7)]
        }
    else:  # month
        return {
            'weeks': ['第1周', '第2周', '第3周', '第4周'],
            'avgScreenHours': [random.uniform(15.0, 30.0) for _ in range(4)],
            'avgDistance': [random.uniform(40.0, 45.0) for _ in range(4)],
            'improvement': random.choice(['显著改善', '略有改善', '保持稳定', '略有下降'])
        }

@router.get('/monitor/eye/trends')
async def eye_trends():
    """用眼趋势（供前端折线图使用）"""
    labels = [f"{h:02d}:00" for h in range(6, 21, 2)]
    data = [round(random.uniform(35.0, 50.0), 1) for _ in labels]
    return { 'labels': labels, 'data': data }

@router.get('/monitor/eye/environment')
async def eye_environment():
    """用眼环境指标（供雷达图使用）"""
    indicators = ['环境亮度', '坐姿稳定', '眨眼频率', '距离安全', '专注度']
    current = [random.randint(60, 90) for _ in indicators]
    return { 'labels': indicators, 'current': current }

@router.get('/monitor/eye/heatmap')
async def eye_heatmap():
    """用眼热力图（周×小时）"""
    days = ['周一','周二','周三','周四','周五','周六','周日']
    hours = [str(h) for h in range(6, 23)]
    matrix = []
    for r in range(len(days)):
        row = []
        for c, h in enumerate(range(6, 23)):
            base = 0.4
            if 12 <= h <= 14:
                base = 0.6
            elif 15 <= h <= 19:
                base = 0.75
            elif h >= 20:
                base = 0.55
            if r >= 5:
                base += 0.08
            row.append(round(max(0, min(1, base + (c % 3) * 0.05)), 2))
        matrix.append(row)
    return { 'days': days, 'hours': hours, 'data': matrix }

@router.get('/monitor/eye/data')
async def eye_detail_data():
    """用眼详情小卡数据"""
    return {
        'blinkRate': random.randint(15, 25),
        'avgDistance': round(random.uniform(40.0, 46.0), 1),
        'screenTime': random.randint(2, 6) * 3600,
        'warningCount': random.randint(0, 4)
    }

@router.get('/monitor/emotion')
async def emotion_data():
    """返回情绪监测数据"""
    emotions = ['happy', 'neutral', 'sad', 'surprised', 'angry', 'fear', 'disgust']
    weights = [0.4, 0.3, 0.1, 0.1, 0.05, 0.025, 0.025]  # 调整各情绪概率
    
    emotion = random.choices(emotions, weights=weights)[0]
    
    history = []
    base_time = datetime.now()
    
    for i in range(5):
        time_point = base_time - timedelta(minutes=15*i)
        history_emotion = random.choices(emotions, weights=weights)[0]
        history.append({
            'time': time_point.isoformat(),
            'emotion': history_emotion,
            'duration': random.randint(600, 1800)  # 10-30分钟
        })
    
    return {
        'currentEmotion': emotion,
        'confidence': round(random.uniform(0.75, 0.98), 2),
        'history': history
    }

@router.get('/monitor/emotion/trends')
async def emotion_trends():
    """情绪趋势（0-1）"""
    labels = [f"{h:02d}:00" for h in range(6, 22, 2)]
    # 早上平稳，中午略高，下午/傍晚更活跃，晚上回落
    data = []
    for h in range(6, 22, 2):
        base = 0.35
        if 12 <= h <= 14:
            base = 0.55
        elif 15 <= h <= 19:
            base = 0.72
        elif h >= 20:
            base = 0.5
        data.append(round(max(0, min(1, base + random.uniform(-0.05, 0.06))), 2))
    return { 'labels': labels, 'data': data }

@router.get('/monitor/emotion/distribution')
async def emotion_distribution():
    """情绪时段分布（每段加总约100）"""
    time_slots = ['上午', '中午', '下午', '晚上']
    # 基于时段生成分布
    def slot():
        happy = random.randint(22, 38)
        neutral = random.randint(28, 42)
        sad = random.randint(6, 14)
        angry = random.randint(4, 10)
        surprised = random.randint(8, 14)
        focused = 100 - (happy + neutral + sad + angry + surprised)
        return [happy, neutral, sad, angry, surprised, max(6, focused)]
    cols = list(zip(*(slot() for _ in time_slots)))
    emotions = {
        'happy':     list(cols[0]),
        'neutral':   list(cols[1]),
        'sad':       list(cols[2]),
        'angry':     list(cols[3]),
        'surprised': list(cols[4]),
        'focused':   list(cols[5])
    }
    return { 'timeSlots': time_slots, 'emotions': emotions }

@router.get('/monitor/emotion/radar')
async def emotion_radar():
    """情绪多维雷达"""
    labels = ['专注度','愉悦度','放松度','疲劳度','压力值']
    current = [random.randint(60, 90) for _ in labels]
    return { 'labels': labels, 'current': current }


@router.get('/monitor/emotion/distribution')
async def emotion_distribution():
    """情绪时段分布（每段加总约100）"""
    time_slots = ['上午', '中午', '下午', '晚上']
    
    # 定义不同时段的情绪基线
    base_emotions = {
        '上午': {'happy': 30, 'neutral': 40, 'sad': 8, 'angry': 5, 'surprised': 10, 'focused': 7},
        '中午': {'happy': 40, 'neutral': 30, 'sad': 5, 'angry': 5, 'surprised': 12, 'focused': 8},
        '下午': {'happy': 25, 'neutral': 35, 'sad': 12, 'angry': 8, 'surprised': 10, 'focused': 10},
        '晚上': {'happy': 35, 'neutral': 45, 'sad': 5, 'angry': 3, 'surprised': 7, 'focused': 5}
    }
    
    emotions = {
        'happy': [], 'neutral': [], 'sad': [], 'angry': [], 'surprised': [], 'focused': []
    }
    
    for slot in time_slots:
        total = 0
        temp_emotions = {}
        for emotion, base in base_emotions[slot].items():
            value = base + random.randint(-5, 5)
            temp_emotions[emotion] = value
            total += value
        
        # 归一化到100
        for emotion in temp_emotions:
            temp_emotions[emotion] = round(temp_emotions[emotion] / total * 100)
        
        # 修正总和为100
        current_sum = sum(temp_emotions.values())
        if current_sum != 100:
            diff = 100 - current_sum
            # 加到值最大的情绪上
            max_emotion = max(temp_emotions, key=temp_emotions.get)
            temp_emotions[max_emotion] += diff

        for emotion, value in temp_emotions.items():
            emotions[emotion].append(value)
            
    return { 'timeSlots': time_slots, 'emotions': emotions }

@router.get('/monitor/emotion/heatmap')
async def emotion_heatmap():
    """周情绪热力图（值 0-1）"""
    days = ['周一','周二','周三','周四','周五','周六','周日']
    hours = [str(h) for h in range(6, 23)]
    matrix: List[List[float]] = []
    
    for r in range(len(days)):
        row: List[float] = []
        for c, h_str in enumerate(hours):
            h = int(h_str)
            
            # 基础情绪值，模拟一天中的情绪波动
            base = 0.4
            if 8 <= h < 12: # 上午学习
                base = 0.6 + random.uniform(-0.1, 0.1)
            elif 12 <= h < 14: # 午休
                base = 0.3 + random.uniform(-0.1, 0.1)
            elif 14 <= h < 18: # 下午学习
                base = 0.7 + random.uniform(-0.15, 0.15)
            elif 18 <= h < 21: # 晚上放松
                base = 0.5 + random.uniform(-0.1, 0.1)
            else: # 早晚
                base = 0.2 + random.uniform(-0.1, 0.1)
            
            # 周末情绪更放松
            if r >= 5:
                base += 0.15
            
            # 增加随机性
            val = max(0, min(1, base + random.uniform(-0.1, 0.1)))
            row.append(round(val, 2))
        matrix.append(row)
        
    return { 'days': days, 'hours': hours, 'data': matrix }


# API路由 - 视频流（展示版：固定返回 static/home.jpg）
@router.get('/video')
async def video_stream():
    """提供模拟视频流（静态图像：static/home.jpg）"""
    try:
        root_dir = Path(__file__).resolve().parents[3]
        img_path = root_dir / 'static' / 'home.jpg'
        if img_path.exists():
            image_bytes = img_path.read_bytes()
        else:
            image_bytes = b""

        async def generator():
            while True:
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + image_bytes + b'\r\n')
                await asyncio.sleep(0.1)

        return StreamingResponse(
            generator(),
            media_type='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception:
        # 失败时也返回空流，避免前端报错
        async def generator():
            while True:
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + b'' + b'\r\n')
                await asyncio.sleep(0.1)
        return StreamingResponse(generator(), media_type='multipart/x-mixed-replace; boundary=frame')
