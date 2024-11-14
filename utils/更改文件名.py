import os
import ffmpeg
import filetype


def convert_all_videos_in_folder(input_folder, output_folder):
    """将文件夹中的所有视频文件转换为 MP4 格式"""
    for root, _, files in os.walk(input_folder):
        for file_name in files:
            # 获取文件的完整路径
            file_path = os.path.join(root, file_name)

            # 仅处理视频文件
            if file_path.lower().endswith(('.mkv', '.mov', '.avi', '.flv', '.3gp', '.wmv')):
                output_file = os.path.join(output_folder, file_name.rsplit('.', 1)[0] + '.mp4')
                print(f"正在转换 {file_path} -> {output_file}")
                try:
                    # 使用 ffmpeg 将视频转换为 mp4 格式
                    ffmpeg.input(file_path).output(output_file, vcodec='libx264', acodec='aac').run()
                    print(f"转换成功：{output_file}")
                except ffmpeg.Error as e:
                    print(f"转换失败：{e}")

# 示例：批量转换文件夹中的所有视频
input_folder = "/path/to/your/folder"  # 替换为你的输入文件夹路径
output_folder = "/path/to/output/folder"  # 替换为你的输出文件夹路径

convert_all_videos_in_folder(input_folder, output_folder)


def check_file_format(directory):
    """检查指定目录下所有文件的格式"""
    for root, _, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            # 使用 filetype 库检测文件格式
            kind = filetype.guess(file_path)
            print(kind)
            if kind is None:
                print(f"{file_path} - 无法识别文件格式")
            else:
                print(f"{file_path} - 文件格式: {kind.mime}, 扩展名: {kind.extension}")
def check_file_format_with_ffmpeg(directory):
    """使用 ffprobe 检查目录中所有文件的格式"""
    for root, _, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            try:
                # 使用 ffprobe 检查文件格式
                probe = ffmpeg.probe(file_path)
                format_name = probe['format']['format_name']
                format_long_name = probe['format']['format_long_name']
                print(f"{file_path} - 文件格式: {format_name}, 格式详细信息: {format_long_name}")
            except ffmpeg.Error as e:
                print(f"无法获取文件格式: {file_path}")
                print(e)
def delete_mp4_files(directory):
    """删除目录中所有 .mp4 文件"""
    for root, _, files in os.walk(directory):  # 遍历目录及子目录
        for file_name in files:
            if file_name.lower().endswith('.mp4'):  # 判断是否为 .mp4 文件
                file_path = os.path.join(root, file_name)
                try:
                    os.remove(file_path)  # 删除文件
                    print(f"已删除文件：{file_path}")
                except Exception as e:
                    print(f"无法删除文件 {file_path}: {e}")
if __name__ == '__main__':
    input_folder = 'K:/music'
    output_folder = 'K:/mp4'
    convert_all_videos_in_folder(input_folder,output_folder)
