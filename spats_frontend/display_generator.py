from pprint import pformat

class DisplayGenerator:
	def __init__(self):
		pass

	def _single_material(self, material, symbolic):
		fields = material['fields']
		primary = symbolic.get('primary')
		order = symbolic.get('order')
		output = []
		for key in order:
			if key != primary and key in fields:
				raw = fields[key]
				val = raw if (not isinstance(raw, list)) else ', '.join([str(r) for r in raw])
				output.append((key, val))
		return {
			'_id': material['_id'],
			'primary': fields[primary],
			'type': material['type'],
			'symbolic': symbolic['name'],
			'fields': output
		}

	def _many_material(self, material, symbolic):
		fields = material['fields']
		primary = None
		secondary = None
		tertiary = []
		primary_field = symbolic.get('primary')
		secondary_field = symbolic.get('secondary')
		tertiary_fields = symbolic.get('tertiary', [])
		if primary_field:
			value = fields.get(primary_field)
			if value:
				primary = (primary_field, value)
		if secondary_field:
			value = fields.get(secondary_field)
			if value:
				secondary = (secondary_field, value)
		if tertiary_fields:
			for tertiary_field in tertiary_fields:
				value = fields.get(tertiary_field)
				if value:
					tertiary.append((tertiary_field, value))

		return {
			'_id': material['_id'],
			'primary': primary,
			'secondary': secondary,
			'tertiary': tertiary,
			'type': material['type'],
			'symbolic': symbolic['name']
		}

	def thing_info(self, doc):
		thing = doc['thing']
		asset = doc['asset'][thing['type']]
		return self._single_material(thing, asset)

	def thing_list(self, doc):
		things = doc['thing']
		res = []
		for thing in things:
			asset = doc['asset'][thing['type']]
			cur = self._many_material(thing, asset)
			res.append(cur)
		return res

	def asset_list(self, docs):
		return [(doc['_id'], doc['name']) for doc in docs]

	def asset_info(self, doc):
		new_doc = {
			'_id': doc['_id'],
			'name': doc['name'],
			'primary': doc['primary'],
			'secondary': doc['secondary'],
			'tertiary': ', '.join(doc['tertiary']) if doc['tertiary'] else doc['tertiary']
		}
		field_order = []
		fields = doc['fields']
		for key in doc['order']:
			current = fields[key]
			field_order.append({
				'name': key,
				'description': current['description'],
				'parameters': current['parameters'],
				'type': current['type']
			})
		new_doc['fields'] = field_order
		return new_doc