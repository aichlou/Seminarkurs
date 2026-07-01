import 'dart:io';

import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hochregallagersteuerung',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: .fromSeed(seedColor: Colors.blue),
      ),
      home: const HomePage(title: 'Hochregallagersteuerung'),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key, required this.title});
  final String title;
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String ipAddr = '127.0.0.1';
  final TextEditingController _controller = TextEditingController();
  List<String> content = ['Search'];
  Map<String, dynamic> data = {'default': 'default'};

  Widget contentVerarbeiten() {
    debugPrint('Content Verarbeiten Funktion: $content');
    if(content.isEmpty || content[0] == '') {
      return NoArticles();
    }
    else if(content[0] == 'Search') {
      return LoadArticles();
    }
    else if(content[0] == 'Error') {
      return NotFound();
    }
    else if(content[0] == 'init') {
      return initWidget();
    }
    else if(content[0] == 'initialising') {
      return InitState();
    }
    else {
      debugPrint(content.toString());
      debugPrint('ARTIKEL WERDEN ANGEZEIGT');
      return showArticles();
    }
  }

  Widget showArticles() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.start,
      children: [
        for (var entry in data.entries) ...[
          showArticle(entry.value),
          SizedBox(height: 10,),
        ]
      ],
    );
  }

  Widget showArticle(dynamic article) {
    return Container(
      height: 100,
      width: MediaQuery.of(context).size.width - 20,
      padding: EdgeInsets.all(5),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.all(Radius.circular(20)),
        color: Colors.blue,
        border: Border.all(
          color: Colors.lightBlue,
          width: 3
        )
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            article['name'],
            style: TextStyle(
              fontSize: 20,
            ),  
          ),
          Text(article['age'].toString())
        ],
      ),
    );
  }

  void newItem() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('Neues Item hinzufügen'),
          content: Text('coming soon...'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context), // schließt den Dialog
              child: Text('Oköööö'),
            ),
          ],
        );
      },
    );
  }

  void settings() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('Einstellungen'),
          content: Row(
            children: [
              Text('IP-Adresse: '),
              Expanded(
                child: TextField(
                  controller: _controller,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  labelText: 'IP-Adresse',
                  hintText: ipAddr,
                ),
              ),
              )
            ]
          ),
          actions: [
            TextButton(
              onPressed: () {
                ipAddr = _controller.text;
                _controller.text = '';
                Navigator.pop(context);
              },
              child: Text('Tschau Kakao')
            )
          ]
        );
      }
    );
  }

  Future<List<List<String>>> fetchContent() async {
    try {
      content = ['Search'];
      setState(() {});
      final response = await http.get(
        Uri.parse('http://$ipAddr:5001/fetch')
      );
      debugPrint('Antwort: ${response.body}');
      content = [response.body];
      if (content[0] == "init") {
        content = ['init'];
      }
      else {
        data = jsonDecode(response.body);
        if (content[0] == 'Kein Inhalt') {
          content = [];
        }
      }
      setState(() {});
    }
    catch (error) {
      debugPrint(error.toString()); //Server nicht gefunden vmtl
      if (error.toString().startsWith('ClientException with SocketException: Connection refused')) {
        debugPrint('Server nicht gefunden');
      }
      else if (error.toString().startsWith('FormatException: Unexpected character')) {
        debugPrint('JSON kann nicht korret entcodet werden');
      }
      else {
        debugPrint('Ein Unbekannter Fehler ist aufgetreten. Probleme mit der Connection zum Server');
      }
      content = ['Error'];
      setState(() {});
      return [['Error']];
    }
    return [['']];
  }

  Future<void> initRequest() async {
    //content = ['Search'];
    //setState(() {});
    final response = await http.get(
      Uri.parse('http://$ipAddr:5001/init')
    );
    debugPrint('Antwort init Request: ${response.body}');
    switch(response.body) {
      case 'OK':
      case 'IS':
        content = ['initialising'];
        break;
      case 'NO':
        content = [''];
        break;
    }
    debugPrint(content.toString());
    setState(() {});
    if (content[0] == 'initialising') {
      await Future.delayed(Duration(seconds: 2));
      initRequest();
    }
    else {
      fetchContent();
    }
    return;
  }

  @override
  void initState() {
    super.initState();
    fetchContent();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
        actions: [
          Image.network(
              'https://imgs.search.brave.com/ubHXZQH1SyCiBb6fMBIlmqo0Wo7atT8qph7mi4w5FYw/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5nZXR0eWltYWdl/cy5jb20vaWQvMjIz/MDM2NDQ0Mi9kZS92/ZWt0b3IvZ2FiZWxz/dGFwbGVyLW1pdC1r/aXN0ZW4tYXVmLXBh/bGV0dGUtcHJvZHVr/dGxpbmllLmpwZz9z/PTYxMng2MTImdz0w/Jms9MjAmYz1Da0Iz/bVJLbFBHTFdpZmtG/dEtteV9nZDNBZkN6/TVkzeDhwRlZwVFdl/d2hNPQ',
              width: 40,
              height: 40,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) {
                return Text('Fehler: $error');
              },
              loadingBuilder: (context, child, loadingProgress) {
                if (loadingProgress == null) return child;
                return CircularProgressIndicator();
              },
            ),
            SizedBox(width: 10)
        ],
      ),
      body: SingleChildScrollView(
        child: Center(
          child: Column(
            mainAxisAlignment: .start,
            children: [
              SizedBox(height: 10,),
              contentVerarbeiten(),
            ],
          ),
        ),
      ),
      floatingActionButton: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          FloatingActionButton(
            onPressed: fetchContent,
            tooltip: 'Connect to Server',
            child: const Icon(Icons.replay_outlined)
          ),
          SizedBox(height: 10,),
          FloatingActionButton(
            onPressed: settings,
            tooltip: 'Settings',
            child: const Icon(Icons.settings)),
          SizedBox(height: 10,),
          FloatingActionButton(
            onPressed: newItem,
            tooltip: 'Add new Item',
            child: const Icon(Icons.add),
          ),
          
        ]
      )
    );
  }

  Widget initWidget () {
    return TextButton(
      onPressed: initRequest,
      child: Text('Initialise'),
    );
  }
}

class LoadArticles extends StatelessWidget {
  const LoadArticles({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text("Verbinde zum Raspberry Pi..."),
        Lottie.asset(
          'assets/animations/Loading Dots Blue.json',
          width: 400,
          height: 200,
          repeat: true
        )
      ],
    );
  }
}


class NoArticles extends StatelessWidget {
  const NoArticles({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text("Keine Artikel im Lager"),
        Lottie.asset(
          'assets/animations/Empty box.json',
          width: 200,
          height: 200,
          repeat: true,
        )
      ]
    );
  }
}

class NotFound extends StatelessWidget {
  const NotFound({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Ip-Adresse nicht gefunden'),
        Lottie.asset(
          'assets/animations/Not Found.json',
          width: 250,
          height: 250,
          repeat: true,
        )
      ],
    );
  }
}

class InitState extends StatelessWidget {
  const InitState({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Initialising'),
        Lottie.asset(
          'assets/animations/Loading.json',
          width: 250,
          height: 250,
          repeat: true,
        )
      ]
    );
  }
}

class Nothing extends StatelessWidget {
  const Nothing({super.key});

  @override
  Widget build(BuildContext context) {
    return Column();
  }
}

