# Import things that are needed generically
from pydantic import BaseModel
from langchain.tools import BaseTool, StructuredTool, tool


def search_function(query: str) -> str:
    """Look up things online."""
    return "LangChain"


customTools = [(StructuredTool.from_function(
    func= search_function,
    name= "Search",
    description= "useful for returning the user input"
))]



