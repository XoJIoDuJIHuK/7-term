import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

import 'user_state.dart';
import 'util.dart';

class AuthenticationPage extends StatefulWidget {
  const AuthenticationPage({super.key});

  @override
  State<AuthenticationPage> createState() => _AuthenticationPageState();
}

class _AuthenticationPageState extends State<AuthenticationPage> {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final usersCollection = FirebaseFirestore.instance.collection('users');
  final GoogleSignIn _googleSignIn = GoogleSignIn();

  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  bool _isLoading = false;
  String _error = '';

  Future<bool> userExists(String email) async {
    final snapshot = await usersCollection.where('email', isEqualTo: email).get();
    return (snapshot).docs.isNotEmpty;
  }


  Future<void> _signInWithEmailAndPassword() async {
    if (!await isOnline()) return;
    final context = this.context;
    setState(() {
      _isLoading = true;
      _error = '';
    });

    try {
      Map<String, dynamic>? user;
      if (await userExists(_emailController.text)) {
        var signedUser = await _auth.signInWithEmailAndPassword(
          email: _emailController.text,
          password: _passwordController.text,
        );
        var existingUser = await getUser(signedUser.user!.email!);
        user = {
          'id': existingUser!['id'],
          'displayName': signedUser.user!.email,
          'email': signedUser.user!.email,
          'isAdmin': existingUser['isAdmin']
        };
      } else {
        final signedUser = await _auth.createUserWithEmailAndPassword(
          email: _emailController.text,
          password: _passwordController.text,
        );
        user = {
          'email': _emailController.text,
          'name': _emailController.text,
          'isAdmin': false
        };
        final addedUser = await usersCollection.add(user);
        user.remove('name');
        user['id'] = addedUser.id;
        user['displayName'] = _emailController.text;
      }
      context.read<UserCubit>().set(user);
    } on FirebaseAuthException catch (e) {
      setState(() {
        _error = e.message ?? 'An unknown error occurred.';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _signInWithGoogle() async {
    if (!await isOnline()) return;
    final context = this.context;
    setState(() {
      _isLoading = true;
      _error = '';
    });

    try {
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
      if (googleUser == null) {
        setState(() {
          _isLoading = false;
        });
        return;
      }

      final GoogleSignInAuthentication googleAuth = await googleUser.authentication;
      final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      await _auth.signInWithCredential(credential);

      var existingUser = await getUser(googleUser.email);
      var userId = existingUser?['id'];
      if (existingUser == null) {
        final addedUser = await usersCollection.add({
          'displayName': googleUser.displayName,
          'email': googleUser.email,
          'isAdmin': false
        });
        userId = addedUser.id;
      }

      context.read<UserCubit>().set({
        'id': userId,
        'name': googleUser.displayName,
        'email': googleUser.email,
        'isAdmin': existingUser != null ? existingUser['isAdmin'] : false,
      });

    } catch (e) {
      setState(() {
        _error = 'Error signing in with Google: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }



  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Authentication')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: BlocBuilder<UserCubit, Map<String, dynamic>?>(
            builder: (context, user) => Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                TextField(
                  controller: _emailController,
                  decoration: const InputDecoration(labelText: 'Email'),
                ),
                TextField(
                  controller: _passwordController,
                  decoration: const InputDecoration(labelText: 'Password'),
                  obscureText: true,
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: _isLoading ? null : () => _signInWithEmailAndPassword(),
                  child: _isLoading ? const CircularProgressIndicator() : const Text('Sign in with Email'),
                ),
                const SizedBox(height: 16),

                ElevatedButton(
                  onPressed: _isLoading ? null : () => _signInWithGoogle(),
                  child:  _isLoading ? const CircularProgressIndicator() : const Text('Sign in with Google'),
                ),

                ElevatedButton(
                  onPressed: () async {
                    if (!await isOnline()) return;
                    if (_emailController.text.isEmpty) return;
                    await _auth.sendPasswordResetEmail(email: _emailController.text);
                  },
                  child: Text('Forgot password')
                ),

                if (_error.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 16.0),
                    child: Text(
                      _error,
                      style: const TextStyle(color: Colors.red),
                    ),
                  ),
              ],
            )
          )
        ),
      ),
    );
  }

    @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

}