# pylint: disable=[W,R,C,import-error]

def createShapelessRecipe(name:str, ingredients:list, result:str, count:int):
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

def createShapedRecipe(name:str, pattern:list[str], key:dict, result:str, count:int):
    recipe = {
        "type": "crafting_shaped",
        "pattern": pattern,
        "key": key,
        "result": {
            "item": f"minecraft:{result}",
            "count": count
        }
    }

def createShapelessRecipeVS(name:str, ingredients:list, result:str, volumetric_count:int, stacking_count:int):
    createShapelessRecipe(f"generated_volumetric/{name}", ingredients, result, volumetric_count)
    createShapelessRecipe(f"generated_stacking/{name}", ingredients, result, stacking_count)

def createShapedRecipeVS(name:str, pattern:list[str], key:dict, result:str, volumetric_count:int, stacking_count:int):
    createShapedRecipe(f"generated_volumetric/{name}", pattern, key, result, volumetric_count)
    createShapedRecipe(f"generated_stacking/{name}", pattern, key, result, stacking_count)




wood_types = [
    "oak", "birch", "acacia", "dark_oak", "spruce", "cherry",
    "mangrove", "bamboo", "jungle", "warped", "crimson"
]


# Sticks:
#
# Stacking:
# stick: 13x13 pixels every 3
# 32/3 = 10.666667 = 10  x16 = 160
# stick recipe = 2 planks = 160 sticks (stacking)
#
# Volumetric:
# 3x11 + 4 = 37 voxels
# 2 planks (8192 voxels) / 37 = 221.405405... = 221

wood_specific_recipes = [
    lambda t: createShapelessRecipeVS(f"{t}_planks", [f"{t}_log"], f"{t}_planks", 1, 1),
    lambda t: createShapedRecipeVS(f"{t}_stairs", ["#  ", "## ", "###"], {"#": {"item": f"minecraft:{t}_planks"}}, f"{t}_stairs", 8, 6),
    lambda t: createShapelessRecipeVS(f"{t}_button", [f"{t}_planks"], f"{t}_button", 85, 80),
    lambda t: createShapedRecipeVS(f"{t}_trapdoor", ["###", "###"], {"#": {"item": f"minecraft:{t}_planks"}}, f"{t}_trapdoor", 32, 32),
    lambda t: createShapedRecipeVS(f"{t}_door", ["##", "##", "##"], {"#": {"item": f"minecraft:{t}_planks"}}, f"{t}_door", 16, 16),
    # 11 x 16 x 2
    lambda t: createShapedRecipeVS(f"{t}_gate", ["|#|", "|#|"], {"#": {"item": f"minecraft:{t}_gate"}}, f"{t}_gate", 1, 1)
]












"""
Enchantments:

Unbreaking            - 2 straps
Mending               - Gold Pages

Looting               - Gold Sword
Fire Aspect           - Sword with flame
Sweeping Edge         - Sword with sweeping effect
Sharpness             - Sword with a sparkle on the tip
Smite                 - Sword with something withery on the tip
Bane of Arthropods    - Sword with something spidery on the tip
Knockback             - Sword with motion ghost

Efficiency            - Pickaxe with motion ghost
Fortune               - Emerald Pickaxe
Silk Touch            - Gold Pickaxe

Flame                 - Flaming Arrow
Punch                 - Arrow with motion ghost
Power                 - Arrow with gold feathers
Infinity              - Arrow with gold head

Protection            - Diamond book trim
Fire Protection       - Firey book trim
Blast Protection      - blackish book trim
Projectile Protection - silver book trim
Thorns                - spikey book cover

Aqua Affinity         - blue helmet?
Respiration           - Bubbles

Swift Sneak           - Sculk Texture cover

Feather Falling       - Feather
Soul Speed            - Soul face particle
Depth Strider         - sea grass
Frost Walker          - ice

Piercing              - Arrow going through something (probably going through the book)
Multishot             - More arrows
Quick Charge          - Arrow in crossbow?

Impaling              - trident going through book
Riptide               - trident with swirling effect
Loyalty               - trident with a heart?
Channeling            - trident with lightning

Curse of Binding      - armor with a lock / just a lock / thicker book
Curse of Vanishing    - half opacity item?

Lure                  - fish
Luck of the Sea       - fancy fish







"""



















