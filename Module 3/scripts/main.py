#************************************************************************
# automatisation de la manipulation des données raster
# Traitement avec Rasterio + numphy
#ouvrir un fichier raster à l'aide re rasterio
# Afficher les metadonnées principales: taille, nombre de bandes, resolution
# verifier le systeme de coordonnées (crs)
#*************************************************************************

import logging
from pathlib import Path
import rasterio
from rasterio.mask import mask
from rasterio.merge import merge
import geopandas as gpd
import numpy as np


#configuration des log
logging.basicConfig(filename=r"Module 3\logs\run.log", level=logging.INFO)

logging.info("debut du script d'extraction des rasters")

with rasterio.open(r"Module 3\data\input\ndvi.tif") as src:
    print("Dimensions:", src.width, "x", src.height)
    print("nombre de bandes:", src.count)
    print("resolution:", src.res)
    print("etendue:", src.bounds)
    print("crs:", src.crs)

#***********************************************************************
# Extraction des valeurs de raster
# charger une bande sous forme de tableau numpy
# Afficher ls valeurs minimales, maximales et moyennes
# Calcules une statistique simple (moyenne de bande)
#***********************************************************************
with rasterio.open(r"Module 3\data\input\ndvi.tif") as src:
    band =src.read(1)
    #print(band)
    #print("valeur minimale" , band.min())
    #print("valeur maximale", band.max())
    #print("la moyenne", np.mean(band))

#*************************************************************************
# Decouper un raster
# lire un shapfile
# rastterio.mask.mas() pour decouper le raster
# exporter le raster decoupé
#*************************************************************************
with rasterio.open(r"Module 3\data\input\ndvi.tif") as src:
    zone=gpd.read_file("Module 3\data\input\zone_etude.shp")
    out_image, out_transforme = mask(src, zone.geometry, crop=True)
    print(out_transforme)

    out_meta = src.meta.copy()

    out_meta.update({
        "driver": "GTIFF",
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transforme
    })

    with rasterio.open(r"Module 3\data\output\ndvi_clip.tif","w", **out_meta) as dest:
        dest.write(out_image)

#****************************************************************************************
#Fusion de plusieurs rasters -Mosaiquage
# taches: identifier tous les rasters
# Lire et fusionner les rasters avec rasterio.merge.merge()
# exporter les raster fusionné dasn un fichier de sortie
#****************************************************************************************
# 1 identification des rasters:
rasters = list(Path("Module 3/data/output").rglob("*.tif"))
src_rasters = [rasterio.open(f) for f in rasters]

# procedons à la fucion
mosaic, out_transforme = merge(src_rasters)

# On procede maintenat à l'export
out_meta = src_rasters[0].meta.copy()

out_meta.update({
        "driver": "GTIFF",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_transforme
    })

with rasterio.open(r"Module 3\data\output\mosaic.tif","w", **out_meta) as desti:
    desti.write(mosaic)

#*****************************************************************************************
# Zone statistic et reclassification
# taches: Lire un raster
# Calcul statistique (moyenne, somme, min, max) pour chaque zone
# reclasser les valeurs du raster selon des seuils definis
#*****************************************************************************************
#Lire le raster
with rasterio.open(r"Module 3\data\input\B7.tif") as src:
    band =src.read(1)

    #Procedons à la reclassification
    classified = np.where(band <0.002, 1,
                          np.where(band < 0.02, 2, 2) )
    
#exporter l'image classifiée
meta = src.meta.copy()
with rasterio.open(r"Module 3\data\output\B7_Classes.tif", "w", **meta) as destina:
    destina.write(classified, 1)


logging.info("fin du script d'extraction des valeurs du raster")