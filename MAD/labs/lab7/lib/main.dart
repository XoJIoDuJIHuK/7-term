// lib/main.dart
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:file_picker/file_picker.dart';
import 'worker.dart';
import 'database_helper.dart';
import 'worker_form.dart';
import 'load_workers_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  runApp(const WorkerManagementApp());
}

class WorkerManagementApp extends StatelessWidget {
  const WorkerManagementApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Worker Management',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const WorkerListScreen(),
      routes: {
        '/loadWorkers': (context) => const LoadWorkersScreen(),
      },
    );
  }
}

class WorkerListScreen extends StatefulWidget {
  const WorkerListScreen({super.key});

  @override
  _WorkerListScreenState createState() => _WorkerListScreenState();
}

class _WorkerListScreenState extends State<WorkerListScreen> {
  final DatabaseHelper _databaseHelper = DatabaseHelper();
  List<Worker> _workers = [];

  @override
  void initState() {
    super.initState();
    _fetchWorkers();
  }

  Future<void> _fetchWorkers() async {
    final workers = await _databaseHelper.getWorkers();
    setState(() {
      _workers = workers.map((e) => Worker.fromMap(e)).toList();
    });
  }

  Future<void> _saveWorkersToJson() async {
    try {
      // Get the directory for storing the file
      final directory = await getExternalStorageDirectory();
      if (directory == null) {
        throw Exception("Unable to access external storage");
      }

      // Convert workers to JSON
      final jsonString = jsonEncode(_workers.map((worker) => worker.toMap()).toList());
      final filePath = '${directory.path}/workers.json';

      // Save the JSON file
      final file = File(filePath);
      await file.writeAsString(jsonString);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Workers saved to $filePath')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error saving workers: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Worker List'),
        actions: [
          IconButton(
            icon: const Icon(Icons.save),
            onPressed: _saveWorkersToJson,
          ),
          IconButton(
            icon: const Icon(Icons.folder_open),
            onPressed: () {
              Navigator.pushNamed(context, '/loadWorkers');
            },
          ),
        ],
      ),
      body: ListView.builder(
        itemCount: _workers.length,
        itemBuilder: (context, index) {
          final worker = _workers[index];
          return ListTile(
            title: Text(worker.name),
            subtitle: Text('Hours worked: ${worker.hoursWorked}'),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const WorkerFormScreen()),
          ).then((_) {
            _fetchWorkers();
          });
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}
