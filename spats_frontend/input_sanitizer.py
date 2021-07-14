"""Sanatize user input"""
from csv import QUOTE_ALL, reader
from io import StringIO


class InputSanitizer:
    """Sanatize user input"""

    def __init__(self):
        pass

    @staticmethod
    def _parse_user_csv(value):
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

    def _material_edit(self, original, form):
        new = {"_id": original["_id"], "type": original["type"]}
        for field in original["fields"]:
            name = field["name"]
            value = form[name]
            if value != '':
                if field["type"] == "list":
                    value = self._parse_user_csv(value)
                    if field.get("parameters", {}).get("ordered", False):
                        value.sort()
                    if field["value"] == "":
                        field["value"] = []
            if field["value"] != value:
                if value == '':
                    if "unset" not in new:
                        new["unset"] = {}
                    new["unset"][name] = ''
                else:
                    if "fields" not in new:
                        new["fields"] = {}

                    new["fields"][name] = {
                        "value": value,
                        "type": field["type"],
                        "parameters": field["parameters"],
                    }
        return new if "fields" in new or "unset" in new else {}

    def _material_new(self, original, form):
        new = {"type": original["type"], "fields": {}}
        for field in original["fields"]:
            name = field["name"]
            value = form[name]
            if value != '':
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

    def _symbolic_edit(self, original, form):
        new = {"_id": original["_id"], "fields": {}}
        if form["primary"] != original["primary"]:
            new["primary"] = form["primary"]
        if form["secondary"] != original["secondary"]:
            new["secondary"] = form["secondary"]
        if form["tertiary"] != original["tertiary"]:
            new["tertiary"] = self._parse_user_csv(form["tertiary"])

        fields = new["fields"]
        og_fields = self._list_to_dict("name", original["fields"])
        active_params = [
            key.rsplit("_", 2) for key in form.keys() if key.endswith("_active")
        ]
        for field, param, _ in active_params:
            if field not in new:
                temp = {
                    "parameters": {},
                }
                name = form[f"{field}_name"]
                type_ = form[f"{field}_type"]
                description = form[f"{field}_description"]

                if name != og_fields[field]["name"]:
                    temp["name"] = name
                if type_ != og_fields[field]["type"]:
                    temp["type"] = type_
                if description != og_fields[field]["description"]:
                    temp["description"] = description

                fields[field] = temp
            val = form.get(f"{field}_{param}", "")
            if param in ["required", "unique", "ordered"]:
                val = val == "on"

            if param.startswith("min"):
                param = f"min_{param[3:]}"
            elif param.startswith("max"):
                param = f"max_{param[3:]}"
            elif param == "dateformat":
                param = "date_format"
            elif param == "listtype":
                param = "list_type"

            fields[field]["parameters"][param] = val

        for field in og_fields.values():
            name = field["name"]
            params = field["parameters"].keys()
            current_params = [val[1] for val in active_params if val[0] == name]
            for full, flat in [(key, key.replace("_", "")) for key in params]:
                if flat not in current_params:
                    if "unset" not in new:
                        new["unset"] = {}
                    if name not in new["unset"]:
                        new["unset"][name] = {"parameters": {}}
                    new["unset"][name]["parameters"][full] = ""
        return new

    def asset_edit(self, original, form):
        """Edit asset"""
        return self._symbolic_edit(original, form)

    def thing_edit(self, original, form):
        """Edit thing"""
        return self._material_edit(original, form)

    def thing_new(self, original, form):
        """New thing"""
        return self._material_new(original, form)
