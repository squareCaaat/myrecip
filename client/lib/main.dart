import 'package:flutter/material.dart';
import 'utils/app_theme.dart';
import 'screens/main_navigator.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/signup_screen.dart';
import 'screens/auth/forgot_password_screen.dart';
import 'screens/recipes/recipe_detail_screen.dart';
import 'models/recipe.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '나만의 칵테일',
      theme: AppTheme.light(),
      routes: {
        '/': (context) => const MainNavigator(),
        '/login': (context) => const LoginScreen(),
        '/signup': (context) => const SignupScreen(),
        '/forgot-password': (context) => const ForgotPasswordScreen(),
      },
      onGenerateRoute: (settings) {
        if (settings.name == '/recipe-detail' && settings.arguments is Recipe) {
          return MaterialPageRoute(
            builder: (_) =>
                RecipeDetailScreen(recipe: settings.arguments as Recipe),
          );
        }
        return null;
      },
    );
  }
}
