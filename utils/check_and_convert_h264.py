import os
import subprocess
import sys

# 支持的视频文件扩展名
VIDEO_EXTS = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.webm']

def is_h264(filepath):
    """
    检查视频文件是否为 h264 (avc1) 编码
    """
    try:
        # ffprobe 检查编码
        cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_name,codec_tag_string',
            '-of', 'default=noprint_wrappers=1:nokey=1', filepath
        ]
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
        lines = output.strip().split('\n')
        if len(lines) >= 1:
            codec = lines[0].strip().lower()
            # h264/avc1
            if codec == 'h264':
                return True
        return False
    except Exception as e:
        print(f"[ERROR] 检查编码失败: {filepath}，原因: {e}")
        return False

def convert_to_h264(filepath, out_dir=None):
    """
    将视频转码为 h264 (avc1) 编码，输出到 out_dir（默认同目录，文件名加 _h264）
    """
    base, ext = os.path.splitext(os.path.basename(filepath))
    if out_dir is None:
        out_dir = os.path.dirname(filepath)
    out_path = os.path.join(out_dir, f"{base}_h264{ext}")
    cmd = [
        'ffmpeg', '-y', '-i', filepath,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-c:a', 'copy', out_path
    ]
    try:
        print(f"[INFO] 转码: {filepath} -> {out_path}")
        subprocess.check_call(cmd)
        return out_path
    except Exception as e:
        print(f"[ERROR] 转码失败: {filepath}，原因: {e}")
        return None

def check_and_convert_folder(folder):
    """
    检查并转码文件夹下所有视频文件
    """
    for root, _, files in os.walk(folder):
        for fname in files:
            if any(fname.lower().endswith(ext) for ext in VIDEO_EXTS):
                fpath = os.path.join(root, fname)
                if is_h264(fpath):
                    print(f"[OK] 已是 h264 编码: {fpath}")
                    pass
                else:
                    print(f"[WARN] 非 h264，准备转码: {fpath}")
                    convert_to_h264(fpath)

def main():
    # if len(sys.argv) < 2:
    #     print("用法: python check_and_convert_h264.py <视频文件夹>")
    #     sys.exit(1)
    # folder = sys.argv[1]
    # if not os.path.isdir(folder):
    #     print(f"[ERROR] 目录不存在: {folder}")
    #     sys.exit(1)

    # folder = "/mnt/data/ai-ground/dataset/LLaVA-Video-large-swift/videos"
    folder = "/mnt/data/ai-ground/dataset/LLaVA-Video-large-swift/videos/academic_source/ego4d"
    check_and_convert_folder(folder)

if __name__ == "__main__":
    main() 