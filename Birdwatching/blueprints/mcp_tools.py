import asyncio
from flask import Blueprint, session
from Birdwatching.mcp_client.py import MCPClient

tools_bp = Blueprint("tools", __name__)


async def async_get_user_post_count(user_id: int) -> str:
    client = MCPClient()
    await client.connect_to_server("/home/ec2-user/mcp_server/mcp_server.py")

    result = await client.call_tool(
        "get_user_post_count_text",
        {"user_id": user_id}
    )

    await client.cleanup()

    return result.content[0].text


@tools_bp.route("/my_posts_count")
def my_posts_count():
    user_id = session.get("user_id")
    if not user_id:
        return "Yoy login first dude"

    text = asyncio.run(async_get_user_post_count(user_id))
    return text
