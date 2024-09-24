import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

Color mainPurpleColor = Color(0xFF6348ed);
Color accentPurpleColor = Color(0xFF5135e1);

class SchedulePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    double screenWidth = MediaQuery.of(context).size.width;
    double scale = screenWidth / 100;

    return Scaffold(
      body: Expanded(
        child: SingleChildScrollView(
          child: Container(
            color: mainPurpleColor,
            child: Column(
              children: [
                Container(
                  width: scale * 80,
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          IconButton(
                            icon: Icon(Icons.arrow_back),
                            onPressed: () {
                              Navigator.of(context).pop();
                            },
                          ),
                          IconButton(onPressed: (){},icon: Icon(Icons.alarm))
                        ],
                      ),
                      SizedBox(height: 20),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '28 March, 2021',
                            style: TextStyle(
                                color: Colors.white,
                                fontSize: scale * 4,
                                fontWeight: FontWeight.bold
                            ),
                          ),
                          SizedBox(height: 16),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              getDayElement('Mo', '22', scale),
                              getDayElement('Tu', '23', scale),
                              getDayElement('We', '24', scale),
                              getDayElement('Th', '25', scale),
                              getDayElement('Fr', '26', scale),
                              getDayElement('Sa', '27', scale),
                              getDayElement('Su', '28', scale, isActive: true),
                            ],
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                SizedBox(height: 20),
                Container(
                    decoration: BoxDecoration(
                        borderRadius: BorderRadius.only(
                            topLeft: Radius.circular(scale * 10),
                            topRight: Radius.circular(scale * 10),
                        ),
                        color: Colors.white
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: scale * 80,
                          child: Column(
                            children: [
                              SizedBox(height: scale * 8),
                              Container(
                                width: scale * 80,
                                child: Row(
                                  children: [
                                    Image.asset('assets/mechet.png', width: scale * 20),
                                    SizedBox(width: scale * 5),
                                    Text(
                                      'Do you have a\nfasting today?',
                                      style: TextStyle(fontWeight: FontWeight.bold),
                                    ),
                                    SizedBox(width: scale * 10),
                                    Icon(Icons.check)
                                  ],
                                ),
                              ),
                              Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Schedule',
                                    style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: scale * 4
                                    ),
                                  ),
                                ],
                              ),
                              getScheduleElement(true, 'Suhoor', '02:00 AM - 04:36 AM', 'moon.png', scale),
                              getScheduleElement(false, 'Dhuhur', '12:07 PM - 04:12 PM', 'sun.png', scale),
                              getScheduleElement(false, 'Asr', '04:30 PM - 06:12 PM', 'cloudy.png', scale),
                              getScheduleElement(false, 'Iftar', '06:16 PM - 07:28 PM', 'cloudy-wind.png', scale),
                            ],
                          ),
                        )
                      ],
                    )
                ),
              ],
            ),
          ),
        )
      )
    );
  }

  Widget getDayElement(
    String topText,
    String bottomText,
    double scale,
    {bool isActive = false}
  ) {
    return Container(
      width: scale * 8, // Responsive width
      height: scale * 12,
      decoration: BoxDecoration(
        color: isActive ? accentPurpleColor : mainPurpleColor,
        borderRadius: BorderRadius.circular(scale * 3),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          Text(topText, style: TextStyle(
            color: Colors.white,
            fontSize: scale * 2
          )),
          Text(bottomText, style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.white,
              fontSize: scale * 3
          ))
        ],
      ),
    );
  }

  Widget getScheduleElement(
      bool isActive, String text, String time, String iconName, double scale
  ) {
    return Container(
      child: Column(
        children: [
          Container(
            height: scale * 15,
            child: Row(
                children: [
                  SvgPicture.asset(
                    'assets/${isActive ? '' : 'in'}active_schedule.svg',
                    width: scale * 6,
                  ),
                  SizedBox(width: scale * 10),
                  Container(
                    decoration: BoxDecoration(
                      boxShadow: [
                        BoxShadow(
                          color: Colors.grey.withOpacity(0.2),
                          blurRadius: 10,
                          spreadRadius: 5,
                        )
                      ]
                    ),
                    child: Row(
                      children: [
                        Container(
                          decoration: BoxDecoration(
                              color: Color(0xFFeeebff),
                              borderRadius: BorderRadius.circular(scale * 3)
                          ),
                          child: Image.asset(
                            'assets/$iconName',
                            width: scale * 10, // Adjust image size
                            height: scale * 10,
                          ),
                        ),
                        SizedBox(width: scale * 4),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              text,
                              style: TextStyle(fontWeight: FontWeight.bold),
                            ),
                            Text(
                                time,
                                style: TextStyle(color: Colors.grey, fontSize: scale * 3)
                            )
                          ],
                        )
                      ],
                    ),
                  )
                ]
            ),
          ),
          Row(
            children: [
              SizedBox(width: scale * 2.5),
              SvgPicture.asset(
                'assets/striped_line.svg',
                height: scale * 10,
              )
            ],
          )
        ],
      )
    );
  }
}
