"""Sanatize user input"""
from csv import QUOTE_ALL, reader
from datetime import datetime
from io import StringIO


class InputSanitizer:
    """Sanatize user input"""

    type_params = {
        "boolean": [],
        "string": ["minlength", "maxlength"],
        "integer": ["default", "minvalue", "maxvalue"],
        "decimal": ["default", "minvalue", "maxvalue", "precision"],
        "date": ["default", "minvalue", "maxvalue"],
        "list": ["ordered", "listtype"],
        "reference": [],
    }

    def __init__(self):
        pass

    @staticmethod
    def _parse_user_csv(value):
        if isinstance(value, list):
            return value
        string = StringIO(value)
        csv_reader = reader(
            string,
            delimiter=",",
            quoting=QUOTE_ALL,
            quotechar='"',
            skipinitialspace=True,
        )
        user_list = list(csv_reader)
        return [val.strip() for val in user_list[0]] if user_list else []

    @staticmethod
    def _list_to_dict(key, values):
        temp = {}
        for value in values:
            temp[value[key]] = value
        return temp

    def material_edit(self, original, form):
        """Edit a material object"""
        new = {"_id": original["_id"], "type": original["type"]}
        for field in original["fields"]:
            name = field["name"]
            value = form[name]
            if value != "":
                if field["type"] == "list":
                    value = self._parse_user_csv(value)
                    if field.get("parameters", {}).get("ordered", False):
                        value.sort()
                    if field["value"] == "":
                        field["value"] = []
            if field["value"] != value:
                if value == "":
                    if "unset" not in new:
                        new["unset"] = {}
                    new["unset"][name] = ""
                else:
                    if "fields" not in new:
                        new["fields"] = {}

                    new["fields"][name] = {
                        "value": value,
                        "type": field["type"],
                        "parameters": field["parameters"],
                    }
        return new if "fields" in new or "unset" in new else {}

    def material_new(self, original, form):
        """Create new material object"""
        new = {"type": original["type"], "fields": {}}
        for field in original["fields"]:
            name = field["name"]
            value = form.get(name, "")
            if value != "":
                if field["type"] == "list":
                    value = self._parse_user_csv(value)
                    if field.get("parameters", {}).get("ordered", False):
                        value.sort()
                new["fields"][name] = {
                    "value": value,
                    "type": field["type"],
                    "parameters": field["parameters"],
                }
        return new

    @staticmethod
    def _uncompress_parameter_name(param):
        if param.startswith("min"):
            param = f"min_{param[3:]}"
        elif param.startswith("max"):
            param = f"max_{param[3:]}"
        elif param == "dateformat":
            param = "date_format"
        elif param == "listtype":
            param = "list_type"
        return param

    def _symbolic_parameters(self, id_name, type_, form):
        params = {}

        if form.get(f"{id_name}_required", "") != "":
            params["required"] = True
        if form.get(f"{id_name}_unique", "") != "":
            params["unique"] = True

        for form_name in self.type_params[type_]:
            db_name = self._uncompress_parameter_name(form_name)
            param_id = f"{id_name}_{form_name}"
            param_value = form.get(param_id, "")
            if param_value != "":
                params[db_name] = param_value

        return self._symbolic_parameter_values(type_, params)

    def _symbolic_unset(self, field_type, new_params, og_params):
        unset = {}

        type_params = ["required", "unique"] + [
            self._uncompress_parameter_name(name)
            for name in self.type_params[field_type]
        ]
        if og_params:
            for param in og_params.keys():
                if param not in type_params or (
                    param in type_params and param not in new_params
                ):
                    unset[param] = ""

        return unset

    # pylint: disable=too-many-branches
    @staticmethod
    def _symbolic_parameter_values(type_, params):
        if type_ == "boolean":
            pass

        elif type_ == "string":
            if "min_length" in params:
                params["min_length"] = int(params["min_length"])
            if "max_length" in params:
                params["max_length"] = int(params["max_length"])

        elif type_ == "integer":
            if "default" in params:
                params["default"] = int(params["default"])
            if "min_value" in params:
                params["min_value"] = int(params["min_value"])
            if "max_value" in params:
                params["max_value"] = int(params["max_value"])

        elif type_ == "decimal":
            if "default" in params:
                params["default"] = float(params["default"])
            if "min_value" in params:
                params["min_value"] = float(params["min_value"])
            if "max_value" in params:
                params["max_value"] = float(params["max_value"])
            if "precision" in params:
                params["precision"] = int(params["precision"])

        elif type_ == "date":
            date_format = params.get("date_format", "%Y-%m-%d")
            if "default" in params:
                params["default"] = datetime.strptime(params["default"], date_format)
            if "min_value" in params:
                params["min_value"] = datetime.strptime(
                    params["min_value"],
                    date_format,
                )
            if "max_value" in params:
                params["max_value"] = datetime.strptime(
                    params["max_value"],
                    date_format,
                )

        elif type_ == "list":
            if "ordered" in params:
                params["ordered"] = params["ordered"] == "on"

        elif type_ == "reference":
            pass

        return params

    def symbolic_edit(self, original, form):
        """Edit a symbolic object"""
        update = {}
        rename = {}
        unset = {}
        if form["primary"] != original["primary"]:
            update["primary"] = form["primary"]
        if form["secondary"] != original["secondary"]:
            update["secondary"] = form["secondary"]
        if form["tertiary"] != original["tertiary"]:
            update["tertiary"] = self._parse_user_csv(form["tertiary"])

        og_fields = self._list_to_dict("name", original["fields"])

        order = []
        for field_num in form["order"].split(","):
            field = {}

            id_name = f"i{field_num}"
            field_name = form[f"{id_name}_name"]
            og_field_name = form.get(f"{id_name}_og_name", "")
            field_type = form[f"{id_name}_type"]
            description = form[f"{id_name}_description"]

            order.append(field_name)

            og_field = og_fields.get(og_field_name, {})
            og_params = og_field.get("parameters") or {}

            if og_field_name == "":
                field["name"] = field_name
                field["type"] = field_type
                field["description"] = description
            else:
                if field_name != og_field["name"]:
                    field["name"] = field_name
                    if "fields" not in rename:
                        rename["fields"] = {}
                    rename["fields"][og_field_name] = field_name
                    if og_field_name == form["primary"] and field_name != update.get(
                        "primary"
                    ):
                        update["primary"] = field_name
                    if og_field_name == form["secondary"] and field_name != update.get(
                        "secondary"
                    ):
                        update["secondary"] = field_name
                    if og_field_name in form[
                        "tertiary"
                    ] and field_name not in update.get("tertiary"):
                        update["tertiary"] = [
                            (field_name if val == og_field_name else val)
                            for val in update["tertiary"]
                        ]
                if field_type != og_field["type"]:
                    field["type"] = field_type
                if description != og_field["description"]:
                    field["description"] = description

            params = self._symbolic_parameters(id_name, field_type, form)
            param_unset = self._symbolic_unset(field_type, params, og_params)
            if og_field_name != "":
                items = list(params.items())
                for param, value in items:
                    if param in og_params:
                        if value == og_params[param]:
                            del params[param]

            if params:
                field["parameters"] = params
            if field:
                if "fields" not in update:
                    update["fields"] = {}
                update["fields"][(og_field_name or field_name)] = field
            if param_unset:
                if "fields" not in unset:
                    unset["fields"] = {}
                unset["fields"][og_field["name"]] = {"parameters": param_unset}

        if order != [field["name"] for field in original["fields"]]:
            update["order"] = order

        return {
            "_id": original["_id"],
            "update": update,
            "unset": unset,
            "rename": rename,
        }

    def symbolic_new(self, original, form):
        """Create new symbolic object"""
        new = {
            "inherit": original["_id"],
            "name": form["asset_name"],
            "primary": form["primary"],
            "secondary": form["secondary"],
            "tertiary": self._parse_user_csv(form["tertiary"]),
            "fields": {},
        }

        named_order = []
        for field_num in form["order"].split(","):
            field = {}
            field_id = f"i{field_num}"
            field_name = form[f"{field_id}_name"]
            named_order.append(field_name)
            field["name"] = field_name
            field["type"] = form[f"{field_id}_type"]
            field["description"] = form[f"{field_id}_description"]

            field["parameters"] = self._symbolic_parameters(
                field_id, field["type"], form
            )
            new["fields"][field_name] = field
        new["order"] = named_order
        return new
