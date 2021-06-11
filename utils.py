import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import glob
import cv2

## Define object charge
class charge:

	# Constructor
	def __init__(self, m, r, v, sign):
		self.m = m
		self.sign = sign
		self.r = r
		self.v = v

	# Display properties of object charge
	def display(self):
		print("mass: " + str(self.m))
		print("sign: " + str(self.sign))
		print("location: x: " + str(self.r[0]) + " y: " + str(self.r[1]))
		print("velocity: x: " + str(self.v[0]) + " y: " + str(self.v[1]))

## Find difference between two vectors
def diff(r1, r2):

	return r1 - r2

## Find absolute value of vector
def absolute(r):

	return np.sqrt(r[0]**2 + r[1]**2)

## Calculating force
def force_calculate(c1, c2):

	# Force constants

	k = 9e9	# Electric force constant
	b = 1e-1 # Linear drag constant
	c = 1e-5 # Quadratic drag constant

	# Finding distance between charges
	r = diff(c2.r, c1.r)
	r_abs = absolute(r)
	
	if r_abs < 100:
		eforce = -k*(c1.sign*c2.sign)*r/(r_abs)**3
	else:
		eforce = np.asarray([0, 0])

	drag = -b*c1.v -c*absolute(c1.v)*c1.v

	# Returning force on c1 due to c2
	return eforce + drag

## Increment the list of charges
def increment(cs, dt):

	# Display remaining defects
	# print('Number of defects: ' + str(len(cs)))

	# Make copy of list
	out = cs.copy()

	# Annihilation

	# For every defect
	for i, c1 in enumerate(cs):

		# For every other defect
		for j, c2 in enumerate(cs):

			# If it is not the same and of opposite charge
			if i != j and c1.sign*c2.sign < 0:

				# Find distance between charges
				cr = diff(c1.r, c2.r)
				dist = absolute(cr)

				# If they are less than one pixel away
				if dist < 1:

					# Remove both charges
					if c1 in out and c2 in out:
						out.remove(c1)
						out.remove(c2)

	# Create new empty list
	cs = []

	# Force calculation
	for i, c1 in enumerate(out):

		# Acceleration vector
		a = np.asarray([0,0])

		# For every other charge
		for j, c2 in enumerate(out):

			# If it is not the same
			if i != j:

				# Add acceleration from charge c2
				a = a + (1/c1.m)*force_calculate(c1, c2)

		# Update position with force and velocity
		c1.r = c1.r + c1.v*dt + (1/2)*a*(dt**2)

		# update velocity with force
		c1.v = c1.v + a*dt

		# Add charge to output 
		cs.append(c1)

	# Return updated list of charges
	return cs

## Viewing a board
def view(cs, outDir, i=0, pad=10):

	# Board dimensions
	dims = (200,200)

	# Arrays to store positive and negative charges
	array_p, array_n = [], []

	# Sort charge positions into arrays
	for c in cs:

		# Positive chare
		if c.sign > 0:
			array_p.append(c.r)

		# Negative charge
		else:
			array_n.append(c.r)

	# Take transpose of arrays
	array_p = np.asarray(array_p).T
	array_n = np.asarray(array_n).T

	# Extract x and y positions from arrays
	x_p = array_p[0]
	y_p = array_p[1]

	x_n = array_n[0]
	y_n = array_n[1]

	# Clear plot
	plt.clf()

	# Plot both positive and negative charges
	plt.scatter(x_p, y_p, color='r', s=4)
	plt.scatter(x_n, y_n, color='b', s=4)

	# for i in range(len(x_p)):
	# 	ax.annotate('('+str(round(x_p[i],3))+', '+str(round(y_p[i],3))+')', (x_p[i], y_p[i]))

	# for i in range(len(x_n)):
	# 	ax.annotate('('+str(round(x_n[i],3))+', '+str(round(y_n[i],3))+')', (x_n[i], y_n[i]))

	# Set size of output plot
	plt.xlim([-dims[0]//2, dims[0]//2])
	plt.ylim([-dims[1]//2, dims[1]//2])

	# Add legend for charges
	red_patch = mpatches.Patch(color='red', label='Plus: '+str(len(x_p))) # positive
	blue_patch = mpatches.Patch(color='blue', label='Minus: '+str(len(x_n))) # negative
	black_patch = mpatches.Patch(color='black', alpha=0, label='Total: '+str(len(x_p)+len(x_n))) # total

	# Plot legend
	plt.legend(handles=[red_patch, blue_patch, black_patch], loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=3)
	
	# Add grid to plot
	plt.grid(True)

	# Save output
	plt.savefig('./output/'+outDir+'/'+str(i).zfill(pad)+'.tif')


## Convert frames to video
def framesToVideo(framesDir, framerate):

	print('\nLoading frames: ' + framesDir + '/*.tif')

	# Frames paths
	fPath = glob.glob(framesDir + '/*.tif')

	# If no frames found
	if len(fPath) == 0:

		print('\nNo Frames were found.')

	# If frames are found
	else:

		print('Found ' + str(len(fPath)) + ' frames.')

		# If output directory does not exist
		if len(glob.glob('output/')) == 0:

			os.mkdir('./output/')

		# Output video name
		vPath = 'output/' + framesDir.split('/')[-1] + '.avi'

		# Reading first file for size
		im0 = cv2.imread(fPath[0])

		# Extracting video size
		height, width, layers = im0.shape
		size = (width, height)

		# Output video
		out = cv2.VideoWriter(vPath, cv2.VideoWriter_fourcc(*'DIVX'), framerate, size)

		# Starting video write
		for i, filename in enumerate(fPath):

			# Displaying progress
			if i%100 == 0:

				print(str(100*i/len(fPath))[0:4]+'%')

			# Reading current frame
			img = cv2.imread(filename)

			# Extracting shape
			h, w, l = img.shape

			# Checking if shape matches spec for video
			if h == height  and w == width and l == layers:

				# Write frame
				out.write(img)

			# If shape is different
			else:

				print('Incorrect shape for frame: ' + filename)
				break

		out.release()
	print('\nDone.')