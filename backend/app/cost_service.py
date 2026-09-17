from typing import Dict, Any
from app.config import settings

def calculate_costs_and_metrics(
    prompt_tokens: int,
    completion_tokens: int,
    video_duration_sec: float,
    elapsed_time_sec: float,
    model_name: str
) -> Dict[str, Any]:
    """
    Computes exact variable cost per operation and itemized resource breakdown.
    Pricing assumptions:
    - Gemini 2.0 Flash: $0.10 per 1M input tokens, $0.40 per 1M output tokens.
    - Llama 3.2 11B Vision: $0.055 per 1M input, $0.055 per 1M output tokens.
    - Hosting/Compute (CPU FFmpeg): ~$0.0001 per run (assumed c6i.large equivalent $0.085/hr).
    """
    # Pricing rates per 1M tokens
    input_rate = settings.INPUT_TOKEN_PRICE_PER_M
    output_rate = settings.OUTPUT_TOKEN_PRICE_PER_M
    
    # Adjust for known models if different
    if "llama-3.2" in model_name.lower():
        input_rate = 0.055
        output_rate = 0.055
    elif "gemini-2.0-flash" in model_name.lower():
        input_rate = 0.10
        output_rate = 0.40
    
    input_cost = (prompt_tokens / 1_000_000.0) * input_rate
    output_cost = (completion_tokens / 1_000_000.0) * output_rate
    hosting_compute_cost = (elapsed_time_sec / 3600.0) * 0.085 # Standard cloud compute assumption
    total_variable_cost = round(input_cost + output_cost, 6)

    return {
        "variable_cost_usd": total_variable_cost,
        "token_usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        },
        "processing_time_sec": round(elapsed_time_sec, 2),
        "cost_breakdown": {
            "model_name": model_name,
            "input_tokens_cost_usd": round(input_cost, 6),
            "output_tokens_cost_usd": round(output_cost, 6),
            "estimated_compute_hosting_usd": round(hosting_compute_cost, 6),
            "pricing_assumptions": f"Input: ${input_rate}/1M tokens, Output: ${output_rate}/1M tokens"
        }
    }
