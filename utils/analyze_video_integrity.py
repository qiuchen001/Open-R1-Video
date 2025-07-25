import subprocess
import json
import sys
from pathlib import Path

def analyze_video_comprehensive(video_path):
    """
    对视频文件进行多方面的完整性分析。
    
    Args:
        video_path (str): 视频文件的路径。
    """
    video_path = Path(video_path)
    if not video_path.exists():
        print(f"错误: 视频文件不存在: {video_path}")
        return

    print(f"开始分析视频: {video_path}")
    print("=" * 60)

    # 1. 使用 ffprobe 获取详细的元数据
    print("1. 正在获取视频元数据 (ffprobe)...")
    try:
        cmd = [
            'ffprobe', 
            '-v', 'quiet', 
            '-print_format', 'json', 
            '-show_format', 
            '-show_streams', 
            '-show_chapters',
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        probe_data = json.loads(result.stdout)
        
        # 打印关键信息
        format_info = probe_data.get('format', {})
        print(f"   格式: {format_info.get('format_name', 'N/A')}")
        print(f"   时长: {format_info.get('duration', 'N/A')} 秒")
        print(f"   总比特率: {format_info.get('bit_rate', 'N/A')} bps")
        print(f"   文件大小: {format_info.get('size', 'N/A')} bytes")

        streams = probe_data.get('streams', [])
        for i, stream in enumerate(streams):
            codec_type = stream.get('codec_type', 'unknown')
            print(f"   流 #{i} ({codec_type}):")
            print(f"     编码器: {stream.get('codec_name', 'N/A')}")
            if codec_type == 'video':
                print(f"     分辨率: {stream.get('width', 'N/A')}x{stream.get('height', 'N/A')}")
                print(f"     帧率: {eval(stream.get('r_frame_rate', '0')) if stream.get('r_frame_rate') else 'N/A'} fps")
                print(f"     比特率: {stream.get('bit_rate', 'N/A')} bps")
                print(f"     编码参数: {stream.get('codec_tag_string', 'N/A')}")
            elif codec_type == 'audio':
                print(f"     采样率: {stream.get('sample_rate', 'N/A')} Hz")
                print(f"     声道: {stream.get('channels', 'N/A')}")
        
    except subprocess.CalledProcessError as e:
        print(f"   ffprobe 分析失败: {e}")
    except Exception as e:
        print(f"   解析元数据时出错: {e}")

    print()

    # 2. 使用 ffmpeg 进行解码扫描，检查错误
    print("2. 正在扫描视频解码错误 (ffmpeg)...")
    try:
        cmd = [
            'ffmpeg', 
            '-v', 'error', # 只输出错误信息
            '-i', str(video_path),
            '-f', 'null', # 不输出任何文件
            '-' # 输出到空设备
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        # 如果 stderr 有输出，说明存在解码错误
        if result.stderr.strip():
            print("   发现解码错误:")
            print(result.stderr.strip())
        else:
            print("   未发现解码错误。")
    except Exception as e:
        print(f"   ffmpeg 扫描失败: {e}")

    print()

    # 3. 尝试使用 decord 加载，看是否报错
    print("3. 正在尝试使用 decord 加载...")
    try:
        import decord
        # 设置 decord 日志级别为 INFO 以获取更多信息
        decord.bridge.set_bridge('torch')
        vr = decord.VideoReader(str(video_path))
        print(f"   decord 加载成功。总帧数: {len(vr)}, FPS: {vr.get_avg_fps()}")
        # 尝试读取第一帧和最后一帧，测试随机访问
        first_frame = vr[0].asnumpy()
        last_frame = vr[-1].asnumpy()
        print("   成功读取第一帧和最后一帧。")
    except Exception as e:
        print(f"   decord 加载失败: {type(e).__name__}: {e}")

    print()

    # 4. 尝试使用 torchvision 加载，作为对比
    print("4. 正在尝试使用 torchvision 加载...")
    try:
        from torchvision import io
        video, audio, info = io.read_video(str(video_path), pts_unit='sec')
        print(f"   torchvision 加载成功。视频形状: {video.shape}, 音频形状: {audio.shape if audio is not None else 'None'}")
        print(f"   信息: {info}")
    except Exception as e:
        print(f"   torchvision 加载失败: {type(e).__name__}: {e}")

    print("=" * 60)
    print("分析完成。")

if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     print("用法: python analyze_video_integrity.py <视频文件路径>")
    #     sys.exit(1)
    
    # video_file = sys.argv[1]
    # video_file = "/mnt/data/ai-ground/dataset/LLaVA-Video-large-swift/videos/academic_source/ego4d/6606c60b-1ed9-4b78-976a-f1eb49fb1f19.mp4"
    # video_file = "/mnt/data/ai-ground/dataset/LLaVA-Video-large-swift/videos/academic_source/activitynet/v_-vKXPND_mD8.mp4"
    video_file = "/mnt/data/ai-ground/dataset/LLaVA-Video-large-swift/videos/academic_source/NextQA/1015/3026422534.mp4"

    analyze_video_comprehensive(video_file)
