from langchain.agents import Tool,tool

@tool ("search_pdf_tool",return_direct=True)
def search_pdf_tool():
    """Retrieve the most relevant PDF based on the user query."""
    # docs = retriever.get_relevant_documents(input)
    # if docs:
    #     return f"Found: {docs[0].metadata['path']}"
    return "file not found"

@tool("search_image_tool",return_direct=True)
def search_image_tool(input):
    """Retrieve an image path based on the query."""
    images = {
        "logo": "assets/school_logo.png",
        "banner": "assets/school_banner.jpg"
    }
    return images.get(input.lower(), "file not found")

def create_tools(retriever):
    """Create and return the list of tools for the agent."""
    search_pdf = Tool(
        name="Search PDF",
        func=lambda input: search_pdf_tool(input, retriever),
        description="Search and retrieve PDF files based on user query."
    )

    search_image = Tool(
        name="Search Image",
        func=search_image_tool,
        description="Retrieve images, such as the school logo or banner."
    )

    return [search_pdf, search_image]