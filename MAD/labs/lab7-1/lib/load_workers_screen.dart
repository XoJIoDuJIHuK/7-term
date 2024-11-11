// lib/load_workers_screen.dart
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'worker.dart';
import 'package:logging/logging.dart';

final _log = Logger('MyApp');

class LoadWorkersScreen extends StatefulWidget {
  const LoadWorkersScreen({super.key});

  @override
  _LoadWorkersScreenState createState() => _LoadWorkersScreenState();
}

class _LoadWorkersScreenState extends State<LoadWorkersScreen> {
  List<Worker> _loadedWorkers = [];
  int? _folderToLoad = 1;

  Future<void> _loadWorkersFromJson() async {
    try {
      String filePath = '';
      if (_folderToLoad != null) {
        var directory = await getExternalStorageDirectory();
        switch (_folderToLoad) {
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
        filePath = '${directory!.path}/workers.json';
      } else {
        // Pick a JSON file
        final result = await FilePicker.platform.pickFiles(
          type: FileType.custom,
          allowedExtensions: ['json'],
        );

        if (result == null || result.files.single.path == null) {
          return; // User canceled or no file picked
        }

        filePath = result.files.single.path!;
      }
      final file = File(filePath);

      // Read the file content
      final jsonString = await file.readAsString();
      _log.info("JSON string: $jsonString");
      final List<dynamic> jsonData = jsonDecode(jsonString);
      _log.info("JSON data: $jsonData");

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
          TextFormField(
              initialValue: "$_folderToLoad",
              decoration: const InputDecoration(labelText: 'Folder to load from'),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Please enter number of folder to load workers from';
                }
                return null;
              },
              onChanged: (value) {
                _log.info("Value to save $value");
                _folderToLoad = value.isNotEmpty ? int.parse(value) : null;
              }
          ),
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
