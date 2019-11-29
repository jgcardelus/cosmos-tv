import os
import platform

system = platform.system()

class Path:
	def __init__(self, path):
		self.path = path
		if system == "Windows":
			self.path = self.switch_windows(path)
		
	def switch_windows(self, raw_path):
		path_blocks = raw_path.split('/')
		path = ''
		for i in range(0, len(path_blocks)):
			path = os.path.join(path, path_blocks[i])
			
		return path

class Compiler_Component:
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
				if len(files) > 0:
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
	def __init__(self, input_file, path, components_path, output_file, components=None, web=None):
		self.initial_cwd = os.getcwd()
		self.path = path
		self.input_file = input_file
		
		#Components
		self.components_path = components_path
		self.components = components
		if components == None:
			self.components = self.load_components(components_path)
		self.output_file = output_file

		#Web dependencies
		self.web = None
		self.web_array = web

		self.css_paths = []
		self.js_paths = []

	def start(self):
		if self.web_array == None:
			self.load_web()
		self.scan_document()
		self.add_css()
		self.add_js()
		self.save_output()

	def save_output(self):
		print("Saving the magic")
		os.chdir(os.path.join(self.initial_cwd, self.path))
		output_file = open(self.output_file, 'w+')
		output_file.writelines(self.web_array)
		output_file.close()
		print("Magic saved")

	def load_web(self):
		os.chdir(os.path.join(self.initial_cwd, self.path))
		if os.path.isfile(self.input_file):
			print("Loading app")
			self.web = open(self.input_file, 'r')
			self.web_array = list(self.web)
		else:
			print("File does not exist")
			return -1
		
	def load_components(self, path):
		os.chdir(os.path.join(os.getcwd(), path))
		components = []
		for _, folders, _ in os.walk('.'):
			if len(folders) > 0:
				print("Loading components")
				for i, folder in enumerate(folders):
					print("		Found %s" % (folder))

					folder_path = os.path.join(path, folder)
					component = Compiler_Component(folder_path, folder)
					components.append(component)
				print("Components loaded")
		
		os.chdir(self.initial_cwd)
		return components

	def add_component(self, component_name, i):
		component = None
		for test_component in self.components:
			if test_component.name_ == component_name:
				component = test_component
				break

		if component != None:
			if component.html_template != None:
				compiler = Compiler(self.input_file, 
						component.path, self.components_path, 
						self.output_file, self.components, 
						list(component.html_template.split('\n')))
				compiler.scan_document()
				self.web_array[i] = "\n".join(compiler.web_array)

				self.css_paths.extend(compiler.css_paths)
				self.js_paths.extend(compiler.js_paths)
			else:
				self.web_array[i] = '<!-- ' + component.name_ + ' has been loaded. Headless-->'
			self.css_paths.extend(component.css_paths)
			self.js_paths.extend(component.js_paths)
		else:
			print("Component '%s' is non existant. Ignoring in build" % (component_name))
			self.web_array[i] = ''

	def add_css(self):
		head_pos = 0
		for i, line in enumerate(self.web_array):
			found_state = line.find('</head>')
			if found_state != -1:
				head_pos = i
				break

		print("Adding css paths")
		for i, css_path in enumerate(self.css_paths):
			css_string = '<link rel="stylesheet" href="'+ css_path +'">'
			print("		Adding %s to css paths" % css_path)
			self.web_array.insert((head_pos - 1), css_string)

	def add_js(self):
		html_pos = 0
		for i, line in enumerate(self.web_array):
			if line.find('</html>') != -1:
				html_pos = i

		print("Adding js paths")
		for i, js_path in enumerate(self.js_paths):
			js_string = '<script src="'+js_path+'"></script>'
			print("		Adding %s to js paths" % js_string)
			self.web_array.insert((html_pos - 1), js_string)

	def scan_document(self):
		print("\nScanning doc and adding templates")
		for i, line in enumerate(self.web_array):
			needs_compiling = line.find('{{')
			if needs_compiling != -1:
				start = needs_compiling + 2
				end = line.find('}}')

				raw_component_name = list(line)[start:end]
				component_name = ''
				for char in raw_component_name:
					if char != ' ':
						component_name += char

				print("Adding and scanning %s" % (component_name))
				self.add_component(component_name, i)