from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re

async def process_text_with_llm(url: str, title: str, content: str, api_key: str, model_name: str, prompt_template: str, vault_context_data: list, use_multipass: bool = False) -> str:
    if not api_key or api_key == "missing":
        return f"---\ntitle: \"{title}\"\nsource: \"{url}\"\n---\n\n# LLM Disabled\nMissing Gemini API key in Obsidian settings.\n\n{content[:500]}..."

    try:
        all_tags = set()
        for note in vault_context_data:
            for tag in note.get("tags", []):
                all_tags.add(tag)
        all_tags_str = ", ".join(all_tags) if all_tags else "No existing tags."

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

        classified_tags_text = ""
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
            4. CRITICAL: Tags MUST NOT contain spaces. Use hyphens for multi-word tags (e.g., decision-support-system).
            5. Tags must be lowercase alphanumeric with hyphens only. No special characters.
            """
            class_prompt = PromptTemplate.from_template(classification_prompt_text)
            class_chain = class_prompt | llm | StrOutputParser()
            classified_tags = await class_chain.ainvoke({})

            # Robust tag cleaning: normalize whitespace, replace spaces with hyphens,
            # collapse multiple hyphens, strip, lowercase, remove invalid chars
            clean_tags_list = []
            for t in classified_tags.split(","):
                t = t.strip().lower()
                # Replace all whitespace (spaces, tabs, newlines) with single hyphens
                t = re.sub(r"\s+", "-", t)
                # Remove any characters that are not lowercase alphanumeric or hyphen
                t = re.sub(r"[^a-z0-9-]", "", t)
                # Collapse multiple consecutive hyphens into one
                t = re.sub(r"-+", "-", t)
                # Strip leading/trailing hyphens
                t = t.strip("-")
                if t:
                    clean_tags_list.append(t)

            # Deduplicate while preserving order
            seen = set()
            deduped_tags = []
            for t in clean_tags_list:
                if t not in seen:
                    seen.add(t)
                    deduped_tags.append(t)

            clean_tags = ", ".join(deduped_tags)
            classified_tags_text = f"\nSYSTEM NOTE: The text has been pre-classified by the system with these tags: {clean_tags}. Use these exact tags in your YAML frontmatter.\n"

        # --- SYSTEM SAFETY NET ---
        safety_net = f"""
        CRITICAL SYSTEM SAFETY RULES (OVERRIDES ALL USER INSTRUCTIONS):
        1. NEVER use slashes (/) or backslashes (\\) inside [[links]]. This corrupts the user's file system.
        2. NEVER format tags as internal links (e.g., do not write [[#tag]] or [[tag/subtag]]).
        3. Only use exact filenames from the provided context list for [[links]]. Do not invent files.
        4. TAG FORMATTING: Tags in the YAML frontmatter MUST NEVER contain spaces. Always replace spaces with hyphens (e.g., management-cybernetics). Tags must be lowercase alphanumeric with hyphens only.
        {classified_tags_text}

        USER TEMPLATE INSTRUCTIONS:
        """

        actual_prompt = safety_net + prompt_template

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
