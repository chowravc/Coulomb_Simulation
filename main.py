import argparse
import numpy as np
import os
import glob
import shutil

from utils import *

def main(args):

	# p1 = charge(1e10, np.asarray([0, 0]), np.asarray([0, 0]), 1)
	# p2 = charge(1, np.asarray([0, 10]), np.asarray([3e4, 0]), -1)
	# ps = [p1, p2]

	# For randomly initialized charges
	if args.random:

		# Output directory
		outDir = args.outDir
		
		# If output directory doesn't exist
		if len(glob.glob('output/')) == 0:

			# Make it
			os.mkdir('output/')

		# If random directory doesn't exist
		if len(glob.glob('output/random')) == 0:

			# Make it
			os.mkdir('output/random')

		# If it does exist
		else:

			# Make sure it is empty
			for file in glob.glob('output/' + outDir + '/*'):
				os.remove(file)

		# Set seed for random
		np.random.seed(args.seed)

		# Total euler steps needed
		n = int(args.time/args.dt)

		# Length required to pad the output frames
		pad = len(str(n))

		# Create array of random charge signs
		chargeSigns = np.concatenate((np.ones(args.count//2), (-1.0)*np.ones(args.count - args.count//2)))
		np.random.shuffle(chargeSigns)

		# Array to store charges
		ps = []

		# Initialize array of charges
		for i in range(args.count):

			# Finding which mass to use from charge
			if chargeSigns[i] > 0:
				m = args.mPlus
			else:
				m = args.mMinus

			# Initialize charge:  (m, r, v, sign)

			# Initilization terms
			r = 100*(np.random.random_sample((2,))-0.5)
			v = np.asarray([0, 0])
			polarity = chargeSigns[i]*1

			# Creating charge
			c = charge(m, r, v, polarity)

			# Adding to list of charges
			ps.append(c)

		# Keeping track of saved frames
		frame = 0

		# Increment each time
		for i in range(n):

			# Displaying progress
			if i%100 == 0:
				print(str(100*i/n)[:4] + '%')

			# Check if not empty list of charges
			if len(ps) != 0:

				# For each required frame
				if i*args.dt*args.fps - frame >= 0:

					# Increment frame
					frame += 1

					# Save frame
					view(ps, outDir, i, pad)

				# Take step
				ps = increment(ps, args.dt)

	# If you want to save video
	if args.f2v:

		print('\nConverting frames to video')

		framesToVideo('output/'+args.outDir, args.fps//40)

	print('\nmain.py executed successfully.')

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Reading info for main.')

	# Arguments to convert video to frames
	parser.add_argument('--random', action='store_true', help='Flag to randomly initialize particles.')
	parser.add_argument('--f2v', action='store_true', help='Flag to create video.')

	parser.add_argument('--count', action='store', nargs='?', type=int, default=100, help='Number of charges.')
	parser.add_argument('--seed', action='store', nargs='?', type=int, default=0, help='Seed for random.')

	parser.add_argument('--mPlus', action='store', nargs='?', type=float, default=1e4, help='Mass of positive charge.')
	parser.add_argument('--mMinus', action='store', nargs='?', type=float, default=1e4, help='Mass of negative charge.')

	parser.add_argument('--width', action='store', nargs='?', type=int, default=300, help='Width of frame.')
	parser.add_argument('--height', action='store', nargs='?', type=int, default=200, help='Height of frame.')

	parser.add_argument('--outDir', action='store', nargs='?', type=str, default='random', help='Name of output directory.')

	parser.add_argument('--dt', action='store', nargs='?', type=float, default=1e-5, help='Time step size.')
	parser.add_argument('--fps', action='store', nargs='?', type=int, default=1000, help='Wanted video fps * 40.')
	parser.add_argument('--time', action='store', nargs='?', type=float, default=0.25, help='Length of experiment in seconds/40.')
	# Example:
	# python main.py --random

	# Parse arguments
	args = parser.parse_args()

	# Call main
	main(args)