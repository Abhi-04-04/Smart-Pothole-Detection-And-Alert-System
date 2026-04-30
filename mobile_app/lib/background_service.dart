import 'dart:async';
import 'dart:convert';
import 'package:flutter_background_service/flutter_background_service.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;

const backendURL =
    "https://pothole-detection-1-i67w.onrender.com";

Future<void> initializeService() async {

  final service = FlutterBackgroundService();

  await service.configure(

    androidConfiguration:

        AndroidConfiguration(

      onStart: onStart,

      autoStart: true,

      isForegroundMode: true,

    ),

    iosConfiguration: IosConfiguration(),

  );

}

void onStart(ServiceInstance service) {

  service.on("stopService").listen((event) {

    service.stopSelf();

  });

  service.invoke("setAsForeground");

  Timer.periodic(

    const Duration(seconds: 10),

    (timer) async {

      Position position =
          await Geolocator.getCurrentPosition();

      double lat = position.latitude;

      double lon = position.longitude;

      final response = await http.get(

        Uri.parse(
          "$backendURL/nearby_potholes?lat=$lat&lon=$lon"
        ),

      );

      if (response.statusCode == 200) {

        var data = json.decode(response.body);

        if (data.length > 0) {

          print("Background alert: pothole ahead");

        }

      }

    },

  );

}