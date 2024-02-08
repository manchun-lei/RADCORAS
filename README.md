# s2l2a_to_ultracam

## How to run from the command line

```batch
python s2l2a_to_ultracam.py -p src_path_name -n data_name -d dst_path_name
```

src_path_name: Source data path name, excluding the data name itself

data_name:  THEIA-LAND L2A data name, likes: SENTINEL2B_20230623-103858-070_L2A_T31TFJ_C_V3-1

dst_path_name: Destination path name

## Output

epsg2154_data_name_FRE_ultracam_band_name.tif

FRE: THEIA-LAND L2A product, ground reflectance with correction of slope effects

DN = FRE*10000

Invalid = -10000
