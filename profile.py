"""
Calculate PSF profile over the whole image from the comb data
"""
import numpy as np

def open_comb_file(ccd,plate):
	#open comb file:
	hdulist = pyfits.open('%s-p%s-m.fits' % (int(ccd), int(plate)))
