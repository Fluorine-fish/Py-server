"""
摄像头处理模块 - 提供摄像头初始化、配置和帧处理功能
从原始posture_module.py拆分而来，减少单个文件代码量
"""
import os
import sys
import cv2
import time

# 摄像头优化配置常量
CAMERA_BUFFER_SIZE = 1  # 摄像头缓冲区大小
CAMERA_API_PREFERENCE = cv2.CAP_V4L2  # Linux上使用V4L2后端
CAMERA_FPS_TARGET = 30  # 摄像头目标帧率
CAMERA_FOURCC_OPTIONS = ['MJPG', 'YUYV', 'RGB3']  # 优先使用MJPG编码

# 分辨率和性能相关参数
PROCESS_WIDTH = 320
PROCESS_HEIGHT = 240

# 更新处理分辨率级别，设置320x240为最低分辨率
RESOLUTION_LEVELS = [
    (640, 480),   # 高分辨率
    (480, 360),   # 中分辨率
    (320, 240)    # 最低分辨率 - 不再使用更低的分辨率以保证分析质量
]

def init_camera():
    """
    初始化摄像头设备
    
    Returns:
        (cap, success): 摄像头对象和是否成功
    """
    try:
        # 先使用find_available_cameras找到所有可用的摄像头
        available_cameras = find_available_cameras()
        camera_found = False
        cap = None
        
        if available_cameras:
            # 首先尝试available_cameras中的相机
            for camera_index in available_cameras:
                try:
                    print(f"尝试初始化摄像头索引 {camera_index}...")
                    cap = cv2.VideoCapture(camera_index, CAMERA_API_PREFERENCE)
                    if cap.isOpened():
                        # 读取一帧验证相机是否真正可用
                        ret, test_frame = cap.read()
                        if ret and test_frame is not None:
                            print(f"找到可用摄像头：索引 {camera_index}")
                            camera_found = True
                            break
                        else:
                            print(f"摄像头索引 {camera_index} 无法读取帧")
                            cap.release()
                except Exception as e:
                    print(f"尝试摄像头索引 {camera_index} 失败: {e}")
                    if cap:
                        cap.release()
        
        # 如果上面的方法没找到摄像头，尝试直接使用索引6（对应Bus 006）
        if not camera_found:
            try:
                print("尝试直接访问Bus 006上的摄像头 (索引6)...")
                # 使用V4L2后端，这在Linux上对USB摄像头效果更好
                cap = cv2.VideoCapture(6, CAMERA_API_PREFERENCE)
                if cap.isOpened():
                    ret, test_frame = cap.read()
                    if ret and test_frame is not None:
                        print("成功连接到索引6的摄像头")
                        camera_found = True
                else:
                    print("无法打开索引6的摄像头")
            except Exception as e:
                print(f"尝试访问索引6摄像头失败: {e}")
        
        # 继续尝试更多相机索引
        if not camera_found:
            for camera_index in range(10):
                if camera_index in available_cameras:
                    continue  # 已经尝试过
                try:
                    print(f"尝试初始化扩展搜索摄像头索引 {camera_index}...")
                    cap = cv2.VideoCapture(camera_index, CAMERA_API_PREFERENCE)
                    if cap.isOpened():
                        ret, test_frame = cap.read()
                        if ret and test_frame is not None:
                            print(f"扩展搜索找到可用摄像头：索引 {camera_index}")
                            camera_found = True
                            break
                        else:
                            cap.release()
                except Exception as e:
                    print(f"扩展搜索摄像头索引 {camera_index} 失败: {e}")
                    if cap:
                        cap.release()
        
        # 最后尝试直接设备路径
        if not camera_found:
            for dev_path in ["/dev/video0", "/dev/video1", "/dev/video2", "/dev/video6"]:
                try:
                    print(f"尝试使用设备路径 {dev_path} 访问摄像头...")
                    cap = cv2.VideoCapture(dev_path, CAMERA_API_PREFERENCE)
                    if cap.isOpened():
                        ret, test_frame = cap.read()
                        if ret and test_frame is not None:
                            print(f"通过设备路径 {dev_path} 找到可用摄像头")
                            camera_found = True
                            break
                        else:
                            cap.release()
                except Exception as e:
                    print(f"尝试设备路径 {dev_path} 失败: {e}")
                    if cap:
                        cap.release()
        
        if not camera_found or not cap or not cap.isOpened():
            print("未找到可用摄像头")
            return None, False
            
        # 获取摄像头原始属性
        original_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        original_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"摄像头原始属性: {original_width}x{original_height}@{original_fps}fps")
        
        # 优化摄像头配置以提高捕获帧率
        optimize_camera_settings(cap)
        
        # 验证摄像头是否能够正常读取帧
        ret, test_frame = cap.read()
        if not ret or test_frame is None:
            print("摄像头无法读取帧，初始化失败")
            if cap:
                cap.release()
            return None, False
            
        # 获取实际的摄像头属性
        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        actual_fps = cap.get(cv2.CAP_PROP_FPS)
        actual_format = int(cap.get(cv2.CAP_PROP_FOURCC))
        
        # 将4字节格式代码转换为可读字符串
        try:
            format_chars = "".join([chr((int(actual_format) >> (8 * i)) & 0xFF) for i in range(4)])
            print(f"摄像头最终配置: {actual_width}x{actual_height}@{actual_fps}fps, 格式: {format_chars}")
        except:
            print(f"摄像头最终配置: {actual_width}x{actual_height}@{actual_fps}fps")
        
        # 测试实际帧率
        measured_fps = test_camera_fps(cap, frames=15)
        print(f"测量的实际摄像头帧率: {measured_fps:.1f} FPS")
        
        return cap, True
    except Exception as e:
        print(f"初始化摄像头失败: {e}")
        if cap:
            cap.release()
        return None, False

def optimize_camera_settings(cap):
    """
    优化摄像头设置以提高性能
    
    Args:
        cap: 摄像头对象
    
    Returns:
        success: 优化是否成功
    """
    try:
        if not cap or not cap.isOpened():
            return False
        
        # 设置缓冲区大小为1，减少延迟
        cap.set(cv2.CAP_PROP_BUFFERSIZE, CAMERA_BUFFER_SIZE)
        
        # 尝试设置目标FPS
        cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS_TARGET)
        
        # 尝试不同的编码格式，优先使用MJPG
        best_format = None
        best_fps = 0
        
        for fourcc_code in CAMERA_FOURCC_OPTIONS:
            try:
                fourcc = cv2.VideoWriter_fourcc(*fourcc_code)
                cap.set(cv2.CAP_PROP_FOURCC, fourcc)
                # 读取一帧测试格式是否生效
                ret, test = cap.read()
                if ret:
                    # 测试这个格式下的帧率
                    test_fps = test_camera_fps(cap, frames=10)
                    print(f"{fourcc_code} 格式下测得帧率: {test_fps:.1f} FPS")
                    
                    if test_fps > best_fps:
                        best_fps = test_fps
                        best_format = fourcc_code
            except Exception as e:
                print(f"设置 {fourcc_code} 格式失败: {e}")
        
        if best_format:
            print(f"选择最佳格式: {best_format} 帧率: {best_fps:.1f} FPS")
            # 再次设置最佳格式
            fourcc = cv2.VideoWriter_fourcc(*best_format)
            cap.set(cv2.CAP_PROP_FOURCC, fourcc)
        
        # 尝试不同的分辨率以找到最佳性能
        resolutions_to_try = [(640, 480), (480, 360), (320, 240)]
        
        for width, height in resolutions_to_try:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # 检查设置是否成功
            actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            
            print(f"尝试设置分辨率 {width}x{height}, 实际: {actual_width}x{actual_height}")
            
            # 只有在成功设置到接近目标分辨率时才进行测试
            if abs(actual_width - width) < 30 and abs(actual_height - height) < 30:
                ret, test = cap.read()
                if ret:
                    fps = test_camera_fps(cap, frames=10)
                    print(f"分辨率 {width}x{height} 下测得帧率: {fps:.1f} FPS")
                    
                    # 如果帧率超过15fps就可以使用这个分辨率
                    if fps >= 15:
                        print(f"选择分辨率 {width}x{height} 帧率足够")
                        break
        
        return True
    except Exception as e:
        print(f"优化摄像头设置失败(非致命错误): {e}")
        return False

def test_camera_fps(cap, frames=20, use_separate_grab=True):
    """
    测试摄像头的实际FPS
    
    Args:
        cap: 摄像头对象
        frames: 测试帧数
        use_separate_grab: 是否使用分离的grab/retrieve操作
    
    Returns:
        fps: 实际帧率
    """
    if not cap or not cap.isOpened():
        return 0
        
    # 丢弃前几帧以稳定摄像头
    for _ in range(5):
        cap.grab()
        
    # 测量获取指定数量帧所需的时间
    start_time = time.time()
    frames_read = 0
    
    for _ in range(frames):
        if use_separate_grab:
            if cap.grab():
                _, _ = cap.retrieve()
                frames_read += 1
        else:
            ret, _ = cap.read()
            if ret:
                frames_read += 1
    
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    if elapsed_time > 0 and frames_read > 0:
        return frames_read / elapsed_time
    else:
        return 0

def resize_frame(frame, target_width, target_height, method='resize'):
    """
    调整帧大小，支持普通缩放和跳采样
    
    Args:
        frame: 原始帧
        target_width: 目标宽度
        target_height: 目标高度
        method: 'resize'或'subsampling'
    
    Returns:
        resized_frame: 调整大小后的帧
    """
    if frame is None:
        return None
    
    if method == 'subsampling':
        # 使用跳采样保持原始视角
        h, w = frame.shape[:2]
        
        # 计算跳采样间隔
        step_x = max(1, w // target_width)
        step_y = max(1, h // target_height)
        
        # 进行跳采样
        subsampled = frame[::step_y, ::step_x]
        
        # 如果跳采样后的尺寸与目标尺寸不完全匹配，进行最小程度的缩放调整
        actual_h, actual_w = subsampled.shape[:2]
        if actual_w != target_width or actual_h != target_height:
            return cv2.resize(subsampled, (target_width, target_height), 
                             interpolation=cv2.INTER_NEAREST)
        
        return subsampled
    else:
        # 使用传统缩放方法
        return cv2.resize(frame, (target_width, target_height))

def find_available_cameras():
    """
    查找系统中所有可用的摄像头并返回可用的索引列表
    
    Returns:
        available_cameras: 可用摄像头索引列表
    """
    available_cameras = []
    
    # 尝试前10个摄像头索引
    for i in range(10):
        try:
            cap = cv2.VideoCapture(i, CAMERA_API_PREFERENCE)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"摄像头索引 {i} 可用，分辨率: {frame.shape[1]}x{frame.shape[0]}")
                    available_cameras.append(i)
                else:
                    print(f"摄像头索引 {i} 打开成功但无法读取帧")
            cap.release()
        except Exception as e:
            print(f"测试摄像头索引 {i} 失败: {e}")
    
    if available_cameras:
        print(f"找到 {len(available_cameras)} 个可用摄像头: {available_cameras}")
    else:
        print("未找到任何可用摄像头")
    
    return available_cameras