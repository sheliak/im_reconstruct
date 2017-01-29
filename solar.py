import numpy as np
import pyfits
import matplotlib
from matplotlib.pyplot import *
import peakutils
import cPickle as pickle
from cheb import reconstruct

def find_center(x,y):
	"""
	Finds centre of a tramline.
	"""
	try:
		center=peakutils.peak.gaussian_fit(x, y)
	except:#sometimes the above function fails
		center=np.average(x,weights=y)

	if abs(center-np.median(x))>2: return np.median(x)#if center jumps too much, return next best thing
	else: return center

def get_moments(x,y):
	"""
	Return all moments for position (x,y)
	"""
	z=[p(x,y) for p in moments_packed]
	m=np.reshape(z,(int( np.sqrt(len(z)) ),int( np.sqrt(len(z)) )))
	return m

def get_transf_matrix(x,y,N):
	"""
	Convert moments into transformation matrix
	"""
	return np.asarray(reconstruct(N,get_moments(x,y)))

def precalculate_transf_matrix():
	"""
	Precalculates the transformation matrix, so it does not have to be done every time
	Returns position and the matrix
	"""
	t=[]
	c=[]
	for i in range(0,4100,200):
		print i
		for j in range(0,4100,200):
			m=get_transf_matrix(i,j,10)
			t.append(m)
			c.append([i,j])

	return np.array(c),t


def fit_tramlines(plot=True):
	"""
	Fits tramlines on an mage. Tramline fits are saved and the number of tramlines is returned.
	"""
	#open a twilight flat. It should have a solar spectrum in each fibre
	hdulist = pyfits.open('data/twilight_ccd3.fits')
	scidata = np.array(hdulist[0].data)

	#make a crossection of the image to find tramlines
	if plot: fig_detection=figure(1)
	if plot: ax1=fig_detection.add_subplot(111)

	if plot: fig_tramlines=figure(2)
	if plot: ax2=fig_tramlines.add_subplot(111)

	if plot: ax1.plot(np.average(scidata[:,0:10],axis=1),'k-')

	band=np.average(scidata[:,0:10],axis=1)

	tramlines_first=peakutils.indexes(band, thres=0.1, min_dist=7.0)

	tramlines_fine = peakutils.interpolate(np.arange(len(band)), band, ind=tramlines_first, width=3, func=peakutils.peak.centroid)

	if plot: ax1.plot(tramlines_fine,band[tramlines_first],'bo')

	if plot: ax2.imshow(scidata, cmap=cm.gray, origin='lower', vmax=np.percentile(scidata,99))

	tramlines=[]
	bands=[]

	tramlines.append(tramlines_fine)
	bands.append(5.0)

	#repeat for bands over the whole image
	for i in range(10,4090,10):
		band=np.average(scidata[:,i:i+10],axis=1)
		tramlines_previous=np.rint(tramlines_fine).astype(int)
		tramlines_fine = peakutils.interpolate(np.arange(len(band)), band, ind=tramlines_previous, width=2, func=find_center)

		if plot: ax2.plot(np.ones(len(tramlines_fine))*(i+5),tramlines_fine,'g.')

		tramlines.append(tramlines_fine)

		bands.append(i+5)

	tramlines=np.array(tramlines)
	bands=np.array(bands)

	fitted_tramlines=[]

	#fit tramlines with a polynomial:
	for i in range(len(tramlines_first)):
		if plot: plot(bands,tramlines[:,i],'g-')
		fitted_tramlines.append(np.polynomial.chebyshev.Chebyshev.fit(bands,tramlines[:,i],deg=5))

	#save the fits:
	out_file = open('profiles/tramlines_ccd%s.pic' % (3), 'wb')
	pickle.dump(tramlines, out_file)
	out_file.close()

	if plot: show()

	return len(tramlines_first)

def get_tramlines(ccd,plate):
	ccd=int(ccd)
	plate=int(plate)

	try:
		in_file = open('profiles/tramlines_ccd%s.pic' % (ccd), 'rb')
		tramlines=pickle.load(in_file)
		in_file.close()
		return tramlines
	except:
		print 'No tramlines have been fitted yet for ccd %s, plate %s.' % (ccd,plate)
		return None

print get_tramlines(3,0)

#open high res solar spectrum
#data=np.loadtxt("solar.txt", dtype='float', comments='#')
in_file = open('solar.pic', 'rb')
solar=pickle.load(in_file)
in_file.close()

data=solar[::4]

#select correct range:
data[:,0]=data[:,0]*10#convert from nm to A

l_range=6480
u_range=6740

data=data[(data[:,0]>l_range)&(data[:,0]<u_range)]

c,t=precalculate_transf_matrix()