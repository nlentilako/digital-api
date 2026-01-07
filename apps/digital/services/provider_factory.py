from typing import Type, Dict
from apps.digital.providers.base_provider import BaseProvider
from apps.digital.providers.mtn_provider import MTNProvider
# Additional providers will be imported as they are created


class ProviderFactory:
    """
    Factory class to create and manage provider instances.
    """
    
    _providers: Dict[str, Type[BaseProvider]] = {
        'mtn': MTNProvider,
        # Add more providers here as they are implemented
        # 'vodafone': VodafoneProvider,
        # 'airteltigo': AirtelTigoProvider,
        # 'waec': WAECProvider,
    }

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseProvider]):
        """
        Register a new provider with the factory.
        
        Args:
            name: The name of the provider
            provider_class: The provider class to register
        """
        cls._providers[name.lower()] = provider_class

    @classmethod
    def get_provider(cls, provider_name: str) -> BaseProvider:
        """
        Get an instance of a provider by name.
        
        Args:
            provider_name: The name of the provider to instantiate
            
        Returns:
            An instance of the requested provider
            
        Raises:
            ValueError: If the provider is not registered
        """
        provider_name = provider_name.lower()
        
        if provider_name not in cls._providers:
            available_providers = ', '.join(cls._providers.keys())
            raise ValueError(f"Provider '{provider_name}' is not registered. "
                           f"Available providers: {available_providers}")
        
        provider_class = cls._providers[provider_name]
        return provider_class()

    @classmethod
    def get_available_providers(cls) -> list:
        """
        Get a list of available provider names.
        
        Returns:
            List of available provider names
        """
        return list(cls._providers.keys())