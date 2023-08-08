# pylint: disable=[W,R,C,import-error]

from shutil import make_archive
import re, json, os

class DisableRecipe:
    def __init__(self, name):
        self.name = name
    def to_dict(self):
        return {}
    
    def generate(self, path):
        with open(f"./{path}/data/minecraft/recipes/{self.name}.json", "w+", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

class ShapedRecipe:

    def __init__(self, name, shape, key, result, count):
        self.name = name
        self.shape = shape

        # _key = {}
        # for k, v in key.items():
        #     _key.update({k: {"item": v}})

        self.key = key
        self.result = result
        self.count = count

    def __repr__(self):
        return f"{self.name}.json\n" + json.dumps(self.to_dict(), indent=2) #"\n".join(self.shape) + "\n" + json.dumps(self.key, indent=2) + f"\n-> {self.result} x{self.count}"

    def __dict__(self):
        return self.to_dict()
    
    def to_dict(self):
        return {
            "type": "crafting_shaped",
            "pattern": self.shape,
            "key": self.key,
            "result": {
                "item": self.result,
                "count": self.count
            }
        }
    
    def generate(self, path):
        with open(f"./{path}/data/minecraft/recipes/{self.name}.json", "w+", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

class ShapelessRecipe:
    def __init__(self, name, ingredients, result, count):
        self.name = name
        self.ingredients = ingredients
        self.result = result
        self.count = count
    
    def __repr__(self):
        return f"{self.name}.json\n" + json.dumps(self.to_dict(), indent=2)#"\n".join(self.ingredients) + f"\n-> {self.result} x{self.count}"

    def __dict__(self):
        return self.to_dict()
    
    def to_dict(self):
        return {
            "type": "crafting_shapeless",
            "ingredients": self.ingredients,
            "result": {
                "item": self.result,
                "count": self.count
            }
        }
    
    def generate(self, path):
        with open(f"./{path}/data/minecraft/recipes/{self.name}.json", "w+", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

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
        self.disable = []

    def __repr__(self):
        return f"== {self.name} ==\n{json.dumps(self.mcmeta, indent=2)}\n{len(self.recipes)} recipes\n{len(self.disable)} default recipes disabled"

    def generate(self):
        os.mkdir(f"./{self.name}")
        os.mkdir(f"./{self.name}/data")
        os.mkdir(f"./{self.name}/data/minecraft")
        os.mkdir(f"./{self.name}/data/minecraft/recipes")

        with open(f"./{self.name}/pack.mcmeta", "w+", encoding="utf-8") as f:
            json.dump(
                self.mcmeta,
                f,
                indent=4
            )

        for disabled in self.disable:
            with open(f"./{self.name}/data/minecraft/recipes/{disabled}.json", "w+", encoding="utf-8") as f:
                f.write("{}")
        
        for recipe in self.recipes:
            recipe.generate(self.name)

        make_archive(f"{self.name}", "zip", root_dir=f"./{self.name}")

    def parse(self, file_name:str):
        with open(file_name, "r+", encoding="utf-8") as f:
            text = f.read()

        sections = text.split("----\n")

        pack_data_section = sections.pop(0).strip()

        if m := re.fullmatch(r"== *(?P<name>[a-z0-9_]+) *==\n+// *(?P<description>[A-Za-z0-9_ \-\+=~`!@#\$%\^&\*\(\)\\|[\];:'\",<\.>\?]*) *//\n+f-(?P<format>[0-9]+)", pack_data_section):
            d = m.groupdict()
            pack_name = d.get("name")
            description = d.get("description").strip()
            format = d.get("format")

            self.name = pack_name
            self.mcmeta = {
                "pack": {
                    "pack_format": int(format),
                    "description": description
                }
            }

        for section in sections:
            self.parse_section(section)

    def parse_patterns(self, text:str) -> list[list[str]]:
        lines = text.strip().split("\n")
        line_len = 0
        patterns = []
        for line in lines: line_len = max(line_len, len(line))

        for i in range(len(lines)): # get all lines to be the same length (just in case)
            lines[i] = f"{lines[i]: <{line_len}}"
        
        bounds: list[list] = []
        y = 0
        for line in lines:
            line_bounds = [[i.start(), i.end()] for i in re.finditer(r"\+-{3}(-{2}(-{2})?)?\+", line)]

            for b in line_bounds:
                for bound in bounds:
                    if len(bound) == 4:
                        continue
                    elif b == bound[0:2]:
                        bound.append(y)
                        break
                else:
                    bounds.append(b + [y])

            y += 1

        #print(bounds)

        for bound in bounds:
            x, w, y, h = bound

            sub = []
            for line in lines[y+1:h]:
                sub.append(re.sub(r"(.) ", r"\1", line[x+2:w-2]))
            
            #print(sub)
            patterns.append(sub)

        return patterns

    def parse_section(self, text:str):

        if not text.strip():
            return

        data_iter = None
        if "#ITER" in text:
            if "#END" not in text:
                return
            
            iters, recipe_data = text.split("#END")
            iters = iters.strip().split("#ITER")[1:]
            recipe_data = recipe_data.strip()

            for _iter in iters:
                _names, _data = _iter.split("=")
                names = [n.strip() for n in _names.split(",") if n.strip()]
                data = eval(_data.strip())
                dataIter = DataIter(names, data)

                if data_iter is None:
                    data_iter = dataIter
                else:
                    data_iter.set_sub_iter(dataIter)

        else:
            recipe_data = text.strip()


        if recipe_data.startswith(">") or recipe_data.startswith("#>"):
            ingredients = re.findall(r"^> *(.+)", recipe_data, re.RegexFlag.M)
            tag_ingredients = re.findall(r"^#> *(.+)", recipe_data, re.RegexFlag.M)
            m = re.search(r"\n-> *(?P<count>[0-9]+)x *(?P<result>.+)", recipe_data)
            d = m.groupdict()
            count = int(d["count"])
            result = d["result"]

            m = re.search(r"\n: *(?P<name>.*)", recipe_data)
            d = m.groupdict()
            name = d["name"]

            if data_iter:
                context = {}
                data_iter.start()

                try:
                    while True:
                        data_iter.next(context)
                        _ingredients = [{"item": eval(i, context)} for i in ingredients]
                        _ingredients += [{"tag": eval(i, context)} for i in tag_ingredients]
                        _result = eval(result, context)

                        self.recipes.append(ShapelessRecipe(eval(name, context), _ingredients, _result, count))

                except Exception as e:
                    if not isinstance(e, StopIteration):
                        print(e)
            
            else:
                self.recipes.append(ShapelessRecipe(eval(name), [eval(i) for i in ingredients] + [eval(i) for i in tag_ingredients], eval(result), count))

        elif recipe_data.startswith("#DISABLE"):
            recipe_names = [n.strip() for n in recipe_data.replace("#DISABLE", "").strip().split("\n")]
            for name in recipe_names:
                if data_iter:
                    context = {}
                    data_iter.start()

                    try:
                        while True:
                            data_iter.next(context)
                            n = eval(name, context)
                            if n not in self.disable:
                                self.disable.append(n)

                    except Exception as e:
                        if not isinstance(e, StopIteration):
                            print(e)
                else:
                    n = eval(name)
                    if n not in self.disable:
                        self.disable.append(n)

        else:

            k = re.findall(r"^((.) = (.+))", recipe_data, re.RegexFlag.M)
            k2 = re.findall(r"^((.) #= (.+))", recipe_data, re.RegexFlag.M)
            #print(k)
            key_data = []
            for line, key, val in k:
                recipe_data = recipe_data.replace(line, "")
                key_data.append([key, val])

            #print(k2)
            tag_key_data = []
            for line, key, val in k2:
                recipe_data = recipe_data.replace(line, "")
                tag_key_data.append([key, val])

            #print(recipe_data)
            m = re.search(r"^(?P<line>-> *(?P<count>[0-9]+)x *(?P<result>.+))", recipe_data, re.RegexFlag.M)
            d = m.groupdict()
            line = d["line"]
            count = int(d["count"])
            result = d["result"]
            recipe_data = recipe_data.replace(line, "")

            m = re.search(r"\n(?P<line>: *(?P<name>.*))", recipe_data)
            d = m.groupdict()
            line = d["line"]
            name = d["name"]

            recipe_data = recipe_data.replace(line, "")

            recipe_data = recipe_data.strip()

            patterns: list[list[str]] = self.parse_patterns(recipe_data)

            p = 0
            for pattern in patterns:
                if data_iter:
                    context = {}
                    data_iter.start()

                    try:
                        while True:
                            data_iter.next(context)
                            key = {}
                            for d in key_data:
                                k, v = d
                                key.update({k: {"item": eval(v, context)}})

                            for d in tag_key_data:
                                k, v = d
                                key.update({k: {"tag": eval(v, context)}})

                            _result = eval(result, context)

                            self.recipes.append(ShapedRecipe(eval(name, context) + f"_{p}" if len(patterns) > 1 else eval(name, context), pattern, key, _result, count))

                    except Exception as e:
                        if not isinstance(e, StopIteration):
                            print(e)
                else:
                    key = {}
                    for k, v in key_data:
                        key.update({k: {"item": eval(v)}})
                    for k, v in tag_key_data:
                        key.update({k: {"tag": eval(v)}})
                    self.recipes.append(ShapedRecipe(eval(name) + f"_{p}" if len(patterns) > 1 else eval(name), pattern, key, eval(result), count))

                p += 1


import glob

if __name__ == "__main__":

    files = glob.glob("generate/*.txt")

    for fn in files:

        recipeParser = RecipeParser()

        recipeParser.parse(fn)

        try:
            recipeParser.generate()
        except FileExistsError:
            print("Folder with this name already exists")

        print(recipeParser)

        with open(fn, "r+", encoding="utf-8") as f:
            dat = f.read()
        
        with open(fn.replace("generate\\", ""), "w+", encoding="utf-8") as f:
            f.write(dat)

        os.remove(f"./{fn}")
        (f"./{fn}")




