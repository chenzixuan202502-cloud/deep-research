# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.config.loader import get_str_env

logger = logging.getLogger(__name__)

# 创建认证路由
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

# 数据库连接配置
DATABASE_URL = get_str_env(
    "DATABASE_URL",
    "mysql+pymysql://flask:123456@172.16.16.199:3306/model_test?charset=utf8mb4"
)

# 创建数据库引擎
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


# ============== 请求/响应模型 ==============

class LoginRequest(BaseModel):
    """登录请求"""
    work_id: str
    password: str


class UserInfo(BaseModel):
    """用户信息"""
    work_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    edit_permission: bool = False


class LoginResponse(BaseModel):
    """登录响应"""
    success: bool
    user: Optional[UserInfo] = None
    message: Optional[str] = None


class LogoutResponse(BaseModel):
    """登出响应"""
    success: bool
    message: str = "Logged out successfully"


# ============== 数据库模型 ==============

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """用户模型 - 对应数据库中的 user 表"""
    __tablename__ = 'user'

    work_id = Column(String(32), primary_key=True, comment='work_id')
    password = Column(String(128), nullable=False, comment='password')
    name = Column(String(100), nullable=True, comment='姓名')
    email = Column(String(100), nullable=True, comment='邮箱')
    register_time = Column(DateTime, nullable=True, comment='注册时间')
    last_login_time = Column(DateTime, nullable=True, comment='最近登录时间')
    edit_permission = Column(Boolean, default=False, comment='修改权限')
    last_role_name = Column(String(100), nullable=True, comment='最近使用角色名称')


# ============== API 路由 ==============

@auth_router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    用户登录接口
    
    参数:
        work_id: 用户工号/账号
        password: 密码（明文）
    
    返回:
        登录成功返回用户信息，失败返回错误信息
    """
    logger.info(f"Login attempt for work_id: {request.work_id}")
    
    try:
        with Session(engine) as session:
            # 查询用户
            stmt = select(User).where(User.work_id == request.work_id)
            user = session.scalar(stmt)
            
            if not user:
                logger.warning(f"User not found: {request.work_id}")
                return LoginResponse(
                    success=False,
                    message="Invalid username or password"
                )
            
            logger.info(f"User found: work_id={user.work_id}, stored_password={user.password}, input_password={request.password}")
            
            # 验证密码（明文比较）
            if user.password != request.password:
                logger.warning(f"Invalid password for user: {request.work_id}")
                return LoginResponse(
                    success=False,
                    message="Invalid username or password"
                )
            
            # 更新最后登录时间
            user.last_login_time = datetime.now()
            session.commit()
            
            logger.info(f"User logged in successfully: {request.work_id}")
            
            return LoginResponse(
                success=True,
                user=UserInfo(
                    work_id=user.work_id,
                    name=user.name,
                    email=user.email,
                    edit_permission=user.edit_permission or False
                )
            )
            
    except Exception as e:
        logger.exception(f"Login error for work_id {request.work_id}: {str(e)}")
        return LoginResponse(
            success=False,
            message="Login failed, please try again later"
        )


@auth_router.post("/logout", response_model=LogoutResponse)
async def logout():
    """
    用户登出接口
    
    由于使用前端 localStorage 存储认证状态，
    后端只需要返回成功响应即可
    """
    return LogoutResponse(success=True)


@auth_router.get("/me", response_model=LoginResponse)
async def get_current_user():
    """
    获取当前用户信息
    
    前端可以通过此接口验证登录状态
    """
    # TODO: 如果需要 JWT 或 session，可以在这里验证
    # 当前返回未认证状态，由前端管理登录状态
    return LoginResponse(
        success=False,
        message="Not authenticated"
    )
