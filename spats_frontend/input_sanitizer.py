from io import StringIO
from csv import reader, QUOTE_ALL

class InputSanitizer:
	def __init__(self):
		pass

	def _parse_user_csv(self, value):
		string = StringIO(value)
		csv_reader = reader(string, delimiter=',', quoting=QUOTE_ALL, quotechar='"', skipinitialspace=True)
		user_list = list(csv_reader)[0]
		return [ val.strip() for val in user_list ]

	def _symbolic_edit(self, form):
		new = {
			'primary': form['primary'],
			'secondary': form['secondary'],
			'tertiary': self._parse_user_csv(form['tertiary'])
		}
		active_params = [key for key in form.keys() if key.endswith('_active')]
		for active in active_params:
			field, param, _ = active.rsplit('_', 2)
			if field not in new:
				new[field] = {
					'name': form[f'{field}_name'],
					'type': form[f'{field}_type'],
					'description': form[f'{field}_description'],
					'parameters': {}
				}
			val = form[f'{field}_{param}']
			if param in ['required', 'unique', 'ordered']:
				val = True if val == 'on' else False

			if param.startswith('min'):
				param = f'min_{param[3:]}'
			elif param.startswith('max'):
				param = f'max_{param[3:]}'
			elif param == 'dateformat':
				param = 'date_format'
			elif param == 'listtype':
				param = 'list_type'

			new[field]['parameters'][param] = val
		return new

	def asset_edit(self, form):
		return self._symbolic_edit(form)