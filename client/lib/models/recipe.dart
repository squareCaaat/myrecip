import 'ingredient.dart';

class Recipe {
  final String recipeId;
  final String title;
  final String baseSpirit;
  final List<Ingredient> ingredients;
  final String? instructions;
  final String? notes;
  final String? photoUrl;

  Recipe({
    required this.recipeId,
    required this.title,
    required this.baseSpirit,
    required this.ingredients,
    this.instructions,
    this.notes,
    this.photoUrl,
  });
}


