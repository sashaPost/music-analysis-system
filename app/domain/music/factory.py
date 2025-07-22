from app.domain.music.interfaces.music_provider import MusicProvider
from app.domain.music.providers.spotify_oauth import SpotifyOAuthService

PROVIDERS: dict[str, type[MusicProvider]] = {
    "spotify": SpotifyOAuthService,
    # future: "apple": AppleMusicOAuthService,
}


def get_provider(provider_id: str) -> MusicProvider:
    """
    Factory function to get the appropriate music provider instance.
    
    Args:
        provider_id (str): The ID of the music provider.
        
    Returns:
        MusicProvider: An instance of the requested music provider.
    """
    try:
        return PROVIDERS[provider_id.lower()]()
    except KeyError:
        raise ValueError(f"Unsupported music provider: {provider_id}")
    except Exception as e:
        raise RuntimeError(
            f"Failed to create provider instance for {provider_id}: {e}"
        ) from e
    