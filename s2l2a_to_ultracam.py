# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 11:05:36 2023

@author: Manchun LEI

Package name:
    none
Module name:
    s2l2a_to_ultracam
    ---------------
    band transformation, Sentinel-2 A/B L2A to UltraCam
"""
import argparse
import os
import sys
import glob
import numpy as np
from osgeo import gdal,osr
import cv2
import imageio.v2 as imageio

INVALID = -10000

def multi_band_transformation(datas,Ts):
    ny,nx = datas[0].shape
    res = np.zeros([ny,nx])
    for i in range(len(datas)):
        res += datas[i]*Ts[i]
    return res

def ultracam_b(srcpath,header,sensor,tmp_dstpath):
    if sensor=='A':
        T = 0.97086669 #B2, 10m, s2a
    elif sensor=='B':
        T = 0.97129836 #B2, 10m, s2b
    else:
        print("Warning, incorrect sensor name!")
        return False
    
    srcfile = os.path.join(srcpath,header+'_B2.tif')    
    src = gdal.Open(srcfile)
    tsf = src.GetGeoTransform()
    proj = src.GetProjection()
    dtype = src.GetRasterBand(1).DataType
    nx = src.RasterXSize
    ny = src.RasterYSize
    array = src.GetRasterBand(1).ReadAsArray()
    src = None
        
    res = array.astype(float)*T
    
    maskfile = os.path.join(tmp_dstpath,'mask_R1.tif')
    mask = cv2.imread(maskfile,cv2.IMREAD_UNCHANGED)
    mask1 = (res>0)*(mask>0)
    res[mask1==0] = INVALID
    
    dstfile = os.path.join(tmp_dstpath,header+'_UC.B.tif')
    driver = gdal.GetDriverByName('GTiff')
    dst = driver.Create(dstfile,nx,ny,1,dtype)
    dst.SetGeoTransform(tsf)
    dst.SetProjection(proj)
    dst.GetRasterBand(1).WriteArray(res)
    dst.FlushCache()
    dst = None
    print('UltraCam blue channel done')
    return True

def ultracam_g(srcpath,header,sensor,tmp_dstpath):    
    if sensor=='A':
        Ts = [0.34913303,0.63495627,0.01866673] #[B2,B3,B4], 10m, s2a
    elif sensor=='B':
        Ts = [0.34435740,0.63423135,0.02418108] #[B2,B3,B4], 10m, s2b
    else:
        print("Warning, incorrect sensor name!")
        return False
    
    datas = []
    srcfile = os.path.join(srcpath,header+'_B2.tif')    
    src = gdal.Open(srcfile)
    tsf = src.GetGeoTransform()
    proj = src.GetProjection()
    dtype = src.GetRasterBand(1).DataType
    nx = src.RasterXSize
    ny = src.RasterYSize
    array = src.GetRasterBand(1).ReadAsArray()
    src = None
    datas.append(array.astype(float))    
    
    for bname in ['B3','B4']:    
        srcfile = os.path.join(srcpath,header+'_'+bname+'.tif') 
        src = gdal.Open(srcfile)
        array = src.GetRasterBand(1).ReadAsArray()
        src = None
        datas.append(array.astype(float))
        
    res = multi_band_transformation(datas,Ts)
    
    maskfile = os.path.join(tmp_dstpath,'mask_R1.tif')
    mask = cv2.imread(maskfile,cv2.IMREAD_UNCHANGED)
    mask1 = (res>0)*(mask>0)
    res[mask1==0] = INVALID
    
    dstfile = os.path.join(tmp_dstpath,header+'_UC.G.tif')
    driver = gdal.GetDriverByName('GTiff')
    dst = driver.Create(dstfile,nx,ny,1,dtype)
    dst.SetGeoTransform(tsf)
    dst.SetProjection(proj)
    dst.GetRasterBand(1).WriteArray(res)
    dst.FlushCache()
    dst = None
    print('UltraCam green channel done')
    return True

def ultracam_r(srcpath,header,sensor,tmp_dstpath):
    if sensor=='A':
        Ts = [0.21497731,0.75052792,0.03294420] #[B3,B4,B5], 20m, s2a
    elif sensor=='B':
        Ts = [0.21389771,0.74952970,0.03500057] #[B3,B4,B5], 20m, s2b
    else:
        print("Warning, incorrect sensor name!")
        return False
    
    datas = []
    srcfile = os.path.join(srcpath,header+'_B5.tif')    
    src = gdal.Open(srcfile)
    tsf = src.GetGeoTransform()
    proj = src.GetProjection()
    dtype = src.GetRasterBand(1).DataType
    nx = src.RasterXSize
    ny = src.RasterYSize
    array_b5 = src.GetRasterBand(1).ReadAsArray()
    src = None
    
    for bname in ['B3','B4']:
        srcfile = os.path.join(srcpath,header+'_'+bname+'.tif') 
        src = gdal.Open(srcfile)
        array = src.GetRasterBand(1).ReadAsArray()
        array = cv2.resize(array.astype(float),(nx,ny),interpolation=cv2.INTER_AREA)
        src = None
        datas.append(array)
    
    datas.append(array_b5.astype(float))
    
    res = multi_band_transformation(datas,Ts)
    
    maskfile = os.path.join(tmp_dstpath,'mask_R2.tif')
    mask = cv2.imread(maskfile,cv2.IMREAD_UNCHANGED)
    mask1 = (res>0)*(mask>0)
    res[mask1==0] = INVALID
    
    dstfile = os.path.join(tmp_dstpath,header+'_UC.R.tif')
    driver = gdal.GetDriverByName('GTiff')
    dst = driver.Create(dstfile,nx,ny,1,dtype)
    dst.SetGeoTransform(tsf)
    dst.SetProjection(proj)
    dst.GetRasterBand(1).WriteArray(res)
    dst.FlushCache()
    dst = None
    print('UltraCam red channel done')
    return True


def ultracam_n(srcpath,header,sensor,tmp_dstpath):
    if sensor=='A':
        Ts = [0.02496498,0.22020289,0.27045367,0.20769001,0.27688184] #[B4,B5,B6,B7,B8A], 20m, s2a
    elif sensor=='B':
        Ts = [0.02510620,0.21460815,0.26341978,0.21363374,0.28344226] #[B4,B5,B6,B7,B8A], 20m, s2b
    else:
        print("Warning, incorrect sensor name!")
        return False
    
    datas = []
    srcfile = os.path.join(srcpath,header+'_B8A.tif')    
    src = gdal.Open(srcfile)
    tsf = src.GetGeoTransform()
    proj = src.GetProjection()
    dtype = src.GetRasterBand(1).DataType
    nx = src.RasterXSize
    ny = src.RasterYSize
    array_b8a = src.GetRasterBand(1).ReadAsArray()
    src = None
    
    srcfile = os.path.join(srcpath,header+'_B4.tif') 
    src = gdal.Open(srcfile)
    array = src.GetRasterBand(1).ReadAsArray()
    array = cv2.resize(array.astype(float),(nx,ny),interpolation=cv2.INTER_AREA)
    src = None
    datas.append(array)
    
    for bname in ['B5','B6','B7']:
        srcfile = os.path.join(srcpath,header+'_'+bname+'.tif') 
        src = gdal.Open(srcfile)
        array = src.GetRasterBand(1).ReadAsArray()
        src = None
        datas.append(array.astype(float))
    
    datas.append(array_b8a.astype(float))
    
    res = multi_band_transformation(datas,Ts)
    
    maskfile = os.path.join(tmp_dstpath,'mask_R2.tif')
    mask = cv2.imread(maskfile,cv2.IMREAD_UNCHANGED)
    mask1 = (res>0)*(mask>0)
    res[mask1==0] = INVALID
        
    dstfile = os.path.join(tmp_dstpath,header+'_UC.N.tif')
    driver = gdal.GetDriverByName('GTiff')
    dst = driver.Create(dstfile,nx,ny,1,dtype)
    dst.SetGeoTransform(tsf)
    dst.SetProjection(proj)
    dst.GetRasterBand(1).WriteArray(res)
    dst.FlushCache()
    dst = None
    print('UltraCam nir channel done')
    return True


def a_or_b(data_name):
    return data_name[9]

def mask_image(srcpath,data_name,tmp_dstpath):
    maskpath = os.path.join(srcpath,'MASKS')
    exts = ['_CLM','_MG2','_SAT']
    ress = ['_R1','_R2']
    for res in ress:
        ext = exts[0]
        file = os.path.join(maskpath,data_name+ext+res+'.tif')
        img = cv2.imread(file,cv2.IMREAD_UNCHANGED)
        mask = img==0
        for ext in exts[1:]:
            file = os.path.join(maskpath,data_name+ext+res+'.tif')
            img = imageio.imread(file)
            mask = mask*(img==0)
        #save result in tmp_dstpath
        dstfile = os.path.join(tmp_dstpath,'mask'+res+'.tif')
        cv2.imwrite(dstfile,(255*mask).astype(np.uint8))


def to_epsg2154(dstpath,header):
    tmp_dstpath = os.path.join(dstpath,'tmp')
    for bname in ['UC.B','UC.G','UC.R','UC.N']:
        srcfile = os.path.join(tmp_dstpath,header+'_'+bname+'.tif')
        src = gdal.Open(srcfile)
        tsf = src.GetGeoTransform()
        ps = tsf[1]
        proj = src.GetProjection()
        srs = osr.SpatialReference(wkt=proj)
        in_crs = 'Unkown'
        if srs.IsProjected:
            in_crs = str(srs.GetAuthorityName(None))+':'+str(srs.GetAuthorityCode(None))
        src = None
        
        if in_crs=='Unkown':
            print('Cannot reproject to epsg2154')
            return False
        else:        
            dstfile = os.path.join(dstpath,'epsg2154_'+header+'_'+bname+'.tif')
            out_crs = 'EPSG:2154'
            gdal.Warp(dstfile,srcfile,dstSRS=out_crs,xRes=ps,yRes=ps)
    print('done')
    return True

def rgb16(dstpath,header):
    datas = [] #[R,G,B]
    srcfile = os.path.join(dstpath,'epsg2154_'+header+'_UC.R.tif')
    src = gdal.Open(srcfile)
    tsf = src.GetGeoTransform()
    proj = src.GetProjection()
    dtype = src.GetRasterBand(1).DataType
    nx = src.RasterXSize
    ny = src.RasterYSize
    array = src.GetRasterBand(1).ReadAsArray()
    src = None
    datas.append(array)
    
    for bname in ['UC.G','UC.B']:
        srcfile = os.path.join(dstpath,'epsg2154_'+header+'_'+bname+'.tif') 
        src = gdal.Open(srcfile)
        array = src.GetRasterBand(1).ReadAsArray()
        array = cv2.resize(array.astype(float),(nx,ny),interpolation=cv2.INTER_AREA)
        src = None
        datas.append(array)
    
    
    dstfile = os.path.join(dstpath,'rgb16.tif')
    driver = gdal.GetDriverByName('GTiff')
    # out_dtype = gdal.GDT_Byte
    nb = len(datas)
    dst = driver.Create(dstfile,nx,ny,nb,dtype)
    dst.SetGeoTransform(tsf)
    dst.SetProjection(proj)
    for iband in range(nb):
        dst.GetRasterBand(1+iband).WriteArray(datas[iband])
    dst.FlushCache()
    dst = None
    
def main():
    parser = argparse.ArgumentParser(description='Description of your script')
    parser.add_argument('-p', '--path', required=True, help='Specify the s2l2a_path_name',
                        default=None)
    
    parser.add_argument('-n', '--name', required=True, help='Specify the data name',
                        default=None)
    
    parser.add_argument('-d', '--dstpath', required=True, help='Specify the dst_path_name',
                        default=None)
    
    args = parser.parse_args()

    # Access the value of the argument
    src_path_name = args.path
    data_name = args.name
    dst_path_name = args.dstpath
    srcpath = os.path.join(src_path_name,data_name)

    # Your script logic here
    print(f"Input src_path_name: {src_path_name}")
    print(f"Input data_name: {data_name}")
    print(f"Input dst_path_name: {dst_path_name}")
    
    ####################################################################
    # check path
    if not os.path.exists(srcpath):
        print("{srcpath} doesn't exists")
        sys.exit(-1)
    
    dstpath = os.path.join(dst_path_name,data_name)
    if not os.path.exists(dstpath):
        os.mkdir(dstpath)
    #call band transformation prog
    tmp_dstpath = os.path.join(dstpath,'tmp')
    if not os.path.exists(tmp_dstpath):
        os.mkdir(tmp_dstpath)
        
    ####################################################################    
    print('- Create mask image')
    mask_image(srcpath,data_name,tmp_dstpath)    
    header = data_name+'_FRE'
    print('- Band transformation')
    if ultracam_b(srcpath,header,a_or_b(data_name),tmp_dstpath)==False:
        sys.exit(-1)
    if ultracam_g(srcpath,header,a_or_b(data_name),tmp_dstpath)==False:
        sys.exit(-1)
    if ultracam_r(srcpath,header,a_or_b(data_name),tmp_dstpath)==False:
        sys.exit(-1)   
    if ultracam_n(srcpath,header,a_or_b(data_name),tmp_dstpath)==False:
        sys.exit(-1)
    print('- Change projection')
    to_epsg2154(dstpath,header)
    
    ####################################################################    
    print('- Remove tmp files')
    pattern = os.path.join(tmp_dstpath,'*.tif')
    flist = glob.glob(pattern)
    for file in flist:
        os.remove(file)
    print('done')
    
    ####################################################################
    # rgb16.tif
    rgb16(dstpath,header)
    ####################################################################
    
if __name__ == '__main__':
    main()