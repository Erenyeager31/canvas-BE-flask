import logging
from typing import Dict, Optional, Union, List
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from app.utils.subjectExtractor import extract_subject
import re
from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from transformers import pipeline

# pip install torch==2.5.1+cu121 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
# As per colab configuration, the torch version is 1.9.0+cu102

# cpu
# pip install torch==2.2.0+cpu

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Phi2Generator:
    def __init__(self, 
                 model_name: str = "microsoft/phi-2",
                 embedding_model: str = 'sentence-transformers/all-mpnet-base-v2',
                 device: Optional[str] = None):
        try:
            self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"Using device: {self.device}")

            logger.info(f"Loading Phi-2 model: {model_name}")
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                trust_remote_code=True
            )
            logger.info("Model loaded, starting tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)

            logger.info(f"Loading embedding model: {embedding_model}")
            self.encoder = SentenceTransformer(embedding_model)

            self.model = self.model.to(self.device)

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.pipe = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=150,
                do_sample=True,
                temperature=0.7
            )
            self.llm = HuggingFacePipeline(pipeline=self.pipe)

            # Initialize LangChain components
            # self._setup_chains()

            logger.info(f"Loading complete...")
                
        except Exception as e:
            logger.error(f"Error initializing Phi2Generator: {str(e)}")
            raise

    def get_context_relevance(self, text: str, context: str) -> float:
        """
        Compute the similarity between query and context.
        """
        embeddings = self.encoder.encode([text, context])
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return similarity
    
    def generate_with_custom_instructions(
        self,
        context: str,
        query: str,
        style_guide:str="Historical",
        words_per_sentence: int = 15,
        temperature: float = 0.9,
    ) -> Dict[str, Union[str, float]]:
        try:
            # Set absolute minimum and maximum token limits
            MIN_CONTEXT_LENGTH = 50
            MAX_NEW_TOKENS = 200
            TOTAL_MAX_LENGTH = 2048
            TARGET_WORDS = 125
            
            # Ensure inputs are strings
            context = str(context) if context is not None else ""
            query = str(query) if query is not None else ""

            style_map = {
                "Historical": "Provide a historical account of",
                "Biography": "Write an inspiring biography of",
                "Cinematic": "Write a cinematic narration of"
            }
            
            # Get the appropriate style instruction or use default if style not found
            style_instruction = style_map.get(style_guide, "Provide a historical account of")
            
            # Prepare the base prompt template with emphasis on narrative flow
            sentence_instruction = (f"\nImportant: Write in a clear narrative style using approximately {words_per_sentence} words per sentence. Your response MUST be between 100-150 words total. Do not exceed 150 words." 
            if words_per_sentence else 
                "\nImportant: Write in a clear narrative style. Your response MUST be between 100-150 words total. Do not exceed 150 words.")
            base_prompt = """Based on this context:
            {context}

            {style_instruction} {query}{instruction}
            
            Focus on creating a flowing story with clear progression and connections between ideas. Each sentence should naturally lead to the next, maintaining narrative coherence while being concise and informative.
            Count your total words carefully before submitting. If your narrative exceeds 150 words, revise it to fit within the 100-150 word limit while preserving the most important information.
            Narrative:"""
            
            # Rest of the function remains the same...
            context_tokens = self.tokenizer.encode(
                context,
                add_special_tokens=False,
                truncation=True,
                max_length=TOTAL_MAX_LENGTH - MAX_NEW_TOKENS
            )
            
            if len(context_tokens) > (TOTAL_MAX_LENGTH - MAX_NEW_TOKENS - MIN_CONTEXT_LENGTH):
                context_tokens = context_tokens[:TOTAL_MAX_LENGTH - MAX_NEW_TOKENS - MIN_CONTEXT_LENGTH]
            
            truncated_context = self.tokenizer.decode(context_tokens, skip_special_tokens=True)
            
            full_prompt = base_prompt.format(
                context=truncated_context,
                query=query,
                instruction=sentence_instruction,
                style_instruction=style_instruction
            )
            
            encoded_input = self.tokenizer(
                full_prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=TOTAL_MAX_LENGTH - MAX_NEW_TOKENS
            )
            
            input_ids = encoded_input["input_ids"].to(self.device)
            attention_mask = encoded_input["attention_mask"].to(self.device)
            
            target_tokens = int(TARGET_WORDS * 1.3)
            
            outputs = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=target_tokens + 50,
                min_length=int(target_tokens * 0.8),
                max_length=int(target_tokens * 1.2),
                temperature=temperature,
                top_p=0.92,
                top_k=40,
                repetition_penalty=1.1,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                length_penalty=1.0
            )
            
            story = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            if "Narrative:" in story:
                story = story.split("Narrative:")[-1].strip()
            story = story.replace("Context:", "").replace("Query:", "").strip()
            
            relevance_score = self.get_context_relevance(query, context)
            sentences = [s.strip() for s in story.split('.') if s.strip()]
            avg_words = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
            total_words = sum(len(s.split()) for s in sentences)
            
            if total_words > 150:
                cumulative_words = 0
                truncated_sentences = []
                for sentence in sentences:
                    sentence_words = len(sentence.split())
                    if cumulative_words + sentence_words <= 150:
                        truncated_sentences.append(sentence)
                        cumulative_words += sentence_words
                    else:
                        break
                story = '. '.join(truncated_sentences) + '.'
                sentences = truncated_sentences
                total_words = cumulative_words
            
            return {
                'generated_text': story,
                # 'relevance_score': relevance_score,
                # 'avg_words_per_sentence': avg_words,
                # 'num_sentences': len(sentences),
                # 'total_words': total_words
            }
            
        except Exception as e:
            logger.error(f"Error in story generation: {str(e)}")
            return {
                'generated_text': "Error occurred during text generation.",
                'error': str(e)
            }

    def generate_concise_image_prompts(
        self,
        story: str,
        style_guide: str = "cinematic, 8k",
        max_words: int = 20,
        temperature: float = 0.7
    ) -> List[str]:
        """
        Convert a story into concise image generation prompts.

        Args:
            model: The language model (Phi-2)
            tokenizer: The model's tokenizer
            story: Input story text
            max_words: Maximum number of words per prompt
            style_guide: Brief style specifications
            temperature: Temperature for generation

        Returns:
            List of concise image generation prompts
        """
        try:
            sentences = [s.strip() for s in story.split('.') if s.strip()]
            image_prompts = []

            # Shorter system prompt encouraging brevity
            system_prompt = f"""Convert the sentence into a brief, vivid image prompt. Focus on the subject present in the Sentence.
    Use max {max_words} words.
    Focus on key visual elements only.
    End with: {style_guide}"""

            for sentence in sentences:
                input_prompt = f"""{system_prompt}

    Sentence: "{sentence}"

    Brief image prompt:"""

                inputs = self.tokenizer(
                    input_prompt,
                    return_tensors="pt",
                    truncation=True,
                    padding=True
                ).to(self.device)

                # Set stricter length limits
                outputs = self.model.generate(
                    **inputs,
                    max_length=100,  # Reduced from previous version
                    min_length=20,   # Ensure some minimum content
                    temperature=temperature,
                    top_p=0.9,
                    top_k=50,
                    repetition_penalty=1.2,
                    do_sample=True,
                    num_return_sequences=1
                )

                generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                prompt = generated_text.split("Brief image prompt:")[-1].strip()

                # Enforce word limit through post-processing
                words = prompt.split()
                if len(words) > max_words:
                    prompt = ' '.join(words[:max_words-2] + [style_guide])
                elif style_guide.lower() not in prompt.lower():
                    prompt = f"{prompt}, {style_guide}"
                    
                print(prompt)

                image_prompts.append(prompt)

            return image_prompts

        except Exception as e:
            print(f"Error generating image prompts: {str(e)}")
            return []