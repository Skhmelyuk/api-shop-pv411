from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class BurstRateThrottle(UserRateThrottle):
    """
    Короткострокове обмеження - захист від спаму
    """
    scope = 'burst'

class SustainedRateThrottle(UserRateThrottle):
    """
    Довгострокове обмеження - загальний ліміт за годину
    """
    scope = 'sustained'

class StrictAnonRateThrottle(AnonRateThrottle):
    """
    Більш суворе обмеження для анонімних користувачів
    """
    scope = 'strict_anon'

class PremiumUserRateThrottle(UserRateThrottle):
    """
    Більше запитів для преміум користувачів
    """
    scope = 'premium'
    
    def allow_request(self, request, view):
        # Перевірка, чи користувач преміум
        # Це приклад - адаптуйте під вашу логіку
        if hasattr(request.user, 'is_premium') and request.user.is_premium:
            return super().allow_request(request, view)
        # Для звичайних користувачів використовуємо стандартний ліміт
        return super().allow_request(request, view)