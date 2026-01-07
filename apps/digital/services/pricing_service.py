from decimal import Decimal
from typing import Dict, Any
from apps.digital.models import DigitalProduct, UserPricing
from apps.users.models import User


class PricingService:
    """
    Service class for handling pricing logic for digital products.
    """
    
    def __init__(self):
        # Default markup percentages for different user types
        self.default_markups = {
            'admin': 0,      # 0% markup for admins
            'agent': 0.05,   # 5% markup for agents
            'user': 0.10,    # 10% markup for regular users
            'reseller': 0.02 # 2% markup for resellers
        }
        
        # Default base prices (these would typically come from a database or API)
        self.default_base_prices = {
            # Data bundles
            '1GB': Decimal('50.00'),
            '2GB': Decimal('90.00'),
            '5GB': Decimal('200.00'),
            '10GB': Decimal('350.00'),
            
            # Airtime
            'airtime_10': Decimal('10.00'),
            'airtime_50': Decimal('50.00'),
            'airtime_100': Decimal('100.00'),
        }

    def get_user_price(self, user: User, product: DigitalProduct) -> Decimal:
        """
        Get the price for a user and product combination.
        
        Args:
            user: The user to get price for
            product: The product to get price for
            
        Returns:
            The price for the user
        """
        # First, check if there's a specific user pricing
        try:
            user_pricing = UserPricing.objects.get(user=user, product=product, is_active=True)
            return user_pricing.price
        except UserPricing.DoesNotExist:
            # If no specific pricing, calculate based on user type and base price
            return self._calculate_default_price(user, product)

    def _calculate_default_price(self, user: User, product: DigitalProduct) -> Decimal:
        """
        Calculate the default price for a user based on their type.
        
        Args:
            user: The user to calculate price for
            product: The product to calculate price for
            
        Returns:
            The calculated price
        """
        # Get base price - this could come from the product itself or default prices
        if product.denomination:
            base_price = product.denomination
        else:
            # Use a default price based on product code if available
            base_price = self.default_base_prices.get(product.code, Decimal('10.00'))
        
        # Get markup percentage based on user type
        markup_percentage = self.default_markups.get(user.user_type, self.default_markups['user'])
        
        # Calculate final price with markup
        markup_amount = base_price * Decimal(str(markup_percentage))
        final_price = base_price + markup_amount
        
        return final_price.quantize(Decimal('0.01'))  # Round to 2 decimal places

    def set_user_pricing(self, user: User, product: DigitalProduct, price: Decimal) -> UserPricing:
        """
        Set a specific price for a user and product combination.
        
        Args:
            user: The user to set pricing for
            product: The product to set pricing for
            price: The price to set
            
        Returns:
            The created or updated UserPricing object
        """
        user_pricing, created = UserPricing.objects.get_or_create(
            user=user,
            product=product,
            defaults={'price': price, 'is_active': True}
        )
        
        if not created:
            user_pricing.price = price
            user_pricing.is_active = True
            user_pricing.save()
        
        return user_pricing

    def get_pricing_for_user_type(self, user_type: str, product: DigitalProduct) -> Decimal:
        """
        Get the default price for a specific user type.
        
        Args:
            user_type: The type of user (admin, agent, user, reseller)
            product: The product to get price for
            
        Returns:
            The calculated price for the user type
        """
        if product.denomination:
            base_price = product.denomination
        else:
            base_price = self.default_base_prices.get(product.code, Decimal('10.00'))
        
        markup_percentage = self.default_markups.get(user_type, self.default_markups['user'])
        markup_amount = base_price * Decimal(str(markup_percentage))
        final_price = base_price + markup_amount
        
        return final_price.quantize(Decimal('0.01'))