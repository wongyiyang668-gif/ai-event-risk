import discord
from datetime import datetime

class RiskEmbedFormatter:
    """
    Utility class to format AI Analysis results into professional Discord Embeds.
    """
    
    @staticmethod
    def format_analysis(result: dict) -> discord.Embed:
        # Determine color based on risk levels
        semantics = result.get("risk_semantics", {})
        # Note: Depending on backend response, keys might be different. 
        # Checking for the highest score.
        max_risk = 0
        if isinstance(semantics, dict):
            # Try to find numeric values
            max_risk = max([v for v in semantics.values() if isinstance(v, (int, float))] or [0])
        
        color = discord.Color.red() if max_risk >= 0.6 else discord.Color.orange() if max_risk >= 0.3 else discord.Color.green()
        
        embed = discord.Embed(
            title="🔍 Risk Analysis Result",
            description=result.get("risk_summary", "No summary provided."),
            color=color,
            timestamp=datetime.utcnow()
        )
        
        # Event Details
        event_info = result.get("event", {})
        embed.add_field(name="Event ID", value=f"`{event_info.get('id', 'N/A')}`", inline=False)
        embed.add_field(name="Source", value=event_info.get("source", "N/A").capitalize(), inline=True)
        
        # Risk Semantics
        if semantics:
            risk_text = "\n".join([f"**{k.replace('_', ' ').title()}**: {v*100:.1f}%" for k, v in semantics.items() if isinstance(v, (int, float))])
            embed.add_field(name="Risk Breakdown", value=risk_text or "N/A", inline=False)
        
        # Recommendation
        embed.add_field(name="💡 Recommendation", value=result.get("recommendation", "N/A"), inline=False)
        
        embed.set_footer(text="AI Event Risk Scoring System")
        return embed

    @staticmethod
    def format_stats(stats: dict) -> discord.Embed:
        embed = discord.Embed(
            title="📊 System Statistics",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Total Events", value=str(stats.get("total_events", 0)), inline=True)
        embed.add_field(name="Manual Reviews", value=str(stats.get("total_reviews", 0)), inline=True)
        embed.add_field(name="System Status", value=f"✅ {stats.get('status', 'Operational').capitalize()}", inline=True)
        return embed

    @staticmethod
    def format_error(error_msg: str) -> discord.Embed:
        return discord.Embed(
            title="❌ Error",
            description=error_msg,
            color=discord.Color.red()
        )
