import os
import sys
    

path = 'templates/'
components = 'static/components'
output = 'templates/out-app.html'

class Progressbar:
	def __init__(self, maxval, val):
		self.maxval = maxval
		self.update(val)

	def update(self, val):
		if self.maxval > 0:
			n_aprox = (val + 1) // self.maxval * 100
			n = (val + 1) / self.maxval * 100

			sys.stdout.write('\r')
			# the exact output you're looking for:
			output = "["
			for i in range(100):
				if i <= n_aprox:
					output += chr(9619)
				else:
					output += '.'
			output += "] -- {0:.2f}%".format(n)

			sys.stdout.write(output)
			sys.stdout.flush()

			if n == 100:
				print()
			

class Component:
	def __init__(self, path, folder_name):
		#Component reference
		self.name_ = folder_name
		self.path = path
		#Component parts
		self.js_paths = []
		self.css_paths = []
		self.html_template = None
		
		self.initial_wd = os.getcwd()
		self.full_path = os.path.join(os.getcwd(), folder_name)

		self.load_component()

	def load_component(self):
		if os.path.isdir(self.full_path):
			os.chdir(self.full_path)
			for _, _, files in os.walk('.'):
				for c_file in files:
					self.load_file(c_file)

			os.chdir(self.initial_wd)
		else:
			print("ERR: This path is non existant")
			return -1

	def load_file(self, c_file):
		c_file_chunks = c_file.split('.')
		c_file_extension = c_file_chunks[len(c_file_chunks) - 1]

		if c_file_extension == 'html':
			self.html_template = open(os.path.join(self.full_path, c_file), 'r').read()
		elif c_file_extension == 'js':
			self.js_paths.append(os.path.join(self.path, c_file))
		elif c_file_extension == 'css':
			self.css_paths.append(os.path.join(self.path, c_file))


class Compiler:
	def __init__(self, path, components, ouput):
		self.initial_cwd = os.getcwd()
		self.path = path
		self.components = self.load_components(components)
		self.output = output

		self.web = None
		self.web_array = None

		self.css_paths = []
		self.js_paths = []

	def start(self):
		self.load_web()
		self.scan_document()
		self.load_css()
		self.load_js()
		self.save_output()

	def save_output(self):
		print("Saving the magic")
		os.chdir(self.initial_cwd)
		output_file = open(self.output, 'w+')
		output_file.writelines(self.web_array)
		output_file.close()
		print("Magic saved")

	def load_web(self):
		os.chdir(os.path.join(self.initial_cwd, self.path))
		if os.path.isfile('app.html'):
			print("Loading app")
			self.web = open('app.html', 'r')
			self.web_array = list(self.web)
		else:
			print("File does not exist")
			return -1
		
	def load_components(self, path):
		os.chdir(os.path.join(os.getcwd(), path))
		components = []
		for _, folders, _ in os.walk('.'):
			print("Loading components")
			progressbar = Progressbar(len(folders), 0)
			for i, folder in enumerate(folders):
				progressbar.update(i)
				print("Found %s" % (folder))

				folder_path = os.path.join(path, folder)
				component = Component(folder_path, folder)
				components.append(component)
			print("Components loaded")
			break
		
		return components

	def add_component(self, component_name, i):
		component = None
		for test_component in self.components:
			if test_component.name_ == component_name:
				component = test_component
				break

		if component != None:
			if component.html_template != None:
				
				self.web_array[i] = component.html_template
			else:
				self.web_array[i] = '<!-- ' + component.name_ + ' has been loaded-->'
			self.css_paths.extend(component.css_paths)
			self.js_paths.extend(component.js_paths)
		else:
			print("Component '%s' is non existant. Ignoring in build" % (component_name))
			self.web_array[i] = ''

	def load_css(self):
		head_pos = 0
		for i, line in enumerate(self.web_array):
			found_state = line.find('</head>')
			if found_state != -1:
				head_pos = i
				break

		print("Adding css paths")
		progressbar = Progressbar(len(self.css_paths), 0)
		for i, css_path in enumerate(self.css_paths):
			progressbar.update(i)
			css_string = '<link rel="stylesheet" href="'+ css_path +'">'
			self.web_array.insert((head_pos - 1), css_string)

	def load_js(self):
		html_pos = 0
		for i, line in enumerate(self.web_array):
			if line.find('</html>') != -1:
				html_pos = i

		print("Adding js paths")
		progressbar = Progressbar(len(self.js_paths), 0)
		for i, js_path in enumerate(self.js_paths):
			progressbar.update(i)
			js_string = '<script src="'+js_path+'"></script>'
			self.web_array.insert((html_pos - 1), js_string)



	def scan_document(self):
		print("Scanning doc and adding templates")
		progressbar = Progressbar(len(self.web_array), 0)
		for i, line in enumerate(self.web_array):
			progressbar.update(i)
			needs_compiling = line.find('{{')
			if needs_compiling != -1:
				start = needs_compiling + 2
				end = line.find('}}')

				raw_component_name = list(line)[start:end]
				component_name = ''
				for char in raw_component_name:
					if char != ' ':
						component_name += char

				self.add_component(component_name, i)

compiler = Compiler(path, components, output)
compiler.start()
