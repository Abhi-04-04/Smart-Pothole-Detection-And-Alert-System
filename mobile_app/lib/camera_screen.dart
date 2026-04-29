// import 'dart:io';
// import 'package:flutter/material.dart';
// import 'package:image_picker/image_picker.dart';
// import 'package:http/http.dart' as http;
// import 'package:geolocator/geolocator.dart';

// class CameraScreen extends StatefulWidget {
// const CameraScreen({super.key});

// @override
// State<CameraScreen> createState() => _CameraScreenState();
// }

// class _CameraScreenState extends State<CameraScreen> {

// final picker = ImagePicker();

// final backendIP = "http://192.168.1.12:5000";

// Future captureAndSend() async {

 
// final image = await picker.pickImage(
//   source: ImageSource.camera
// );

// if (image == null) return;

// Position position =
//     await Geolocator.getCurrentPosition();

// var request = http.MultipartRequest(
//   "POST",
//   Uri.parse("$backendIP/detect_from_mobile"),
// );

// request.files.add(
//   await http.MultipartFile.fromPath(
//     "image",
//     image.path,
//   ),
// );

// request.fields["latitude"] =
//     position.latitude.toString();

// request.fields["longitude"] =
//     position.longitude.toString();

// await request.send();

// ScaffoldMessenger.of(context).showSnackBar(
//   const SnackBar(
//     content: Text("Frame sent for detection"),
//   ),
// );
 

// }

// @override
// Widget build(BuildContext context) {

 
// return Scaffold(

//   appBar: AppBar(
//     title: const Text("Capture Road Frame"),
//   ),

//   body: Center(

//     child: ElevatedButton(
//       onPressed: captureAndSend,
//       child: const Text("Capture & Detect"),
//     ),

//   ),

// );
// }
// }
