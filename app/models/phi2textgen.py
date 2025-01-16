import logging
from typing import Dict, Optional, Union, List
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

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
        words_per_sentence: int = None,
        temperature: float = 0.9
    ) -> Dict[str, Union[str, float]]:
        """
        Generate text with a specified number of words per sentence.
        
        Args:
            context (str): The background context or information
            query (str): The specific query or task
            words_per_sentence (int): Target average words per sentence
            temperature (float): Sampling temperature
            
        Returns:
            Dict containing generated text and metadata
        """
        try:
            # Modify prompt to include sentence length instruction if specified
            sentence_instruction = ""
            if words_per_sentence:
                sentence_instruction = f"\nImportant: Use approximately {words_per_sentence} words per sentence."

            prompt = f"""Based on this historical context:
{context}

Write a historical narrative that {query}{sentence_instruction}

Your narrative should maintain consistent sentence lengths while being natural and engaging.

Narrative:"""

            tokenizer_output = self.tokenizer(
                prompt,
                padding=True,
                truncation=True,
                return_tensors="pt"
            )

            input_ids = tokenizer_output["input_ids"].to(self.device)
            attention_mask = tokenizer_output["attention_mask"].to(self.device)

            outputs = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_length=400,
                min_length=100,
                temperature=temperature,
                top_p=0.92,
                top_k=40,
                repetition_penalty=1.1,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )

            story = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            story = story.split("Narrative:")[-1].strip()
            story = story.replace("Context:", "").replace("Query:", "")

            # Calculate metrics
            relevance_score = self.get_context_relevance(query, context)
            sentences = [s.strip() for s in story.split('.') if s.strip()]
            avg_words = sum(len(s.split()) for s in sentences) / len(sentences)

            return {
                'generated_text': story,
                'relevance_score': relevance_score,
                'avg_words_per_sentence': avg_words,
                'num_sentences': len(sentences),
                'total_words': sum(len(s.split()) for s in sentences)
            }

        except Exception as e:
            logger.error(f"Error in story generation: {str(e)}")
            return {
                'generated_text': "Error occurred during text generation.",
                'error': str(e)
            }

    def generate_concise_image_prompts(
        # model,
        # tokenizer,
        self,
        story: str,
        max_words: int = 30,
        style_guide: str = "cinematic, 8k",
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
            system_prompt = f"""Convert the sentence into a brief, vivid image prompt.
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

                image_prompts.append(prompt)

            return image_prompts

        except Exception as e:
            print(f"Error generating image prompts: {str(e)}")
            return []