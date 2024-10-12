import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import './schedule.dart';

class Home extends StatefulWidget {
  const Home({super.key});

  @override
  _HomeState createState() => _HomeState();
}

class _HomeState extends State<Home> {
  int _selectedIndex = 0;
  String transfer_value = '';
  final Uri _url = Uri.parse('alarm:lmao');
  final TextEditingController _controller = TextEditingController();

  void onSubmitted(value) {
    setState(() {
      transfer_value = value;
    });
  }

  Future<void> _launchUrl() async {
    if (!await launchUrl(_url)) {
      throw Exception('Could not launch $_url');
    }
  }

  @override
  Widget build(BuildContext context) {
    double screenWidth = MediaQuery.of(context).size.width;
    double scale = screenWidth / 100; // Similar to vw unit in CSS

    return Scaffold(
      backgroundColor: const Color(0xFFF5F6FA),
      appBar: AppBar(
        title: const Text('Prayer Times', style: TextStyle(color: Colors.black)),
        elevation: 0,
        backgroundColor: Colors.transparent,
        leading: const Icon(Icons.menu, color: Colors.black),
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                child: Padding(
                  padding: EdgeInsets.all(scale * 4), // Responsive padding
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Header with Date and Hijri Date
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const DrawerButton(),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Text(
                                'Wednesday, 28 March',
                                style: TextStyle(
                                  fontSize: scale * 4,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                '13 Sha\'ban, 1442 AH',
                                style: TextStyle(
                                  fontSize: scale * 3,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.purple,
                                ),
                              ),
                            ],
                          )
                        ],
                      ),
                      SizedBox(height: scale * 5),

                      ElevatedButton(
                          onPressed: _launchUrl,
                          child: Text("ALARM")
                      ),

                      // Sehri Time, Dhuhr Remaining Time, Asr Time, Iftar Time
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          buildPrayerTimeCard(
                              title: 'Sehri Time',
                              time: '3:40',
                              timePostfix: 'am',
                              timeColor: Colors.purple,
                              iconColor: Colors.purple,
                              scale: scale,
                              backgroundColor: const Color(0xFFE3DDFF),
                              titleColor: Colors.black,
                              iconPath: "assets/moon.png"
                          ),
                          buildPrayerTimeCard(
                              title: 'Remaining',
                              accentText: 'Dhuhr',
                              time: '15:20',
                              timePostfix: 'min',
                              timeColor: Colors.white,
                              iconColor: Colors.orange,
                              scale: scale,
                              backgroundColor: const Color(0xFF36229F),
                              titleColor: Colors.white,
                              iconPath: "assets/sun.png"
                          ),
                        ],
                      ),
                      SizedBox(height: scale * 5),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          buildPrayerTimeCard(
                              title: 'Next Prayer',
                              accentText: 'Asr',
                              time: '4:24',
                              timePostfix: 'pm',
                              timeColor: Colors.white,
                              iconColor: Colors.blue,
                              scale: scale,
                              backgroundColor: const Color(0xFF826AFB),
                              titleColor: Colors.white,
                              iconPath: "assets/cloudy.png"
                          ),
                          buildPrayerTimeCard(
                              title: 'Iftar Time',
                              time: '6:45',
                              timePostfix: 'pm',
                              timeColor: const Color(0xFFE8BD46),
                              iconColor: Colors.limeAccent,
                              scale: scale,
                              backgroundColor: const Color(0xFFFDE9C2),
                              titleColor: Colors.black,
                              iconPath: "assets/cloudy-wind.png"
                          ),
                        ],
                      ),

                      SizedBox(height: scale * 5),

                      // Daily Dua section
                      buildDailyDuaCard(scale),

                      SizedBox(height: scale * 5),

                      // Categories Section
                      buildCategoriesSection(scale),
                      Column(
                        children: [
                          TextField(
                            controller: _controller,
                            decoration: const InputDecoration(labelText: 'Enter a value'),
                          ),
                          const SizedBox(height: 20),
                          ElevatedButton(
                            onPressed: () {
                              onSubmitted(_controller.text);
                            },
                            child: const Text('Submit'),
                          ),
                        ],
                      ),
                    ]
                  )
                ),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) {
          setState(() {
            _selectedIndex = index;
          });
          if (index == 1) {
            _navigateToSecondPage(context);
          }
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.access_time),
            label: 'Schedule',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.notifications),
            label: 'Notifications',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.settings),
            label: 'Settings',
          ),
        ],
        selectedItemColor: Colors.purple,
        unselectedItemColor: Colors.grey,
        backgroundColor: Colors.white,
        elevation: 8,
      ),
    );
  }

  Widget buildPrayerTimeCard({
    required String title,
    required String time,
    required String timePostfix,
    required Color timeColor,
    required Color iconColor,
    required double scale,
    required Color backgroundColor,
    required Color titleColor,
    required String iconPath,
    String accentText = '',
  }) {
    Text titleElement = Text(
      title,
      style: TextStyle(
          fontSize: scale * 3,
          fontWeight: FontWeight.w600,
          color: titleColor
      ),
    );
    Text accentTextElement = Text(
      accentText,
      style: TextStyle(
          fontSize: scale * 4,
          fontWeight: FontWeight.bold,
          color: const Color(0xFFE9AA81)
      ),
    );
    Row timeElement = Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(
            time,
            style: TextStyle(
              fontSize: scale * 4,
              color: timeColor,
            ),
          ),
          Text(
            timePostfix,
            style: TextStyle(
              fontSize: scale * 2,
              color: timeColor,
            ),
          ),
        ]
    );
    Image iconImage = Image.asset(iconPath, width: scale * 10, height: scale * 10);
    List<Widget> widgets = [
      titleElement,
      accentTextElement,
      SizedBox(height: scale * 1),
      Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          timeElement,
          iconImage
        ],
      )
    ];
    if (accentText == '') {
      widgets.removeAt(1);
    }
    return Container(
      width: scale * 40,
      height: scale * 35,
      padding: EdgeInsets.all(scale * 4),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(scale * 7),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: widgets,
      ),
    );
  }

  Widget buildDailyDuaCard(double scale) {
    return Container(
      padding: EdgeInsets.all(scale * 4),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(scale * 5),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            blurRadius: 10,
            spreadRadius: 5,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Daily Dua',
            style: TextStyle(
              fontSize: scale * 4.5,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: scale * 2),
          Text(
            '"Our Lord! Accept (this service) from us: For Thou art the All-Hearing, the All-knowing."',
            style: TextStyle(
              fontSize: scale * 4,
              color: Colors.grey,
            ),
          ),
          SizedBox(height: scale * 2),
          Text(
            'Surah Al-Baqarah - 2:127',
            style: TextStyle(
              fontSize: scale * 3.5,
              fontStyle: FontStyle.italic,
              color: Colors.purple,
            ),
          ),
        ],
      ),
    );
  }

  Widget buildCategoriesSection(double scale) {
    return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              SizedBox(width: scale * 3),
              Text(
                'Categories',
                style: TextStyle(
                  fontSize: scale * 4.5,
                  fontWeight: FontWeight.bold,
                ),
              )
            ],
          ),
          SizedBox(height: scale * 3),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              buildCategoryCard("assets/prayer-time.png", 'Prayer Time', scale),
              buildCategoryCard("assets/mosque-finder.png", 'Mosque Finder', scale),
              buildCategoryCard("assets/al-quran.png", 'Al-Quran', scale),
            ],
          )
        ]
    );
  }

  Widget buildCategoryCard(String imagePath, String title, double scale) {
    return Container(
      width: scale * 25, // Square width
      height: scale * 25, // Square height
      padding: EdgeInsets.all(scale * 3),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(scale * 5),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            blurRadius: 10,
            spreadRadius: 5,
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Image.asset(
            imagePath,
            width: scale * 10, // Adjust image size
            height: scale * 10,
          ),
          SizedBox(height: scale * 2), // Space between image and text
          Text(
            title,
            style: TextStyle(
              fontSize: scale * 2,
              fontWeight: FontWeight.w600,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  // Function to navigate to the second page with animation
  void _navigateToSecondPage(BuildContext context) {
    Navigator.of(context).push(_createRoute());
    setState(() {
      _selectedIndex = 0;
    });
  }

  // Route for custom animated transition
  Route _createRoute() {
    return PageRouteBuilder(
      pageBuilder: (context, animation, secondaryAnimation) => SchedulePage(
        transfer_value: transfer_value
      ),
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        const begin = Offset(0.0, 1.0);
        const end = Offset.zero;
        const curve = Curves.ease;

        var tween = Tween(begin: begin, end: end).chain(CurveTween(curve: curve));
        var offsetAnimation = animation.drive(tween);

        return SlideTransition(
          position: offsetAnimation,
          child: child,
        );
      },
    );
  }
}