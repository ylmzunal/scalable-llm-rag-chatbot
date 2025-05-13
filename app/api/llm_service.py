import os
import logging
from typing import Optional, Dict, Any, List
import asyncio
from vllm import AsyncLLMEngine, AsyncEngineArgs, SamplingParams

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, engine: AsyncLLMEngine):
        self.engine = engine
        self.model_id = os.environ.get("MODEL_ID", "mistralai/Mistral-7B-v0.1")
        logger.info(f"LLM Service initialized with model: {self.model_id}")

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
            # Format prompt with system prompt if provided
            if system_prompt:
                formatted_prompt = f"<s>[INST] {system_prompt} [/INST]</s>[INST] {prompt} [/INST]"
            else:
                formatted_prompt = f"<s>[INST] {prompt} [/INST]"
            
            # Set sampling parameters
            sampling_params = SamplingParams(
                temperature=temperature,
                max_tokens=max_tokens,
                stop=["</s>", "[/INST]"]
            )
            
            # Generate response
            logger.debug(f"Generating response for prompt: {prompt[:50]}...")
            result = await self.engine.generate(formatted_prompt, sampling_params)
            
            # Extract and return the generated text
            if result and result.outputs:
                response = result.outputs[0].text.strip()
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
        # vLLM engine doesn't require explicit cleanup

async def get_llm_engine():
    """
    Initialize and return the LLM engine.
    """
    try:
        model_id = os.environ.get("MODEL_ID", "mistralai/Mistral-7B-v0.1")
        logger.info(f"Initializing LLM engine with model: {model_id}")
        
        # Configure vLLM engine
        engine_args = AsyncEngineArgs(
            model=model_id,
            dtype="half",  # Use half precision (float16) to reduce memory usage
            tensor_parallel_size=1,  # Adjust based on available GPUs
            gpu_memory_utilization=0.85,
            max_model_len=8192,
            trust_remote_code=True
        )
        
        # Initialize the engine
        engine = AsyncLLMEngine.from_engine_args(engine_args)
        logger.info("LLM engine initialized successfully")
        
        return LLMService(engine)
        
    except Exception as e:
        logger.error(f"Failed to initialize LLM engine: {str(e)}", exc_info=True)
        raise 