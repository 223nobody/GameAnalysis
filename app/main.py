from flask import Flask, render_template, send_from_directory
from routes.api_routes import api_bp, load_game_data
import os
import mimetypes

# 设置Flask应用，指定模板和静态文件路径
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# 注册API蓝图
app.register_blueprint(api_bp, url_prefix='/api')

# 基本路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict')
def charts():
    return render_template('predict.html')

@app.route('/history')
def history():
    """预测历史记录页面"""
    return render_template('history.html')

@app.route('/data/<filename>')
def serve_data_file(filename):
    """提供数据文件服务（支持JSON、PNG等格式）"""
    try:
        # 获取当前文件的目录（app目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 获取项目根目录（GameAnalysis目录）
        project_root = os.path.dirname(current_dir)
        # 数据目录路径
        data_dir = os.path.join(project_root, 'data')

        # 检查文件是否存在
        file_path = os.path.join(data_dir, filename)
        if not os.path.exists(file_path):
            return f"文件不存在: {filename}", 404

        # 根据文件扩展名设置适当的MIME类型
        mimetype = None
        if filename.lower().endswith('.png'):
            mimetype = 'image/png'
        elif filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
            mimetype = 'image/jpeg'
        elif filename.lower().endswith('.json'):
            mimetype = 'application/json'

        return send_from_directory(data_dir, filename, mimetype=mimetype)
    except Exception as e:
        return f"服务器错误: {str(e)}", 500

if __name__ == "__main__":
    # 加载游戏数据
    if load_game_data():
        print("启动Flask应用...")
        app.run(debug=True, host='127.0.0.1', port=5000)
    else:
        print("数据加载失败，无法启动应用")
