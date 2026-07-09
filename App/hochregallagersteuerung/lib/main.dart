import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter/gestures.dart';

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
      scrollBehavior: const MaterialScrollBehavior().copyWith(
        dragDevices: {
          PointerDeviceKind.touch,
          PointerDeviceKind.mouse,
          PointerDeviceKind.trackpad,
        },
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
  String ipAddr = '100.80.147.7';
  final TextEditingController _controller = TextEditingController();
  List<String> content = ['Search'];
  String addContent = 'Search';
  Map<String, dynamic> data = {'default': 'default'};
  final _nameController = TextEditingController();
  final _beschreibungController = TextEditingController();
  bool _isAddDialogOpen = false;

  Widget contentVerarbeiten() {
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
      return showArticles();
    }
  }

  void addDialog() {
    late StateSetter dialogSetState;
    bool isSetStarted = false;
    setState(() { _isAddDialogOpen = true; });
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('Neues Item hinzufügen'),
              content: StatefulBuilder(
            builder: (context, setState) {
              dialogSetState = setState; 
              if (!isSetStarted) {
                isSetStarted = true;
                WidgetsBinding.instance.addPostFrameCallback((_) {
                  if (_isAddDialogOpen) isSet(dialogSetState);
                });
              }
              return addContentVerarbeiten();
            },
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                fetchContent();
                sendItem(_nameController.text, _beschreibungController.text);
              },
              child: Text('Item lagern'),
            ),
          ],
        );
      },
    ).then((_) {
      // Dialog closed
      if (mounted) setState(() { _isAddDialogOpen = false; });
    });
  }

  Widget addContentVerarbeiten() {
    switch(addContent) {
      case 'Search':
        return LoadArticles();
      case 'Error':
        return NotFound();
      case 'Document':
        return newItem();
      case 'FillBox':
        return FillBox();
      default:
        return Nothing();
    }
  }

  double _dismissProgress = 0;
  DismissDirection _dismissDirection = DismissDirection.endToStart;

  Widget showArticles() {
    // If the backend returned the special "Kein Inhalt" map, show empty state
    if (data.isEmpty) return NoArticles();
    if (data.length == 1) {
      final firstVal = data.values.first;
      if (firstVal is String && firstVal == 'Kein Inhalt') return NoArticles();
    }

    return Align(
      alignment: Alignment.topCenter,
      child: RefreshIndicator(
        triggerMode: RefreshIndicatorTriggerMode.onEdge,
        onRefresh: () => fetchContent(showContent: false),
        child: ListView(
          scrollDirection: Axis.vertical,
          shrinkWrap: true,
          padding: const EdgeInsets.all(4),
          children: [
            for (var entry in data.entries) ...[
              if (entry.value is Map) Dismissible(
                key: Key(entry.key),
                background: FractionallySizedBox(
                  alignment: _dismissDirection == DismissDirection.startToEnd ? Alignment.centerLeft : Alignment.centerRight,
                  widthFactor: _dismissProgress,
                  child: Container(
                    alignment: Alignment.centerLeft,
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(400),
                      color: Colors.red,
                    ),
                    child: const Row(
                      children: [
                        SizedBox(width: 20,),
                        Icon(Icons.delete, color: Colors.white)
                      ]
                    ),
                  ),
                ),
                onUpdate: (details) => setState(() {
                  _dismissProgress = details.progress;
                  _dismissDirection = details.direction;
                }),
                onDismissed: (_) => returnItem(entry.key),
                child: Padding(
                  padding: EdgeInsets.only(bottom: 16),
                  child: showArticle(entry.value),
                ),
              ),
            ]
          ],
        )
      )
    );
  }

  Widget showArticle(dynamic article) {
    final name = article['name'] ?? 'Unbenannt';
    final beschreibung = article['beschreibung'] ?? '';

    return Container(
      width: MediaQuery.of(context).size.width,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        borderRadius: const BorderRadius.all(Radius.circular(12)),
        color: Colors.blue.shade700,
        border: Border.all(
          color: Colors.lightBlue,
          width: 2,
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  beschreibung,
                  style: const TextStyle(
                    fontSize: 14,
                    color: Colors.white70,
                  ),
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: Colors.lightBlue,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.inventory_2, color: Colors.white),
          ),
        ],
      ),
    );
  }

Widget newItem() {
  return Column(
    mainAxisSize: MainAxisSize.min,
    children: [
      TextField(
        controller: _nameController,
        decoration: const InputDecoration(
          labelText: 'Name',
          border: OutlineInputBorder(),
        ),
      ),
      const SizedBox(height: 12),
      TextField(
        controller: _beschreibungController,
        decoration: const InputDecoration(
          labelText: 'Beschreibung',
          border: OutlineInputBorder(),
        ),
      ),
    ],
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
                if (_controller.text != "") {
                  ipAddr = _controller.text;
                }
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

  Future<List<List<String>>> fetchContent({bool showContent = true}) async {
    try {
      content = ['Search'];
      if (showContent) setState(() {});
      final response = await http.get(
        Uri.parse('http://$ipAddr:5001/fetch')
      );
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
      if (showContent) setState(() {});
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
      if (showContent) setState(() {});
      return [['Error']];
    }
    return [['']];
  }

  Future<void> initRequest() async {
    http.Response response;
    try {
      response = await http.get(
        Uri.parse('http://$ipAddr:5001/init')
      );
    }
    catch (e) {
      content = ['Error'];
      setState(() {});
      return;
    }
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
  bool _isSetInProgress = false;

  Future<void> isSet(StateSetter? dialogSetState) async { //TODO: Lichtschranke AHHH
    if (_isSetInProgress) return;
    _isSetInProgress = true;
    try {
      while (true) {
        final response = await http.get(
          Uri.parse('http://$ipAddr:5001/isset')
        );
        final body = response.body.trim();
        const Map<String,String> map = {
          'YES': 'Document',
          'NO': 'FillBox'
        };
        if (response.statusCode != 200) {
          addContent = 'Error';
          try {
            dialogSetState?.call(() {});
          } catch (_) {
            // dialog likely closed/disposed; stop polling
            break;
          }
          break;
        }

        addContent = map[body] ?? 'Error';
        // stop polling if dialog was closed
        if (!_isAddDialogOpen) break;
        try {
          dialogSetState?.call(() {});
        } catch (_) {
          break;
        }

        if (body == 'YES' || body == 'Error') {
          break;
        }

        if (!_isAddDialogOpen) break;
        await Future.delayed(const Duration(seconds: 2));
      }
    }
    catch (e) {
      addContent = 'Error';
      debugPrint(e.toString());
      try {
        dialogSetState?.call(() {});
      } catch (_) {
        // ignore: setState after dispose or dialog already closed
      }
    }
    finally {
      _isSetInProgress = false;
    }
    return;
  }

  Future<void> sendItem(String name, String beschreibung) async {
    final response = await http.get(
      Uri.parse('http://$ipAddr:5001/send?name=$name&beschreibung=$beschreibung')
    );
    debugPrint('Antwort Send Request: ${response.body}');
    return;
  }

  Future<void> returnItem(String id) async {
    data.remove(id);
    final response = await http.get(
      Uri.parse('http://$ipAddr:5001/return?id=$id')
    );
    debugPrint('Antwort return Request: ${response.body}');
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
      body: Center(child:contentVerarbeiten()),
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
            onPressed: addDialog,
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
        SizedBox(height: 10,),
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
        SizedBox(height: 10,),
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
        SizedBox(height: 10,),
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

class FillBox extends StatelessWidget {
  const FillBox({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SizedBox(height: 10,),
        Text('Fülle die Box und stelle Sie auf die Station'),
        Lottie.asset(
          'assets/animations/box-changecolor.json',
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