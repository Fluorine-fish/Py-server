from fastapi import APIRouter

# 创建路由器
router = APIRouter(prefix="/api/data", tags=["pc_data"])

@router.get('/posture')
async def posture_data():
    """PC端返回完整姿态数据"""
    return {
        'good': 62,
        'mild': 28,
        'bad': 10,
        'recent_photos': ["/snapshot/1.jpg", "/snapshot/2.jpg", "/snapshot/3.jpg"],
        'hourly_stats': {
            'labels': ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00'],
            'data': [75, 68, 62, 45, 57, 62]
        },
        'recommendations': ['调整座椅高度', '保持背部挺直', '每小时起身活动5分钟']
    }

@router.get('/eye')
async def eye_data():
    """PC端返回完整眼部数据"""
    return {
        'blink_rate': 18,
        'distance': 42,
        'focus_time': 25,
        'heatmap': [[0,1,2],[1,3,2],[2,4,1],[1,2,0]],
        'time_series': {
            'labels': ['09:00', '10:00', '11:00', '12:00', '13:00'],
            'blink_data': [20, 18, 15, 12, 18],
            'distance_data': [45, 42, 38, 36, 42]
        },
        'notifications': ['适当休息', '保持30cm以上距离', '调整显示器亮度']
    }

@router.get('/emotion')
async def emotion_data():
    """PC端返回详细情绪数据"""
    return {
        'trend': [0.1, 0.5, 0.2, 0.7, 0.4, 0.6, 0.8],
        'labels': ['08:00','09:00','10:00','11:00','12:00','14:00','16:00'],
        'current_mood': 'positive',
        'stress_level': 0.3,
        'emotions_detected': {
            'happy': 45,
            'neutral': 30,
            'focused': 20,
            'tired': 5
        },
        'recommendations': ['休息5分钟', '做深呼吸练习', '户外短暂散步', '喝杯水']
    }