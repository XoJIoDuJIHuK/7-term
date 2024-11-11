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
import 'package:logging/logging.dart';

void main() async {
  Logger.root.level = Level.ALL; // Set the desired logging level
  Logger.root.onRecord.listen((record) {
    print('${record.level.name}: ${record.time}: ${record.message}');
  });

  WidgetsFlutterBinding.ensureInitialized();

  runApp(const WorkerManagementApp());
}

final _log = Logger('MyApp');

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
  int _folderToSave = 1;

  @override
  void initState() {
    super.initState();
    _fetchWorkers();
  }

  Future<void> _fetchWorkers() async {
    final workers = await _databaseHelper.getWorkers();
    _log.info("Workers: ");
    _log.info(workers);
    setState(() {
      _workers = workers.map((e) => Worker.fromMap(e)).toList();
    });
  }

  Future<void> _saveWorkersToJson() async {
    try {
      // Get the directory for storing the file
      var directory = await getExternalStorageDirectory();
      switch (_folderToSave) {
        case 1:
          {
            directory = await getTemporaryDirectory();
            // /data/data/con.example.empty_test/cache
            break;
          }
        case 2:
          {
            directory = await getApplicationSupportDirectory();
            // /data/user/0/com.example.empty_test/files
            break;
          }
        case 3:
          {
            directory = await getApplicationDocumentsDirectory();
            // /data/user/0/com.example.empty_test/app_flutter
            break;
          }
        case 4:
          {
            directory = await getLibraryDirectory();
            // not supported on android
            break;
          }
        case 5:
          {
            directory = await getApplicationCacheDirectory();
            // /data/user/0/com.example.empty_test/cache
            break;
          }
        case 6:
          {
            directory = await getApplicationDocumentsDirectory();
            // /data/user/0/com.example.empty_test/app_flutter
            break;
          }
        case 7:
          {
            directory = (await getExternalCacheDirectories())![0];
            // /storage/emulated/0/Android/data/com.example.empty_test/cache
            break;
          }
        case 8:
          {
            directory = await getExternalStorageDirectory();
            // /storage/emulated/0/Android/data/com.example.empty_test/files
            break;
          }
        default:
          {
            directory = await getDownloadsDirectory();
            // /storage/emulated/0/Android/data/com.example.empty_test/files/downloads
            break;
          }
      }
      if (directory == null) {
        throw Exception("Unable to access external storage");
      }

      _log.info("Number: $_folderToSave, Directory: ${directory.path}");
      // return;

      // Convert workers to JSON
      final jsonString = jsonEncode(
          _workers.map((worker) => worker.toMap()).toList());
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
      body: Column(
        children: [
          TextFormField(
              initialValue: "$_folderToSave",
              decoration: const InputDecoration(labelText: 'Folder to save'),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Please enter number of folder to save';
                }
                return null;
              },
              onChanged: (value) {
                _log.info("Value to save $value");
                _folderToSave = int.parse(value);
              }
          ),
          Expanded(
              child: ListView.builder(
                  itemCount: _workers.length,
                  itemBuilder: (context, index) {
                    final worker = _workers[index];
                    return ListTile(
                        title: Text(worker.name),
                        subtitle: Text('Hours worked: ${worker.hoursWorked}'),
                        onTap: () {
                          // Navigate to the WorkerFormScreen with the selected worker
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) =>
                                  WorkerFormScreen(worker: worker),
                            ),
                          ).then((_) {
                            _fetchWorkers(); // Refresh the list after returning
                          });
                        }
                    );
                  }
              )
          )
        ],
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