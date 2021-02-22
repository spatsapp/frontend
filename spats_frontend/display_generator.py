from pprint import pformat

class DisplayGenerator:
	def __init__(self):
		pass

	def _get_thing(self, thing, asset):
		fields = thing['fields']
		primary = asset.get('primary')
		order = asset.get('order')
		output = []
		for key in order:
			if key != primary and key in fields:
				raw = fields[key]
				val = raw if (not isinstance(raw, list)) else ', '.join([str(r) for r in raw])
				output.append((key, val))
		return {
			'_id': thing['_id'],
			'primary': fields[primary],
			'type': thing['type'],
			'asset': asset['name'],
			'fields': output
		}

	def thing_get(self, doc):
		thing = doc['thing']
		asset = doc['asset'][thing['type']]
		return self._get_thing(thing, asset)

	def thing_get_all(self, doc):
		things = doc['thing']
		asset = doc['asset'][things[0]['type']]
		res = []
		for thing in things:
			cur = self._get_thing(thing, asset)
			res.append(cur)
		return res