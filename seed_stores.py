import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gau_shala.settings')
django.setup()

from inventory.models import MedicalStore

stores = [
    ("Shreeji Health Care", "9723235678, 9444947108"),
    ("Noble Drugs & Medical Stores", "9825181392"),
    ("Kayvee Aeropharm Pvt Ltd", "9825144504"),
    ("Manglam Surgicare", "9558899382"),
    ("Animal Care Centre Trust", "9998984564"),
    ("Lalji Medical Agency", "9925958529"),
    ("Surveshwary Private Ltd", "8401444044"),
]

for name, contact in stores:
    MedicalStore.objects.get_or_create(name=name, defaults={'contact_no': contact})

print("Successfully seeded medical stores.")
