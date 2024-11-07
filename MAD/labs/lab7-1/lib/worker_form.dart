// lib/worker_form.dart
import 'package:flutter/material.dart';
import 'worker.dart';
import 'database_helper.dart';

class WorkerFormScreen extends StatefulWidget {
  final Worker? worker;

  const WorkerFormScreen({super.key, this.worker});

  @override
  _WorkerFormScreenState createState() => _WorkerFormScreenState();
}

class _WorkerFormScreenState extends State<WorkerFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final DatabaseHelper _databaseHelper = DatabaseHelper();
  String _name = '';
  int _hoursWorked = 0;
  int? _id = 0;

  @override
  void initState() {
    super.initState();
    if (widget.worker != null) {
      _id = widget.worker!.id;
      _name = widget.worker!.name;
      _hoursWorked = widget.worker!.hoursWorked;
    }
  }

  void _saveWorker() async {
    if (_formKey.currentState!.validate()) {
      _formKey.currentState!.save();
      print(_name);

      final worker = Worker(
        id: _id, // This can be null for a new worker
        name: _name,
        hoursWorked: _hoursWorked,
      );

      if (worker.id == null) {
        // Insert a new worker
        await _databaseHelper.insertWorker(worker.toMap());
      } else {
        // Update existing worker
        await _databaseHelper.updateWorker(worker.toMap());
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.worker == null ? 'Add Worker' : 'Edit Worker'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                initialValue: _name,
                decoration: const InputDecoration(labelText: 'Name'),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter a name';
                  }
                  return null;
                },
                onSaved: (value) => _name = value!,
              ),
              TextFormField(
                initialValue: _hoursWorked.toString(),
                decoration: const InputDecoration(labelText: 'Hours Worked'),
                keyboardType: TextInputType.number,
                validator: (value) {
                  if (value == null || int.tryParse(value) == null) {
                    return 'Please enter a valid number';
                  }
                  return null;
                },
                onSaved: (value) => _hoursWorked = int.parse(value!),
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: _saveWorker,
                child: const Text('Save'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
