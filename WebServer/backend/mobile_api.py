from fastapi import APIRouter

# 创建路由器
router = APIRouter(prefix="/api/data", tags=["mobile_data"])

@router.get('/posture')
async def posture_data():
    """移动端返回简化姿态数据"""
    return {
        'summary': '62% 良好',
        'status': 'good',  # good, warning, bad
        'recent_photo': '/snapshot/1.jpg',
        'tip': '保持背部挺直'
    }

@router.get('/eye')
async def eye_data():
    """移动端返回关键眼部指标"""
    return {
        'blink_rate': 18,
        'distance_status': 'optimal',  # optimal, warning, danger
        'focus_score': 25,
        'focus_time': '25',
        'distance': '45',
        'tip': '每20分钟远眺20秒'
    }

@router.get('/emotion')
async def emotion_data():
    """移动端返回核心情绪状态"""
    return {
        'mood_score': 0.8,
        'status': 'good',  # good, normal, low
        'primary_emotion': 'focused',
        'tip': '继续保持专注状态',
        'labels': ['9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00'],
        'trend': [0.7, 0.8, 0.75, 0.9, 0.85, 0.8, 0.82]
    }