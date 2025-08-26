from app.domain.music.interfaces.music_provider import IMusicProvider
from app.domain.music.providers.spotify_oauth import SpotifyOAuthService


def get_provider(provider_id: str) -> IMusicProvider:
    """
    Factory function to get the appropriate music provider instance.
    
    Args:
        provider_id (str): The ID of the music provider.
        
    Returns:
        MusicProvider: An instance of the requested music provider.
    """
    match provider_id.lower():
        case "spotify":
            return SpotifyOAuthService()
        # future: case "apple":
        #     return AppleMusicOAuthService()
        case _:
            raise ValueError(f"Unsupported music provider: {provider_id}")
