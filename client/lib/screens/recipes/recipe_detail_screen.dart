import 'package:flutter/material.dart';
import '../../models/recipe.dart';

class RecipeDetailScreen extends StatelessWidget {
  final Recipe recipe;

  const RecipeDetailScreen({super.key, required this.recipe});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 240.0,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              title: Text(recipe.title),
              background: Container(color: Colors.grey.shade300),
            ),
            actions: [
              IconButton(icon: const Icon(Icons.share), onPressed: () {}),
              IconButton(icon: const Icon(Icons.edit), onPressed: () {}),
            ],
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '베이스: ${recipe.baseSpirit}',
                    style: const TextStyle(fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    '재료',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 8),
                  ...recipe.ingredients.map(
                    (i) => Text('- ${i.name} ${i.amount}${i.unit}'),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    '제작 과정',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 8),
                  Text(recipe.instructions ?? '설명이 없습니다'),
                  const SizedBox(height: 16),
                  const Text(
                    '노트',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 8),
                  Text(recipe.notes ?? '노트가 없습니다'),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}


