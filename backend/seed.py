"""Données de départ : régions / préfectures / villes (extrait, à compléter)."""
import asyncio

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.geo import City, Prefecture, Region

DATA = {
    "Maritime": {"Golfe": [("Lomé", True)], "Zio": [("Tsévié", True)]},
    "Plateaux": {"Kloto": [("Kpalimé", True)], "Ogou": [("Atakpamé", True)]},
    "Centrale": {"Tchaoudjo": [("Sokodé", True)]},
    "Kara": {"Kozah": [("Kara", True)], "Bassar": [("Bassar", False)]},
    "Savanes": {"Tône": [("Dapaong", True)]},
}


async def main():
    async with SessionLocal() as db:
        if (await db.execute(select(Region))).first():
            print("Déjà initialisé")
            return
        for region_name, prefs in DATA.items():
            region = Region(name=region_name)
            db.add(region)
            await db.flush()
            for pref_name, cities in prefs.items():
                pref = Prefecture(name=pref_name, region_id=region.id)
                db.add(pref)
                await db.flush()
                for city_name, urban in cities:
                    db.add(City(name=city_name, is_urban=urban, prefecture_id=pref.id))
        await db.commit()
        print("Géographie initialisée")


if __name__ == "__main__":
    asyncio.run(main())
