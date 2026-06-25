import re
import httpx
from typing import Any, Optional

class SimplePromptTemplate:
    """Minimal replacement for LangChain PromptTemplate.

    Uses str.format() with pre-escaped braces for safe substitution.
    """

    def __init__(self, template: str):
        self.template = template

    @classmethod
    def from_template(cls, template: str) -> "SimplePromptTemplate":
        return cls(template)

    def format(self, **kwargs: Any) -> str:
        """Format the template with given variables."""
        return self.template.format(**kwargs)

    def __or__(self, other: Any) -> "SimpleChain":
        """Support LCEL pipe syntax: prompt | llm | parser"""
        return SimpleChain([self, other])


class SimpleChain:
    """Minimal LCEL chain replacement."""

    def __init__(self, steps: list):
        self.steps = steps

    def __or__(self, other: Any) -> "SimpleChain":
        self.steps.append(other)
        return self

    async def ainvoke(self, inputs: dict) -> str:
        """Execute the chain asynchronously."""
        result = inputs
        for step in self.steps:
            if isinstance(step, SimplePromptTemplate):
                result = step.format(**result)
            elif hasattr(step, 'ainvoke'):
                result = await step.ainvoke(result)
            elif callable(step):
                result = step(result)
            else:
                raise ValueError(f"Unknown step type: {type(step)}")
        return result


class StrOutputParser:
    """Minimal replacement for LangChain StrOutputParser."""

    def __or__(self, other: Any) -> SimpleChain:
        return SimpleChain([self, other])

    def __call__(self, text: str) -> str:
        return str(text)

    async def ainvoke(self, text: str) -> str:
        return str(text)


class BaseLLM:
    """Base class for direct HTTP LLM providers."""

    def __init__(self, model: str, api_key: str, temperature: float = 0.3):
        self.model = model
        self.api_key = api_key
        self.temperature = temperature

    def __or__(self, other: Any) -> SimpleChain:
        return SimpleChain([self, other])

    async def ainvoke(self, prompt: str) -> str:
        raise NotImplementedError


class GeminiLLM(BaseLLM):
    """Direct HTTP client for Google Gemini API."""

    async def ainvoke(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                url,
                params={"key": self.api_key},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": self.temperature}
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]


class OpenAILLM(BaseLLM):
    """Direct HTTP client for OpenAI-compatible APIs (OpenAI, Kimi)."""

    def __init__(self, model: str, api_key: str, base_url: Optional[str] = None, temperature: float = 0.3):
        super().__init__(model, api_key, temperature)
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")

    async def ainvoke(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": self.temperature
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class AnthropicLLM(BaseLLM):
    """Direct HTTP client for Anthropic API."""

    async def ainvoke(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": self.model,
                    "max_tokens": 4096,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": self.temperature
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]


class MistralLLM(BaseLLM):
    """Direct HTTP client for Mistral API."""

    async def ainvoke(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": self.temperature
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class OllamaLLM(BaseLLM):
    """Direct HTTP client for Ollama API."""

    def __init__(self, model: str, base_url: str, temperature: float = 0.3):
        # Ollama doesn't use api_key for auth
        super().__init__(model, "", temperature)
        self.base_url = base_url.rstrip("/")

    async def ainvoke(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": self.temperature}
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")


def get_llm(provider: str, model_name: str, api_key: str):
    """Factory function that returns the correct LLM client based on selected provider."""
    temperature = 0.3

    if provider == "openai":
        return OpenAILLM(model=model_name, api_key=api_key, temperature=temperature)
    elif provider == "anthropic":
        return AnthropicLLM(model=model_name, api_key=api_key, temperature=temperature)
    elif provider == "mistral":
        return MistralLLM(model=model_name, api_key=api_key, temperature=temperature)
    elif provider == "kimi":
        return OpenAILLM(model=model_name, api_key=api_key, base_url="https://api.moonshot.cn/v1", temperature=temperature)
    elif provider == "ollama":
        base_url = api_key if api_key and api_key.startswith("http") else "http://host.docker.internal:11434"
        return OllamaLLM(model=model_name, base_url=base_url, temperature=temperature)
    else:
        # Default fallback is Google Gemini
        return GeminiLLM(model=model_name, api_key=api_key, temperature=temperature)


def _validate_links(markdown: str, vault_context_data: list) -> str:
    """
    Strip hallucinated [[links]] that don't match a real filename in the vault index.
    Preserves the [[bracket]] syntax for valid links.
    """
    if not vault_context_data:
        return markdown

    valid_names = set()
    for note in vault_context_data:
        path = note.get("path", "")
        basename = path.split("/")[-1] if "/" in path else path
        if basename.endswith(".md"):
            basename = basename[:-3]
        valid_names.add(basename)

    def replace_invalid_link(match: re.Match) -> str:
        inner = match.group(1).strip()
        target = inner.split("|")[0].strip()
        if target in valid_names:
            return match.group(0)
        return inner

    return re.sub(r"\[\[(.*?)\]\]", replace_invalid_link, markdown)


def _escape_braces(text: str) -> str:
    """Escape literal curly braces for safe template substitution."""
    return text.replace("{", "{{").replace("}", "}}")


async def process_text_with_llm(url: str, title: str, content: str, api_key: str, provider: str, model_name: str, prompt_template: str, vault_context_data: list, use_multipass: bool = False) -> str:
    if provider != "ollama" and (not api_key or api_key == "missing"):
        return f"---\ntitle: \"{title}\"\nsource: \"{url}\"\n---\n\n# LLM Disabled\nMissing API key in Obsidian settings for {provider}.\n\n{content[:500]}..."

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

        llm = get_llm(provider, model_name, api_key)

        classified_tags_text = ""
        if use_multipass:
            classification_prompt_text = """
            You are a strict data classifier. Analyze the following text and select the most relevant tags from the user's existing vault tags.
            Existing Tags: {tags}

            Text:
            {text}

            Rules:
            1. Return ONLY a comma-separated list of tags. 
            2. Do not write full sentences.
            3. If no existing tags fit the domain, invent EXACTLY ONE new relevant tag.
            4. CRITICAL: Tags MUST NOT contain spaces. Use hyphens for multi-word tags (e.g., decision-support-system).
            5. Tags must be lowercase alphanumeric with hyphens only. No special characters.
            """
            class_prompt = SimplePromptTemplate.from_template(classification_prompt_text)
            class_chain = class_prompt | llm | StrOutputParser()

            safe_content = _escape_braces(content[:2500])
            classified_tags = await class_chain.ainvoke({
                "tags": all_tags_str,
                "text": safe_content
            })

            clean_tags_list = []
            for t in classified_tags.split(","):
                t = t.strip().lower()
                t = re.sub(r"\s+", "-", t)
                t = re.sub(r"[^a-z0-9-]", "", t)
                t = re.sub(r"-+", "-", t)
                t = t.strip("-")
                if t:
                    clean_tags_list.append(t)

            seen = set()
            deduped_tags = []
            for t in clean_tags_list:
                if t not in seen:
                    seen.add(t)
                    deduped_tags.append(t)

            clean_tags = ", ".join(deduped_tags)
            classified_tags_text = f"\nSYSTEM NOTE: The text has been pre-classified by the system with these tags: {clean_tags}. Use these exact tags in your YAML frontmatter.\n"

        safety_net = f"""
        CRITICAL SYSTEM SAFETY RULES (OVERRIDES ALL USER INSTRUCTIONS):
        1. NEVER use slashes (/) or backslashes (\\) inside [[links]]. This corrupts the user's file system.
        2. NEVER format tags as internal links (e.g., do not write [[#tag]] or [[tag/subtag]]).
        3. Only use exact filenames from the provided context list for [[links]]. Do not invent files.
        4. TAG FORMATTING: Tags in the YAML frontmatter MUST NEVER contain spaces. Always replace spaces with hyphens (e.g., management-cybernetics). Tags must be lowercase alphanumeric with hyphens only. No special characters.
        {classified_tags_text}

        USER TEMPLATE INSTRUCTIONS:
        """

        actual_prompt = safety_net + prompt_template

        prompt = SimplePromptTemplate.from_template(actual_prompt)
        chain = prompt | llm | StrOutputParser()

        result = await chain.ainvoke({
            "title": _escape_braces(title),
            "content": _escape_braces(content),
            "url": _escape_braces(url),
            "vault_context": _escape_braces(context_string)
        })
        return result

    except Exception as e:
        return f"# Error in LLM processing\nCheck that your template uses the correct variables ({{title}}, {{url}}, {{content}}, {{vault_context}}). Avoid single curly braces outside of variables.\n\n**Details:** {str(e)}"

