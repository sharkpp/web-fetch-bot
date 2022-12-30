# web-fetch-bot

A tool for downloading books on the web.

To use it, you need a recipe that suits your target.

## usage

```console
$ git clone https://github.com/sharkpp/web-fetch-bot.git web-fetch-bot
$ cd web-fetch-bot
$ pip install -r src/requirements.lock
$ python src/main.py https://example.net/donquijote/episode/15
$ ls
don quijote vol.15/
```

## directory tree

```console
/
+-- src/
+-- tools/
+-- recipes/
      +-- pages/
      +-- series/
```

