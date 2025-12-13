from mcp.server.fastmcp import FastMCP
from Birdwatching.utils.databases import init_db_for_mcp, post_sql_select
mcp = FastMCP("mcp-server")

@mcp.tool()
def get_documentation_from_database() -> dict:
    """
    This tool returns the documentation from the database for the project. 
    It is very useful for figuring out what the project is about.
    """
    
    return {
        "title": "How to Use MCP Servers",
        "body": "This is a mocked documentation entry from the database. MCP servers expose tools and resources for AI agents.",
        "source": "mocked_database"
    }

@mcp.tool()
def get_user_post_count_text(user_id: int) -> str:
    """
    Returns a count of posts that the current user has uploaded.
    """
    result = post_sql_select(
        "SELECT COUNT(*) FROM posts WHERE user_id = :user_id",
        {"user_id": user_id}
    )
    count = result[0] if result else 0 
    return f"You published {count} posts."


if __name__ == "__main__":
    try:
        init_db_for_mcp()
    except Exception as e:
        print(f"MCP server database connection error: {e}")
        exit(1)
        
    mcp.run("stdio")