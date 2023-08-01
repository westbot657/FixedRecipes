# pylint: disable=[W,R,C,import-error]

import re, json

class ShapedRecipe:

    def __init__(self, shape, key, result, count):
        self.shape = shape
        self.key = key
        self.result = result
        self.count = count

class ShapelessRecipe:
    def __init__(self, ingredients, result, count):
        self.ingredients = ingredients
        self.result = result
        self.count = count

class DataIter:
    def __init__(self, var_names:str, data:list|dict):
        self.var_names = var_names
        self.data = data
        self.active_iter = None
        self.sub_iter = None
    
    def set_sub_iter(self, _iter):
        if self.sub_iter is None:
            self.sub_iter = _iter
        else:
            self.sub_iter.set_sub_iter(_iter)

    def start(self):
        if isinstance(self.data, dict):
            self.active_iter = iter(self.data.items())
        elif isinstance(self.data, list):
            self.active_iter = iter(self.data)
        
        if self.sub_iter:
            self.sub_iter.start()

    def next(self, context:dict):

        if self.sub_iter:
            try:
                self.sub_iter.next(context)
                return
            except Exception as e:
                self.sub_iter.start()

        if isinstance(self.data, dict):
            a, b = self.active_iter.__next__()
            context[self.var_names[0]] = a
            context[self.var_names[1]] = b

        elif isinstance(self.data, list):
            context[self.var_names[0]] = self.active_iter.__next__()

class RecipeParser:

    def __init__(self):
        self.name = ""
        self.mcmeta = {}
        self.recipes = []

    def __repr__(self):
        return f"== {self.name} ==\n{json.dumps(self.mcmeta, indent=2)}\n{len(self.recipes)} recipes"

    def parse(self, file_name:str):
        with open(file_name, "r+", encoding="utf-8") as f:
            text = f.read()
        
        sections = text.split("----\n")

        pack_data_section = sections.pop(0).strip()

        if m := re.fullmatch(r"== *(?P<name>[a-z0-9_]+) *==\n+// *(?P<description>[A-Za-z0-9_ \-\+=~`!@#\$%\^&\*\(\)\\|[\];:'\",<\.>\?]*) *//\n+f-(?P<format>[0-9]+)", pack_data_section):
            d = m.groupdict()
            pack_name = d.get("name")
            description = d.get("description")
            format = d.get("format")

            self.name = pack_name
            self.mcmeta = {
                "pack": {
                    "format": int(format),
                    "description": description
                }
            }

        for section in sections:
            self.parse_section(section)

    def parse_section(self, text:str):
        if "#ITER" in text:
            if "#END" not in text:
                return
            
            iters, recipe_data = text.split("#END")
            iters = iters.strip().split("#ITER")[1:]
            recipe_data = recipe_data.strip()

            data_iter = None

            for _iter in iters:
                _names, _data = _iter.split("=")
                names = [n.strip() for n in _names.split(",") if n.strip()]
                data = eval(_data.strip())
                dataIter = DataIter(names, data)

                if data_iter is None:
                    data_iter = dataIter
                else:
                    data_iter.set_sub_iter(dataIter)

            



if __name__ == "__main__":
    recipeParser = RecipeParser()

    recipeParser.parse("visual_recipes.txt")

    print(recipeParser)






