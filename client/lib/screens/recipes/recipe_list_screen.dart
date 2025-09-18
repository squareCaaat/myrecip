import 'package:flutter/material.dart';
import '../../models/ingredient.dart';
import '../../models/recipe.dart';
import '../../widgets/recipe_card.dart';

class RecipeListScreen extends StatelessWidget {
  const RecipeListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final List<Recipe> mock = [
      Recipe(
        recipeId: 'r1',
        title: '마티니',
        baseSpirit: '진',
        ingredients: [
          Ingredient(name: '진', amount: 60, unit: 'ml', color: '#FFFFFF'),
          Ingredient(
            name: '드라이 베르무스',
            amount: 10,
            unit: 'ml',
            color: '#FFFF00',
          ),
        ],
      ),
      Recipe(
        recipeId: 'r2',
        title: '올드 패션드',
        baseSpirit: '버번',
        ingredients: [
          Ingredient(name: '버번', amount: 60, unit: 'ml', color: '#A0522D'),
          Ingredient(name: '설탕', amount: 5, unit: 'g', color: '#FFD700'),
        ],
      ),
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('내 칵테일')),
      body: ListView.builder(
        itemCount: mock.length,
        itemBuilder: (context, index) {
          final item = mock[index];
          return RecipeCard(
            recipe: item,
            onTap: () => Navigator.of(
              context,
            ).pushNamed('/recipe-detail', arguments: item),
          );
        },
      ),
    );
  }
}


