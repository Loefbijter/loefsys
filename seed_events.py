import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loefsys.settings')
django.setup()

from loefsys.events.models import Event
from loefsys.events.models.choices import EventCategories

def seed():
    # Make timezone aware dates
    now = timezone.now()
    
    # 1. Sintercantus (Open for registration)
    sintercantus_start = timezone.make_aware(datetime(2025, 12, 6, 20, 0))
    sintercantus_end = timezone.make_aware(datetime(2025, 12, 6, 23, 59))
    
    Event.objects.filter(slug='sintercantus').delete()
    
    e1 = Event.objects.create(
        title="Sintercantus",
        slug="sintercantus",
        description="De jaarlijkse Sintercantus! Zing mee met de beste Sinterklaasliedjes onder het genot van een biertje.",
        start=sintercantus_start,
        end=sintercantus_end,
        registration_start=sintercantus_start - timedelta(days=20),
        registration_deadline=sintercantus_start - timedelta(days=1),
        cancelation_deadline=sintercantus_start - timedelta(days=3),
        category=EventCategories.LEISURE,
        capacity=50,
        price=10.00,
        fine=5.00,
        location="De Villa",
        is_open_event=True,
        published=True
    )
    print(f"Created event: {e1.title} (Open)")

    # 2. Full Event
    full_start = now + timedelta(days=5)
    Event.objects.filter(slug='zeilkamp-vol').delete()
    e2 = Event.objects.create(
        title="Zeilkamp (Vol)",
        slug="zeilkamp-vol",
        description="Een fantastisch weekend zeilen. Dit evenement is helemaal volgeboekt!",
        start=full_start,
        end=full_start + timedelta(days=2),
        registration_start=now - timedelta(days=20),
        registration_deadline=now + timedelta(days=1),
        cancelation_deadline=now - timedelta(days=1),
        category=EventCategories.SAILING,
        capacity=2, # Very low capacity so we can fill it
        price=45.00,
        location="Friesland",
        is_open_event=False,
        published=True
    )
    # Fill it up
    from loefsys.members.models import User
    from loefsys.events.models import EventRegistration
    
    # ensure we have at least 2 users
    admin, _ = User.objects.get_or_create(email="admin@loefbijter.nl", defaults={"first_name": "Admin", "last_name": "User"})
    user2, _ = User.objects.get_or_create(email="test@loefbijter.nl", defaults={"first_name": "Test", "last_name": "User"})
    
    EventRegistration.objects.get_or_create(event=e2, contact=admin, defaults={"price_at_registration": e2.price, "fine_at_registration": e2.fine, "costs_paid": 0.00})
    EventRegistration.objects.get_or_create(event=e2, contact=user2, defaults={"price_at_registration": e2.price, "fine_at_registration": e2.fine, "costs_paid": 0.00})
    print(f"Created event: {e2.title} (Full)")

    # 3. Closed Event
    closed_start = now + timedelta(days=10)
    Event.objects.filter(slug='gesloten-borrel').delete()
    e3 = Event.objects.create(
        title="Gesloten Borrel",
        slug="gesloten-borrel",
        description="De inschrijvingen voor deze borrel zijn helaas al gesloten.",
        start=closed_start,
        end=closed_start + timedelta(hours=4),
        registration_start=now - timedelta(days=20),
        registration_deadline=now - timedelta(days=1), # Deadline passed
        cancelation_deadline=now - timedelta(days=2),
        category=EventCategories.LEISURE,
        capacity=100,
        price=0.00,
        location="Café de Fuik",
        is_open_event=True,
        published=True
    )
    print(f"Created event: {e3.title} (Closed)")

if __name__ == '__main__':
    seed()
