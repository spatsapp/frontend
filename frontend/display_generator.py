"""Generate docs for display"""


class DisplayGenerator:
    """Generate documents for display"""

    def __init__(self):
        pass

    @staticmethod
    def _symbolic_fields_to_list(fields, order, _id):
        field_order = []
        for key in order:
            current = fields[key]
            field_order.append(
                {
                    "name": key,
                    "description": current["description"],
                    "parameters": current.get("parameters") or "",
                    "type": current["type"],
                    "inherited": _id != current.get("origin"),
                    "origin": current.get("origin", _id),
                }
            )
        return field_order

    @staticmethod
    def _material_fields_to_list(material_fields, symbolic_fields, order, _id):
        field_order = []
        for key in order:
            symbolic = symbolic_fields[key]
            field_order.append(
                {
                    "name": key,
                    "value": material_fields.get(key) or "",
                    "parameters": symbolic["parameters"],
                    "type": symbolic["type"],
                }
            )
        return field_order

    @staticmethod
    def _single_material(material, symbolic):
        fields = material["fields"]
        primary = symbolic.get("primary")
        order = symbolic.get("order")
        output = []
        for key in order:
            if key != primary and key in fields:
                raw = fields[key]
                val = (
                    raw
                    if (not isinstance(raw, list))
                    else ", ".join(
                        [(str(r) if "," not in str(r) else f'"{r}"') for r in raw]
                    )
                )
                output.append((key, val))
        return {
            "_id": material["_id"],
            "primary": fields[primary],
            "type": material["type"],
            "symbolic": symbolic["name"],
            "fields": output,
        }

    @staticmethod
    def _many_material(material, symbolic):
        fields = material["fields"]
        primary = None
        secondary = None
        tertiary = []
        primary_field = symbolic.get("primary")
        secondary_field = symbolic.get("secondary")
        tertiary_fields = symbolic.get("tertiary", [])
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
            "_id": material["_id"],
            "primary": primary,
            "secondary": secondary,
            "tertiary": tertiary,
            "type": material["type"],
            "symbolic": symbolic["name"],
        }

    def material_info(self, material_type, symbolic_type, doc):
        material = doc[material_type]
        symbolic = doc[symbolic_type][material["type"]]
        return self._single_material(material, symbolic)

    def material_list(self, material_type, symbolic_type, doc):
        materials = doc[material_type]
        docs = []
        for material in materials:
            symbolic = doc[symbolic_type][material["type"]]
            cur = self._many_material(material, symbolic)
            docs.append(cur)
        ret = {"docs": docs}
        if doc.get("paginate"):
            ret["paginate"] = doc["paginate"]
        return ret

    def material_edit(self, material_type, symbolic_type, doc):
        material = doc[material_type]
        symbolic_id = material["type"]
        symbolic = doc[symbolic_type][symbolic_id]

        return {
            "_id": material["_id"],
            "type": symbolic_id,
            "fields": self._material_fields_to_list(
                material["fields"],
                symbolic["fields"],
                symbolic["order"],
                symbolic_id,
            ),
        }

    @staticmethod
    def material_new(type_, doc):
        symbolic = doc[type_]
        fields = []
        for field in symbolic["order"]:
            value = symbolic["fields"][field]
            fields.append(
                {
                    "name": field,
                    "description": value["description"],
                    "parameters": value["parameters"],
                    "type": value["type"],
                }
            )

        return {"type": symbolic["_id"], "name": symbolic["name"], "fields": fields}

    @staticmethod
    def symbolic_list(docs):
        return [(doc["_id"], doc["name"]) for doc in docs]

    def symbolic_info(self, type_, doc):
        symbolic = doc[type_]
        return {
            "_id": symbolic["_id"],
            "name": symbolic["name"],
            "primary": symbolic["primary"],
            "secondary": symbolic.get("secondary") or "",
            "tertiary": ", ".join(symbolic.get("tertiary", [])) or "",
            "fields": self._symbolic_fields_to_list(
                symbolic["fields"],
                symbolic["order"],
                symbolic["_id"],
            ),
        }

    def symbolic_edit(self, type_, doc):
        symbolic = doc[type_]
        return {
            "_id": symbolic["_id"],
            "name": symbolic["name"],
            "primary": symbolic["primary"],
            "secondary": symbolic.get("secondary") or "",
            "tertiary": ", ".join(symbolic.get("tertiary", [])) or "",
            "fields": self._symbolic_fields_to_list(
                symbolic["fields"],
                symbolic["order"],
                symbolic["_id"],
            ),
        }

    def _symbolic_search(self, doc):
        res = {
            "_id": doc["_id"],
            "name": doc["name"]
        }
        if "primary" in doc:
            name = doc["primary"]
            desc = doc["fields"][name]["description"]
            res["primary"] = (name, desc)
        if "secondary" in doc:
            name = doc["secondary"]
            desc = doc["fields"][name]["description"]
            res["secondary"] = (name, desc)
        if "tertiary" in doc:
            tertiary = []
            for tert in doc["tertiary"]:
                desc = doc["fields"][tert]["description"]
                tertiary.append((tert, desc))
            res["tertiary"] = tertiary
        return res

    def search(self, res):
        result = {
            "asset": [],
            "combo": [],
            "thing": [],
            "group": [],
        }

        for asset in res.get("asset", []):
            result["asset"].append(self._symbolic_search(asset))

        for combo in res.get("combo", []):
            result["combo"].append(self._symbolic_search(combo))

        for thing in res.get("thing", []):
            material = thing["thing"]
            symbolic = thing["asset"][material["type"]]
            result["thing"].append(self._many_material(material, symbolic))

        for group in res.get("group", []):
            material = group["group"]
            symbolic = group["combo"][material["type"]]
            result["group"].append(self._many_material(material, symbolic))

        return result
