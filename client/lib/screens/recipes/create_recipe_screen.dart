import 'package:flutter/material.dart';
import '../../models/ingredient.dart';

class CreateRecipeScreen extends StatefulWidget {
  const CreateRecipeScreen({super.key});

  @override
  State<CreateRecipeScreen> createState() => _CreateRecipeScreenState();
}

class _CreateRecipeScreenState extends State<CreateRecipeScreen> {
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  final TextEditingController _titleController = TextEditingController();
  final TextEditingController _instructionsController = TextEditingController();
  final TextEditingController _notesController = TextEditingController();

  final List<Ingredient> _ingredients = [];
  String? _selectedBaseSpirit;

  @override
  void dispose() {
    _titleController.dispose();
    _instructionsController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  void _addIngredient() {
    setState(() {
      _ingredients.add(
        Ingredient(name: '', amount: 0, unit: 'ml', color: '#FFFFFF'),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('새 레시피'),
        actions: [TextButton(onPressed: () {}, child: const Text('저장'))],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16.0),
          children: [
            TextFormField(
              controller: _titleController,
              decoration: const InputDecoration(labelText: '제목'),
              validator: (v) => (v == null || v.isEmpty) ? '제목을 입력하세요' : null,
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: _selectedBaseSpirit,
              items: const [
                DropdownMenuItem(value: '진', child: Text('진')),
                DropdownMenuItem(value: '보드카', child: Text('보드카')),
                DropdownMenuItem(value: '럼', child: Text('럼')),
                DropdownMenuItem(value: '위스키', child: Text('위스키')),
                DropdownMenuItem(value: '테킬라', child: Text('테킬라')),
              ],
              onChanged: (v) => setState(() => _selectedBaseSpirit = v),
              decoration: const InputDecoration(labelText: '베이스 주류'),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                const Text('재료'),
                const Spacer(),
                IconButton(
                  onPressed: _addIngredient,
                  icon: const Icon(Icons.add),
                ),
              ],
            ),
            ..._ingredients.asMap().entries.map((e) {
              final index = e.key;
              return Card(
                margin: const EdgeInsets.symmetric(vertical: 6),
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    children: [
                      TextFormField(
                        decoration: const InputDecoration(labelText: '재료명'),
                        onChanged: (v) => _ingredients[index] = Ingredient(
                          name: v,
                          amount: _ingredients[index].amount,
                          unit: _ingredients[index].unit,
                          color: _ingredients[index].color,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Expanded(
                            child: TextFormField(
                              decoration: const InputDecoration(labelText: '양'),
                              keyboardType: TextInputType.number,
                              onChanged: (v) =>
                                  _ingredients[index] = Ingredient(
                                    name: _ingredients[index].name,
                                    amount: double.tryParse(v) ?? 0,
                                    unit: _ingredients[index].unit,
                                    color: _ingredients[index].color,
                                  ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: TextFormField(
                              decoration: const InputDecoration(
                                labelText: '단위 (ml, g 등)',
                              ),
                              onChanged: (v) =>
                                  _ingredients[index] = Ingredient(
                                    name: _ingredients[index].name,
                                    amount: _ingredients[index].amount,
                                    unit: v,
                                    color: _ingredients[index].color,
                                  ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              );
            }),
            const SizedBox(height: 12),
            TextFormField(
              controller: _instructionsController,
              decoration: const InputDecoration(labelText: '제작 과정'),
              maxLines: 4,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _notesController,
              decoration: const InputDecoration(labelText: '노트'),
              maxLines: 3,
            ),
          ],
        ),
      ),
    );
  }
}


