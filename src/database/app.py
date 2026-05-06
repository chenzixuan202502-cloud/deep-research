# Flask 应用入口文件：负责创建应用、加载配置、注册蓝图
# 说明：按功能模块拆分蓝图以保持代码清晰、便于维护
from flask import Flask
from flask_cors import CORS
from models import db
from api.admin import admin_bp
from api.user import user_bp
from api.register import register_bp
from api.message import message_bp
from api.chat_history import chat_history_bp
from api.chat_detail import chat_detail_bp
from api.model_answer import model_answer_bp
from api.like import like_bp
from api.neural_config import neural_config_bp
from api.model_manager import model_manager_bp
from api.role_manager import role_manager_bp
from api.dialog_manager import dialog_manager_bp
from api.scenarios_manager import scenarios_manager_bp


from api.knowledge_manager import knowledge_manager_bp

from api.arena import arena_bp
from api.arena_feedback import arena_feedback_bp
from api.chat_detail_feedback import chat_detail_feedback_bp
from api.export import export_bp
from api.qa_upload import qa_upload_bp
from api.multi_model_manager import multi_model_bp
from api.teach_chat import teach_chat_bp
#from ai_prompt.search.search import search_bp

from ai_prompt.search.tavily_search import tavily_search_bp
from ai_prompt.search.search_chain import search_chain_bp
from ai_prompt.search.database_search_chain import database_search_bp
from ai_prompt.search.combined_search import combined_search_bp
#from ai_prompt.search.ai_brief_answer import ai_brief_bp
import os

# 创建 Flask 应用，静态资源目录为 `static`
app = Flask(__name__, static_folder='static')
# 启用跨域访问，允许所有来源；生产环境建议收敛到可信域名
CORS(app, resources={r"/*": {"origins": "*"}})

# 全局配置：会话与请求超时，静态文件缓存
# 设置 Flask 应用的超时配置
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1小时，会话在无活动后失效
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 关闭静态文件缓存，便于开发调试

# 设置请求/响应超时时间为25分钟（1500秒）
app.config['REQUEST_TIMEOUT'] = 1500
app.config['RESPONSE_TIMEOUT'] = 1500

# 深度搜索类任务超时（与搜索链路相关）
app.config['DEEP_SEARCH_TIMEOUT'] = 1500

class Config(object):
    # 配置对象：集中管理数据库与扩展配置
    # 优先从环境变量读取数据库配置；若未设置则使用默认值（仅用于开发/内网环境）
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        "mysql+pymysql://flask:123456@172.16.16.199:3306/model_test?charset=utf8mb4"
    )
    # SQLAlchemy 是否追踪对象修改（会有额外开销）；如无必要可关闭
    SQLALCHEMY_TRACK_MODIFICATIONS = True

# 加载配置对象并初始化数据库连接
app.config.from_object(Config)
db.init_app(app)

# 蓝图注册：按功能模块挂载到统一 `/api` 前缀
# 基础与用户管理
app.register_blueprint(admin_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(register_bp, url_prefix='/api')
app.register_blueprint(message_bp, url_prefix='/api')
# 对话与答案流
app.register_blueprint(chat_history_bp, url_prefix='/api')
app.register_blueprint(chat_detail_bp, url_prefix='/api')
app.register_blueprint(model_answer_bp, url_prefix='/api')
app.register_blueprint(like_bp, url_prefix='/api')
# 模型/配置管理
app.register_blueprint(neural_config_bp, url_prefix='/api')
app.register_blueprint(model_manager_bp, url_prefix='/api')
app.register_blueprint(role_manager_bp, url_prefix='/api')
app.register_blueprint(dialog_manager_bp, url_prefix='/api')
app.register_blueprint(scenarios_manager_bp, url_prefix='/api')
# 知识库管理
app.register_blueprint(knowledge_manager_bp, url_prefix='/api')

# 评测与反馈
app.register_blueprint(arena_bp, url_prefix='/api')
app.register_blueprint(arena_feedback_bp, url_prefix='/api')
app.register_blueprint(chat_detail_feedback_bp, url_prefix='/api')

# 工具与数据
app.register_blueprint(export_bp, url_prefix='/api')
app.register_blueprint(qa_upload_bp, url_prefix='/api')
app.register_blueprint(multi_model_bp, url_prefix='/api')
app.register_blueprint(teach_chat_bp, url_prefix='/api')
# app.register_blueprint(search_bp, url_prefix='/api')  # 旧搜索入口（已禁用）

# 搜索能力
app.register_blueprint(tavily_search_bp, url_prefix='/api')
app.register_blueprint(search_chain_bp, url_prefix='/api')
app.register_blueprint(database_search_bp, url_prefix='/api')
app.register_blueprint(combined_search_bp, url_prefix='/api')
# app.register_blueprint(ai_brief_bp, url_prefix='/api')  # 简答入口（已禁用）

# 意图识别
from api.intent import intent_bp
app.register_blueprint(intent_bp, url_prefix='/api')

if __name__ == "__main__":
    # 启动参数来自环境变量，可通过部署配置注入
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 8000))
    # 当 `FLASK_ENV=development` 时启用调试模式
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    # 运行应用
    
    app.run(host=host, port=port, debug=debug)