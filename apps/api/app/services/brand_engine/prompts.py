from pydantic import BaseModel, Field
from typing import Optional, Any

class PromptTemplate(BaseModel):
    prompt_id: str
    version: str
    provider: str = "gemini"
    temperature: float = 0.7
    system_prompt: str
    user_prompt: str
    output_schema: dict = Field(default_factory=dict)
    industry: str
    language: str = "en"

class PromptEngine:
    """Manages compilation and versioning of AI generation prompts."""
    
    def __init__(self):
        # Default prompt template metadata
        self.default_template = PromptTemplate(
            prompt_id="nomen_names_generator_v1",
            version="1.0.0",
            provider="gemini",
            temperature=0.75,
            system_prompt=(
                "You are the Nomen Brand Intelligence naming agent. Generate creative, brandable, "
                "unique, and easy-to-pronounce startup names based on the user description."
            ),
            user_prompt=(
                "Generate {target_count} startup names for a brand in the '{industry}' industry. "
                "Context: {context}. Target syllable count constraint: {syllable_limit}."
            ),
            output_schema={
                "type": "array",
                "items": {"type": "string", "maxLength": 18, "minLength": 2}
            },
            industry="general",
            language="en"
        )
        
    def get_template(self, industry: str) -> PromptTemplate:
        """Retrieves prompt template matches for target industry or fallback."""
        template = self.default_template.model_copy()
        template.industry = industry
        return template
        
    def compile_prompt(self, industry: str, context: str, target_count: int, syllable_limit: Optional[int] = None) -> PromptTemplate:
        """Injects contextual details into prompt templates and returns full metadata details."""
        template = self.get_template(industry)
        limit_str = f"{syllable_limit} syllables" if syllable_limit else "any length"
        
        # Compile user prompt
        compiled_user = template.user_prompt.format(
            target_count=target_count,
            industry=industry,
            context=context,
            syllable_limit=limit_str
        )
        template.user_prompt = compiled_user
        return template
