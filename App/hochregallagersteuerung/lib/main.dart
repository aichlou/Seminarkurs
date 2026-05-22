import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';
import 'package:http/http.dart' as http;

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

  Widget contentVerarbeiten() {
    debugPrint('Content Verarbeiten Funktion: $content');
    if(content.isEmpty) {
      return NoArticles();
    }
    else if(content[0] == 'Search') {
      return LoadArticles();
    }
    else if(content[0] == 'Error') {
      return NotFound();
    }
    return showArticles(content);
  }

  Widget showArticles(List<String> articles) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.start,
      children: [
        for (String article in articles) ...[
          SizedBox(height: 10,),
          showArticle(article),
        ]
      ],
    );
  }

  Widget showArticle(String article) {
    return Text(article);
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
        Uri.parse('http://$ipAddr:5000/fetch')
      );
      debugPrint('Antwort: ${response.body}');
      content = [response.body];
      if (content[0] == 'Kein Inhalt') {
        content = [];
      }
      setState(() {});
    }
    catch (error) {
      debugPrint(error.toString()); //Server nicht gefunden vmtl
      if (error.toString().startsWith('ClientException with SocketException: Connection refused')) {
        debugPrint('Server nicht gefunden');
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
      body: Center(
        child: Column(
          mainAxisAlignment: .start,
          children: [
            SizedBox(height: 30,),
            contentVerarbeiten(),
          ],
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

class Nothing extends StatelessWidget {
  const Nothing({super.key});

  @override
  Widget build(BuildContext context) {
    return Column();
  }
}