import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

import 'user_state.dart';
import 'util.dart';

class AuthenticationPage extends StatefulWidget {
  final FirebaseAuth? auth; // Optional parameter for FirebaseAuth
  const AuthenticationPage({Key? key, this.auth}) : super(key: key);

  @override
  State<AuthenticationPage> createState() => _AuthenticationPageState();
}

class _AuthenticationPageState extends State<AuthenticationPage> {
  late final FirebaseAuth _auth;
  final usersCollection = FirebaseFirestore.instance.collection('users');
  final GoogleSignIn _googleSignIn = GoogleSignIn();

  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  bool _isLoading = false;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _auth = widget.auth ?? FirebaseAuth.instance;
  }


  Future<void> _signInWithEmailAndPassword() async {
    // if (!await isOnline()) return;
    final context = this.context;
    setState(() {
      _isLoading = true;
      _error = 'xd';
    });

    try {
      Map<String, dynamic>? user;
      if (_emailController.text.isEmpty) {
        throw FirebaseAuthException(code: '123', message: 'Enter email');
      }
      if (_passwordController.text.length < 6) {
        throw FirebaseAuthException(code: '123', message: 'Password must be at least 6 characters');
      }
      if (!_emailController.text.contains('@')) {
        throw FirebaseAuthException(code: '123', message: 'Invalid email');
      }
      user = await authenticateUser(_auth, _emailController.text, _passwordController.text);
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
                    // if (!await isOnline()) return;
                    if (_emailController.text.isEmpty) {
                      setState(() {
                        _error = 'Enter email';
                      });
                      return;
                    }
                    await _auth.sendPasswordResetEmail(email: _emailController.text);
                  },
                  child: Text('Forgot password')
                ),

                Padding(
                  padding: const EdgeInsets.only(top: 16.0),
                  child: Text(
                    _error,
                    // 'xd',
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