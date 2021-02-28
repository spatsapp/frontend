console.log('hello world!');

const input = document.querySelector('.type_select');
input.addEventListener('change', updateValue);

function hide_param_options(field_name, param_type) {
	if (param_type != 'string') {
		param_div = document.querySelector('#'+field_name+'_param_string');
		param_div.hidden = true;
	}
	if (param_type != 'integer') {
		param_div = document.querySelector('#'+field_name+'_param_integer');
		param_div.hidden = true;
	}
	if (param_type != 'decimal') {
		param_div = document.querySelector('#'+field_name+'_param_decimal');
		param_div.hidden = true;
	}
	if (param_type != 'date') {
		param_div = document.querySelector('#'+field_name+'_param_date');
		param_div.hidden = true;
	}
	if (param_type != 'list') {
		param_div = document.querySelector('#'+field_name+'_param_list');
		param_div.hidden = true;
	}
}

function show_param_options(field_name, param_type) {
	param_div = document.querySelector('#'+field_name+'_param_'+param_type);
	param_div.hidden = false;
}

function updateValue(e) {
	type_value = e.target.value;
	name_value = e.target.id.split('_')[0];
	console.log(name_value, type_value)
	hide_param_options(name_value, type_value);
	show_param_options(name_value, type_value);
}
