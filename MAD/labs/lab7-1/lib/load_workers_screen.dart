// lib/load_workers_screen.dart
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'worker.dart';

class LoadWorkersScreen extends StatefulWidget {
  const LoadWorkersScreen({super.key});

  @override
  _LoadWorkersScreenState createState() => _LoadWorkersScreenState();
}

class _LoadWorkersScreenState extends State<LoadWorkersScreen> {
  List<Worker> _loadedWorkers = [];

  Future<void> _loadWorkersFromJson() async {
    try {
      // Pick a JSON file
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['json'],
      );

      if (result == null || result.files.single.path == null) {
        return; // User canceled or no file picked
      }

      final filePath = result.files.single.path!;
      final file = File(filePath);

      // Read the file content
      final jsonString = await file.readAsString();
      final List<dynamic> jsonData = jsonDecode(jsonString);

      // Convert JSON data to a list of workers
      setState(() {
        _loadedWorkers = jsonData.map((item) => Worker.fromMap(item)).toList();
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Loaded workers from $filePath')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading workers: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Load Workers'),
      ),
      body: Column(
        children: [
          ElevatedButton(
            onPressed: _loadWorkersFromJson,
            child: const Text('Load Workers from JSON'),
          ),
          Expanded(
            child: ListView.builder(
              itemCount: _loadedWorkers.length,
              itemBuilder: (context, index) {
                final worker = _loadedWorkers[index];
                return ListTile(
                  title: Text(worker.name),
                  subtitle: Text('Hours worked: ${worker.hoursWorked}'),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
