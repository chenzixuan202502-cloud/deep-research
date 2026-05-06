# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
from typing import List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

from src.config.loader import get_str_env

logger = logging.getLogger(__name__)

history_router = APIRouter(prefix="/history", tags=["history"])

DATABASE_URL = get_str_env(
    "DATABASE_URL",
    "mysql+pymysql://flask:123456@172.16.16.199:3306/model_test?charset=utf8mb4"
)

# 配置连接池参数，避免数据库断连问题
# - pool_recycle: 每小时回收连接（小于 MySQL 的 wait_timeout 默认 8 小时）
# - pool_pre_ping: 使用前检查连接有效性
# - pool_size: 最小连接数
# - max_overflow: 最大额外连接数
# - pool_timeout: 获取连接超时时间
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True,
    pool_timeout=30,
)


# ============== 响应模型 ==============

class NewChatResponse(BaseModel):
    success: bool
    chat_seq: Optional[int] = None
    message: Optional[str] = None


# ============== 响应模型 ==============

class HistoryItem(BaseModel):
    chat_seq: str
    question: str
    time: Optional[str] = None


class HistoryResponse(BaseModel):
    success: bool
    items: List[HistoryItem] = []
    message: Optional[str] = None


class HistoryDetailMessage(BaseModel):
    question_seq: str
    question: str
    answer: Optional[str] = None


class HistoryDetailResponse(BaseModel):
    success: bool
    messages: List[HistoryDetailMessage] = []
    message: Optional[str] = None


# ============== API 路由 ==============

def _detect_time_column(conn, table_name: str) -> Optional[str]:
    """探测表中实际存在的时间字段名，返回第一个找到的，没有则返回 None"""
    candidates = ["create_time", "created_at", "createTime", "time", "timestamp"]
    sql = text(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :tbl AND COLUMN_NAME IN :cols"
    )
    rows = conn.execute(sql, {"tbl": table_name, "cols": tuple(candidates)}).fetchall()
    found = {row[0] for row in rows}
    for c in candidates:
        if c in found:
            return c
    return None


@history_router.get("", response_model=HistoryResponse)
async def get_history(user_id: str = Query(..., description="用户工号")):
    """
    获取用户的聊天历史记录

    流程:
    1. 根据 user_id 查询 User_chat_history，获取所有 chat_seq
    2. 对每个 chat_seq，从 Chat_detail_history 中查询 question_seq 最小的那条问题
    3. 返回历史记录列表（按时间倒序，若无时间字段则按 chat_seq 倒序）
    """
    logger.info(f"Fetching history for user_id: {user_id}")

    try:
        with engine.connect() as conn:
            # 探测 User_chat_history 是否有时间字段
            time_col = _detect_time_column(conn, "User_chat_history")
            logger.info(f"User_chat_history time column: {time_col}")

            # 第一步：查询该用户的所有 chat_seq
            if time_col:
                order_clause = f"`{time_col}` DESC"
                chat_sql = text(
                    f"SELECT chat_seq, `{time_col}` FROM `User_chat_history` "
                    f"WHERE user_id = :uid ORDER BY `{time_col}` DESC"
                )
            else:
                order_clause = "chat_seq DESC"
                chat_sql = text(
                    "SELECT chat_seq FROM `User_chat_history` "
                    "WHERE user_id = :uid ORDER BY chat_seq DESC"
                )

            chat_rows = conn.execute(chat_sql, {"uid": user_id}).fetchall()

            if not chat_rows:
                logger.info(f"No chat history found for user_id: {user_id}")
                return HistoryResponse(success=True, items=[])

            logger.info(f"Found {len(chat_rows)} chat sessions for user_id: {user_id}")

            # 第二步：对每个 chat_seq 查询序号最小的问题
            items = []
            for row in chat_rows:
                chat_seq = row[0]
                time_val = row[1] if time_col else None

                detail_sql = text(
                    "SELECT question FROM `Chat_detail_history` "
                    "WHERE chat_seq = :seq "
                    "ORDER BY question_seq ASC LIMIT 1"
                )
                detail_row = conn.execute(detail_sql, {"seq": chat_seq}).fetchone()

                if detail_row and detail_row[0]:
                    time_str = None
                    if time_val:
                        try:
                            time_str = time_val.strftime("%Y-%m-%d %H:%M")
                        except AttributeError:
                            time_str = str(time_val)[:16]

                    items.append(
                        HistoryItem(
                            chat_seq=str(chat_seq),
                            question=detail_row[0],
                            time=time_str,
                        )
                    )

            logger.info(f"Returning {len(items)} history items for user_id: {user_id}")
            return HistoryResponse(success=True, items=items)

    except Exception as e:
        logger.exception(f"Error fetching history for user_id {user_id}: {str(e)}")
        return HistoryResponse(
            success=False,
            message="Failed to fetch history, please try again later",
        )


@history_router.get("/detail", response_model=HistoryDetailResponse)
async def get_history_detail(chat_seq: str = Query(..., description="会话序号")):
    """
    获取某次会话的完整对话详情

    查询 Chat_detail_history 表中指定 chat_seq 的所有问答记录，
    按 question_seq 升序返回。

    参数:
        chat_seq: 会话序号

    返回:
        对话消息列表，每项包含 question_seq、question 和 answer
    """
    logger.info(f"Fetching detail for chat_seq: {chat_seq}")

    try:
        with engine.connect() as conn:
            sql = text(
                "SELECT question_seq, question, answer "
                "FROM `Chat_detail_history` "
                "WHERE chat_seq = :seq "
                "ORDER BY question_seq ASC"
            )
            rows = conn.execute(sql, {"seq": chat_seq}).fetchall()

            if not rows:
                logger.info(f"No detail found for chat_seq: {chat_seq}")
                return HistoryDetailResponse(success=True, messages=[])

            messages = [
                HistoryDetailMessage(
                    question_seq=str(row[0]),
                    question=row[1] or "",
                    answer=row[2],
                )
                for row in rows
            ]

            logger.info(f"Returning {len(messages)} messages for chat_seq: {chat_seq}")
            return HistoryDetailResponse(success=True, messages=messages)

    except Exception as e:
        logger.exception(f"Error fetching detail for chat_seq {chat_seq}: {str(e)}")
        return HistoryDetailResponse(
            success=False,
            message="Failed to fetch detail, please try again later",
        )


@history_router.post("/new", response_model=NewChatResponse)
async def create_new_chat(user_id: str = Query(..., description="用户工号")):
    """
    创建新会话

    流程:
    1. 查询该用户当前最大的 chat_seq
    2. 如果没有记录，则返回 1；否则返回 max + 1
    3. 在 User_chat_history 中插入新记录（可选，这里先只返回 chat_seq）

    注意: 只有当产生第一个问答时，才会真正写入数据库
    """
    logger.info(f"Creating new chat for user_id: {user_id}")

    try:
        with engine.connect() as conn:
            # 查询该用户当前最大的 chat_seq
            sql = text(
                "SELECT MAX(chat_seq) FROM `User_chat_history` WHERE user_id = :uid"
            )
            result = conn.execute(sql, {"uid": user_id}).fetchone()
            max_seq = result[0] if result and result[0] is not None else 0
            new_seq = max_seq + 1

            # 插入新会话记录到 User_chat_history
            insert_sql = text(
                "INSERT INTO `User_chat_history` (user_id, chat_seq) VALUES (:uid, :seq)"
            )
            conn.execute(insert_sql, {"uid": user_id, "seq": new_seq})
            conn.commit()

            logger.info(f"Created new chat_seq: {new_seq} for user_id: {user_id}")
            return NewChatResponse(success=True, chat_seq=new_seq)

    except Exception as e:
        logger.exception(f"Error creating new chat for user_id {user_id}: {str(e)}")
        return NewChatResponse(
            success=False,
            message="Failed to create new chat, please try again later",
        )


# ============== 可直接调用的创建新会话函数 ==============

def create_new_chat_session(user_id: str) -> int | None:
    """
    直接创建新会话并返回 chat_seq（供其他模块调用）

    参数:
        user_id: 用户工号

    返回:
        int | None: 成功返回新的 chat_seq，失败返回 None
    """
    try:
        with engine.connect() as conn:
            # 查询该用户当前最大的 chat_seq
            sql = text(
                "SELECT MAX(chat_seq) FROM `User_chat_history` WHERE user_id = :uid"
            )
            result = conn.execute(sql, {"uid": user_id}).fetchone()
            max_seq = result[0] if result and result[0] is not None else 0
            new_seq = max_seq + 1

            # 插入新会话记录到 User_chat_history
            insert_sql = text(
                "INSERT INTO `User_chat_history` (user_id, chat_seq) VALUES (:uid, :seq)"
            )
            conn.execute(insert_sql, {"uid": user_id, "seq": new_seq})
            conn.commit()

            logger.info(f"Created new chat_seq: {new_seq} for user_id: {user_id}")
            return new_seq

    except Exception as e:
        logger.exception(f"Error creating new chat for user_id {user_id}: {str(e)}")
        return None


@history_router.post("/save", response_model=NewChatResponse)
async def save_chat_message(
    user_id: str = Query(..., description="用户工号"),
    chat_seq: int = Query(..., description="会话序号"),
    question: str = Query(..., description="问题内容"),
    answer: str = Query("", description="回答内容"),
):
    """
    保存问答消息到数据库

    流程:
    1. 查询该 chat_seq 当前最大的 question_seq
    2. 如果没有记录，则 question_seq = 1；否则 question_seq = max + 1
    3. 插入到 Chat_detail_history 表
    """
    logger.info(f"Saving message for chat_seq: {chat_seq}, question: {question[:50]}...")

    try:
        with engine.connect() as conn:
            # 查询该 chat_seq 当前最大的 question_seq
            sql = text(
                "SELECT MAX(question_seq) FROM `Chat_detail_history` WHERE chat_seq = :seq"
            )
            result = conn.execute(sql, {"seq": chat_seq}).fetchone()
            max_seq = result[0] if result and result[0] is not None else 0
            new_seq = max_seq + 1

            # 插入问答记录
            insert_sql = text(
                "INSERT INTO `Chat_detail_history` "
                "(chat_seq, question_seq, question, answer) "
                "VALUES (:chat_seq, :question_seq, :question, :answer)"
            )
            conn.execute(insert_sql, {
                "chat_seq": chat_seq,
                "question_seq": new_seq,
                "question": question,
                "answer": answer,
            })
            conn.commit()

            logger.info(f"Saved message: chat_seq={chat_seq}, question_seq={new_seq}")
            return NewChatResponse(success=True, chat_seq=chat_seq)

    except Exception as e:
        logger.exception(f"Error saving message for chat_seq {chat_seq}: {str(e)}")
        return NewChatResponse(
            success=False,
            message="Failed to save message, please try again later",
        )


# ============== 可直接调用的保存函数 ==============

def save_chat_message_to_db(
    user_id: str,
    chat_seq: int,
    question: str,
    answer: str,
) -> bool:
    """
    直接保存问答消息到数据库（供其他模块调用）

    参数:
        user_id: 用户工号
        chat_seq: 会话序号
        question: 问题内容
        answer: 回答内容

    返回:
        bool: 是否保存成功
    """
    try:
        with engine.connect() as conn:
            # 查询该 chat_seq 当前最大的 question_seq
            sql = text(
                "SELECT MAX(question_seq) FROM `Chat_detail_history` WHERE chat_seq = :seq"
            )
            result = conn.execute(sql, {"seq": chat_seq}).fetchone()
            max_seq = result[0] if result and result[0] is not None else 0
            new_seq = max_seq + 1

            # 插入问答记录
            insert_sql = text(
                "INSERT INTO `Chat_detail_history` "
                "(chat_seq, question_seq, question, answer) "
                "VALUES (:chat_seq, :question_seq, :question, :answer)"
            )
            conn.execute(insert_sql, {
                "chat_seq": chat_seq,
                "question_seq": new_seq,
                "question": question,
                "answer": answer,
            })
            conn.commit()

            logger.info(f"Saved message: chat_seq={chat_seq}, question_seq={new_seq}")
            return True

    except Exception as e:
        logger.exception(f"Error saving message for chat_seq {chat_seq}: {str(e)}")
        return False


# ============== 可直接调用的获取历史函数 ==============

def get_chat_history(chat_seq: int) -> list[tuple[str, str]]:
    """
    获取指定会话的历史问答记录（供其他模块调用）

    参数:
        chat_seq: 会话序号

    返回:
        list[tuple[str, str]]: 历史问答列表，每个元素是 (question, answer) 元组
    """
    try:
        with engine.connect() as conn:
            sql = text(
                "SELECT question, answer FROM `Chat_detail_history` "
                "WHERE chat_seq = :seq ORDER BY question_seq ASC"
            )
            rows = conn.execute(sql, {"seq": chat_seq}).fetchall()
            return [(row[0] or "", row[1] or "") for row in rows]
    except Exception as e:
        logger.exception(f"Error getting history for chat_seq {chat_seq}: {str(e)}")
        return []
