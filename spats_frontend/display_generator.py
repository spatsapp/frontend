from pprint import pformat

class DisplayGenerator:
	def __init__(self):
		pass

	def thing_get(self, doc):
		thing = doc['thing']
		asset = doc['asset'][thing['type']]
		fields = thing['fields']
		primary = asset.get('primary')
		order = asset.get('order')
		order.remove(primary)
		output = []
		for key in order:
			if key in fields:
				raw = fields[key]
				val = raw if (not isinstance(raw, list)) else ', '.join([str(r) for r in raw])
				output.append((key, raw))
		return {
			'_id': thing['_id'],
			'primary': fields[primary],
			'type': thing['type'],
			'asset': asset['name'],
			'fields': output
		}