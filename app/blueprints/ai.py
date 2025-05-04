from flask import Blueprint, stream_with_context, Response, request

from app.api.qweather.weather import get_weather_now
from app.api.map import get_location
from app.extensions import generate

ai_blueprint = Blueprint("ai", __name__)


@ai_blueprint.route("/generate", methods=["POST"])
def generate_api():
    data = request.get_json()
    location = data.get("location", "秦皇岛")
    messages = data.get("messages", [])
    max_length = data.get("max_length", 500)

    # 构建历史对话内容
    history_text = ""
    for msg in messages:
        role = "用户" if msg["role"] == "user" else "助手"
        history_text += f"{role}: {msg['content']}\n"

    # 构造 prompt（在历史后追加任务说明）
    prompt = f"{history_text}\n"
    prompt += f"你现在是秦皇岛的一位本地向导，以热情、口语化的语气回答用户的咨询，像和朋友聊天一样自然。不要说自己是导游，也不要提及任何API、数据来源或‘根据接口返回’等表述。\n"
    prompt += f"如果用户不是第一次询问，就不要重复寒暄打招呼，但保持友好、亲切的语气。\n"
    prompt += f"用户的核心关注点是：{location}。请优先基于你对秦皇岛的了解，回答用户具体提出的问题或需求，提供实用、丰富的建议或介绍。你的回答应以用户的问题为中心，内容生动、贴合实际场景，特别注重历史文化背景和当地美食推荐（例如，提及景点的历史故事或附近的特色小吃）。\n"
    prompt += f"以下信息可作为补充，仅在与用户问题相关且能自然融入时使用，不要直接引用或堆砌数据：\n"
    prompt += f"1. 实时天气：{get_weather_now(location)}（例如，可提醒用户带伞或防晒，但不要让天气主导回答）。\n"
    prompt += f"2. 位置信息：{get_location(location)}（例如，可提取历史文化或美食特色融入介绍，但不要照搬）。\n"
    prompt += f"如果这些信息与用户问题无关或不足以回答，就忽略它们，基于你对秦皇岛的通用知识或推测，提供自然、合理的回答。避免生硬提及数据，确保回答流畅、贴合本地特色。\n"
    prompt += f"特别注意：如果用户提到具体景点（如鸽子窝公园），尽量围绕其历史渊源、文化故事或周边美食展开介绍，推荐相关活动或体验（如看日出、品尝海鲜）。如果用户问题较泛泛，主动提供历史文化或美食相关的建议，激发兴趣。\n"

    @stream_with_context
    def generate_stream():
        for chunk in generate(prompt, max_length):
            yield chunk

    return Response(generate_stream(), content_type='text/plain; charset=utf-8')
