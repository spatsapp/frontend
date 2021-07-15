function title(str) {
    // https://stackoverflow.com/a/196991
    return str.replace(
        /\w\S*/g,
        (txt) => { return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase(); }
    );
}

function _display(field) {
    return title(field).replace("_", " ")
}

function _param_setup(elem, id_name, field) {
    id_name = `i${id_name}_${field.replace("_", "")}`;

    let label = document.createElement("label");
    label.for = id_name;
    label.innerText = _display(field);
    elem.appendChild(label);
}

function _param_text(elem, id_name, field) {
    _param_setup(elem, id_name, field)

    let input = document.createElement("input");
    input.type = "text";
    input.id = input.name = id_name;
    elem.appendChild(input);
}


function _param_checkbox(elem, id_name, field) {
    _param_setup(elem, id_name, field)

    let input = document.createElement("input");
    input.type = "checkbox";
    input.id = input.name = id_name;
    elem.appendChild(input);
}

function _param_select(elem, id_name, field, options) {
    _param_setup(elem, id_name, field)

    let select = document.createElement("select");
    select.id = select.name = id_name;
    options.forEach((option) => {
        let opt = document.createElement("option");
        opt.value = option[0];
        opt.innerText = option[1];
        select.appendChild(opt);
    });
    elem.appendChild(select);
}

function _param_number(elem, id_name, field, step=1) {
    _param_setup(elem, id_name, field)

    let input = document.createElement("input");
    input.type = "number";
    input.id = input.name = id_name;
    input.step = step;
    elem.appendChild(input);
}

function _param_required(elem, id_name) {
    _param_checkbox(elem, id_name, "required");
}

function _param_unique(elem, id_name) {
    _param_checkbox(elem, id_name, "unique");
}

function _param_default(elem, id_name) {
    _param_text(elem, id_name, "default");
}


function _param_list_type(elem, id_name) {
    let options = [
        ["", ""],
        ["boolean", "Boolean"],
        ["string", "String"],
        ["integer", "Integer"],
        ["decimal", "Decimal"],
        ["date", "Date"],
        ["reference", "Reference"],
    ];
    _param_select(elem, id_name, "list_type", options);
}

function _param_max_length(elem, id_name) {
    _param_number(elem, id_name, "max_length", "1");
}

function _param_max_value(elem, id_name) {
    _param_number(elem, id_name, "max_value", "any");
}

function _param_min_length(elem, id_name) {
    _param_number(elem, id_name, "min_length", "1");
}

function _param_min_value(elem, id_name) {
    _param_number(elem, id_name, "min_value", "any");
}

function _param_ordered(elem, id_name) {
    _param_checkbox(elem, id_name, "ordered");
}

function _param_precision(elem, id_name) {
    _param_number(elem, id_name, "precision", "1");
}

function _param_date_format(elem, id_name) {
    let options = [
        ["",""],
        ["%Y", "yyyy (1970)"],
        ["%y", "yy (70)"],
        ["%b %d, %Y", "mmm dd, yyyy (Dec 26, 1970)"],
        ["%B %d, %y", "mmmm dd, yy (December 26, 70)"],

        ["%Y-%m-%d", "yyyy-mm-dd (1970-12-26)"],
        ["%y-%m-%d", "yy-mm-dd (70-12-26)"],
        ["%m-%d-%Y", "mm-dd-yyyy (12-26-1970)"],
        ["%m-%d-%y", "mm-dd-yy (12-26-70)"],
        ["%b-%d-%Y", "mmm-dd-yyyy (Dec-26-1970)"],
        ["%B-%d-%y", "mmmm-dd-yy (December-26-70)"],
        ["%d-%m-%Y", "dd-mm-yyyy (26-12-1970)"],
        ["%d-%m-%y", "dd-mm-yy (26-12-70)"],
        ["%d-%b-%Y", "dd-mmm-yyyy (26-Dec-1970)"],
        ["%d-%B-%y", "dd-mmmm-yy (26-December-70)"],

        ["%m-%d", "mm-dd (12-26)"],
        ["%d-%m", "dd-mm (26-12)"],
        ["%b-%d", "mmm-dd (Dec-26)"],
        ["%d-%b", "dd-mmm (26-Dec)"],
        ["%B-%d", "mmmm-dd (December-26)"],
        ["%d-%B", "dd-mmmm (26-December)"],

        ["%m-%Y", "mm-yyyy (12-1970)"],
        ["%m-%y", "mm-yy (12-70)"],
        ["%b-%Y", "mmm-yyyy (Dec-1970)"],
        ["%B-%y", "mmmm-yy (December-70)"],
        ["%Y-%m", "yyyy-mm (1970-12)"],
        ["%y-%m", "yy-mm (70-12)"],
        ["%Y-%b", "yyyy-mmm (1970-Dec)"],
        ["%y-%B", "yy-mmmm (70-December)"],

        ["%m/%d/%Y", "mm/dd/yyyy (12/26/1970)"],
        ["%m/%d/%y", "mm/dd/yy (12/26/70)"],
        ["%b/%d/%Y", "mmm/dd/yyyy (Dec/26/1970)"],
        ["%B/%d/%y", "mmmm/dd/yy (December/26/70)"],
        ["%d/%m/%Y", "dd/mm/yyyy (26/12/1970)"],
        ["%d/%m/%y", "dd/mm/yy (26/12/70)"],
        ["%d/%b/%Y", "dd/mmm/yyyy (26/Dec/1970)"],
        ["%d/%B/%y", "dd/mmmm/yy (26/December/70)"],
        ["%m/%d", "mm/dd (12/26)"],
        ["%d/%m", "dd/mm (26/12)"],
        ["%b/%d", "mmm/dd (Dec/26)"],
        ["%d/%b", "dd/mmm (26/Dec)"],
        ["%B/%d", "mmmm/dd (December/26)"],
        ["%d/%B", "dd/mmmm (26/December)"],

        ["%m/%Y", "mm/yyyy (12/1970)"],
        ["%m/%y", "mm/yy (12/70)"],
        ["%b/%Y", "mmm/yyyy (Dec/1970)"],
        ["%B/%y", "mmmm/yy (December/70)"],
        ["%Y/%m", "yyyy/mm (1970/12)"],
        ["%y/%m", "yy/mm (70/12)"],
        ["%Y/%b", "yyyy/mmm (1970/Dec)"],
        ["%y/%B", "yy/mmmm (70/December)"],

        ["%m.%d.%Y", "mm.dd.yyyy (12.26.1970)"],
        ["%m.%d.%y", "mm.dd.yy (12.26.70)"],
        ["%b.%d.%Y", "mmm.dd.yyyy (Dec.26.1970)"],
        ["%B.%d.%y", "mmmm.dd.yy (December.26.70)"],
        ["%d.%m.%Y", "dd.mm.yyyy (26.12.1970)"],
        ["%d.%m.%y", "dd.mm.yy (26.12.70)"],
        ["%d.%b.%Y", "dd.mmm.yyyy (26.Dec.1970)"],
        ["%d.%B.%y", "dd.mmmm.yy (26.December.70)"],
        ["%m.%d", "mm.dd (12.26)"],
        ["%d.%m", "dd.mm (26.12)"],
        ["%b.%d", "mmm.dd (Dec.26)"],
        ["%d.%b", "dd.mmm (26.Dec)"],
        ["%B.%d", "mmmm.dd (December.26)"],
        ["%d.%B", "dd.mmmm (26.December)"],

        ["%m.%Y", "mm.yyyy (12.1970)"],
        ["%m.%y", "mm.yy (12.70)"],
        ["%b.%Y", "mmm.yyyy (Dec.1970)"],
        ["%B.%y", "mmmm.yy (December.70)"],
        ["%Y.%m", "yyyy.mm (1970.12)"],
        ["%y.%m", "yy.mm (70.12)"],
        ["%Y.%b", "yyyy.mmm (1970.Dec)"],
        ["%y.%B", "yy.mmmm (70.December)"],

        ["%m %d %Y", "mm dd yyyy (12 26 1970)"],
        ["%m %d %y", "mm dd yy (12 26 70)"],
        ["%b %d %Y", "mmm dd yyyy (Dec 26 1970)"],
        ["%B %d %y", "mmmm dd yy (December 26 70)"],
        ["%d %m %Y", "dd mm yyyy (26 12 1970)"],
        ["%d %m %y", "dd mm yy (26 12 70)"],
        ["%d %b %Y", "dd mmm yyyy (26 Dec 1970)"],
        ["%d %B %y", "dd mmmm yy (26 December 70)"],
        ["%m %d", "mm dd (12 26)"],
        ["%d %m", "dd mm (26 12)"],
        ["%b %d", "mmm dd (Dec 26)"],
        ["%d %b", "dd mmm (26 Dec)"],
        ["%B %d", "mmmm dd (December 26)"],
        ["%d %B", "dd mmmm (26 December)"],

        ["%m %Y", "mm yyyy (12 1970)"],
        ["%m %y", "mm yy (12 70)"],
        ["%b %Y", "mmm yyyy (Dec 1970)"],
        ["%B %y", "mmmm yy (December 70)"],
        ["%Y %m", "yyyy mm (1970 12)"],
        ["%y %m", "yy mm (70 12)"],
        ["%Y %b", "yyyy mmm (1970 Dec)"],
        ["%y %B", "yy mmmm (70 December)"],
    ];
    _param_select(elem, id_name, "date_format", options);
}


function _add_td(elem, id_name, callback, span=null) {
    let td_elem = document.createElement("td");
    if (span != null) {
        td_elem.colspan = span;
    }
    callback(td_elem, id_name);
    elem.appendChild(td_elem);
}

function _add_td_empty(elem, span=null) {
    let td_elem = document.createElement("td");
    if (span != null) {
        td_elem.colspan = span;
    }
    elem.appendChild(td_elem);
}

function _param_rows(elem, id_name) {
    let all_fields = document.createElement("tr");
    all_fields.classList.add("param_row");
    _add_td(all_fields, id_name, _param_required);
    _add_td(all_fields, id_name, _param_unique);
    _add_td(all_fields, id_name, _param_default);
    elem.appendChild(all_fields);

    let string_row = document.createElement("tr");
    string_row.classList.add("param_row");
    string_row.id = `${id_name}_param_string`;
    _add_td(string_row, id_name, _param_min_length);
    _add_td(string_row, id_name, _param_max_length);
    _add_td_empty(string_row);
    elem.appendChild(string_row);

    let integer_row = document.createElement("tr");
    integer_row.classList.add("param_row");
    integer_row.id = `${id_name}_param_integer`;
    integer_row.hidden = true;
    _add_td(integer_row, id_name, _param_min_value);
    _add_td(integer_row, id_name, _param_max_value);
    _add_td_empty(integer_row);
    elem.appendChild(integer_row);

    let decimal_row = document.createElement("tr");
    decimal_row.classList.add("param_row");
    decimal_row.id = `${id_name}_param_decimal`;
    decimal_row.hidden = true;
    _add_td(decimal_row, id_name, _param_min_value);
    _add_td(decimal_row, id_name, _param_max_value);
    _add_td(decimal_row, id_name, _param_precision);
    elem.appendChild(decimal_row);

    let date_row = document.createElement("tr");
    date_row.classList.add("param_row");
    date_row.id = `${id_name}_param_date`;
    date_row.hidden = true;
    _add_td(date_row, id_name, _param_min_value);
    _add_td(date_row, id_name, _param_max_value);
    _add_td(date_row, id_name, _param_date_format);
    elem.appendChild(date_row);

    let list_row = document.createElement("tr");
    list_row.classList.add("param_row");
    list_row.id = `${id_name}_param_list`;
    list_row.hidden = true;
    _add_td(list_row, id_name, _param_list_type);
    _add_td(list_row, id_name, _param_ordered);
    _add_td_empty(list_row);
    elem.appendChild(list_row);
}

function _field_row(elem, id_name) {
    let row = document.createElement("tr");
    row.classList.add("field_row");

    let name = document.createElement("td");
    let name_input = document.createElement("input");
    name_input.type = "text";
    name_input.id = name_input.name = `${id_name}_name`;
    name_input.placeholder = "Field Name";
    name.appendChild(name_input);
    row.appendChild(name);

    let type = document.createElement("td");
    let type_select = document.createElement("select");
    type_select.classList.add("type_select");
    type_select.id = type_select.name = `${id_name}_type`;
    let options = [
        ["boolean", "Boolean"],
        ["string", "String"],
        ["integer", "Integer"],
        ["decimal", "Decimal"],
        ["date", "Date"],
        ["list", "List"],
        ["reference", "Reference"],
    ];
    options.forEach((option) => {
        let opt = document.createElement("option");
        opt.value = option[0];
        opt.innerText = option[1];
        if (option[0] == "string") {
            opt.selected = true;
        }
        type_select.appendChild(opt);
    });
    type_select.addEventListener("change", updateValue)
    type.appendChild(type_select);
    row.appendChild(type);

    let desc = document.createElement("td");
    let desc_textarea = document.createElement("textarea");
    desc_textarea.id = desc_textarea.name = `${id_name}_description`;
    desc.appendChild(desc_textarea);
    row.appendChild(desc);
    elem.appendChild(row);
}

function _field_management(elem, counter) {
    let row = document.createElement("tr");

    let moveup_td = document.createElement("td");
    let moveup_button = document.createElement("button");
    moveup_button.classList.add("moveup");
    moveup_button.dataset.index = counter.toString();
    moveup_button.innerHTML = "Move Field Up";
    moveup_button.addEventListener("click", moveup);
    moveup_td.appendChild(moveup_button);
    row.appendChild(moveup_td);

    let movedown_td = document.createElement("td");
    let movedown_button = document.createElement("button");
    movedown_button.classList.add("movedown");
    movedown_button.dataset.index = counter.toString();
    movedown_button.innerHTML = "Move Field Down";
    movedown_button.addEventListener("click", movedown);
    movedown_td.appendChild(movedown_button);
    row.appendChild(movedown_td);

    let remove_td = document.createElement("td");
    let remove_button = document.createElement("button");
    remove_button.classList.add("removerow");
    remove_button.dataset.index = counter.toString();
    remove_button.innerHTML = "Remove Field";
    remove_button.addEventListener("click", removerow);
    remove_td.appendChild(remove_button);
    row.appendChild(remove_td);
    elem.appendChild(row);
}

function remove(arr) {
    // https://stackoverflow.com/a/3955096
    var what, a = arguments, L = a.length, ax;
    while (L > 1 && arr.length) {
        what = a[--L];
        while ((ax= arr.indexOf(what)) !== -1) {
            arr.splice(ax, 1);
        }
    }
    return arr;
}

function swap(arr, e1, e2) {
    e1 = e1.toString();
    e2 = e2.toString();
    let i1 = arr.indexOf(e1);
    let i2 = arr.indexOf(e2);
    if (i1 != -1 && i2 != -1) {
        arr[i2] = e1;
        arr[i1] = e2;
    } else if (i1 == -1) {
        console.error(`First element (${e1}) not found in array, no swap occuring: ${arr}`)
        console.log(arr);
    } else {
        console.error(`Second element (${e2}) not found in array, no swap occuring: ${arr}`)
        console.log(arr);
    }
    return arr;
}

function hide_param_options(field_name, param_type) {
    if (param_type != "string") {
        param_div = document.querySelector(`#${field_name}_param_string`);
        param_div.hidden = true;
    }
    if (param_type != "integer") {
        param_div = document.querySelector(`#${field_name}_param_integer`);
        param_div.hidden = true;
    }
    if (param_type != "decimal") {
        param_div = document.querySelector(`#${field_name}_param_decimal`);
        param_div.hidden = true;
    }
    if (param_type != "date") {
        param_div = document.querySelector(`#${field_name}_param_date`);
        param_div.hidden = true;
    }
    if (param_type != "list") {
        param_div = document.querySelector(`#${field_name}_param_list`);
        param_div.hidden = true;
    }
}

function show_param_options(field_name, param_type) {
    param_div = document.querySelector(`#${field_name}_param_${param_type}`);
    param_div.hidden = false;
}

function updateValue(event) {
    type_value = event.target.value;
    name_value = event.target.id.split("_")[0];
    console.log(name_value, type_value)
    hide_param_options(name_value, type_value);
    show_param_options(name_value, type_value);
}

function addrow(event) {
    event.preventDefault();
    counter++;
    order.push(counter.toString());
    let tbody = document.createElement("tbody");
    tbody.classList.add(`i${counter}`);
    tbody.dataset.index = counter.toString();
    _field_row(tbody, `i${counter}`);
    _param_rows(tbody, `i${counter}`);
    _field_management(tbody, counter);
    document.querySelector("#data").appendChild(tbody);

    console.log(`Position added: ${counter}`);
    console.log(`Current order: ${order}`);
}

function removerow(event) {
    event.preventDefault();
    let position = parseInt(event.target.dataset.index);
    console.log(`Removing position: ${position}`);
    document.querySelectorAll(`.i${position}`).forEach((elem) => {elem.remove();});
    remove(order, position.toString());
    console.log(`Current order: ${order}`);
}

function moveup(event) {
    event.preventDefault();
    let position = parseInt(event.target.dataset.index);
    let table = document.querySelector("#data");
    let moving = table.querySelector(`.i${position}`);
    let previous = moving.previousElementSibling;
    if (previous.nodeName == "TBODY") {
        console.log(`Moving i${position} up`);
        table.insertBefore(moving, previous);
        order = swap(order, position, previous.dataset.index.toString());
        console.log(`New order: ${order}`);
    }
}

function movedown(event) {
    event.preventDefault();
    let position = parseInt(event.target.dataset.index);
    let table = document.querySelector("#data");
    let moving = table.querySelector(`.i${position}`);
    let next = moving.nextElementSibling;
    if (next != null && next.nodeName == "TBODY") {
        console.log(`Moving i${position} down`);
        table.insertBefore(next, moving);
        order = swap(order, position, next.dataset.index.toString());
        console.log(`New order: ${order}`);
    }
}

function submit_form(event) {
    document.querySelector('#order').value = order;
    return true;
}

console.log("hello symbolic form!");
var counter = 0;
var order = [];
document.addEventListener("DOMContentLoaded", () => { 
    counter = document.querySelectorAll(".field_row").length;
    for (let i = 0; i < counter; i++) {
        order.push(i.toString());
    }
    console.log(`Starting order: ${order}`)
    console.log(`Starting counter: ${counter}`);
    document.querySelectorAll(".type_select").forEach(elm => elm.addEventListener("change", updateValue));
    document.querySelector("#addrow").addEventListener("click", addrow);
    document.querySelectorAll(".moveup").forEach(elm => elm.addEventListener("click", moveup));
    document.querySelectorAll(".movedown").forEach(elm => elm.addEventListener("click", movedown));
    document.querySelectorAll(".removerow").forEach(elm => elm.addEventListener("click", removerow));
    document.querySelector("#submit").addEventListener("click", submit_form)
});
