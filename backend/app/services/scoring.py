import random
from app.models.score import ScoreMatrix

def calculate_scores(content: str) -> ScoreMatrix:
    # Normalize signal strength based on content length
    # Max length considered for normalization is 1000 characters
    signal_strength = min(len(content) / 1000.0, 1.0)
    
    historical_rarity = random.uniform(0.3, 0.8)
    trend_acceleration = random.uniform(0.0, 1.0)
    cross_source_presence = random.uniform(0.0, 1.0)
    
    # Uncertainty is inversely proportional to signal strength
    uncertainty = 1.0 - signal_strength
    
    return ScoreMatrix(
        signal_strength=signal_strength,
        historical_rarity=historical_rarity,
        trend_acceleration=trend_acceleration,
        cross_source_presence=cross_source_presence,
        uncertainty=uncertainty
    )
