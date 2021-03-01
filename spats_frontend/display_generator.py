from pprint import pformat

class DisplayGenerator:
	def __init__(self):
		pass

	def _fields_to_list(self, fields, order, _id):
		field_order = []
		for key in order:
			current = fields[key]
			field_order.append({
				'name': key,
				'description': current['description'],
				'parameters': current['parameters'],
				'type': current['type'],
				'inherited': _id != current['origin'],
				'origin': current['origin']
			})
		return field_order

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

	def _material_info(self, doc, material_type, symbolic_type):
		material = doc[material_type]
		symbolic = doc[symbolic_type][material['type']]
		return self._single_material(material, symbolic)

	def _material_list(self, doc, material_type, symbolic_type):
		materials = doc[material_type]
		docs = []
		for material in materials:
			symbolic = doc['asset'][material['type']]
			cur = self._many_material(material, symbolic)
			docs.append(cur)
		return docs

	def _symbolic_list(self, docs):
		return [(doc['_id'], doc['name']) for doc in docs]

	def _symbolic_info(self, doc, symbolic_type):
		symbolic = doc[symbolic_type]
		return {
			'_id': symbolic['_id'],
			'name': symbolic['name'],
			'primary': symbolic['primary'],
			'secondary': symbolic['secondary'],
			'tertiary': ', '.join(symbolic['tertiary']) if symbolic['tertiary'] else symbolic['tertiary'],
			'fields': self._fields_to_list(symbolic['fields'], symbolic['order'], symbolic['_id'])
		}

	def _symbolic_edit(self, doc, type_):
		symbolic = doc[type_]
		return {
			'_id': symbolic['_id'],
			'name': symbolic['name'],
			'primary': symbolic['primary'],
			'secondary': symbolic['secondary'],
			'tertiary': ', '.join(symbolic['tertiary']) if symbolic['tertiary'] else symbolic['tertiary'],
			'fields': self._fields_to_list(symbolic['fields'], symbolic['order'], symbolic['_id'])
		}


	def asset_info(self, doc):
		return self._symbolic_info(doc, 'asset')

	def asset_list(self, doc):
		return self._symbolic_list(doc)

	def asset_edit(self, doc):
		return self._symbolic_edit(doc, 'asset')


	def thing_info(self, doc):
		return self._material_info(doc, 'thing', 'asset')

	def thing_list(self, doc):
		return self._material_list(doc, 'thing', 'asset')


	def combo_info(self, doc):
		return self._symbolic_info(doc, 'combo')

	def combo_list(self, doc):
		return self._symbolic_list(doc)

	def combo_edit(self, doc):
		return self._symbolic_edit(doc, 'combo')


	def group_info(self, doc):
		return self._material_info(doc, 'group', 'combo')

	def group_list(self, doc):
		return self._material_list(doc, 'group', 'combo')