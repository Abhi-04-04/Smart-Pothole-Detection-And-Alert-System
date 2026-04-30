import 'package:image_picker/image_picker.dart';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'background_service.dart';
import 'package:camera/camera.dart';
import 'dart:async';

void main() async {

  WidgetsFlutterBinding.ensureInitialized();

  await initializeService();

  runApp(const PotholeApp());

}

class PotholeApp extends StatelessWidget {
const PotholeApp({super.key});

@override
Widget build(BuildContext context) {
return const MaterialApp(
home: MapScreen(),
);
}
}

class MapScreen extends StatefulWidget {
const MapScreen({super.key});

@override
State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
CameraController? cameraController;
List<CameraDescription>? cameras;
bool autoDetectEnabled = false;
Timer? detectionTimer;
// final String backendIP = "http://10.10.48.104:8000";
final String backendIP = "https://pothole-detection-1-i67w.onrender.com";

List<Marker> potholeMarkers = [];

bool alertShown = false;

// -----------------------------
// LOAD NEARBY POTHOLES
// -----------------------------
Future<void> startAutoDetection() async {
  cameras = await availableCameras();

  cameraController = CameraController(
    cameras ![0],
    ResolutionPreset.medium,
    enableAudio: false,
  );
  await cameraController!.initialize();
  autoDetectEnabled = true;
  detectionTimer = Timer.periodic(
    const Duration(seconds: 15),
    (_) => sendAutoFrame(),
  ); 
}

Future<void> sendAutoFrame() async {
  if (!autoDetectEnabled || cameraController == null) return;

  try {
    final image = await cameraController!.takePicture();
    Position position = await Geolocator.getCurrentPosition();

    var request = http.MultipartRequest(
      "POST",
      Uri.parse("$backendIP/detect_from_mobile"),
    );

    request.files.add(
      await http.MultipartFile.fromPath(
        "image",
        image.path,
      ),
    );

    request.fields["latitude"] = position.latitude.toString();
    request.fields["longitude"] = position.longitude.toString();

    await request.send();

    await loadNearbyPotholes();
  } catch (_) {}
}

void stopAutoDetection() {
  detectionTimer?.cancel();
  autoDetectEnabled = false;
}
Future<void> loadNearbyPotholes() async {

 
Position position =
    await Geolocator.getCurrentPosition();

double lat = position.latitude;
double lon = position.longitude;

final response = await http.get(
  Uri.parse(
    "$backendIP/nearby_potholes?lat=$lat&lon=$lon"
  )
);

if (response.statusCode == 200) {

  var data = json.decode(response.body);

  List<Marker> markers = [];


  // -----------------------------
  // LIVE ALERT POPUP
  // -----------------------------

  if (data.length > 0 && !alertShown) {

    alertShown = true;

    showDialog(
      context: context,
      builder: (context) => const AlertDialog(
        title: Text(" Pothole Ahead"),
        content: Text("Detected within 100 meters"),
      ),
    );
  }


  // -----------------------------
  // CREATE MARKERS
  // -----------------------------

  for (var pothole in data) {

    Color color;

    if (pothole["severity"] == "LOW") {
      color = Colors.green;
    }
    else if (pothole["severity"] == "MEDIUM") {
      color = Colors.orange;
    }
    else {
      color = Colors.red;
    }


    markers.add(

      Marker(

        point: LatLng(
          pothole["latitude"],
          pothole["longitude"],
        ),

        width: 40,
        height: 40,

        child: GestureDetector(

          onTap: () async {

            await http.post(
              Uri.parse(
                "$backendIP/auto_repair_check"
                "?lat=${pothole["latitude"]}"
                "&lon=${pothole["longitude"]}"
                ),
            );

            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content:
                    Text("Repair confirmation submitted"),
              ),
            );

            await loadNearbyPotholes();

          },

          child: Icon(
            Icons.warning,
            color: color,
            size: 35,
          ),

        ),

      ),

    );

  }

  setState(() {
    potholeMarkers = markers;
  });

}
 

}

@override
void initState() {

 
super.initState();

loadNearbyPotholes();
 

}

// -----------------------------
// CAMERA DETECTION FUNCTION
// -----------------------------

Future<void> captureAndDetect() async {

 
final imagePicker = ImagePicker();

final image = await imagePicker.pickImage(
  source: ImageSource.camera,
);

if (image == null) return;

Position position =
    await Geolocator.getCurrentPosition();

var request = http.MultipartRequest(

  "POST",

  Uri.parse("$backendIP/detect_from_mobile"),

);

request.files.add(
  await http.MultipartFile.fromPath(
    "image",
    image.path,
  ),
);

request.fields["latitude"] =
    position.latitude.toString();

request.fields["longitude"] =
    position.longitude.toString();


await request.send();


ScaffoldMessenger.of(context).showSnackBar(
  const SnackBar(
    content: Text("Frame sent for detection"),
  ),
);


// refresh map markers after detection
await loadNearbyPotholes();
 

}

@override
Widget build(BuildContext context) {

 
return FutureBuilder<Position>(

  future: Geolocator.getCurrentPosition(),

  builder: (context, snapshot) {

    if (!snapshot.hasData) {

      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );

    }

    Position position = snapshot.data!;


    return Scaffold(

      appBar: AppBar(
        title: const Text("Smart Pothole Map"),
      ),


      // -----------------------------
      // CAMERA DETECTION BUTTON
      // -----------------------------

      floatingActionButton:Column(
        mainAxisAlignment:MainAxisAlignment.end,
        children:[
          FloatingActionButton(
            heroTag:"manual",
            onPressed: captureAndDetect,
            child: const Icon(Icons.camera_alt),
          ),
          const SizedBox(height: 12),
          FloatingActionButton(
            heroTag:"auto",
            backgroundColor:
                autoDetectEnabled ? Colors.red : Colors.green,
            onPressed: () {
              if (autoDetectEnabled) {
                stopAutoDetection();
              }
              else {
                startAutoDetection();
              }
              setState(() {
                
              });
            },
            child: Icon(
              autoDetectEnabled
                  ? Icons.stop
                  : Icons.play_arrow,
            ),
          ),
        ],
      ),


      body: FlutterMap(

        options: MapOptions(

          initialCenter: LatLng(
            position.latitude,
            position.longitude
          ),

          initialZoom: 15,

        ),

        children: [

          TileLayer(

            urlTemplate:
                "https://tile.openstreetmap.org/{z}/{x}/{y}.png",

            userAgentPackageName:
                "com.example.pothole_app",

          ),

          MarkerLayer(
            markers: potholeMarkers,
          ),

        ],

      ),

    );

  },

);
 

}

}


