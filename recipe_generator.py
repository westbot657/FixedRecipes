# pylint: disable=[W,R,C,import-error]

def createShaplessRecipe(name:str, ingredients:list, result:str, count:int):
    recipe = {
        "type": "crafting_shapeless",
        "ingredients": [
            {"item": f"minecraft:{item}"} for item in ingredients
        ],
        "result": {
            "item": f"minecraft:{result}",
            "count": count
        }
    }

    





wood_types = [
    "oak", "birch", "acacia", "dark_oak", "spruce", "cherry",
    "mangrove", "bamboo", "jungle", "warped", "crimson"
]


































