from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

async def process_text_with_llm(url: str, title: str, content: str, api_key: str, model_name: str, prompt_template: str, vault_context_data: list, use_multipass: bool = False) -> str:
    # Security check
    if not api_key or api_key == "missing":
        return f"---\ntitle: \"{title}\"\nsource: \"{url}\"\n---\n\n# LLM Disabled\nMissing Gemini API key in Obsidian settings.\n\n{content[:500]}..."

    try:
        # Extract all unique tags from the vault context to show the LLM
        all_tags = set()
        for note in vault_context_data:
            for tag in note.get("tags", []):
                all_tags.add(tag)
        all_tags_str = ", ".join(all_tags) if all_tags else "No existing tags."

        # Format the context string for the main prompt
        context_lines = []
        for note in vault_context_data:
            tags_str = ", ".join(note.get("tags", []))
            context_lines.append(f"- {note['path']} [{tags_str}]")
        context_string = "\n".join(context_lines) if context_lines else "No notes."

        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.3,
            google_api_key=api_key
        )

        actual_prompt = prompt_template

        # --- MULTI-PASS AGENT LOGIC ---
        if use_multipass:
            classification_prompt_text = f"""
            You are a strict data classifier. Analyze the following text and select the most relevant tags from the user's existing vault tags.
            Existing Tags: {all_tags_str}
            
            Text:
            {content[:2500]}...
            
            Rules:
            1. Return ONLY a comma-separated list of tags. 
            2. Do not write full sentences.
            3. If no existing tags fit the domain, invent EXACTLY ONE new relevant tag.
            """
            class_prompt = PromptTemplate.from_template(classification_prompt_text)
            class_chain = class_prompt | llm | StrOutputParser()
            classified_tags = await class_chain.ainvoke({})
            
            # Inject a hidden strict directive into the user's template
            hidden_directive = f"""
            SYSTEM DIRECTIVE FOR LINKING AND TAGGING:
            You have already classified this text under the following tags: {classified_tags}.
            CRITICAL RULE: You are ONLY allowed to create internal [[links]] to files in the context list that share at least one of these exact tags. Do not link to unrelated domains.
            Use these tags in your YAML frontmatter.
            
            """
            actual_prompt = hidden_directive + actual_prompt

        # --- MAIN PROCESSING ---
        prompt = PromptTemplate.from_template(actual_prompt)
        chain = prompt | llm | StrOutputParser()

        result = await chain.ainvoke({
            "title": title,
            "content": content,
            "url": url,
            "vault_context": context_string
        })
        return result

    except Exception as e:
        return f"# Error in LLM processing\nCheck that your template uses the correct variables ({{title}}, {{url}}, {{content}}, {{vault_context}}). Avoid single curly braces outside of variables.\n\n**Details:** {str(e)}"
