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
            # base_prompt = """Based on this context:
            # {context}

            # {style_instruction} {query}{instruction}
            
            # Focus on creating a flowing story with clear progression and connections between ideas. Each sentence should naturally lead to the next, maintaining narrative coherence while being concise and informative.
            # Count your total words carefully before submitting. If your narrative exceeds 150 words, revise it to fit within the 100-150 word limit while preserving the most important information.
            # Narrative:"""
            base_prompt = """Based on the following context:
{context}

{style_instruction} {query}{instruction}

As an expert, your task is to craft a precise, factually accurate narrative using only the provided context. Ensure your narrative reflects deep subject matter expertise and avoids any unverified details. Create a flowing story with clear progression between ideas, where each sentence naturally leads to the next while remaining concise and informative. Maintain a tone of authority and factual precision throughout. Count your total words carefully before submitting; if your narrative exceeds 150 words, revise it to fit within the 100-150 word limit while preserving the most essential information.
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
        try:
            sentences = [s.strip() for s in story.split('.') if s.strip()]
            image_prompts = []

            style_map = {
                "Historical": "vintage. antique. period.",
                "Biography": "portrait. candid. iconic",
                "Cinematic": "dramatic. scenic. cinematography"
            }
            # Retrieve style details or default to "Cinematic"
            style_guide = style_map.get(style_guide, "Cinematic")

            # Modified system prompt that includes the complete story context.
            system_prompt = f"""You are an expert prompt engineer for AI image generation using PHI.
Using the complete story context provided, transform the following sentence into a vivid, detailed, and visually rich prompt that can be directly used by an image generation model.
Incorporate any relevant character names, cultural or ethnic details, and context from the full story.
Include specific visual details such as setting, mood, lighting, style, and key objects.
**Important:** Retain all specific details, including proper names and key objects, exactly as mentioned in the sentence and context. Do not substitute these details with names or items from other contexts.
Ensure the refined prompt is strictly between 20 and 30 words, and do not add any extra commentary."""

            for sentence in sentences:
                input_prompt = f"""{system_prompt}
    Complete Story Context: "{story}"
    Sentence: "{sentence}"

    Brief image prompt:"""

                inputs = self.tokenizer(
                    input_prompt,
                    return_tensors="pt",
                    truncation=True,
                    padding=True
                ).to(self.device)

                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=50,
                    min_length=10,
                    temperature=temperature,
                    top_p=0.85,
                    top_k=40,
                    repetition_penalty=1.3,
                    do_sample=True,
                    num_return_sequences=1,
                    no_repeat_ngram_size=2
                )

                generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                prompt = generated_text.split("Brief image prompt:")[-1].strip()

                # Append the chosen style guide to the prompt
                prompt = f"{prompt}, {style_guide}"
                image_prompts.append(prompt)

            return image_prompts

        except Exception as e:
            print(f"Error generating image prompts: {str(e)}")
            return []