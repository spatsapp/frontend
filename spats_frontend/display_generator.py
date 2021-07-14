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
                    "parameters": current["parameters"],
                    "type": current["type"],
                    "inherited": _id != current["origin"],
                    "origin": current["origin"],
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
                    "value": material_fields.get(key) or '',
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
                    else ", ".join([(str(r) if "," not in str(r) else f'"{r}"') for r in raw])
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

    def _material_info(self, doc, material_type, symbolic_type):
        material = doc[material_type]
        symbolic = doc[symbolic_type][material["type"]]
        return self._single_material(material, symbolic)

    def _material_list(self, doc, material_type, symbolic_type):
        materials = doc[material_type]
        docs = []
        for material in materials:
            symbolic = doc[symbolic_type][material["type"]]
            cur = self._many_material(material, symbolic)
            docs.append(cur)
        return docs

    def _material_edit(self, doc, material_type, symbolic_type):
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
    def _material_new(doc, type_):
        symbolic = doc[type_]
        fields = []
        for field in symbolic["order"]:
            value = symbolic["fields"][field]
            fields.append({
                "name": field,
                "description": value["description"],
                "parameters": value["parameters"],
                "type": value["type"],
            })

        return {
            "type": symbolic["_id"],
            "name": symbolic["name"],
            "fields": fields
        }

    @staticmethod
    def _symbolic_list(docs):
        return [(doc["_id"], doc["name"]) for doc in docs]

    def _symbolic_info(self, doc, symbolic_type):
        symbolic = doc[symbolic_type]
        return {
            "_id": symbolic["_id"],
            "name": symbolic["name"],
            "primary": symbolic["primary"],
            "secondary": symbolic["secondary"],
            "tertiary": ", ".join(symbolic["tertiary"])
            if symbolic["tertiary"]
            else symbolic["tertiary"],
            "fields": self._symbolic_fields_to_list(
                symbolic["fields"], symbolic["order"], symbolic["_id"]
            ),
        }

    def _symbolic_edit(self, doc, type_):
        symbolic = doc[type_]
        return {
            "_id": symbolic["_id"],
            "name": symbolic["name"],
            "primary": symbolic["primary"],
            "secondary": symbolic["secondary"],
            "tertiary": ", ".join(symbolic["tertiary"])
            if symbolic["tertiary"]
            else symbolic["tertiary"],
            "fields": self._symbolic_fields_to_list(
                symbolic["fields"], symbolic["order"], symbolic["_id"]
            ),
        }

    def asset_info(self, doc):
        """Get asset info"""
        return self._symbolic_info(doc, "asset")

    def asset_list(self, doc):
        """List asset"""
        return self._symbolic_list(doc)

    def asset_edit(self, doc):
        """Edit asset"""
        return self._symbolic_edit(doc, "asset")

    def thing_info(self, doc):
        """Get thing info"""
        return self._material_info(doc, "thing", "asset")

    def thing_list(self, doc):
        """List things"""
        return self._material_list(doc, "thing", "asset")

    def thing_edit(self, doc):
        """Edit thing"""
        return self._material_edit(doc, "thing", "asset")

    def thing_new(self, doc):
        """Create new thing"""
        return self._material_new(doc, "asset")

    def combo_info(self, doc):
        """Get combo info"""
        return self._symbolic_info(doc, "combo")

    def combo_list(self, doc):
        """List combo"""
        return self._symbolic_list(doc)

    def combo_edit(self, doc):
        """Edit combo"""
        return self._symbolic_edit(doc, "combo")

    def group_info(self, doc):
        """Get group info"""
        return self._material_info(doc, "group", "combo")

    def group_list(self, doc):
        """List group"""
        return self._material_list(doc, "group", "combo")
