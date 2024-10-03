import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class PageViewer extends StatefulWidget {
  const PageViewer({super.key});

  @override
  _PageViewerState createState() => _PageViewerState();
}

class _PageViewerState extends State<PageViewer> {

  Container getPage(String text, Color color) => Container(
    color: color,
    child: Center(
      child: Text(
        text,
        style: const TextStyle(fontSize: 32, color: Colors.black),
      ),
    ),
  );

  static const platform = MethodChannel('cpu_usage_channel');
  String _cpuUsage = 'А где проц?';

  Future<void> _getCpuUsage() async {
    String cpuUsage;
    try {
      final result = await platform.invokeMethod('getCpuUsage');
      cpuUsage = 'CPU Usage: $result%';
    } on PlatformException catch (e) {
      cpuUsage = "Failed to get CPU usage: '${e.message}'.";
    }

    setState(() {
      _cpuUsage = cpuUsage;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('PageView Example'),
      ),
      body: PageView(
        children: <Widget>[
          getPage('Push me', const Color(0xffffffff)),
          getPage('And then just touch me', const Color(0xff826f7a)),
          getPage('Till I can get my', Colors.deepPurple),
          getPage('Satisfaction', Colors.yellow),
          Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              Text(
                _cpuUsage,
                style: const TextStyle(fontSize: 24),
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: _getCpuUsage,
                child: const Text('Get CPU Usage'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
