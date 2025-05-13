import os
import logging
from typing import Optional, Dict, Any, List
import asyncio
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.model_id = os.environ.get("MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.2")
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        logger.info(f"LLM Service initializing with model: {self.model_id} on device: {self.device}")
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        
        # For local development on M3 Mac, use 8-bit quantization to reduce memory usage
        self.model = None
        self.pipe = None
        logger.info(f"LLM Service initialized with model: {self.model_id}")

    async def _load_model_if_needed(self):
        """Lazy load the model only when needed"""
        if self.pipe is None:
            logger.info(f"Loading model {self.model_id} on device {self.device}")
            
            # Use text-generation pipeline with 8-bit quantization for efficiency
            self.pipe = pipeline(
                "text-generation",
                model=self.model_id,
                tokenizer=self.tokenizer,
                torch_dtype=torch.float16,
                device_map=self.device,
            )
            logger.info("Model loaded successfully")

    async def generate(
        self, 
        prompt: str, 
        temperature: float = 0.7, 
        max_tokens: int = 1024,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response from the LLM based on the input prompt.
        """
        try:
            # Load model if not already loaded
            await self._load_model_if_needed()
            
            # Format prompt with system prompt if provided
            if system_prompt:
                formatted_prompt = f"<s>[INST] {system_prompt} [/INST]</s>[INST] {prompt} [/INST]"
            else:
                formatted_prompt = f"<s>[INST] {prompt} [/INST]"
            
            # Generate response
            logger.debug(f"Generating response for prompt: {prompt[:50]}...")
            
            # Run generation in a separate thread to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.pipe(
                    formatted_prompt,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.95,
                    top_k=50,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            )
            
            # Extract generated text
            if result and len(result) > 0:
                # Extract the generated text and remove the prompt
                generated_text = result[0]['generated_text']
                response = generated_text[len(formatted_prompt):].strip()
                logger.debug(f"Generated response: {response[:50]}...")
                return response
            else:
                logger.warning("Empty response from LLM")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            raise

    async def shutdown(self):
        """
        Clean up resources used by the LLM service.
        """
        logger.info("Shutting down LLM service")
        # Free up memory
        if self.model is not None:
            del self.model
        if self.pipe is not None:
            del self.pipe
        torch.cuda.empty_cache() if torch.cuda.is_available() else None

async def get_llm_engine():
    """
    Initialize and return the LLM engine.
    """
    try:
        logger.info("Initializing LLM engine")
        return LLMService()
        
    except Exception as e:
        logger.error(f"Failed to initialize LLM engine: {str(e)}", exc_info=True)
        raise 