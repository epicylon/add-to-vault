from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

async def process_text_with_llm(url: str, title: str, content: str, api_key: str, model_name: str, prompt_template: str, vault_context: str = "No notes.") -> str:
    # Security check
    if not api_key or api_key == "missing":
        return f"---\ntitle: \"{title}\"\nsource: \"{url}\"\n---\n\n# LLM Disabled\nMissing Gemini API key in Obsidian settings.\n\n{content[:500]}..."

    try:
        # Initialize LLM with the user's selected model and key
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.3,
            google_api_key=api_key
        )

        # Use the template from the user's Obsidian vault
        prompt = PromptTemplate.from_template(prompt_template)
        chain = prompt | llm | StrOutputParser()

        result = await chain.ainvoke({
            "title": title,
            "content": content,
            "url": url,
            "vault_context": vault_context
        })
        return result

    except Exception as e:
        # Catch errors, e.g., if the user's template is missing required {variables}
        return f"# Error in LLM processing\nCheck that your template uses the correct variables ({{title}}, {{url}}, {{content}}, {{vault_context}}). Avoid single curly braces outside of variables (use double {{{{}}}} to escape them).\n\n**Details:** {str(e)}"
