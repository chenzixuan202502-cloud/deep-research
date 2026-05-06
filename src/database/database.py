from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Admin(db.Model):
    __tablename__ = 'admin'
    work_id = db.Column(db.String(32), primary_key=True, comment='work_id')
    password = db.Column(db.String(128), nullable=False, comment='password')

class User(db.Model):
    __tablename__ = 'user'
    work_id = db.Column(db.String(32), primary_key=True, comment='work_id')
    password = db.Column(db.String(128), nullable=False, comment='password')
    name = db.Column(db.String(100), nullable=True, comment='姓名')
    email = db.Column(db.String(100), nullable=True, comment='邮箱')
    register_time = db.Column(db.DateTime, nullable=True, comment='注册时间')
    last_login_time = db.Column(db.DateTime, nullable=True, comment='最近登录时间')
    edit_permission = db.Column(db.Boolean, default=False, comment='修改权限')
    last_role_name = db.Column(db.String(100), comment='最近使用角色名称')


class Scenarios(db.Model):
    __tablename__ = 'scenarios_template'
    id = db.Column(db.Integer, primary_key=True, comment='id')
    scenarios_type = db.Column(db.String(255), nullable=True, comment='任务场景类型')
    template = db.Column(db.String(4096), nullable=True, comment='模板')
    work_id = db.Column(db.String(32), nullable=False, comment='work_id')
   


class Role(db.Model):
    __tablename__ = 'role'
    
    # --- 核心字段 ---
    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='角色ID')
    work_id = db.Column(db.String(32), nullable=False, index=True, comment='工作空间ID/所属项目ID')
    role_name = db.Column(db.String(100), comment='角色名称')

    # --- 模型参数字段 ---
    max_context_length = db.Column(db.Integer, comment='最大上下文长度')
    temperature = db.Column(db.Float, comment='温度参数')
    top_p = db.Column(db.Float, comment='Top P参数')
    max_length = db.Column(db.Integer, comment='最大生成长度')
    frequency_penalty = db.Column(db.Float, comment='频率惩罚')
    presence_penalty = db.Column(db.Float, comment='存在惩罚')
    system_prompt = db.Column(db.String(4096), comment='系统提示词')
    is_stream = db.Column(db.Boolean, comment='是否流式输出') # tinyint(1) 对应 Boolean

    # --- 搜索/RAG 相关字段 (Search/Knowledge Base) ---
    is_search = db.Column(db.Boolean, comment='是否启用搜索') # tinyint(1) 对应 Boolean
    is_deep_search = db.Column(db.Boolean, comment='是否启用深度搜索') # tinyint(1) 对应 Boolean
    search_method = db.Column(db.String(32), comment='搜索方法')
    search_language = db.Column(db.JSON, comment='搜索语言 (JSON)') # JSON 类型
    search_period_start = db.Column(db.Date, comment='搜索开始日期')
    search_period_end = db.Column(db.Date, comment='搜索结束日期')
    
    knowledge_base_select = db.Column(db.JSON, comment='知识库选择')
    knowledge_keyword = db.Column(db.JSON, comment='知识库关键词 (JSON)') # JSON 类型
    knowledge_search_method = db.Column(db.String(32), comment='知识库搜索方法')
    opening=db.Column(db.String(2048), comment='开场白')
    template=db.Column(db.String(4096), comment='模板')


class ModelLikesAndImpression(db.Model):
    __tablename__ = 'Model_likes_and_impression'
    model_name = db.Column(db.String(100), primary_key=True, comment='模型名字')
    model_code = db.Column(db.String(100), nullable=False, comment='模型代号')
    like_count = db.Column(db.Integer, default=0, comment='点赞数')
    dislike_count = db.Column(db.Integer, default=0, comment='点踩数')

class ModelProblemTable(db.Model):
    __tablename__ = 'Model_problem_table'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增主键')
    model_name = db.Column(db.String(100), nullable=False, comment='模型名字')
    question = db.Column(db.Text, comment='问题')
    answer = db.Column(db.Text, comment='问题回答')
    asker = db.Column(db.Integer, comment='问题提问人')
    is_modified = db.Column(db.Boolean, default=False, comment='是否修改')
    is_liked = db.Column(db.Boolean, default=False, comment='点赞')
    is_disliked = db.Column(db.Boolean, default=False, comment='点踩')

class UserChatHistory(db.Model):
    __tablename__ = 'User_chat_history'
    user_id = db.Column(db.Integer, primary_key=True, comment='用户工号')
    chat_seq = db.Column(db.Integer, primary_key=True, comment='历史对话序列号')

class ChatDetailHistory(db.Model):
    __tablename__ = 'Chat_detail_history'
    chat_seq = db.Column(db.Integer, primary_key=True, comment='历史对话序号')
    question_seq = db.Column(db.Integer, primary_key=True, comment='问题序列号')
    question = db.Column(db.Text, comment='问题')
    answer = db.Column(db.Text, comment='回答')
    is_modified = db.Column(db.Boolean, default=False, comment='修改与否')
    is_liked = db.Column(db.Boolean, default=False, comment='点赞情况')
    is_disliked = db.Column(db.Boolean, default=False, comment='点踩情况')

class ModelAnswer(db.Model):
    __tablename__ = 'Model_answer'
    model_name = db.Column(db.String(100), primary_key=True, comment='模型名称')
    chat_seq = db.Column(db.Integer, primary_key=True, comment='历史对话序号')
    question_seq = db.Column(db.Integer, primary_key=True, comment='问题序列号')
    multi_model_answer_seq = db.Column(db.Integer, nullable=True, comment='多模型回答编号')

class QuestionEvaluation(db.Model):
    __tablename__ = 'Question_evaluation'
    chat_seq = db.Column(db.Integer, primary_key=True, comment='历史对话序号')
    question_seq = db.Column(db.Integer, primary_key=True, comment='问题序列号')
    rating = db.Column(db.Integer, nullable=True, comment='问题评分')
    evaluation = db.Column(db.Text, nullable=True, comment='回答评价')

class NeuralParams(db.Model):
    __tablename__ = 'Neural_params'
    user_id = db.Column(db.Integer, primary_key=True, comment='用户工号')
    max_context_length = db.Column(db.Integer, nullable=False, default=32768, comment='最大上下文长度')
    temperature = db.Column(db.Float, nullable=False, default=0.7, comment='温度参数')
    top_p = db.Column(db.Float, nullable=False, default=0.9, comment='TopP参数')
    max_length = db.Column(db.Integer, nullable=False, default=1024, comment='最大长度')
    frequency_penalty = db.Column(db.Float, nullable=False, default=0.5, comment='舞弊系数')
    presence_penalty = db.Column(db.Float, nullable=False, default=0.5, comment='存在惩罚')
    system_prompt = db.Column(db.Text, nullable=True, comment='系统提示词')
    created_time = db.Column(db.DateTime, default=db.func.current_timestamp(), comment='创建时间')
    updated_time = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), comment='更新时间')

class QAPairs(db.Model):
    __tablename__ = 'qa_pairs'
    qa_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='QA编号')
    name = db.Column(db.String(100), nullable=False, comment='提问人姓名')
    qa_pairs_data = db.Column(db.Text, nullable=False, comment='问答对JSON数据')
    submit_time = db.Column(db.DateTime, default=db.func.current_timestamp(), comment='提交时间')


