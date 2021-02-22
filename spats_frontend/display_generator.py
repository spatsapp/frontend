from pprint import pformat

class DisplayGenerator:
	def __init__(self):
		pass

	def generate(self, output):
		return self.base_html(f'<div class="container" style="color:lime;">{output}</div>')

	def base_html(self, value):
		return f"""<html>
		<head>
			<title>SPATS</title>
			<link
				rel="stylesheet"
				href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css"
				integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm"
				crossorigin="anonymous"
			>
		</head>
		<body style="background-color:black;font-size:1.5em;">{value}</body></html>"""


	def thing_get(self, doc):
		thing = doc['thing']
		asset = doc['asset'][thing['type']]
		fields = thing['fields']
		primary = asset.get('primary')
		order = asset.get('order')
		order.remove(primary)
		output = f'<h1>{fields[primary]}</h1>'
		for key in order:
			if key in fields:
				raw = fields[key]
				val = raw if (not isinstance(raw, list)) else ', '.join([str(r) for r in raw])
				output += f'<b>{key}:</b> {val}<br />'
		return self.generate(output)