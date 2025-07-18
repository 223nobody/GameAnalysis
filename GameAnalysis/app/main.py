from flask import Flask, render_template
from api_routes import api_bp, load_game_data

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

@app.route('/charts')
def charts():
    return render_template('charts.html')

@app.route('/history')
def history():
    """预测历史记录页面"""
    return render_template('history.html')

if __name__ == "__main__":
    # 加载游戏数据
    if load_game_data():
        print("启动Flask应用...")
        app.run(debug=True, host='127.0.0.1', port=5000)
    else:
        print("数据加载失败，无法启动应用")
