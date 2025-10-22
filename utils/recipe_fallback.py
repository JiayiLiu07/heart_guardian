# utils/recipe_fallback.py

import json
import random
from typing import Dict, List, Any
import os

class RecipeFallbackGenerator:
    """菜谱回退生成器 - 生成中文菜谱数据"""
    
    def __init__(self):
        self.disease_categories = {
            'infectious': ['病毒性心肌炎', '细菌性心内膜炎', '心包炎'],
            'cardiac_tumor': ['原发性心脏肿瘤', '转移性心脏肿瘤'],
            'coronary_artery': ['冠状动脉疾病', '心肌梗死'],
            'valvular': ['二尖瓣疾病', '主动脉瓣疾病'],
            'arrhythmia': ['心房颤动', '室性心动过速'],
            'congenital': ['房间隔缺损', '室间隔缺损'],
            'cardiomyopathy': ['扩张型心肌病', '肥厚型心肌病']
        }
        
        # 中文食材池
        self.ingredients_pool = {
            'proteins': ['鸡胸肉', '三文鱼', '豆腐', '扁豆', '鸡蛋', '火鸡肉', '白鱼', '虾仁'],
            'vegetables': ['菠菜', '西兰花', '胡萝卜', '彩椒', '番茄', '羽衣甘蓝', '西葫芦', '蘑菇'],
            'grains': ['糙米', '藜麦', '燕麦片', '全麦面包', '大麦', '荞麦'],
            'fruits': ['浆果', '苹果', '香蕉', '橙子', '梨', '猕猴桃'],
            'dairy': ['低脂酸奶', '脱脂牛奶', '低脂奶酪', '茅屋奶酪'],
            'fats': ['橄榄油', '牛油果', '坚果', '种子'],
            'seasonings': ['大蒜', '姜', '姜黄', '肉桂', '罗勒', '牛至']
        }
        
        # 过敏原标签
        self.allergen_tags = ['无麸质', '无乳制品', '无坚果', '无大豆', '无蛋类', '无海鲜']
        
        # 菜系类型
        self.cuisine_types = ['地中海风味', '亚洲风味', '美式', '墨西哥风味', '意大利风味', '中东风味']
        
        # 烹饪方法
        self.cooking_methods = ['蒸', '烤', '烘烤', '快炒', '炖煮', '水煮']

    def generate_nutrient_range(self, disease_key: str) -> Dict[str, float]:
        """根据疾病类型生成营养范围"""
        nutrient_ranges = {
            'infectious': {'calories': (400, 600), 'protein': (20, 35), 'carbs': (40, 60), 'fat': (8, 15), 'fiber': (5, 12)},
            'cardiac_tumor': {'calories': (350, 550), 'protein': (25, 40), 'carbs': (35, 55), 'fat': (6, 12), 'fiber': (6, 14)},
            'coronary_artery': {'calories': (300, 500), 'protein': (15, 30), 'carbs': (30, 50), 'fat': (5, 10), 'fiber': (8, 16)},
            'valvular': {'calories': (350, 550), 'protein': (20, 35), 'carbs': (35, 55), 'fat': (7, 13), 'fiber': (6, 12)},
            'arrhythmia': {'calories': (400, 600), 'protein': (18, 32), 'carbs': (45, 65), 'fat': (8, 14), 'fiber': (5, 10)},
            'congenital': {'calories': (450, 650), 'protein': (22, 38), 'carbs': (50, 70), 'fat': (9, 16), 'fiber': (4, 9)},
            'cardiomyopathy': {'calories': (380, 580), 'protein': (24, 42), 'carbs': (38, 58), 'fat': (6, 11), 'fiber': (7, 13)}
        }
        
        base_range = nutrient_ranges.get(disease_key, nutrient_ranges['infectious'])
        
        return {
            'calories': round(random.uniform(*base_range['calories']), 1),
            'protein': round(random.uniform(*base_range['protein']), 1),
            'carbs': round(random.uniform(*base_range['carbs']), 1),
            'fat': round(random.uniform(*base_range['fat']), 1),
            'fiber': round(random.uniform(*base_range['fiber']), 1)
        }

    def generate_ingredients(self, disease_key: str) -> List[str]:
        """生成食材列表"""
        ingredients = []
        
        # 基础蛋白质
        protein = random.choice(self.ingredients_pool['proteins'])
        ingredients.append(protein)
        
        # 蔬菜
        veg_count = random.randint(2, 4)
        vegetables = random.sample(self.ingredients_pool['vegetables'], veg_count)
        ingredients.extend(vegetables)
        
        # 谷物
        if random.random() < 0.8:  # 80%概率包含谷物
            grain = random.choice(self.ingredients_pool['grains'])
            ingredients.append(grain)
        
        # 根据疾病类型调整食材
        if disease_key in ['coronary_artery', 'cardiomyopathy']:
            # 心脏疾病推荐低脂食材
            if '牛油果' in ingredients:
                ingredients.remove('牛油果')
            if random.random() < 0.7:
                ingredients.append('大蒜')  # 大蒜对心脏有益
        
        # 添加调味料
        if len(ingredients) < 6:
            seasoning = random.choice(self.ingredients_pool['seasonings'])
            ingredients.append(seasoning)
        
        return ingredients

    def generate_allergen_tags(self) -> List[str]:
        """生成过敏原标签"""
        if random.random() < 0.3:  # 30%的概率有过敏原
            return random.sample(self.allergen_tags, random.randint(1, 2))
        return []

    def generate_recipe_name(self, cuisine: str, main_ingredient: str, cooking_method: str) -> str:
        """生成菜谱名称"""
        name_templates = [
            f"{cooking_method}{main_ingredient}{cuisine}风味",
            f"{cuisine}{main_ingredient}碗",
            f"健康{cooking_method}{main_ingredient}",
            f"{main_ingredient}{cuisine}美食",
            f"护心{main_ingredient}餐"
        ]
        return random.choice(name_templates)

    def generate_recipe(self, disease_key: str, day: int, meal_type: str) -> Dict[str, Any]:
        """生成单个菜谱"""
        nutrients = self.generate_nutrient_range(disease_key)
        ingredients = self.generate_ingredients(disease_key)
        cuisine = random.choice(self.cuisine_types)
        cooking_method = random.choice(self.cooking_methods)
        main_ingredient = ingredients[0] if ingredients else "鸡胸肉"
        
        recipe_name = self.generate_recipe_name(cuisine, main_ingredient, cooking_method)
        
        return {
            "day": day,
            "meal_type": meal_type,
            "name": recipe_name,
            "calories": nutrients['calories'],
            "protein": nutrients['protein'],
            "carbs": nutrients['carbs'],
            "fat": nutrients['fat'],
            "fiber": nutrients['fiber'],
            "ingredients": ingredients,
            "cuisine": cuisine,
            "cooking_method": cooking_method,
            "allergen_tags": self.generate_allergen_tags(),
            "prep_time": random.randint(15, 45),
            "cook_time": random.randint(10, 60),
            "servings": random.randint(1, 4),
            "description": f"一道{cooking_method}的{cuisine}菜肴，以{main_ingredient}为主料，非常适合心脏健康。",
            "instructions": [
                f"准备所有{len(ingredients)}种食材",
                f"将{main_ingredient}与选定的蔬菜一起{cooking_method}",
                "用心健康的香草调味",
                "温热享用您的营养餐"
            ]
        }

    def generate_weekly_plan(self, disease_key: str) -> List[Dict[str, Any]]:
        """生成一周的饮食计划"""
        weekly_recipes = []
        meal_types = ['早餐', '午餐', '晚餐']
        
        for day in range(1, 8):  # 7天
            for meal_type in meal_types:
                recipe = self.generate_recipe(disease_key, day, meal_type)
                weekly_recipes.append(recipe)
        
        return weekly_recipes

    def generate_recipe_pool(self, min_recipes_per_category: int = 150) -> Dict[str, List[Dict[str, Any]]]:
        """生成菜谱池"""
        print("正在生成菜谱池...")
        recipe_pool = {}
        total_recipes = 0
        
        for disease_key in self.disease_categories.keys():
            print(f"正在为 {disease_key} 生成菜谱...")
            category_recipes = []
            
            # 确保每个疾病类别至少有min_recipes_per_category个菜谱
            weeks_needed = (min_recipes_per_category + 20) // 21  # 每周21餐（7天×3餐）
            
            for week in range(weeks_needed + 2):  # +2 确保足够数量
                weekly_plan = self.generate_weekly_plan(disease_key)
                category_recipes.extend(weekly_plan)
            
            # 如果还是不够，继续添加直到满足要求
            while len(category_recipes) < min_recipes_per_category:
                extra_recipe = self.generate_recipe(disease_key, 
                                                  random.randint(1, 7), 
                                                  random.choice(['早餐', '午餐', '晚餐']))
                category_recipes.append(extra_recipe)
            
            recipe_pool[disease_key] = category_recipes
            total_recipes += len(category_recipes)
            print(f"为 {disease_key} 生成了 {len(category_recipes)} 条菜谱")
        
        print(f"\n菜谱池生成完成！总共生成了 {total_recipes} 条菜谱")
        return recipe_pool

    def save_recipe_pool(self, filepath: str = "../assets/recipe_pool.json"):
        """保存菜谱池到文件"""
        recipe_pool = self.generate_recipe_pool(min_recipes_per_category=150)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(recipe_pool, f, indent=2, ensure_ascii=False)
        
        total_recipes = sum(len(recipes) for recipes in recipe_pool.values())
        print(f"菜谱池保存完成！总共 {total_recipes} 条菜谱")
        print(f"保存路径: {os.path.abspath(filepath)}")
        
        # 打印每个类别的详细数量
        print("\n各疾病类别菜谱数量统计:")
        for disease_key, recipes in recipe_pool.items():
            print(f"  {disease_key}: {len(recipes)} 条菜谱")
        
        return recipe_pool

def main():
    """主函数"""
    generator = RecipeFallbackGenerator()
    recipe_pool = generator.save_recipe_pool()

if __name__ == "__main__":
    main()